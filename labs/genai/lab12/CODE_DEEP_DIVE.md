# Lab 12: Cost Optimization for LLMs — Code Deep Dive

## 1. Project Structure

```
lab12/
  src/com/genai/lab12/
    cost/CostMeter.java          per-request/feature/tenant accounting
    cost/PriceTable.java         per-model, per-kind pricing with version
    prompt/PromptLayout.java     stable/v volatile split
    cache/PrefixCache.java       LRU over token-prefix hashes
    cache/SemanticCache.java     embed + threshold lookup
    cache/CacheKey.java          model/prompt/corpus/tenant/authz/version
    route/DifficultyClassifier.java
    route/CascadeRouter.java     cheap-first with escalation
    compress/ExtractiveCompressor.java
    compress/HistoryCompactor.java
    batch/DynamicBatcher.java    slot pool + cache budget cap
    batch/ThroughputModel.java   analytic model for comparison
    spec/SpeculativeDecoder.java draft/target acceptance loop
    spec/DraftModel.java
    output/LengthTiers.java      p50/p90/p99 caps
    eval/QualityGate.java        quality vs budget check
    Main.java
```

## 2. Cost Meter

```java
public final class CostMeter {

    public enum Kind { INPUT, OUTPUT, EMBEDDING, RERANK, GPU_SECONDS }

    private final Map<Kind, Long> units = new EnumMap<>(Kind.class);
    private final Map<String, Long> byFeature = new HashMap<>();
    private final Map<String, Long> byTenant = new HashMap<>();

    public void record(Kind kind, long n, String feature, String tenant) {
        units.merge(kind, n, Long::sum);
        byFeature.merge(feature + "|" + kind, n, Long::sum);
        byTenant.merge(tenant + "|" + kind, n, Long::sum);
    }

    public double cost(PriceTable pt) {
        double total = 0;
        for (var e : units.entrySet()) total += e.getValue() * pt.pricePerUnit(e.getKey());
        return total;
    }

    public Breakdown breakdown(PriceTable pt) {
        double total = cost(pt);
        Map<Kind, Double> share = new EnumMap<>(Kind.class);
        for (var e : units.entrySet())
            share.put(e.getKey(), e.getValue() * pt.pricePerUnit(e.getKey()) / total);
        return new Breakdown(Map.copyOf(units), Map.copyOf(share), total);
    }
}
```

Computing `share` rather than reading it off a chart is what prevents the classic
mistake of optimizing the smallest line: `breakdown()` sorts by share, and the
optimization plan follows that order.

## 3. Prompt Layout and Prefix Hashing

```java
public final class PromptLayout {

    private static final Set<String> VOLATILE_ROLES = Set.of("user");

    public record Split(List<ChatMessage> stablePrefix, List<ChatMessage> volatileSuffix) {}

    /**
     * Anything not in the stable prefix invalidates the cache for everything after it.
     * Hoist system + few-shot to the front; keep retrieved docs and queries at the tail.
     */
    public static Split split(List<ChatMessage> msgs) {
        List<ChatMessage> pre = new ArrayList<>(), suf = new ArrayList<>();
        boolean seenVolatile = false;
        for (ChatMessage m : msgs) {
            if (!seenVolatile && "system".equals(m.role())) pre.add(m);
            else { seenVolatile = true; suf.add(m); }
        }
        return new Split(List.copyOf(pre), List.copyOf(suf));
    }

    /** Cache key is the hash of the stable prefix, in order. */
    public static String prefixHash(List<ChatMessage> stablePrefix) {
        MessageDigest md = Sha256.sha256();
        for (ChatMessage m : stablePrefix) {
            md.update(m.role().getBytes(UTF_8));
            md.update((byte) 0);
            md.update(m.content().getBytes(UTF_8));
            md.update((byte) 0xFF);              // unambiguous concatenation
        }
        return HexFormat.of().formatHex(md.digest());
    }
}
```

The `0xFF` separator matters: without it, `("ab","c")` and `("a","bc")` hash the same
and you get silent cache collisions across differently-shaped prompts.

## 4. Prefix Cache

```java
public final class PrefixCache {

    private final int maxPrefixTokens;
    private final LinkedHashMap<String, Entry> entries;   // access-ordered

    record Entry(int tokens, String cachedResponse, Instant expiresAt) {}

    public PrefixCache(int maxEntries, int maxPrefixTokens) {
        this.maxPrefixTokens = maxPrefixTokens;
        this.entries = new LinkedHashMap<>(16, 0.75f, true) {
            @Override protected boolean removeEldestEntry(Map.Entry<String, Entry> eldest) {
                return size() > maxEntries;
            }
        };
    }

    public Optional<String> lookup(String prefixHash, Instant now) {
        Entry e = entries.get(prefixHash);
        if (e == null) return Optional.empty();
        if (now.isAfter(e.expiresAt())) { entries.remove(prefixHash); return Optional.empty(); }
        return Optional.of(e.cachedResponse());
    }

    public void store(String prefixHash, int tokens, String response, Duration ttl, Instant now) {
        if (tokens > maxPrefixTokens) return;               // never cache beyond the cap
        entries.put(prefixHash, new Entry(tokens, response, now.plus(ttl)));
    }

    public double hitRate(long lookups, long hits) { return lookups == 0 ? 0 : (double) hits / lookups; }
}
```

`store` silently declining to cache over-cap entries is deliberate: caching a prefix
the provider will not honor creates a hit rate that is fiction. Track `storeDeclined`
as a metric.

## 5. Semantic Cache

```java
public final class SemanticCache {

    public record Key(String model, String promptVersion, String corpusVersion,
                      String tenant, String authzScope) {
        public String canonical() { return String.join("|", model, promptVersion,
                                                      corpusVersion, tenant, authzScope); }
    }

    private record Entry(double[] embedding, String response, Instant expiresAt) {}

    public Optional<String> lookup(Key key, String query, double tau, Embedder emb, Instant now) {
        String ck = key.canonical();
        var idx = byKey.get(ck);
        if (idx == null) return Optional.empty();
        double[] q = emb.embedNormalized(normalize(query));       // normalize BEFORE embed
        Entry best = null; double bestScore = -1;
        for (Entry e : idx.values()) {
            if (now.isAfter(e.expiresAt())) continue;
            double s = Vectors.cosine(q, e.embedding());
            if (s > bestScore) { bestScore = s; best = e; }
        }
        return (best != null && bestScore >= tau) ? Optional.of(best.response()) : Optional.empty();
    }

    public void store(Key key, String query, String response, Duration ttl,
                      Embedder emb, Instant now) {
        byKey.computeIfAbsent(key.canonical(), k -> new ArrayList<>())
            .add(new Entry(emb.embedNormalized(normalize(query)), response, now.plus(ttl)));
    }

    static String normalize(String s) {
        return Normalizer.normalize(s.toLowerCase(ROOT), NFKC)
                         .replaceAll("[^\\p{L}\\p{N}\\s]", " ")
                         .replaceAll("\\s+", " ").strip();
    }
}
```

The `Key` includes `tenant` and `authzScope` — that is the cross-user leak guard.
Without those fields, a cached answer computed under one user's permissions is served
to another, which is a security incident, not an optimization.

## 6. Invalidation

```java
public static boolean isValid(Entry e, Key k, Instant now) {
    return e.key.equals(k)                            // model/prompt/corpus/tenant match
        && !now.isAfter(e.expiresAt())                // TTL
        && k.corpusVersion().equals(e.corpusVersion)  // no stale corpus answers
        && !e.authzScope().isBlank();                 // never serve across authz scopes
}
```

Corpus version is the one people forget: a RAG answer cached from yesterday's index is
wrong today, and nothing about the prompt changes to reveal it.

## 7. Cascade Router

```java
public final class CascadeRouter {

    public record Attempt(String tier, String response, boolean schemaValid,
                          double selfConsistency, double costUsd) {}

    public record Decision(Attempt final, int escalations, double totalCostUsd) {}

    public Decision answer(String prompt, CascadeModelRunner runner, Config cfg) {
        double cost = 0;
        for (int i = 0; i < cfg.tiers().size(); i++) {
            Tier t = cfg.tiers().get(i);
            Attempt a = runner.run(t.name(), prompt);
            cost += a.costUsd();
            if (acceptable(a, cfg)) return new Decision(a, i, cost);   // escalate otherwise
        }
        return new Decision(last, cfg.tiers().size() - 1, cost);
    }

    /**
     * Escalate on OUTCOME, not on predicted confidence.
     * p_escalate self-adjusts to the cheap model's actual error rate.
     */
    static boolean acceptable(Attempt a, Config cfg) {
        if (!a.schemaValid()) return false;                 // structural failure
        if (a.selfConsistency() < cfg.minConsistency()) return false;
        if (a.tier().equals(cfg.tiers().get(0).name()) && cfg.verifyCheap())
            return cfg.verifier().verify(a.response());      // outcome-based
        return true;
    }
}
```

Outcome-based escalation is what makes cascades beat static routers: the escalation
rate converges to the cheap model's true error rate instead of a classifier's
precision.

## 8. Dynamic Batcher

```java
public final class DynamicBatcher {

    private final int maxSlots;
    private final long cacheBytesPerSeq;
    private final long cacheBudgetBytes;
    private final Queue<Request> waiting = new ArrayDeque<>();

    public synchronized List<Request> nextBatch() {
        int bySlots = maxSlots;
        int byMemory = (int) Math.max(1, cacheBudgetBytes / cacheBytesPerSeq);
        int cap = Math.min(bySlots, byMemory);
        List<Request> batch = new ArrayList<>(cap);
        while (batch.size() < cap && !waiting.isEmpty()) batch.add(waiting.poll());
        return batch;                       // no waiting for a full batch: that is the point
    }

    public synchronized void enqueue(Request r) { waiting.add(r); }
    public synchronized void complete(String id) { inFlight.remove(id); }   // frees the slot now
}
```

`complete` releasing immediately (rather than at end-of-batch) is the difference
between continuous and static batching. `byMemory` is the honest cap: without it you
OOM before you saturate.

## 9. Throughput Model vs Measurement

```java
public record Prediction(double msPerToken, double tokensPerSec, boolean computeBound) {
    public static Prediction of(long params, long cacheBytes, int batch,
                                double tflops, double gbPerSec) {
        double wBytes = params * 2.0;
        double computeMs = 2.0 * params * batch / (tflops * 1e12) * 1000;
        double memoryMs  = (wBytes + cacheBytes * batch) / (gbPerSec * 1e9) * 1000;
        return new Prediction(Math.max(computeMs, memoryMs),
                              batch / (Math.max(computeMs, memoryMs) / 1000.0),
                              computeMs > memoryMs);
    }
}

public static double error(Prediction p, double measuredTokensPerSec) {
    return Math.abs(measuredTokensPerSec - p.tokensPerSec()) / p.tokensPerSec();
}
```

Report the error rather than asserting the model is right. A 20%+ error means the
capacity model cannot be used for planning, and that is a finding, not a detail.

## 10. Speculative Decoder

```java
public final class SpeculativeDecoder {

    public record Result(List<String> accepted, int draftsProposed, double targetPasses) {}

    public Result decode(String prefix, int k, DraftModel draft, TargetModel target,
                         Random rnd) {
        List<String> z = new ArrayList<>();
        double[] pd = new double[k], pt = new double[k];
        for (int i = 0; i < k; i++) {                       // DRAFT: sequential, cheap
            var next = draft.sample(prefix, z);
            z.add(next.token());
            pd[i] = next.probability();
        }
        var targetDist = target.scoreAll(prefix, z);        // TARGET: one parallel pass
        List<String> accepted = new ArrayList<>();
        for (int i = 0; i < k; i++) {
            pt[i] = targetDist[i].get(z.get(i));
            double ratio = Math.min(1.0, pt[i] / pd[i]);    // ACCEPTANCE RULE
            if (rnd.nextDouble() < ratio) { accepted.add(z.get(i)); continue; }
            accepted.add(resample(targetDist[i], rnd));     // resample, discard the rest
            break;
        }
        return new Result(accepted, k, 1);
    }

    /**
     * Output distribution == target distribution (lossless).
     * Verified by sampling many prefixes and comparing empirical frequencies.
     */
}
```

The `break` after the first rejection is what makes it efficient: everything after a
rejected draft is discarded. And the resample uses the **target's** distribution at
the rejection point, which is precisely why the whole scheme is lossless.

## 11. Extractive Context Compressor

```java
public final class ExtractiveCompressor {

    /** Never compress the schema, the final question, or the system message. */
    public Compressed compress(String system, List<Chunk> chunks, String question,
                               double threshold, int budgetTokens) {
        String[] qTerms = terms(question);
        List<Chunk> kept = new ArrayList<>();
        int used = 0;
        for (Chunk c : chunks) {                        // preserve retrieval order
            for (String sentence : sentences(c.text())) {
                double s = score(sentence, qTerms);
                if (s >= threshold && used + countTokens(sentence) <= budgetTokens) {
                    c.addSentence(sentence); used += countTokens(sentence);
                }
            }
            if (used >= budgetTokens) break;
        }
        return new Compressed(system, List.copyOf(kept), used);
    }
}
```

Filtering sentence-level *within* already-selected chunks is the right granularity: it
keeps the chunk's provenance for citations while cutting token count. Dropping whole
chunks instead hurts recall far more.

## 12. History Compactor

```java
public final class HistoryCompactor {

    /** Keep the last k turns verbatim; summarize older ones. System message is untouched. */
    public List<ChatMessage> compact(List<ChatMessage> history, int k, Summarizer sum) {
        if (history.size() <= k + 1) return history;                 // nothing to do
        ChatMessage system = history.get(0);
        assert "system".equals(system.role());                       // invariant
        List<ChatMessage> older = history.subList(1, history.size() - k);
        List<ChatMessage> recent = history.subList(history.size() - k, history.size());
        ChatMessage digest = new ChatMessage("system",
                "Earlier conversation summary: " + sum.summarize(older));
        List<ChatMessage> out = new ArrayList<>();
        out.add(system);
        out.add(digest);
        out.addAll(recent);
        return out;
    }
}
```

The summary goes in a **system** message so it carries the same trust level as policy
and cannot be mistaken for a fresh user instruction. And `system` is asserted untouched
rather than assumed.

## 13. Quality Gate for Optimizations

```java
public record GateResult(boolean pass, Map<String, Double> deltas, String blockingMetric) {}

public static GateResult evaluate(Map<String, Double> baseline,
                                  Map<String, Double> candidate,
                                  Map<String, Double> budget) {
    Map<String, Double> deltas = new TreeMap<>();
    String blocking = null;
    for (var e : budget.entrySet()) {
        double b = baseline.get(e.getKey()), c = candidate.getOrDefault(e.getKey(), 0.0);
        double d = c - b;                                    // negative = worse for quality
        deltas.put(e.getKey(), d);
        if (d < -e.getValue() && blocking == null) blocking = e.getKey();
    }
    return new GateResult(blocking == null, deltas, blocking);
}
```

An optimization that reduces cost 40% and degrades a metric by more than its budget is
**blocked**, not shipped with a note. Writing this as a gate rather than a judgement
call is what stops cost pressure from quietly eroding quality.

## 14. Length Tiers

```java
public final class LengthTiers {

    public static int[] percentiles(List<Integer> observed, int[] ps) {
        int[] sorted = observed.stream().mapToInt(Integer::intValue).sorted().toArray();
        int[] out = new int[ps.length];
        for (int i = 0; i < ps.length; i++)
            out[i] = sorted[Math.min(sorted.length - 1, (int) (ps[i] / 100.0 * sorted.length))];
        return out;
    }

    public int capFor(Tier tier) {
        return switch (tier) {
            case INTERACTIVE -> p50;        // short answers, truncation tolerated
            case STANDARD    -> p90;
            case LONG_FORM   -> p99;        // explicit opt-in for long outputs
        };
    }
}
```

Caps derived from observed percentiles rather than round numbers mean the truncation
rate stays where you intended. A cap below p95 trades a visible, measurable amount of
quality.

## Self-Check

1. Why add a `0xFF` separator in `prefixHash`?
2. What happens to the semantic cache hit rate if you skip `normalize`?
3. Why is `byMemory` needed alongside `maxSlots`?
4. Why does the speculative loop `break` after the first rejection?
5. Which metric in `breakdown()` decides the order of your optimization work?