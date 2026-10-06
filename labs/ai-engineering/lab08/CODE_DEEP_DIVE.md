# Lab 08: AI Observability — Code Deep Dive

## 1. Project Structure

```
lab08/
  src/com/aiengineering/lab08/
    trace/Trace.java, Span.java, TraceWriter.java
    trace/ManifestDiff.java
    metric/MetricRegistry.java, LabelValidator.java
    metric/Percentiles.java, AnomalyDetector.java
    cost/CostMeter.java, PriceTable.java, Reconciliation.java
    sampling/StratifiedSampler.java
    drift/Psi.java, DriftMonitor.java
    alert/AlertRouter.java, Runbook.java
    alert/RetryStormDetector.java, CacheCollapseDetector.java
    guardrail/StageAttribution.java
    privacy/PiiScrubber.java, RetentionJob.java
    dashboard/Dashboard.java
    Main.java
```

## 2. Trace

```java
public record Span(String name, long startNanos, long durationNanos,
                   Map<String, String> labels, Map<String, String> hashedPayloads) {

    public Span withPayload(String key, String raw) {
        var p = new HashMap<>(hashedPayloads);
        p.put(key, Sha256.hex(raw));              // content on demand, never inline
        return new Span(name, startNanos, durationNanos, labels, p);
    }

    public double ms() { return durationNanos / 1e6; }
}

public record Trace(String traceId, String tenant, String feature,
                    ReleaseManifest manifest, List<Span> spans, CostBreakdown cost,
                    Outcome outcome) {

    public Span span(String name) {
        return spans.stream().filter(s -> s.name().equals(name)).findFirst()
                .orElseThrow(() -> new IllegalStateException("missing span: " + name));
    }
}
```

`span(name)` throwing rather than returning empty is deliberate: a missing stage span is
an instrumentation bug, and silent absence is how pipelines become undebuggable.

## 3. Trace Writer

```java
public final class TraceWriter implements AutoCloseable {

    private final BufferedWriter out;
    private final Scrubber scrubber;

    public void write(Trace t) throws IOException {
        String line = Json.write(Map.ofEntries(
            Map.entry("traceId", t.traceId()),
            Map.entry("tenant", t.tenant()),
            Map.entry("feature", t.feature()),
            Map.entry("manifest", t.manifest().hash()),        // attribution
            Map.entry("spans", t.spans().stream().map(s -> Map.of(
                    "n", s.name(), "ms", round(s.ms()),
                    "l", s.labels(), "h", s.hashedPayloads())).toList()),
            Map.entry("cost", t.cost().toMap()),
            Map.entry("outcome", Map.of("abstained", t.outcome().abstained(),
                                        "citationsValid", t.outcome().citationsValid()))));
        out.write(scrubber.scrub(line));                       // scrub BEFORE persist
        out.newLine();
    }
}
```

Scrubbing on the serialized line rather than on individual fields guarantees that any
new field added to the writer is also scrubbed — the alternative (per-field scrubbing) is
forgotten the first time someone adds a field.

## 4. Cost Meter

```java
public enum CostLine { INPUT_TOKENS, OUTPUT_TOKENS, EMBED_TOKENS, RERANK_TOKENS, GPU_MS }

public final class CostMeter {
    private final Map<CostLine, Long> totals = new EnumMap<>(CostLine.class);
    private final Map<String, Long> byTenant = new HashMap<>();
    private final Map<String, Long> byFeature = new HashMap<>();
    private final Map<String, Long> byRoute = new HashMap<>();
    private final Map<String, Long> byModelVersion = new HashMap<>();
    private final Map<String, Long> byCacheStatus = new HashMap<>();
    private final Map<String, Double> perRequestCost = new ConcurrentHashMap<>();

    public void record(Usage u, PriceTable pt) {
        double cost = pt.cost(u);
        totals.merge(CostLine.INPUT_TOKENS, u.inputTokens(), Long::sum);
        // ...
        byTenant.merge(u.tenant(), (long) (cost * 1000), Long::sum);   // micro-dollars
        perRequestCost.put(u.requestId(), cost);
    }

    public Breakdown breakdown() {                     // sorted by share, descending
        var shares = new TreeMap<Double, String>(Comparator.reverseOrder());
        for (var e : totals.entrySet()) shares.put(priceOf(e.getKey()) * e.getValue(), e.getKey().name());
        ...
    }
}
```

`breakdown()` sorting by share is what stops the "just shorten the output" reflex — the
largest line is reported first, every time.

## 5. Reconciliation

```java
public record Reconciliation(double meteredUsd, double invoicedUsd, double discrepancy,
                            List<String> untaggedCalls) {

    public boolean within(double tolerance) { return Math.abs(discrepancy) <= tolerance; }

    /** A discrepancy above tolerance means every cost-derived metric is suspect. */
    public String verdict() {
        return within(0.02) ? "OK"
             : discrepancy > 0 ? "METER UNDER-COUNTS: find untagged call paths"
             : "METER OVER-COUNTS: check double counting or stale prices";
    }
}
```

The two-way verdict matters: an over-count usually means double counting or stale
prices, an under-count means an untracked call path. Both have different fixes.

## 6. Label Validator

```java
public final class LabelValidator {

    private static final int MAX_CARDINALITY = 200;

    /** Unbounded labels destroy the metrics backend. Reject at registration time. */
    public static void validate(String metric, Map<String, String> labels) {
        for (var e : labels.entrySet()) {
            if (FORBIDDEN.matcher(e.getKey()).matches())
                throw new IllegalArgumentException(
                        "forbidden label '%s' on %s: high-cardinality detail belongs in traces"
                                .formatted(e.getKey(), metric));
            if (e.getValue().length() > 128)
                throw new IllegalArgumentException("label value too long on " + metric);
        }
        int projected = 1;
        for (int i = 0; i < labels.size(); i++) projected *= MAX_CARDINALITY;   // guard explosion
        if (projected > 1_000_000)
            throw new IllegalArgumentException("label cardinality budget exceeded on " + metric);
    }
}
```

Validating at registration means the mistake cannot be introduced by a well-meaning new
label later.

## 7. Percentiles

```java
public final class Percentiles {

    private final int k;
    private final Random rnd;
    private final double[] reservoir;
    private long seen;

    /** Reservoir sampling: unbiased, but weak on tail percentiles. Document k. */
    public void offer(double v) {
        seen++;
        if (seen <= k) { reservoir[(int) seen - 1] = v; return; }
        long j = (long) (rnd.nextDouble() * seen);
        if (j < k) reservoir[(int) j] = v;
    }

    public double percentile(double p) {
        double[] s = Arrays.stream(reservoir).filter(Double::isFinite).sorted().toArray();
        if (s.length == 0) return Double.NaN;
        return s[Math.min(s.length - 1, (int) Math.floor(p * s.length))];
    }

    public String sketchSpec() { return "reservoir(k=" + k + ")"; }   // publish with the number
}
```

`sketchSpec()` exists because a p99 without knowing the sketch and `k` is not
interpretable — tail percentiles on a reservoir are the least trustworthy number in the
dashboard, and saying so in the API is how readers stop over-trusting it.

## 8. Stratified Sampler

```java
public record Strata(List<Double> random, List<Double> errors,
                     List<Double> escalations, List<Double> disagreements,
                     Map<String, Integer> counts) {

    public double quality() { return mean(random); }          // ONLY the random stratum

    /** Averaging strata together would describe nothing. This method refuses. */
    public double blended() {
        throw new UnsupportedOperationException(
                "strata are deliberately biased; report them separately");
    }
}
```

`blended()` throwing encodes the rule in the type system rather than in a doc comment,
so the mistake cannot be made by a well-meaning dashboard.

## 9. PSI

```java
public final class Psi {

    public static double[] quantileBins(double[] reference, int bins) {
        double[] s = reference.clone();
        Arrays.sort(s);
        double[] edges = new double[bins + 1];
        for (int i = 0; i <= bins; i++)
            edges[i] = s[Math.min(s.length - 1, (int) ((long) i * s.length / bins))];
        return edges;
    }

    public static double of(double[] reference, double[] current, double[] edges) {
        double[] p = hist(reference, edges), q = hist(current, edges);
        double psi = 0;
        for (int i = 0; i < p.length; i++) {
            if (p[i] == 0 && q[i] == 0) continue;
            double pi = Math.max(p[i], 1e-6), qi = Math.max(q[i], 1e-6);
            psi += (pi - qi) * Math.log(pi / qi);              // floor prevents log(0)
        }
        return psi;
    }

    public static String verdict(double psi) {
        return psi < 0.10 ? "STABLE" : psi < 0.25 ? "MODERATE" : "MAJOR";
    }
}
```

The `1e-6` floor matters most exactly when a category appears or disappears, which is
often the shift most worth catching.

## 10. Manifest Diff for Triage

```java
public record ManifestDiff(List<String> changed, String firstHypothesis) {
    public static ManifestDiff between(ReleaseManifest a, ReleaseManifest b) {
        var left = canonical(a);
        var right = canonical(b);
        var changed = left.keySet().stream()
                .filter(k -> !Objects.equals(left.get(k), right.get(k)))
                .sorted().toList();
        return new ManifestDiff(changed, hypothesis(changed));
    }

    static String hypothesis(List<String> changed) {
        if (changed.isEmpty()) return "No config change: inspect data drift or upstream.";
        if (changed.contains("index"))    return "Index changed: freshness? embedding model? partial re-ingest?";
        if (changed.contains("prompt"))   return "Prompt changed: pull the eval diff from CI for that version.";
        if (changed.contains("policy"))   return "Policy changed: refusal thresholds moved.";
        if (changed.contains("tools"))    return "Tool registry changed: schemas or permissions tightened?";
        if (changed.contains("generation")) return "Sampling changed: temperature/top_p/max_tokens.";
        if (changed.contains("model"))    return "Model changed: re-run the full suite, not a spot check.";
        return "Unclassified change: " + changed;
    }
}
```

The `if` order encodes likelihood: index and prompt changes cause most quality
incidents, so the runbook points there first.

## 11. Retry Storm and Cache Collapse Detectors

```java
public final class RetryStormDetector {
    public record Signal(double attemptsPerRequest, double errorRate, double saturation, boolean storm) {}

    public Signal evaluate(List<Trace> window, DoubleSupplier saturationProbe) {
        double ratio = window.stream().mapToDouble(t -> t.span("attempt").count()).sum() / window.size();
        double err = window.stream().filter(t -> !t.outcome().success()).count() / (double) window.size();
        double sat = saturationProbe.getAsDouble();
        // all three conditions: a ratio alone fires on benign retry policies
        return new Signal(ratio, err, sat, ratio > 1.20 && err > 0.05 && sat > 0.70);
    }
}

public final class CacheCollapseDetector {
    public boolean trip(double current, double baseline, double dropFraction) {
        return current < baseline * (1 - dropFraction);   // sudden, not gradual erosion
    }
}
```

Requiring all three conditions in the retry detector is what prevents a constant 5%
retry policy from tripping it every window.

## 12. Guardrail Attribution

```java
public final class StageAttribution {
    public record Report(Map<Integer, Integer> firstCatchByLayer, int uncaught, double detectionRate) {
        public List<Integer> weakestLayers(int threshold) {
            return firstCatchByLayer.entrySet().stream()
                    .sorted(Map.Entry.comparingByValue())            // fewest catches = weakest
                    .filter(e -> e.getValue() < threshold)
                    .map(Map.Entry::getKey).toList();
        }
    }

    public static Report from(List<GuardrailEvent> events) {
        Map<Integer, Integer> byLayer = new TreeMap<>();
        int uncaught = 0;
        for (GuardrailEvent e : events) {
            int first = e.findings().stream().mapToInt(Finding::layer).min().orElse(0);
            if (first == 0) uncaught++; else byLayer.merge(first, 1, Integer::sum);
        }
        int total = events.size();
        return new Report(byLayer, uncaught, 1 - uncaught / (double) total);
    }
}
```

`uncaught` and `detectionRate` are the numbers that matter most: they are the measured
attack surface with no defence, and a declining detection rate is the clearest signal
that the red-team programme is falling behind new attack families.

## 13. Alert Router

```java
public record Alert(String type, String owner, String firstQuestion,
                     String runbookUrl, Severity severity, Decision defaultAction) {}

public static Alert for_(String type) {
    return switch (type) {
        case "QUALITY_DROP" -> new Alert(type, "ml-quality", "Did any versioned component change?",
                "RUNBOOK_QUALITY", PAGE, new Decision("DIFF_MANIFEST", "freeze releases"));
        case "TTFT_P95" -> new Alert(type, "serving", "Did traffic or context length change?",
                "RUNBOOK_LATENCY", PAGE, new Decision("CHECK_CACHE", "roll back if from a release"));
        case "COST_SPIKE" -> new Alert(type, "finops", "Which cost line?",
                "RUNBOOK_COST", PAGE, new Decision("BREAKDOWN", "check retry ratio"));
        case "REFUSAL_SPIKE" -> new Alert(type, "safety", "Was a policy or guardrail change deployed?",
                "RUNBOOK_REFUSAL", WARN, new Decision("DIFF_POLICY", "rollback"));
        case "DRIFT" -> new Alert(type, "data", "Which input dimension shifted?",
                "RUNBOOK_DRIFT", TICKET, new Decision("SAMPLE_REVIEW", "investigate; do NOT roll back"));
        default -> throw new IllegalArgumentException("no runbook for alert: " + type);
    };
}
```

The `default -> throw` is the enforcement: an alert type with no runbook cannot be
registered, so the team cannot create an alert nobody will act on. Note also that DRIFT's
default action is explicitly *not* rollback.

## 14. Retention Job

```java
public final class RetentionJob {
    private final Map<String, Duration> policy = Map.of(
            "trace_success", Duration.ofDays(7),
            "trace_error",   Duration.ofDays(90),
            "log",           Duration.ofDays(30),
            "audit",         Duration.ofDays(2555),            // 7 years, tamper-evident
            "prompt_content", Duration.ofDays(30));             // content rarely, hashes always

    public RetentionReport run(Store store, Instant now) {
        RetentionReport r = new RetentionReport();
        policy.forEach((kind, ttl) -> {
            Instant cutoff = now.minus(ttl);
            r.record(kind, store.deleteBefore(kind, cutoff));
        });
        metrics.gauge("retention_deleted_total", r.total());
        return r;
    }

    /** Tenant deletion on request, enforced and reported. */
    public int purgeTenant(String tenantId, Instant now) {
        int n = store.deleteAllForTenant(tenantId);
        metrics.counter("tenant_purge", tenantId, n);
        return n;
    }
}
```

Separate TTLs for error traces and successful traces are what make 90-day debugging
possible at a sane storage cost.

## Self-Check

1. Why scrub the serialized line rather than individual fields?
2. Why does `LabelValidator` reject forbidden label names?
3. Why does `blended()` throw?
4. Why does `ManifestDiff` check `index` before `prompt`?
5. Why does the DRIFT alert's default action avoid rollback?