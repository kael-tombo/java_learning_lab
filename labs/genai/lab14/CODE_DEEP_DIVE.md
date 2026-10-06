# Lab 14: LLMOps (LLM Operations) — Code Deep Dive

## 1. Project Structure

```
lab14/
  src/com/genai/lab14/
    release/ReleaseManifest.java     all component versions + hash
    release/ConfigRegistry.java      current/pinned versions, rollback
    release/ComponentDiff.java      two-manifest diff for triage
    trace/Trace.java, Span.java      typed spans
    trace/TraceWriter.java           JSONL with hashed payloads
    metrics/Percentiles.java         reservoir + t-digest sketch
    metrics/MetricRegistry.java      counters, histograms, gauges
    cost/CostAttribution.java        per request/feature/tenant/version
    deploy/CanaryController.java     ladder, gates, auto rollback
    deploy/Bucketing.java            stable user hashing
    deploy/ShadowRunner.java         mirror traffic, score both
    drift/Psi.java, DriftMonitor.java
    quality/QualityMonitor.java      100% cheap signals + judged sample
    quality/Sampling.java            stratified + targeted
    incident/SafeMode.java
    incident/SheddingPolicy.java
    incident/RetryStormDetector.java
    feedback/ReviewQueue.java        user signals -> prioritized queue
    ops/RunbookQuality.java          mechanical runbook scoring
    Main.java
```

## 2. Release Manifest

```java
public record ReleaseManifest(
        String modelId, String modelVersion,
        String promptTemplateId, String promptVersion,
        String indexVersion,
        String toolRegistryVersion,
        String policyVersion,
        GenerationConfig generation,
        String evaluatorVersion) {

    /** Canonical, order-independent serialization so field reordering cannot change the hash. */
    public String canonical() {
        var m = new TreeMap<String, String>();
        m.put("model", modelId + "@" + modelVersion);
        m.put("prompt", promptTemplateId + "@" + promptVersion);
        m.put("index", indexVersion);
        m.put("tools", toolRegistryVersion);
        m.put("policy", policyVersion);
        m.put("generation", generation.canonical());
        m.put("evaluator", evaluatorVersion);
        return m.entrySet().stream()
                .map(e -> e.getKey() + "=" + e.getValue())
                .collect(Collectors.joining("\n", "{", "}"));
    }

    public String hash() {
        return HexFormat.of().formatHex(Sha256.sha256(canonical()));
    }
}

public record GenerationConfig(double temperature, double topP, int maxTokens,
                               List<String> stop, String seed) {
    public String canonical() {
        return "t=%s,p=%s,max=%d,stop=%s,seed=%s"
                .formatted(temperature, topP, maxTokens, String.join("|", stop), seed);
    }
}
```

Every response carries `manifestHash`. That single field is what turns "was this the
old prompt?" from an archaeology project into a log filter.

## 3. Component Diff

```java
public record ComponentDiff(List<String> changed) {
    public static ComponentDiff between(ReleaseManifest a, ReleaseManifest b) {
        var left = canonicalMap(a);
        var right = canonicalMap(b);
        var changed = new ArrayList<String>();
        for (String key : left.keySet())
            if (!Objects.equals(left.get(key), right.get(key))) changed.add(key);
        return new ComponentDiff(List.copyOf(changed));
    }

    /** First question for a quality-drop alert. */
    public String firstHypothesis() {
        if (changed.isEmpty()) return "No config change: investigate data or upstream.";
        if (changed.contains("index")) return "Index changed: check corpus freshness and embedding model.";
        if (changed.contains("prompt")) return "Prompt changed: compare against the eval diff.";
        if (changed.contains("policy")) return "Policy changed: check refusal thresholds.";
        if (changed.contains("tools")) return "Tool registry changed: check schemas and permissions.";
        if (changed.contains("model")) return "Model changed: re-run the full eval before blaming traffic.";
        return "Generation config changed: check sampling params and max tokens.";
    }
}
```

Ordering the `if` statements by likelihood is deliberate: index and prompt changes
cause most quality incidents, so the runbook should point there first.

## 4. Trace With Hashed Payloads

```java
public record Span(String name, long startNanos, long durationNanos,
                   Map<String, String> attrs, Map<String, String> hashedPayloads) {

    public Span withPayload(String key, String raw) {
        var p = new HashMap<>(hashedPayloads);
        p.put(key, Sha256.hex(raw));                    // pointer, not content
        return new Span(name, startNanos, durationNanos, attrs, p);
    }
}

public final class TraceWriter implements AutoCloseable {
    private final BufferedWriter out;

    public void write(Trace t) throws IOException {
        out.write(Json.write(Map.of(
            "traceId", t.traceId(), "manifest", t.manifest().hash(),
            "user", t.user(), "tenant", t.tenant(),
            "spans", t.spans().stream().map(Span::name).toList(),
            "cost", t.cost().toMap(),
            "promptHash", t.promptHash(),
            "retrieval", t.retrieval().stream().map(h -> h.chunkId() + ":" + f(h.score())).toList()
        )));
        out.newLine();
    }
}
```

Hashing rendered prompts keeps logs small and PII-safe while preserving
reproducibility: the same prompt always yields the same hash, so you can correlate
incidents without storing the content.

## 5. Percentile Sketch

```java
public final class Percentiles {

    private final int k;
    private final Random rnd;
    private double[] reservoir;
    private long seen;

    /** Reservoir sampling for the body; exact sort for the tail via t-digest-style bucketing. */
    public void offer(double v) {
        seen++;
        if (reservoir.length < k) { reservoir[seen - 1] = v; return; }
        long j = nextLongBounded(rnd, seen);
        if (j < k) reservoir[(int) j] = v;
    }

    /** Returns sorted reservoir; the sample is unbiased so quantiles are consistent. */
    public double[] sortedSample() {
        double[] s = Arrays.copyOf(reservoir, (int) Math.min(seen, k));
        Arrays.sort(s);
        return s;
    }

    public double percentile(double p) {
        double[] s = sortedSample();
        if (s.length == 0) return Double.NaN;
        int idx = (int) Math.min(s.length - 1, Math.floor(p * s.length));
        return s[idx];
    }
}
```

A reservoir is what you can build in one file without pulling in a t-digest. Its
limitation is the honest one from MATH section 1: tail percentiles on heavy-tailed
latency need a bigger `k` or a proper sketch. Document which you are using next to
every reported p99.

## 6. Canary Controller

```java
public final class CanaryController {

    public record Gate(String metric, double maxValue, boolean lowerIsBetter, double budget) {}

    public record Step(double trafficFraction, long minSamples, List<Gate> gates) {}

    public Decision advance(ReleaseManifest current, ReleaseManifest candidate,
                            long now, long stepElapsedMs) {
        if (pinned()) return Decision.hold("release freeze active");

        Step step = ladder.get(idx);
        Map<String, Double> m = metricsFor(candidate, now - stepElapsedMs, now);
        long n = sampleCount(candidate, now - stepElapsedMs, now);

        if (n < step.minSamples()) return Decision.hold("need %d samples".formatted(step.minSamples()));
        for (Gate g : step.gates()) {
            if (breached(g, m.getOrDefault(g.metric(), Double.NaN))) {
                alerts.fire("canary_breach", g.metric(), m.get(g.metric()));
                rollback(candidate);                       // automatic, no human decision
                return Decision.rollback(g.metric());
            }
        }
        idx++;
        return idx >= ladder.size() ? Decision.promote() : Decision.advance(step.trafficFraction());
    }

    static boolean breached(Gate g, double v) {
        if (Double.isNaN(v)) return true;                  // missing metric = breach, fail closed
        return g.lowerIsBetter() ? v > g.maxValue() : v < g.maxValue();
    }
}
```

Two decisions in here matter more than the loop. A **missing** metric counts as a
breach, so a broken telemetry pipeline cannot silently promote a bad release. And
rollback is automatic, because under incident pressure humans make the wrong call.

## 7. Stable Bucketing

```java
public final class Bucketing {

    public static long bucketOf(String userId, long salt, int buckets) {
        byte[] h = Sha256.sha256(salt + ":" + userId);
        return Math.floorMod(ByteBuffer.wrap(h).getLong(), (long) buckets);
    }

    public static boolean inBucket(String userId, long salt, int buckets, double fraction) {
        long b = bucketOf(userId, salt, buckets);
        return (double) b / buckets < fraction;             // b/buckets in [0,1)
    }
}
```

Salting by experiment id keeps a user in the same bucket *within* an experiment
(stability) while randomizing across experiments (avoiding correlated bias).

## 8. PSI and Drift

```java
public final class Psi {

    /** Quantile bins, not equal-width: prompt length is heavily skewed. */
    public static double[] quantileBins(double[] reference, int bins) {
        double[] s = reference.clone();
        Arrays.sort(s);
        double[] edges = new double[bins + 1];
        for (int i = 0; i <= bins; i++) edges[i] = s[Math.min(s.length - 1, (int) (i * (double) s.length / bins))];
        return edges;
    }

    public static double of(double[] reference, double[] current, double[] edges) {
        int n = edges.length - 1;
        double[] p = hist(reference, edges), q = hist(current, edges);
        double psi = 0;
        for (int i = 0; i < n; i++) {
            if (p[i] == 0 && q[i] == 0) continue;
            double pi = Math.max(p[i], 1e-6), qi = Math.max(q[i], 1e-6);
            psi += (pi - qi) * Math.log(pi / qi);
        }
        return psi;
    }

    public static Verdict verdict(double psi) {
        if (psi < 0.10) return Verdict.STABLE;
        if (psi < 0.25) return Verdict.MODERATE;
        return Verdict.MAJOR;
    }
}
```

The `1e-6` floor on empty bins is essential: without it an empty bin produces
`log(0)` and the metric becomes useless exactly when a category appears or vanishes —
which is often the shift you most want to catch.

## 9. Quality Monitor: Two Tiers

```java
public final class QualityMonitor {

    /** Tier 1: cheap, no model call, run on 100% of responses. */
    public CheapSignals cheapSignals(String response, String schema, boolean refused) {
        return new CheapSignals(
                schema != null && SchemaValidator.valid(response, schema),
                refused,
                countTokens(response),
                PiiScrubber.detect(response),
                hasCitation(response));
    }

    /** Tier 2: judged sample. The RANDOM subset is the headline metric. */
    public JudgedSample judgeSample(List<Response> all, JudgingBudget budget) {
        var random  = Sampling.random(all, budget.randomBudget());
        var errors  = all.stream().filter(r -> !r.cheap().schemaValid()).toList();     // all of them
        var escal   = all.stream().filter(r -> r.outcome().escalated()).toList();      // all of them
        var signals = all.stream().filter(r -> disagrees(r)).toList();                // cheap says no, user says no
        return new JudgedSample(score(random), List.copyOf(errors), List.copyOf(escal),
                                List.copyOf(signals));
    }
}
```

The comment in `judgeSample` is the important part: the random subset produces the
reported quality number, and the targeted subsets feed the fix queue. Averaging them
together would produce a number that describes nothing.

## 10. Safe Mode

```java
public final class SafeMode {

    private volatile boolean active;
    private volatile ReleaseManifest pinnedManifest;     // rollback target

    public void engage(String reason) {
        pinnedManifest = registry.current();              // pin before changing anything
        active = true;
        registry.rollbackTo(pinnedManifest);              // config flip, not a rebuild
        audit.engage(reason, pinnedManifest.hash());
    }

    public Request mutate(Request r) {
        if (!active) return r;
        return r.withPolicy(STRICTEST)
                .withTools(ToolRegistry.EMPTY)
                .withRetrieval(false)
                .withOutputMode(BLOCK_ON_UNCERTAIN)
                .withManifest(pinnedManifest);
    }
}
```

Pinning before mutating is what makes the rollback a config flip. If you engage safe
mode and *then* try to reconstruct the previous version, you are doing a rebuild under
pressure, which is exactly when rebuilds fail.

## 11. Retry Storm Detector

```java
public final class RetryStormDetector {

    public record Signal(double attemptsPerRequest, double errorRate, double saturation,
                         boolean storm) {}

    public Signal evaluate(List<Trace> window) {
        double ratio = window.stream().mapToDouble(t -> t.attemptCount()).sum() / window.size();
        double errRate = window.stream().filter(t -> !t.ok()).count() / (double) window.size();
        double sat = saturationProbe();                     // queue depth / service capacity
        boolean storm = ratio > 1.20 && errRate > 0.05 && sat > 0.7;
        if (storm) alerts.fire("retry_storm", ratio, errRate, sat);
        return new Signal(ratio, errRate, sat, storm);
    }
}
```

Requiring all three conditions (ratio, error rate, saturation) prevents a benign
retention retry rate from tripping the alert. A single ratio threshold would fire
constantly.

## 12. Load Shedding

```java
public final class SheddingPolicy {

    public enum Tier { INTERACTIVE, STANDARD, LONG_CONTEXT, BATCH }

    /** Shed least valuable first. Interactive is protected until last. */
    public static Tier nextToShed(Tier t) {
        return switch (t) {
            case BATCH          -> null;             // nothing lower to shed
            case LONG_CONTEXT   -> BATCH;
            case STANDARD       -> LONG_CONTEXT;
            case INTERACTIVE    -> STANDARD;
        };
    }

    public ShedPlan plan(Map<Tier, Integer> loadByTier, double capacity) {
        int total = loadByTier.values().stream().mapToInt(Integer::intValue).sum();
        int excess = Math.max(0, total - (int) capacity);
        var kept = new EnumMap<Tier, Integer>(Tier.class);
        int shed = 0;
        for (Tier t : List.of(BATCH, LONG_CONTEXT, STANDARD, INTERACTIVE)) {
            int n = loadByTier.getOrDefault(t, 0);
            if (shed >= excess) { kept.put(t, n); continue; }
            int drop = Math.min(n, excess - shed);
            kept.put(t, n - drop);
            shed += drop;
        }
        return new ShedPlan(kept, excess, protectedFraction(kept, loadByTier));
    }
}
```

Shedding in a fixed tier order means the same traffic is shed on every overload, so
behavior is predictable and testable rather than emergent.

## 13. Feedback Review Queue

```java
public final class ReviewQueue {

    /** userValue x severity x recency; surface the expensive failures first. */
    public static int priority(Signal s, User u) {
        double value = u.revenue() + 10 * u.tierWeight();
        double severity = switch (s) {
            case ABANDONED -> 3.0; case ESCALATED -> 3.0; case CORRECTED -> 2.5;
            case REGENERATED -> 1.5; case COPIED -> 1.0; case THUMBS_DOWN -> 1.0;
            case THUMBS_UP -> 0.0;
        };
        return (int) Math.round(value * severity * Math.exp(-s.ageHours() / 72.0));
    }
}
```

Weighting by revenue is uncomfortable and correct: a mistake that costs an enterprise
customer more per incident deserves a human label before a hobbyist's. The exponential
decay keeps the queue current.

## 14. Runbook Quality Scoring

```java
public record RunbookScore(int score, List<String> gaps) {
    /** Mechanical scoring: does every alert have a first question, owner, tree, and tested action? */
    public static RunbookScore of(Map<String, RunbookEntry> book) {
        int s = 0; var gaps = new ArrayList<String>();
        for (var e : book.entrySet()) {
            if (e.getValue().firstQuestion().isBlank())     { gaps.add(e.getKey() + ": no first question"); }
            else s += 25;
            if (e.getValue().owner().isBlank())             { gaps.add(e.getKey() + ": no owner"); }
            else s += 25;
            if (e.getValue().decisionTree().depth() < 2)   { gaps.add(e.getKey() + ": shallow tree"); }
            else s += 25;
            if (!e.getValue().containment().tested())      { gaps.add(e.getKey() + ": untested action"); }
            else s += 25;
        }
        return new RunbookScore(s, gaps);
    }
}
```

Scoring runbooks mechanically is the only way to keep them from rotting. A runbook
whose containment action has never been executed is a hypothesis.

## Self-Check

1. Why does `canonical()` use a `TreeMap`?
2. Why does a missing gate metric count as a breach?
3. Why does PSI floor empty bins at `1e-6`?
4. Why pin the manifest before engaging safe mode?
5. Why does `judgeSample` keep the random subset separate from targeted subsets?