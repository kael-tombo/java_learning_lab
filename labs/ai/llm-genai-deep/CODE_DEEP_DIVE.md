# llm-genai-deep — Code Deep Dive

Java 21, no dependencies. Every component is implemented against deterministic test doubles —
a stub embedder, a stub generator, a stub corpus — so runs are reproducible and no network
call appears in a build.

## 1. Project Structure

```
llm-genai-deep/
  src/com/ailab/genai/
    embed/{Cbow,Skipgram,Glove,FastText,SentenceEncoder}.java
    index/{FlatIndex,LshIndex,IvfIndex,HnswIndex}.java
    rag/{Chunker,Retriever,Reranker,RagPipeline}.java
    eval/{RetrievalMetrics,Bleu,Rouge,BertscoreStub,Faithfulness}.java
    prompt/{PromptLibrary,SelfConsistency,ReAct,PromptOptimizer}.java
    agent/{AgentLoop,ToolRegistry,ToolGate,Memory,Approval}.java
    finetune/{Lora,QloraNf4,Dora}.java
    rlhf/{BradleyTerry,Dpo,PpoLite}.java
    hallucination/{Verifier,SelfConsistency,ChainOfVerification,Abstention}.java
    safety/{Sanitizer,DecodeDetector,TieredFilter,OutputPipeline,AuditLog}.java
    Main.java
```

## 2. Embeddings With the Anisotropy Fix

```java
public final class Embedding {

    public final double[] v;

    public double cosine(double[] other) {
        double d = 0, n1 = 0, n2 = 0;
        for (int i = 0; i < v.length; i++) {
            d += v[i] * other[i];
            n1 += v[i] * v[i];
            n2 += other[i] * other[i];
        }
        return d / (Math.sqrt(n1) * Math.sqrt(n2) + 1e-12);
    }

    /**
     * Mean-centering removes the dominant common direction that makes all raw embedding
     * cosines high (anisotropy). One pass, measurable improvement in separation.
     */
    public static List<double[]> centerAndWhiten(List<double[]> raw) {
        int d = raw.get(0).length;
        double[] mu = new double[d];
        for (double[] v : raw) for (int i = 0; i < d; i++) mu[i] += v[i];
        for (int i = 0; i < d; i++) mu[i] /= raw.size();
        for (double[] v : raw) for (int i = 0; i < d; i++) v[i] -= mu[i];
        return raw;                       // full whitening needs eigendecomposition; see Svd
    }

    /** Mean of the pairwise cosine BEFORE and AFTER centering -- the anisotropy diagnostic. */
    public static double meanPairwiseCosine(List<double[]> embs) {
        double s = 0;
        int n = 0;
        for (int i = 0; i < embs.size(); i++)
            for (int j = i + 1; j < embs.size(); j++) { s += new Embedding(embs.get(i)).cosine(embs.get(j)); n++; }
        return n == 0 ? 0 : s / n;
    }
}
```

The `meanPairwiseCosine` diagnostic is the whole reason centering exists. Raw sentence
embeddings often average cosine 0.6-0.8 — almost no discrimination. After centering it drops
toward 0.2, and separation becomes meaningful. Report the before/after number; it is
cheap and it justifies the step.

## 3. HNSW With a Measurable Recall Guarantee

```java
public final class Hnsw {

    public record Config(int m, int efConstruction, int efSearch) {
        public static Config defaults() { return new Config(16, 200, 64); }
    }

    private final int dim, maxLayer, m;
    private final int[] levels;                       // per-node level count
    private final Map<Integer, Set<Integer>>[] graph; // [layer][node] -> neighbours
    private final double[][] vectors;
    private final Rng rng;

    private double dist(int a, int b) {
        double s = 0;
        for (int i = 0; i < dim; i++) { double t = vectors[a][i] - vectors[b][i]; s += t * t; }
        return Math.sqrt(s);
    }

    private int randomLevel() {
        // exponential decay: P(level >= l) = exp(-l / mL)
        double lvl = -Math.log(Math.max(rng.nextDouble(), 1e-12)) * m;
        return (int) Math.floor(lvl);
    }

    /** Greedy descent on one layer, keeping the best ef candidates found. */
    private PriorityQueue<Cand> searchLayer(double[] q, int entry, int ef, int layer) {
        PriorityQueue<Cand> candidates = new PriorityQueue<>(Comparator.comparingDouble(Cand::dist));
        PriorityQueue<Cand> results = new PriorityQueue<>(Comparator.comparingDouble((Cand c) -> -c.dist()));
        Cand e = new Cand(entry, distVec(q, vectors[entry]));
        candidates.add(e); results.add(e);
        Set<Integer> visited = new HashSet<>();
        visited.add(entry);

        while (!candidates.isEmpty()) {
            Cand c = candidates.poll();
            if (results.size() >= ef && c.dist() > results.peek().dist()) break;   // convergence
            for (int nb : graph[layer].getOrDefault(c.id(), Set.of())) {
                if (!visited.add(nb)) continue;
                double d = distVec(q, vectors[nb]);
                if (results.size() < ef || d < results.peek().dist()) {
                    candidates.add(new Cand(nb, d));
                    results.add(new Cand(nb, d));
                    if (results.size() > ef) results.poll();
                }
            }
        }
        return results;
    }

    public List<Cand> search(double[] q, int k, int efSearch) {
        int ep = 0;
        for (int layer = maxLayer; layer >= 1; layer--)          // descend greedily, ef = 1
            ep = searchLayer(q, ep, 1, layer).peek().id();
        return searchLayer(q, ep, Math.max(efSearch, k), 0)
                .stream().sorted(Comparator.comparingDouble(Cand::dist)).limit(k).toList();
    }
}
```

The `efSearch` parameter is the entire query-time story: it widens the layer-0 beam, trading
latency for recall, with no rebuild. Report the recall/latency curve rather than a single
number, and always report recall against exact flat search — an HNSW index with unmeasured
recall is an assumption.

## 4. Chunking: The Step That Dominates Quality

```java
public final class Chunker {

    /**
     * STRUCTURAL chunking: a chunk carries its heading path. A retrieved chunk titled
     * "Refunds > Partial > Under 30 days" is usable; the same text without the heading is
     * nearly useless, because the section identity IS the answer for many questions.
     */
    public record Chunk(String id, String text, String headingPath, List<String> sourceSpans) {}

    public record Doc(String id, List<Section> sections) {}

    public record Section(String headingPath, String text) {}

    public List<Chunk> structural(Doc doc, int maxTokens, int overlap) {
        List<Chunk> out = new ArrayList<>();
        for (Section s : doc.sections()) {
            List<String> spans = tokenize(s.text());
            for (int i = 0; i < spans.size(); i += maxTokens - overlap) {
                int end = Math.min(spans.size(), i + maxTokens);
                String body = String.join(" ", spans.subList(i, end));
                // the heading goes INTO the embedded text, not just the metadata:
                // a bi-encoder only ever sees the embedded string
                String embedded = "[Section: " + s.headingPath() + "]\n" + body;
                out.add(new Chunk(doc.id() + "#" + out.size(), embedded, s.headingPath(),
                        spans.subList(i, end).stream().toList()));
            }
        }
        return out;
    }

    /** Fixed-size with overlap, as the baseline the structural version must beat. */
    public List<Chunk> fixed(String text, int maxTokens, int overlap) {
        List<String> spans = tokenize(text);
        List<Chunk> out = new ArrayList<>();
        for (int i = 0; i < spans.size(); i += maxTokens - overlap) {
            int end = Math.min(spans.size(), i + maxTokens);
            out.add(new Chunk("c" + out.size(), String.join(" ", spans.subList(i, end)), "",
                    spans.subList(i, end).stream().toList()));
        }
        return out;
    }
}
```

Two properties that matter. First, the heading goes **inside the embedded string** —
metadata a bi-encoder never sees is metadata that does not help. Second, `overlap` is
included in the step size (`maxTokens - overlap`, not `maxTokens`), so chunks do not
advance past the overlap window.

## 5. Reranking: Where Accuracy Is Won

```java
public final class Reranker {

    /**
     * Cross-encoder: score(q, d) is a function of the PAIR. This is what a bi-encoder
     * cannot express -- its score is a sum of products of independent projections, so it
     * cannot condition one side on the other.
     */
    public record Candidate(String id, double biEncoderScore, String text) {}

    public List<Candidate> rerank(String query, List<Candidate> candidates, int topK) {
        List<Candidate> scored = new ArrayList<>(candidates);
        for (Candidate c : scored) {
            double joint = crossEncoderScore(query, c.text());    // stub: token-overlap F1
            // blend rather than replace: the bi-encoder score is a useful prior and
            // replacing it discards a signal that costs nothing to keep
            c = new Candidate(c.id(), 0.6 * joint + 0.4 * c.biEncoderScore(), c.text());
            scored.set(scored.indexOf(c), c);
        }
        return scored.stream()
                .sorted(Comparator.comparingDouble(Candidate::biEncoderScore).reversed())
                .limit(topK).toList();
    }
}
```

Blending instead of replacing matters: the bi-encoder score is a cheap prior computed for
every candidate, and discarding it discards information for no benefit. Tune the blend weight
on a validation set and report it.

## 6. Retrieval and Generation Evaluated Separately

```java
public final class RetrievalMetrics {

    public record Graded(String docId, int relevance) {}

    public static double recallAtK(List<Graded> truth, List<String> retrieved, int k) {
        List<String> top = retrieved.subList(0, Math.min(k, retrieved.size()));
        long hit = truth.stream().filter(g -> g.relevance() > 0 && top.contains(g.docId())).count();
        long total = truth.stream().filter(g -> g.relevance() > 0).count();
        return total == 0 ? Double.NaN : (double) hit / total;   // NaN, not 0: "no relevant docs"
    }

    public static double ndcgAtK(List<Graded> truth, List<String> retrieved, int k) {
        List<String> top = retrieved.subList(0, Math.min(k, retrieved.size()));
        Map<String, Integer> rel = truth.stream()
                .collect(Collectors.toMap(Graded::docId, Graded::relevance, (a, b) -> Math.max(a, b)));
        double dcg = 0;
        for (int i = 0; i < top.size(); i++) {
            int r = rel.getOrDefault(top.get(i), 0);
            if (r > 0) dcg += (Math.pow(2, r) - 1) / (Math.log(i + 2) / Math.log(2));
        }
        List<Integer> ideal = truth.stream().map(Graded::relevance)
                .sorted(Comparator.reverseOrder()).toList();
        double idcg = 0;
        for (int i = 0; i < Math.min(k, ideal.size()); i++)
            idcg += (Math.pow(2, ideal.get(i)) - 1) / (Math.log(i + 2) / Math.log(2));
        return idcg == 0 ? Double.NaN : dcg / idcg;
    }
}
```

`exponential gain` (`2^r - 1`) rather than linear `r`, and `log(i+2)` rather than
`log2(i+1)` so rank 1 is finite. And `NaN` rather than `0` when there are no relevant
documents — returning 0 there silently punishes a query set that is simply malformed.

## 7. BLEU With Clipping and Brevity Penalty

```java
public final class Bleu {

    public static double bleu4(List<String> referenceTokens, List<String> candidateTokens) {
        int maxN = 4;
        double logSum = 0;
        for (int n = 1; n <= maxN; n++) {
            Map<String, Integer> refCounts = ngramCounts(referenceTokens, n);
            Map<String, Integer> candCounts = ngramCounts(candidateTokens, n);
            int clipped = 0, total = 0;
            for (var e : candCounts.entrySet()) {
                total += e.getValue();
                // CLIPPED precision: cap the candidate count at the reference count.
                // Without clipping, repeating one n-gram scores arbitrarily high.
                clipped += Math.min(e.getValue(), refCounts.getOrDefault(e.getKey(), 0));
            }
            if (total == 0) return 0.0;                       // no candidate n-grams of this order
            logSum += Math.log(clipped / (double) total) / maxN;
        }
        double c = candidateTokens.size(), r = referenceTokens.size();
        double bp = c > r ? 1.0 : Math.exp(1 - r / Math.max(c, 1));
        return bp * Math.exp(logSum);                          // geometric mean, then BP
    }

    private static Map<String, Integer> ngramCounts(List<String> toks, int n) {
        Map<String, Integer> m = new HashMap<>();
        for (int i = 0; i + n <= toks.size(); i++)
            m.merge(String.join(" ", toks.subList(i, i + n)), 1, Integer::sum);
        return m;
    }
}
```

Three details that decide whether BLEU is meaningful: **clipping** (caps repetition),
the **geometric mean** (one zero precision order kills the score), and the **brevity penalty**
(under-generation is far worse than over-generation for translation).

## 8. LoRA With an Exact No-Op Initialization

```java
public final class Lora {

    public record Adapter(double[] a, double[] b, int dIn, int dOut) {
        public Adapter(int dIn, int dOut, int rank, Rng rng) {
            // A = 0 exactly -> delta W = 0 -> the adapted model starts IDENTICAL to the base.
            // A "small random" A is not equivalent: it perturbs the model before training.
            this.a = new double[rank * dIn];
            this.b = normal(dOut * rank, 0.02, rng);
            Arrays.fill(this.a, 0.0);
        }

        public double[] deltaW() {
            double[] dw = new double[dOut * dIn];
            for (int o = 0; o < dOut; o++)
                for (int k = 0; k < a.length / dIn; k++)
                    for (int i = 0; i < dIn; i++)
                        dw[o * dIn + i] += b[o * a.length / dIn + k] * a[k * dIn + i];
            return dw;
        }

        public static int trainable(int dIn, int dOut, int rank) { return rank * (dIn + dOut); }
    }

    /** Merge is exact: W + BA computed in double must reproduce the adapter's logits. */
    public static double[] merge(double[] w, Adapter ad) {
        double[] merged = w.clone();
        double[] dw = ad.deltaW();
        for (int i = 0; i < merged.length; i++) merged[i] += dw[i];
        return merged;
    }

    /**
     * NF4: quantiles of N(0,1) at the 16 bin centers. For normally distributed weights this
     * minimizes expected squared error; uniform bins waste resolution near zero, which is
     * where most weights live.
     */
    public static double[] nf4Quantize(double[] w) {
        double[] levels = normalQuantileLevels();          // 16 levels
        double max = Arrays.stream(w).map(Math::abs).max().orElse(1e-8);
        double scale = max / 8.0;                          // signed 4-bit: [-8, 7]
        double[] q = new double[w.length];
        for (int i = 0; i < w.length; i++) {
            double scaled = w[i] / scale;
            int idx = nearestLevel(scaled, levels);
            q[i] = levels[idx] * scale;                    // dequantize immediately (simulated)
        }
        return q;
    }
}
```

`Arrays.fill(this.a, 0.0)` is the load-bearing line. It makes the adapter an exact identity at
initialization, so any measured change is attributable to training rather than to
initialization noise. "Small random A" is not equivalent and is a common source of confusing
baseline numbers.

## 9. DPO — the Loss Is the Whole Method

```java
public final class Dpo {

    /**
     * L = -log sigma( beta * ( (log pi(y_w|x) - log pi_ref(y_w|x))
     *                          - (log pi(y_l|x) - log pi_ref(y_l|x)) ) )
     *
     * Derived by inverting the KL-constrained optimum
     *     pi*(y|x) = pi_ref(y|x) * exp(r(x,y)/beta) / Z(x)
     * for r, then substituting into the Bradley-Terry preference likelihood. The Z terms
     * cancel, so no reward model and no value function is ever fitted.
     */
    public static double loss(double logPiW, double logRefW, double logPiL, double logRefL, double beta) {
        double margin = beta * ((logPiW - logRefW) - (logPiL - logRefL));
        // numerically stable: -log sigmoid(z) = log(1 + e^-z) = softplus(-z)
        return Math.log1p(Math.exp(-margin));
    }

    public static double[] grads(double logPiW, double logRefW, double logPiL, double logRefL, double beta) {
        double margin = beta * ((logPiW - logRefW) - (logPiL - logRefL));
        double sig = 1.0 / (1.0 + Math.exp(margin));
        return new double[] {
                -beta * sig,      // d/d logPiW
                 beta * sig,      // d/d logRefW
                 beta * sig,      // d/d logPiL
                -beta * sig       // d/d logRefL
        };
    }

    /** The implicit reward. beta rescales it; the log-ratio shape is the actual signal. */
    public static double implicitReward(double logPi, double logRef, double beta) {
        return beta * (logPi - logRef);
    }
}
```

`Math.log1p(Math.exp(-margin))` instead of `-Math.log(1/(1+Math.exp(margin)))`: for a
margin of 50 the naive form computes `exp(50)` fine but `-Math.log(0.9999999999999938)` loses
precision; for `margin = -800` the naive form overflows to infinity while the stable form
returns 800. Exactly the log-sum-exp pattern from the maths track.

## 10. Agent Loop With Enforced Bounds

```java
public final class AgentLoop {

    public record Budget(int maxSteps, int maxSideEffects, int maxTokens) {}

    public record Stop(String reason) {}

    public enum Reason { TASK_COMPLETE, STEP_BUDGET, SIDE_EFFECT_BUDGET, NO_PROGRESS, REPEAT, TOOL_ERROR }

    public interface Model {
        /** Returns the next action: tool name and arguments, or a final answer. */
        Action next(List<Message> history) throws Exception;
    }

    public record Action(String type, String tool, Map<String, Object> args, String finalAnswer) {}

    public Result run(Model model, ToolRegistry tools, Budget budget, String task) {
        List<Message> history = new ArrayList<>();
        history.add(Message.user(task));
        int sideEffects = 0;
        Map<String, Integer> actionCounts = new HashMap<>();
        String lastObservation = "";

        for (int step = 1; step <= budget.maxSteps(); step++) {
            Action a;
            try { a = model.next(history); }
            catch (Exception e) {
                // a model failure must be observable, not silently swallowed into a
                // fabricated tool result the model then reasons about
                return Result.stopped(Reason.TOOL_ERROR, step, sideEffects, e.getMessage());
            }
            if (a.type().equals("final")) return Result.done(a.finalAnswer(), step, sideEffects);

            String key = a.tool() + "|" + new TreeMap<>(a.args());
            actionCounts.merge(key, 1, Integer::sum);
            if (actionCounts.get(key) >= 3)
                return Result.stopped(Reason.REPEAT, step, sideEffects, "repeated " + key);
            if (Objects.equals(lastObservation, key))
                return Result.stopped(Reason.NO_PROGRESS, step, sideEffects, null);
            lastObservation = key;

            if (tools.isWrite(a.tool())) {
                if (++sideEffects > budget.maxSideEffects())
                    return Result.stopped(Reason.SIDE_EFFECT_BUDGET, step, sideEffects, null);
                Approval approval = tools.approvalFor(a.tool(), a.args());
                if (!approval.granted())
                    return Result.stopped(Reason.TOOL_ERROR, step, sideEffects, "approval required: " + key);
            }
            String observation;
            try { observation = tools.invoke(a.tool(), a.args()); }
            catch (Exception e) { observation = "TOOL_ERROR: " + e.getMessage(); }
            history.add(Message.assistant(actionText(a)));
            history.add(Message.observation(observation));    // a REAL observation, always
        }
        return Result.stopped(Reason.STEP_BUDGET, budget.maxSteps(), sideEffects, null);
    }
}
```

Every termination reason is an explicit enum with a reason code, because "the agent stopped"
without knowing which bound fired is undiagnosable. The idempotency key is
`tool + sorted args`, so the same logical call from a different argument order is recognised.
And `Message.observation(...)` always carries a **real** tool result — the moment a stub
substitutes a model-generated string, accuracy collapses and the trace no longer means
anything.

## 11. Tiered Safety Filter From the Base-Rate Arithmetic

```java
public final class TieredFilter {

    public record Result(boolean blocked, double score, String stage) {}

    /** Stage 1: cheap and high-recall. Runs on 100% of traffic. */
    public static Result stage1(String text, double threshold) {
        double score = cheapSignals(text);          // keyword families + length + entropy
        return new Result(score >= threshold, score, "s1");
    }

    /**
     * Stage 2: precise classifier on the ~5% that survive. Running the precise model on
     * everything costs 10x more and buys nothing: at a 0.1% base rate the decisive factor
     * is FINGERPRINT ACCURACY, not the first stage's recall.
     */
    public static Result stage2(String text, double threshold) {
        double score = preciseClassifier(text);
        return new Result(score >= threshold, score, "s2");
    }

    /** Tiered handling, not one classifier. Precision collapses under a low base rate. */
    public static Result evaluate(String text, Cheap cheap, Precise precise) {
        Result r1 = stage1(text, cheap.threshold());
        if (!r1.blocked()) return new Result(false, r1.score(), "s1-pass");
        Result r2 = stage2(text, precise.threshold());
        return r2;
    }

    /** Report the operating point's numbers, never just "blocked". */
    public static String report(int tp, int fp, int fn, int tn) {
        double precision = (tp + fp) == 0 ? 0 : (double) tp / (tp + fp);
        double recall = (tp + fn) == 0 ? 0 : (double) tp / (tp + fn);
        return String.format("precision=%.3f recall=%.3f flags=%d (tp=%d fp=%d fn=%d tn=%d)",
                precision, recall, tp + fp, tp, fp, fn, tn);
    }
}
```

`report` exists because the temptation is to report a boolean. At a 0.1% disallowed rate a
"blocked" flag with 91% precision is a liability, and only the confusion matrix makes that
visible.

## 12. Output Pipeline That Fails Closed

```java
public final class OutputPipeline {

    public interface Stage { String name(); Check run(String output, Context ctx) throws Exception; }

    public record Check(boolean pass, String detail) {}

    public enum Outcome { PASS, BLOCK, FAIL_CLOSED }

    public record Result(Outcome outcome, String stage, String detail) {}

    public Result run(String output, Context ctx) {
        for (Stage s : stages) {
            Check c;
            try {
                c = s.run(output, ctx);
            } catch (Exception e) {
                // FAIL CLOSED. A stage that throws must block, not pass. try/catch that logs
                // and continues is the single most common serious defect in output filters.
                return new Result(Outcome.FAIL_CLOSED, s.name(), e.toString());
            }
            if (!c.pass()) return new Result(Outcome.BLOCK, s.name(), c.detail());
        }
        return new Result(Outcome.PASS, "all", "ok");
    }
}
```

The `catch` returning `FAIL_CLOSED` rather than propagating is the design. An exception
inside a guardrail means the guardrail did not evaluate, and "did not evaluate" must mean
"block". Every stage gets instrumented so the attribution histogram shows which layer caught
what — and the uncaught count is the number that matters.

## 13. Faithfulness by Claim Extraction

```java
public final class Faithfulness {

    public record Claim(String text, boolean supported, String supportingSpan) {}

    /**
     * Split into atomic claims and check each against the context. Checking the answer as a
     * whole gives a single number that hides WHICH claim was invented -- and the unsupported
     * claim is the actionable output.
     */
    public static List<Claim> verify(String answer, List<String> contextSpans) {
        List<Claim> out = new ArrayList<>();
        for (String sentence : splitSentences(answer)) {
            String best = null;
            for (String span : contextSpans) {
                double overlap = tokenOverlap(sentence, span);
                if (best == null || overlap > tokenOverlap(sentence, best)) best = span;
            }
            boolean supported = best != null && tokenOverlap(sentence, best) >= 0.8;
            out.add(new Claim(sentence, supported, supported ? best : null));
        }
        return out;
    }

    public static double faithfulness(List<Claim> claims) {
        return claims.isEmpty() ? 1.0 : claims.stream().filter(Claim::supported).count() / (double) claims.size();
    }
}
```

Claim-level granularity is what makes the output actionable. "This answer is 81%
faithful" is a metric; "sentence 3 has no support in the context" is a bug report you can
file. The same decomposition is what the output-pipeline grounding stage should use.

## 14. Audit Log With a Hash Chain

```java
public final class AuditLog {

    private String previous = "0".repeat(64);
    private final List<String> records = new ArrayList<>();

    public String append(String event, String actor) {
        String record = previous + "|" + event + "|" + actor + "|" + Instant.now();
        previous = sha256(record);
        records.add(previous);
        anchors.add(previous);                 // periodically published to an immutable store
        return previous;
    }

    /** Recompute the chain and return the index of the first mismatch, or -1. */
    public int verify() {
        String h = "0".repeat(64);
        for (int i = 0; i < events.size(); i++) {
            h = sha256(h + "|" + events.get(i) + "|" + actors.get(i) + "|" + times.get(i));
            if (!h.equals(records.get(i))) return i;
        }
        return -1;
    }

    /** An attacker who controls the writer can rewrite the WHOLE chain.
     *  External anchors are what make that detectable. */
    public void anchor(String immutableStore) { immutableStore.write(previous); }
}
```

Chain verification catches edits by a party without write access to history. It does **not**
catch a party who controls the writer, because they can rewrite every hash. External
anchoring is the mitigation, and both are needed.

## Self-Check

- [ ] Anisotropy measured before and after centering, with the number reported.
- [ ] HNSW recall measured against exact flat search, not assumed.
- [ ] `efSearch` treated as a query-time knob with a recall/latency curve.
- [ ] Chunk heading placed inside the embedded string, not only in metadata.
- [ ] Chunk step is `maxTokens - overlap`, not `maxTokens`.
- [ ] Reranker blends the bi-encoder prior rather than discarding it.
- [ ] Retrieval metrics return `NaN` when no relevant documents exist.
- [ ] NDCG uses exponential gain and `log(i+2)`.
- [ ] BLEU clips n-gram counts, uses a geometric mean, and applies the brevity penalty.
- [ ] LoRA `A` zero-initialized so the adapter starts as an exact no-op.
- [ ] Merge verified to reproduce adapter logits exactly.
- [ ] NF4 levels from normal quantiles, not uniform bins.
- [ ] DPO loss uses `log1p(exp(-margin))` rather than the naive form.
- [ ] Agent termination reasons are an explicit enum with codes.
- [ ] Tool observations are always real; a model-generated stub is a test failure.
- [ ] Write actions require approval and consume a side-effect budget.
- [ ] Safety filter reports the confusion matrix, not just a boolean.
- [ ] Output pipeline fails closed on exception.
- [ ] Faithfulness reported per claim, not only in aggregate.
- [ ] Audit chain verified by recomputation with external anchors.
