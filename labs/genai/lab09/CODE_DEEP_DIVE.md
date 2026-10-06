# Lab 09: LLM Evaluation & Benchmarks — Code Deep Dive

## 1. Project Structure

```
lab09/
  src/com/genai/lab09/
    text/Tokenizer.java              whitespace / char-ngram / mock BPE
    text/Normalize.java
    metric/ExactMatch.java
    metric/TokenF1.java
    metric/Bleu.java                 clipped n-gram precision + BP
    metric/Rouge.java                ROUGE-1/2/L/Lsum
    metric/BertScore.java            greedy embedding match
    metric/ConfusionMatrix.java, PerCategoryReport.java
    judge/LlmJudge.java              interface + Rubric
    judge/PositionBiasCorrected.java randomizes order, checks both orders
    judge/JudgeCalibration.java      agreement vs gold labels, drift detection
    halluc/ClaimSplitter.java
    halluc/Faithfulness.java
    halluc/AbstentionPolicy.java
    safety/RefusalMetrics.java, JailbreakSuite.java
    fairness/FairnessMetrics.java    parity, opportunity, bias ratio, intersectional
    stats/Bootstrap.java, PairedTest.java
    bench/Benchmark.java, BenchmarkRunner.java, RegressionDiff.java
    Main.java
```

## 2. Normalization and Tokenization

```java
public final class Normalize {
    private static final Pattern ARTICLES = Pattern.compile("\\b(a|an|the)\\b", Pattern.CASE_INSENSITIVE);
    private static final Pattern PUNCT    = Pattern.compile("[^\\p{L}\\p{N}\\s]");

    public static String forMatch(String s) {
        String t = ARTICLES.matcher(s.toLowerCase(Locale.ROOT)).replaceAll(" ");
        t = PUNCT.matcher(t).replaceAll(" ");
        return t.replaceAll("\\s+", " ").strip();
    }
}

public interface Tokenizer { List<String> encode(String s); }

public static final Tokenizer WHITESPACE = s -> Arrays.stream(Normalize.forMatch(s).split(" "))
        .filter(x -> !x.isEmpty()).toList();
public static final Tokenizer CHAR_NGRAM = s -> charNgrams(Normalize.forMatch(s), 1);
```

Never compare a candidate normalized against a gold that was not — and never mix
tokenizers between a BLEU implementation and its reference numbers.

## 3. Token F1 With Multiset Counts

```java
public static double[] prf(List<String> cand, List<String> ref) {
    Map<String, Integer> c = counts(cand), r = counts(ref);
    int overlap = 0;
    for (var e : c.entrySet()) overlap += Math.min(e.getValue(), r.getOrDefault(e.getKey(), 0));
    double p = cand.isEmpty() ? 0 : (double) overlap / cand.size();
    double rr = ref.isEmpty()  ? 0 : (double) overlap / ref.size();
    double f1 = (p + rr) == 0 ? 0 : 2 * p * rr / (p + rr);
    return new double[] { p, rr, f1 };
}

static Map<String, Integer> counts(List<String> toks) {
    Map<String, Integer> m = new HashMap<>();
    for (String t : toks) m.merge(t, 1, Integer::sum);
    return m;
}
```

`Math.min` of counts is the multiset intersection. Using `Set` instead would treat
"the the the cat" as one "the" — a silent bug that inflates scores on repetitive text.

## 4. BLEU

```java
public final class Bleu {

    public static double score(List<String> cand, List<String> ref, int maxN) {
        int c = cand.size(), r = ref.size();
        if (c == 0 || r == 0) return 0.0;
        double logSum = 0;
        for (int n = 1; n <= maxN; n++) {
            Map<String, Integer> cg = ngrams(cand, n), rg = ngrams(ref, n);
            if (cg.isEmpty()) return 0.0;                    // no candidate n-grams
            int overlap = 0;
            for (var e : cg.entrySet())
                overlap += Math.min(e.getValue(), rg.getOrDefault(e.getKey(), 0));
            double p = (double) overlap / totalCount(cg);
            if (p == 0) return 0.0;                         // any zero precision -> 0
            logSum += Math.log(p);
        }
        double bp = c > r ? 1.0 : Math.exp(1 - (double) r / c);
        return bp * Math.exp(logSum / maxN);
    }

    /** Corpus BLEU: pool counts across sentences BEFORE computing precision. */
    public static double corpus(List<List<String>> cands, List<List<String>> refs, int maxN) {
        double logSum = 0;
        for (int n = 1; n <= maxN; n++) {
            int ov = 0, tot = 0;
            for (int i = 0; i < cands.size(); i++) {
                Map<String, Integer> cg = ngrams(cands.get(i), n), rg = ngrams(refs.get(i), n);
                tot += totalCount(cg);
                for (var e : cg.entrySet())
                    ov += Math.min(e.getValue(), rg.getOrDefault(e.getKey(), 0));
            }
            logSum += Math.log((double) ov / tot);
        }
        // aggregate BP from total lengths
        int tc = cands.stream().mapToInt(List::size).sum();
        int tr = refs.stream().mapToInt(List::size).sum();
        double bp = tc > tr ? 1.0 : Math.exp(1 - (double) tr / tc);
        return bp * Math.exp(logSum / maxN);
    }

    static Map<String, Integer> ngrams(List<String> toks, int n) {
        Map<String, Integer> m = new LinkedHashMap<>();
        for (int i = 0; i + n <= toks.size(); i++)
            m.merge(String.join(" ", toks.subList(i, i + n)), 1, Integer::sum);
        return m;
    }

    static int totalCount(Map<String, Integer> m) {
        return m.values().stream().mapToInt(Integer::intValue).sum();
    }
}
```

Two subtleties: a single `p_n == 0` makes BLEU exactly 0 (the geometric mean), and
the zero-n-gram case must return 0 rather than `NaN` from `log(0)`. Corpus BLEU
pools counts *then* takes the log — pooling after averaging gives a different number.

## 5. ROUGE-L With DP

```java
public static double rougeL(List<String> cand, List<String> ref, double beta) {
    int[][] lcs = new int[cand.size() + 1][ref.size() + 1];
    for (int i = 1; i <= cand.size(); i++)
        for (int j = 1; j <= ref.size(); j++)
            lcs[i][j] = cand.get(i - 1).equals(ref.get(j - 1))
                     ? lcs[i - 1][j - 1] + 1
                     : Math.max(lcs[i - 1][j], lcs[i][j - 1]);
    double l = lcs[cand.size()][ref.size()];
    if (l == 0) return 0;
    double p = l / cand.size(), r = l / ref.size();
    double b2 = beta * beta;
    return ((1 + b2) * p * r) / (r + b2 * p);       // recall-weighted: beta > 1
}
```

Memory: `O(|cand| * |ref|)` ints. For long documents cap lengths or use a
Hirschberg variant — a 5,000 x 5,000 DP is 100 MB.

## 6. BERTScore with a Deterministic Embedder

```java
public static double f1(List<String> cand, List<String> ref, double[][] emb,
                        double alpha) {
    int n = cand.size(), m = ref.size();
    if (n == 0 || m == 0) return 0;
    double[] r = new double[n], p = new double[m];
    for (int i = 0; i < n; i++)
        for (int j = 0; j < m; j++) r[i] = Math.max(r[i], cos(emb[i], emb[j]));
    for (int j = 0; j < m; j++)
        for (int i = 0; i < n; i++) p[j] = Math.max(p[j], cos(emb[i], emb[j]));
    double P = Arrays.stream(r).average().orElse(0);
    double R = Arrays.stream(p).average().orElse(0);
    return alpha == 0 ? R : (P * R) / (alpha * P + (1 - alpha) * R);
}
```

The double loop is `O(n*m*d)` — precompute embedding norms once. A hashed char-trigram
embedder keeps this deterministic and dependency-free while preserving the
paraphrase tolerance that motivates BERTScore.

## 7. Position-Bias-Corrected Judge

```java
public final class PositionBiasCorrectedJudge {

    /** Runs both orders; returns 0, 1, or 0.5 when the judge is self-inconsistent. */
    public double compare(String query, String answerA, String answerB, long seed) {
        boolean abFirst = new Random(seed).nextBoolean();
        String first  = abFirst ? answerA : answerB;
        String second = abFirst ? answerB : answerA;
        int v1 = judge(query, first, second);          // 1 if "first" wins
        int v2 = judge(query, second, first);
        boolean aWins = abFirst ? (v1 == 1) : (v2 == 1);
        boolean bWins = abFirst ? (v2 == 1) : (v1 == 1);
        if (aWins == bWins) return 0.5;                // inconsistent across orders
        return aWins ? 1.0 : 0.0;
    }
}
```

Returning `0.5` for order-inconsistent judgments is the important part: silently
taking one order lets position bias leak into the win rate. Count how many items are
inconsistent — a high count means the judge is too weak for pairwise work.

## 8. Claim Splitting and Faithfulness

```java
public final class ClaimSplitter {

    private static final Pattern SPLIT = Pattern.compile("(?<=[.!?])\\s+|;\\s+|,\\s+and\\s+");

    public static List<String> split(String answer) {
        List<String> out = new ArrayList<>();
        for (String s : SPLIT.split(answer.strip())) {
            String t = Normalize.forMatch(s);
            if (!t.isEmpty() && t.split(" ").length >= 3) out.add(t);   // drop fragments
        }
        return out;
    }
}

public static Faithfulness score(List<String> claims, String evidence) {
    List<String> supported = new ArrayList<>(), unsupported = new ArrayList<>();
    for (String c : claims) {
        double[] tf = TokenF1.prf(tokens(c), tokens(evidence));
        if (containsNormalized(evidence, c) || tf[2] >= 0.85) supported.add(c);
        else unsupported.add(c);
    }
    double f = claims.isEmpty() ? 1.0 : (double) supported.size() / claims.size();
    return new Faithfulness(f, supported, unsupported);
}
```

The `0.85` token-F1 threshold catches paraphrases; the exact-substring path catches
short numeric claims where F1 is misleadingly high.

## 9. Abstention Policy

```java
public record Decision(boolean answer, double confidence, String reason) {}

public Decision decide(double evidenceSupport, double agreement) {
    if (evidenceSupport < MIN_SUPPORT)                       // nothing in the sources
        return new Decision(false, evidenceSupport, "NO_SUPPORTING_EVIDENCE");
    if (agreement < MIN_AGREEMENT)                           // samples disagree
        return new Decision(false, agreement, "LOW_SELF_CONSISTENCY");
    return new Decision(true, Math.min(evidenceSupport, agreement), "ANSWERED");
}

/** Sweep thresholds and report the coverage/accuracy frontier. */
static List<Point> sweep(List<Decision> truth) { /* grid search over both thresholds */ }
```

Typed reasons matter for operations: "no supporting evidence" is a retrieval problem,
"low self-consistency" is a model problem, and they route to different teams.

## 10. Fairness Metrics

```java
public static Map<String, Double> positiveRate(Map<String, List<Integer>> byGroup, int positive) {
    Map<String, Double> out = new LinkedHashMap<>();
    byGroup.forEach((g, ys) -> {
        long pos = ys.stream().filter(v -> v == positive).count();
        out.put(g, (double) pos / ys.size());
    });
    return out;
}

public static Map<String, Double> truePositiveRate(Map<String, List<int[]>> byGroup) {
    // int[] rows: { yTrue, yPred }
    Map<String, Double> out = new LinkedHashMap<>();
    byGroup.forEach((g, rows) -> {
        long tp = Arrays.stream(rows).filter(r -> r[0] == 1 && r[1] == 1).count();
        long pos = Arrays.stream(rows).filter(r -> r[0] == 1).count();
        out.put(g, pos == 0 ? Double.NaN : (double) tp / pos);
    });
    return out;
}

public static double biasRatio(Map<String, Double> rates) {
    double max = rates.values().stream().mapToDouble(Double::doubleValue).max().orElseThrow();
    double min = rates.values().stream().mapToDouble(Double::doubleValue).min().orElseThrow();
    return min == 0 ? Double.POSITIVE_INFINITY : max / min;
}
```

`Double.NaN` for a group with no positives is honest; defaulting to 0 fabricates a
finding. Always print per-group rates next to the ratio — a ratio alone hides which
group is which.

## 11. Paired Bootstrap

```java
public static double[] pairedBootstrap(double[] a, double[] b, int B, long seed) {
    int n = a.length;
    Random rnd = new Random(seed);
    double[] deltas = new double[B];
    for (int t = 0; t < B; t++) {
        double sum = 0;
        for (int i = 0; i < n; i++) {
            int k = rnd.nextInt(n);                 // resample indices, paired
            sum += a[k] - b[k];                     // SAME index for both systems
        }
        deltas[t] = sum / n;
    }
    Arrays.sort(deltas);
    return new double[] { percentile(deltas, 2.5), percentile(deltas, 97.5) };
}
```

Resampling the **same** index for both systems is what makes it paired; independent
resampling would destroy the covariance cancellation and inflate the interval.

## 12. Benchmark Runner and Regression Diff

```java
public record Item(String id, String query, String gold, String category,
                   boolean unanswerable, List<String> allowedSources) {}

public PerCategoryReport run(Benchmark bench, SystemUnderTest sut) {
    Map<String, List<Score>> byCat = new LinkedHashMap<>();
    for (Item it : bench.items()) {
        Output o = sut.run(it.query(), RunConfig.SEEDED);      // fixed config, logged
        Score s = switch (o.finishReason()) {
            case LENGTH -> Score.abstain("truncated");
            case REFUSED -> Score.abstain("refused");
            case STOP -> Score.graded(it, o.text(), sut.judge());
        };
        byCat.computeIfAbsent(it.category(), k -> new ArrayList<>()).add(s);
    }
    return PerCategoryReport.of(byCat, bench.hash(), RunConfig.describe());
}

public String diff(PerCategoryReport baseline, PerCategoryReport candidate) {
    return baseline.categories().stream()
        .map(c -> "%-24s %+.3f %s".formatted(c, candidate.mean(c) - baseline.mean(c),
                     Math.abs(candidate.mean(c) - baseline.mean(c)) > THRESHOLD ? "  <== REGRESSION" : ""))
        .collect(Collectors.joining("\n"));
}
```

The `<== REGRESSION` marker is the whole point — a 1-point average move can hide a
20-point collapse in one category.

## 13. Safety Metrics Pair

```java
public record SafetyReport(double refusalRateDisallowed, double overRefusalRateBenign,
                           double jailbreakSuccessRate, double consistency) {}

public SafetyReport evaluate(List<Pair<String, Boolean>> disallowed,
                             List<String> benignLookalikes,
                             List<String> jailbreakVariants, SafetyFn fn) {
    double refused  = disallowed.stream().filter(p -> fn.refuses(p.text())).count() / (double) disallowed.size();
    double over     = benignLookalikes.stream().filter(s -> fn.refuses(s)).count() / (double) benignLookalikes.size();
    double jail     = jailbreakVariants.stream().filter(s -> fn.complies(s)).count() / (double) jailbreakVariants.size();
    return new SafetyReport(refused, over, jail, refusalConsistency(disallowed, fn));
}
```

Four numbers, always printed together. Reporting only refusal rate is how a
production guardrail ends up refusing "how do I kill a process".

## Self-Check

1. Why must `p_n == 0` return 0 rather than let `log(0)` propagate?
2. In corpus BLEU, why pool counts before taking the log?
3. What does a high order-inconsistency count from the judge tell you?
4. Why resample the same index for both systems in the bootstrap?
5. Why return `NaN` for a group with no positive examples?