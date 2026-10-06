# Lab 05: Prompt Engineering at Scale — Code Deep Dive

## 1. Project Structure

```
lab05/
  src/com/aiengineering/lab05/
    registry/PromptVersion.java
    registry/PromptRegistry.java      promote/rollback/deprecate
    registry/RiskTier.java
    registry/PromptFamily.java        bundle versioning
    template/PromptRenderer.java      typed vars, assertNoUnfilled
    template/SectionOrder.java
    template/RenderCache.java
    lint/PromptLinter.java
    experiment/Bucketing.java         stable user assignment
    experiment/PromptExperiment.java   registry of running experiments
    experiment/PairedRunner.java      variants on identical items
    stats/Bootstrap.java, Significance.java
    rollout/CanaryController.java     ladder + gates + auto rollback
    rollout/ShadowRunner.java
    metrics/PromptMetrics.java        per-version quality/cost
    optimizer/PromptOptimizer.java
    Main.java
```

## 2. Prompt Version

```java
public record PromptVersion(
        String promptId, int version, String template,
        Map<String, TypeSpec> variables, String owner, RiskTier riskTier,
        String changelog, String hash, Instant created, String specHash) {

    public record TypeSpec(String type, int maxLength, Set<String> enumValues) {}

    public static PromptVersion create(String promptId, int version, String template,
                                       Map<String, TypeSpec> vars, String owner,
                                       RiskTier tier, String changelog) {
        String hash = sha256(template + "|" + canonical(vars));
        return new PromptVersion(promptId, version, template, vars, owner, tier,
                                 changelog, hash, now(), hash);
    }

    public String id() { return promptId + "@v" + version; }
}
```

Two hashes with different jobs: `hash` identifies the content for caching and diffing,
`specHash` identifies the full specification (template plus variable schema) for
reproducibility. A schema change with an unchanged template must be a different artifact.

## 3. Registry with Gated Promotion

```java
public final class PromptRegistry {

    private final Map<String, Deque<PromptVersion>> history = new LinkedHashMap<>();
    private final Map<String, PromptVersion> active = new LinkedHashMap<>();
    private final Map<String, RenderCache> caches = new HashMap<>();

    public void promote(String promptId, PromptVersion candidate, GateResult gate) {
        if (gate.missingMetrics())
            throw new IllegalStateException("gate missing metrics: " + gate.missing());
        if (!gate.passed())
            throw new IllegalStateException(candidate.id() + " failed the gate");
        if (candidate.owner() == null || candidate.owner().isBlank())
            throw new IllegalStateException("prompt needs an owner: " + candidate.id());
        if (candidate.riskTier() == RiskTier.HIGH && !gate.safetySuitePassed())
            throw new IllegalStateException("high-risk prompt requires the safety suite");

        PromptVersion previous = active.get(promptId);
        if (previous != null) history.get(promptId).push(previous);
        active.put(promptId, candidate);
        caches.get(promptId).invalidate();
        audit.promote(candidate, previous, gate);
    }

    public synchronized void rollback(String promptId) {
        Deque<PromptVersion> h = history.get(promptId);
        PromptVersion previous = h.pop();                 // known-good body
        active.put(promptId, previous);
        caches.get(promptId).invalidate();               // never serve a stale render
        audit.rollback(promptId, previous);
    }
}
```

`missingMetrics()` throwing before the pass/fail check is deliberate: broken telemetry
must not be able to promote anything. The high-risk safety-suite requirement encodes
risk tiers into the API rather than into a review checklist.

## 4. Typed Rendering

```java
public final class PromptRenderer {

    public static String render(PromptVersion v, Map<String, Object> values) {
        String out = substitute(v.template(), values);
        for (PromptVersion.TypeSpec spec : v.variables().values())
            if (!out.contains("{{" + specKey(spec) + "}}")) { /* placeholder was consumed */ }
        assertNoUnfilled(out);                            // literal {{x}} -> throw
        assertDeclaredOnly(v, values);
        assertTypes(v, values);
        return out;
    }

    static void assertNoUnfilled(String rendered) {
        if (UNFILLED.matcher(rendered).find())
            throw new IllegalStateException("unfilled placeholder reached the model: "
                    + UNFILLED.matcher(rendered).results().stream().map(r -> r.group()).toList());
    }

    static void assertTypes(PromptVersion v, Map<String, Object> values) {
        for (var e : v.variables().entrySet()) {
            Object val = values.get(e.getKey());
            if (val == null) throw new IllegalArgumentException("missing: " + e.getKey());
            switch (e.getValue().type()) {
                case "STRING" -> {
                    if (val.toString().length() > e.getValue().maxLength())
                        throw new IllegalArgumentException("too long: " + e.getKey());
                }
                case "ENUM" -> {
                    if (!e.getValue().enumValues().contains(val.toString()))
                        throw new IllegalArgumentException("not in enum: " + e.getKey());
                }
                case "INT" -> { if (!(val instanceof Integer i)) throw ...; }
            }
        }
    }
}
```

Checking length and enum membership at render time moves failures from "the model
ignored the field" to an exception at the call site, which is where they are debuggable.

## 5. Section Order and Prefix Stability

```java
public enum Section { SYSTEM, INSTRUCTIONS, CONTEXT, SCHEMA, QUESTION }

public static String stablePrefix(PromptVersion v) {
    int cut = v.template().indexOf("{{context}}");
    return cut < 0 ? v.template() : v.template().substring(0, cut);
}

public static void assertPrefixStable(List<String[]> renderPairs) {
    String ref = null;
    for (String[] pair : renderPairs) {
        String p = stablePrefix(PromptVersion.of(pair[0]));
        if (ref == null) ref = p;
        else if (!ref.equals(p))
            throw new IllegalStateException("stable prefix varies across renders; caching will miss");
    }
}
```

The test asserts the property the cache depends on. Without it, "we should be getting
cache hits" is an unverified assumption.

## 6. Stable Bucketing

```java
public final class Bucketing {

    public static long bucketOf(String userId, long salt, int buckets) {
        byte[] h = sha256("exp:" + salt + ":" + userId);
        return Math.floorMod(ByteBuffer.wrap(h).getLong(), (long) buckets);
    }

    /** Stable within an experiment, randomized across experiments. */
    public static String variantFor(String userId, PromptExperiment e) {
        long b = bucketOf(userId, e.salt(), 10_000);
        return b < e.treatmentShare() * 10_000 ? e.variant() : e.control();
    }
}
```

Salting by experiment keeps a user in one bucket within an experiment while preventing
the same users from being in the treatment group of every experiment.

## 7. Paired Runner

```java
public record ItemScore(String itemId, String category, double variantScore,
                        double controlScore, boolean formatValid) {}

public final class PairedRunner {

    public PairedResult run(String promptId, List<PromptVersion> variants,
                            EvalSuite suite, LlmClient llm) {
        List<ItemScore> scores = new ArrayList<>();
        for (Item item : suite.items()) {
            Map<String, Double> v = new LinkedHashMap<>();
            for (PromptVersion p : variants) v.put(p.id(), score(scorer, llm, p, item));
            double control = v.get(variants.get(0).id());
            for (PromptVersion p : variants)
                scores.add(new ItemScore(item.id(), item.category(), v.get(p.id()), control, true));
        }
        return analyze(scores);
    }

    static PairedResult analyze(List<ItemScore> scores) {
        // ONE bootstrap over paired deltas: same items, both systems
        double[] deltas = scores.stream().mapToDouble(ItemScore::variantScore).toArray();
        double[] controls = scores.stream().mapToDouble(ItemScore::controlScore).toArray();
        double[] diff = new double[deltas.length];
        for (int i = 0; i < diff.length; i++) diff[i] = deltas[i] - controls[i];
        double[] ci = Bootstrap.pairedCI(diff, 10_000, seed);
        Map<String, CategoryDelta> perCategory = groupByCategory(scores);
        return new PairedResult(mean(diff), ci[0], ci[1], perCategory, n(scores));
    }
}
```

The single bootstrap over `diff` (rather than two independent bootstraps) is the
implementation detail that makes the interval narrow. Getting it wrong makes every
experiment inconclusive.

## 8. Bootstrap

```java
public final class Bootstrap {

    /** Resample PAIRED deltas; resampling the two systems independently is a bug. */
    public static double[] pairedCI(double[] diff, int B, long seed) {
        int n = diff.length;
        Random rnd = new Random(seed);
        double[] means = new double[B];
        for (int b = 0; b < B; b++) {
            double sum = 0;
            for (int i = 0; i < n; i++) sum += diff[rnd.nextInt(n)];
            means[b] = sum / n;
        }
        Arrays.sort(means);
        return new double[] { percentile(means, 2.5), percentile(means, 97.5) };
    }

    public static double[] wilsonCI(long successes, long n, double z) {
        if (n == 0) return new double[] { 0, 1 };
        double p = successes / (double) n;
        double denom = 1 + z * z / n;
        double centre = (p + z * z / (2 * n)) / denom;
        double margin = z / denom * Math.sqrt(p * (1 - p) / n + z * z / (4 * n * n));
        return new double[] { Math.max(0, centre - margin), Math.min(1, centre + margin) };
    }
}
```

Wilson is included because Wald intervals produce impossible bounds at small `n` or at
rates near 0 or 1, which is exactly where prompt format-validity rates often live.

## 9. Canary Controller

```java
public final class CanaryController {

    public record Gate(String metric, boolean lowerIsBetter, double threshold) {}

    public Decision advance(PromptVersion candidate, Instant now) {
        if (freeze.isActive()) return Decision.hold("release freeze active");

        Step step = ladder.get(idx);
        var m = metrics.since(candidate, step.window());
        if (m.samples() < step.minSamples())
            return Decision.hold("need %d samples, have %d".formatted(step.minSamples(), m.samples()));

        for (Gate g : step.gates()) {
            Double v = m.value(g.metric());
            if (v == null) { rollback(candidate); return Decision.rollback("MISSING:" + g.metric()); }
            boolean breach = g.lowerIsBetter() ? v < g.threshold() : v > g.threshold();
            if (breach) { alerts.fire(g.metric(), v); rollback(candidate); return Decision.rollback(g.metric()); }
        }
        idx++;
        return idx >= ladder.size() ? Decision.promote() : Decision.advance(step.fraction());
    }
}
```

`v == null -> rollback` is the fail-closed decision from the theory, and it is the line
that stops a broken metrics pipeline from promoting a bad prompt.

## 10. Per-Version Metrics

```java
public record VersionMetrics(String promptId, int version, long samples,
                             double accuracy, double formatValidity, double refusalRate,
                             double tokensPerRequest, double costPerRequest,
                             double cacheHitRate, Map<String, Double> perCategory) {

    public double tokensPerCorrect()  { return accuracy == 0 ? Double.NaN : tokensPerRequest / accuracy; }
    public double costPerCorrect()    { return accuracy == 0 ? Double.NaN : costPerRequest / accuracy; }

    public VersionMetrics compare(VersionMetrics baseline) {
        return new VersionMetrics(promptId, version, samples, accuracy, formatValidity,
                refusalRate, tokensPerRequest, costPerRequest, cacheHitRate,
                diffPerCategory(baseline.perCategory()));
    }
}
```

`tokensPerCorrect` and `costPerCorrect` live on the metrics object rather than in a
reporting script, so every consumer of the metric gets the normalized version and nobody
reports raw accuracy as a standalone win.

## 11. Prompt Linter

```java
public final class PromptLinter {

    public record Finding(String rule, int line, String detail, Severity severity) {}

    public List<Finding> lint(PromptVersion v) {
        List<Finding> out = new ArrayList<>();
        if (UNFILLED.matcher(v.template()).find())
            out.add(new Finding("UNFILLED_PLACEHOLDER", 0, "literal {{var}}", Severity.ERROR));
        for (String banned : BANNED)                                   // "as an AI", etc.
            if (v.template().toLowerCase().contains(banned))
                out.add(new Finding("BANNED_PHRASE", 0, banned, Severity.WARN));
        if (v.variables().isEmpty() && v.template().contains("{{"))
            out.add(new Finding("UNDECLARED_VARIABLES", 0, "no schema declared", Severity.ERROR));
        if (v.owner() == null)
            out.add(new Finding("NO_OWNER", 0, "prompt has no owner", Severity.ERROR));
        if (v.riskTier() == RiskTier.HIGH && !v.template().contains("{{schema}}"))
            out.add(new Finding("HIGH_RISK_NO_SCHEMA", 0, "high-risk prompt without an output schema",
                    Severity.ERROR));
        return out;
    }
}
```

Running the linter in CI is what stops prompt sprawl from reappearing through the front
door after the registry was built.

## 12. Deprecation

```java
public final class Deprecation {

    public void notifyAt(double trafficShare, String phase) {
        consumers.forEach(c -> c.notify(deprecationNotice(c, phase)));
        notices.increment();
    }

    public void enforceDeadline(Instant deadline) {
        if (now().isBefore(deadline)) return;
        for (String consumer : unmigratedConsumers()) {
            registry.alias(consumer, previousStableVersion(consumer));   // auto-pin
            audit.autoPin(consumer);
        }
    }

    /** k for p(t) = p0 * e^(-kt) from p0 to target in T days. */
    public static double decayRate(double p0, double target, int days) {
        return Math.log(p0 / target) / days;
    }
}
```

Auto-pinning at the deadline is what keeps an un-migrated caller from breaking in
production. The decay-rate formula makes the notice schedule a calculation rather than a
guess.

## 13. Optimizer with Held-Out Validation

```java
public final class PromptOptimizer {

    public Optimized optimize(String promptId, ValidationSet val, TestSet test,
                              int maxIterations, int patience) {
        PromptVersion best = current(promptId);
        double bestScore = score(best, val);
        int stale = 0;

        for (int i = 0; i < maxIterations && stale < patience; i++) {
            PromptVersion candidate = mutate(best, new Random(seed + i));
            double s = score(candidate, val);
            history.add(new Iteration(i, candidate.specHash(), s));      // auditable
            if (s > bestScore) { best = candidate; bestScore = s; stale = 0; }
            else stale++;
        }

        // Confirm on the TEST set; a gain that does not survive is not a gain.
        double valDelta = bestScore - score(current(promptId), val);
        double testDelta = score(best, test) - score(current(promptId), test);
        return new Optimized(best, valDelta, testDelta);
    }
}
```

`testDelta` next to `valDelta` is the whole point. When they diverge sharply, the
optimizer fit the validator.

## Self-Check

1. Why maintain both a content `hash` and a `specHash`?
2. Why does `promote` check `missingMetrics()` before `passed()`?
3. What breaks if the bootstrap resamples the two systems independently?
4. Why is Wilson alongside Wald in `Bootstrap`?
5. What does a large gap between `testDelta` and `valDelta` indicate?