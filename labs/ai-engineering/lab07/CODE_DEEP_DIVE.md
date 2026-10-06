# Lab 07: AI Testing & Evaluation — Code Deep Dive

## 1. Project Structure

```
lab07/
  src/com/aiengineering/lab07/
    doubles/ScriptedLlmClient.java, HashingEmbedder.java, SeededRng.java, FakeClock.java
    suite/GoldenCase.java, GoldenSet.java
    suite/EvalConfig.java, EvalReport.java, CategoryReport.java
    runner/EvalRunner.java
    stats/Bootstrap.java, Wilson.java, SampleSize.java
    metrics/Recall.java, Rouge.java, Bleu.java, F1.java, Iou.java
    safety/SafetySuite.java
    quality/AbstentionMetrics.java, JudgeCalibration.java
    property/PropertySuite.java, Fuzzer.java
    mutate/MutationRunner.java
    drift/SampledEval.java
    Main.java
```

## 2. Deterministic Doubles

```java
public final class ScriptedLlmClient implements LlmClient {

    private final Deque<String> script;
    private final AtomicInteger calls = new AtomicInteger();

    public ScriptedLlmClient(String... responses) {
        this.script = new ArrayDeque<>(List.of(responses));
    }

    @Override
    public String complete(String prompt, Sampling sampling) {
        int i = calls.getAndIncrement();
        if (script.isEmpty())
            throw new IllegalStateException("script exhausted at call " + i
                    + " -- the loop ran longer than the plan");
        return script.poll();
    }
}
```

The throw is the assertion. An agent that needed a seventh turn when the script had six
means the loop is not converging, and that should surface as a test failure rather than a
surprise in production.

```java
public final class FakeClock {
    private long nanos;
    public long now() { return nanos; }
    public void advance(Duration d) { nanos += d.toNanos(); }
}
```

Timeouts become tests without sleeping, so the whole suite runs in milliseconds.

## 3. Golden Set

```java
public record GoldenCase(String id, String input, String gold, String category,
                         List<String> tags, boolean unanswerable,
                         List<String> allowedSources, int difficulty) {}

public final class GoldenSet {
    private final List<GoldenCase> cases;
    private final String hash;          // content hash: results are comparable only within a hash

    public static GoldenSet load(Path p) {
        List<GoldenCase> cases = readJsonl(p).sorted(comparing(GoldenCase::id)).toList();
        return new GoldenSet(cases, sha256(canonical(cases)));
    }

    /** Editing a gold answer is a reviewed change: it changes the hash. */
    public GoldenCase replaceGold(String id, String newGold) {
        throw new UnsupportedOperationException(
                "golden edits go through a versioned new set; the hash must change");
    }

    public List<GoldenCase> splitByUser(Map<String, String> userOfCase, double evalFraction) {
        List<GoldenCase> out = new ArrayList<>();
        for (GoldenCase c : cases) {
            String u = userOfCase.get(c.id());
            long b = Math.floorMod((long) sha256(u)[0], 100);
            if ((b / 100.0) < evalFraction) out.add(c);      // user-level, not query-level
        }
        return out;
    }
}
```

`replaceGold` throwing enforces the discipline in code rather than in a review comment,
and the user-level split prevents paraphrase leakage that silently inflates scores.

## 4. Evaluation Config and Report

```java
public record EvalConfig(String suiteId, String suiteHash, String manifestHash,
                         String judgeVersion, Sampling sampling, long seed, int replicates) {

    public String key() {                                   // everything that affects results
        return suiteId + "|" + suiteHash + "|" + manifestHash + "|"
             + judgeVersion + "|" + sampling.canonical() + "|" + seed;
    }
}

public record CategoryReport(Map<String, Double> perCategory,
                             Map<String, Double> deltas,
                             List<String> regressions, int samples,
                             Map<String, Double> sampleCounts) {

    public boolean hasRegressions() { return !regressions.isEmpty(); }

    /** An aggregate can hide a collapse; regressions are always per category. */
    public List<String> regressionsAbove(double tolerance) {
        return perCategory.entrySet().stream()
                .filter(e -> deltas.getOrDefault(e.getKey(), 0.0) < -tolerance)
                .map(Map.Entry::getKey).toList();
    }
}
```

`config.key()` bundles every input that changes results. Two reports with different keys
are not comparable, and the key makes that checkable rather than a matter of memory.

## 5. Runner

```java
public final class EvalRunner {

    public EvalReport run(GoldenSet set, EvalConfig cfg, SystemUnderTest sut, Metric metric) {
        var perCase = new ArrayList<CaseResult>();
        for (GoldenCase c : set.cases()) {
            for (int r = 0; r < cfg.replicates(); r++) {     // catch flakiness
                Output o = sut.run(c, cfg.sampling(), cfg.seed() + r);
                perCase.add(score(c, o, metric, cfg));
            }
        }
        return aggregate(set, perCase, cfg);
    }

    private CaseResult score(GoldenCase c, Output o, Metric m, EvalConfig cfg) {
        if (c.unanswerable()) {
            boolean abstained = o.text().contains(SENTINEL);
            return CaseResult.abstention(c, o, abstained);  // decline rate matters here
        }
        if (o.finishReason() == LENGTH) return CaseResult.truncated(c);
        if (o.refused())               return CaseResult.refusal(c);
        return CaseResult.graded(c, o, m.score(o.text(), c.gold()), o.formatValid(), o);
    }
}
```

Handling `unanswerable`, `truncated`, and `refused` as distinct outcomes rather than
scoring them as text is what makes the metrics mean what their names say.

## 6. Statistics

```java
public final class Bootstrap {

    public static double[] pairedCI(double[] delta, int B, long seed) {
        int n = delta.length;
        Random rnd = new Random(seed);
        double[] means = new double[B];
        for (int b = 0; b < B; b++) {
            double sum = 0;
            for (int i = 0; i < n; i++) sum += delta[rnd.nextInt(n)];
            means[b] = sum / n;
        }
        Arrays.sort(means);
        return new double[] { percentile(means, 2.5), percentile(means, 97.5) };
    }

    public static double[] wilson(long k, long n, double z) {
        if (n == 0) return new double[] { 0, 1 };
        double p = k / (double) n, z2 = z * z, denom = 1 + z2 / n;
        double centre = (p + z2 / (2 * n)) / denom;
        double margin = z / denom * Math.sqrt(p * (1 - p) / n + z2 / (4 * n * n));
        return new double[] { Math.max(0, centre - margin), Math.min(1, centre + margin) };
    }
}

public final class SampleSize {
    public static int forProportion(double targetHalfWidth) {
        return (int) Math.ceil(Math.pow(1.96 / targetHalfWidth, 2));
    }
    public static int forAbsoluteChange(double p1, double p2, double z) {
        double delta = Math.abs(p2 - p1);
        return (int) Math.ceil(z * z * (p1 * (1 - p1) + p2 * (1 - p2)) / (delta * delta));
    }
    public static boolean ladderFeasible(int nPerStep, int[] fractions, double rps) {
        double requests = 0;
        for (int f : fractions) requests += nPerStep / (f / 100.0);
        return requests / rps < 60 * 60 * 24 * 7;              // within a week
    }
}
```

`ladderFeasible` answers the question teams forget: whether a canary ladder can even
complete at their traffic volume before they design one.

## 7. Property Suite

```java
public final class PropertySuite {

    /** Invariants that must hold for ALL inputs. */
    public static List<PropertyFailure> check(Object input, Object output) {
        List<PropertyFailure> fails = new ArrayList<>();
        if (output == null)                    fails.add(new PropertyFailure("NULL_OUTPUT", ""));
        if (countItems(output) > MAX_ITEMS)    fails.add(new PropertyFailure("UNBOUNDED_GROWTH", ""));
        if (PII.matcher(text(output)).find())   fails.add(new PropertyFailure("PII_LEAK", snippet(output)));
        if (!schemaValid(output))              fails.add(new PropertyFailure("SCHEMA_VIOLATION", ""));
        return fails;
    }

    /** Shrink a failing input to a minimal reproducer. */
    public static Object shrink(Object input, Predicate<Object> fails) {
        Object cur = input;
        for (List<?> list : decompose(cur)) {
            for (Object piece : list) {
                if (piece.equals(cur)) continue;
                if (fails.test(piece)) { cur = piece; break; }
            }
            if (!cur.equals(input)) return shrink(cur, fails);   // recurse: keep reducing
        }
        return cur;
    }
}
```

Shrinking to a minimal reproducer is what turns "4 KB of text fails" into "`null` fails",
which is the difference between a fixable bug report and a mystery.

## 8. Mutation Runner

```java
public enum Mutant {
    LORA_INIT_RANDOM      (m -> { m.loraInitRandom(); }),
    MASK_AFTER_SOFTMAX    (m -> { m.applyMaskAfterSoftmax(); }),
    RRF_OFF_BY_ONE        (m -> { m.rffRankOffset(1); }),
    DROP_ADDITIONAL_PROPS  (m -> { m.schema().put("additionalProperties", true); }),
    SKIP_SENTINEL_CHECK   (m -> { m.enforceSentinel = false; }),
    TRUNCATE_SCHEMA_FIRST (m -> { m.truncationOrder = List.of("SCHEMA", "CONTEXT"); });

    public static MutationReport run(List<GoldenCase> suite, Runnable mutant) {
        int killed = 0;
        var survivors = new ArrayList<String>();
        for (Mutant m : values()) {
            SystemUnderTest sut = build(m);
            if (suiteIsFailing(suite, sut)) killed++; else survivors.add(m.name());
        }
        return new MutationReport(killed / (double) values().length, survivors);
    }
}
```

The `survivors` list is the actionable output: each survivor is a behaviour the suite
does not check, and each one gets a new test before the score is accepted.

## 9. Flakiness Audit

```java
public record FlakinessReport(Map<String, Double> byTest, List<String> unstable) {

    public static FlakinessReport audit(List<GoldenCase> suite, SystemUnderTest sut, int runs) {
        Map<String, Integer> pass = new HashMap<>(), fail = new HashMap<>();
        for (int r = 0; r < runs; r++)
            for (GoldenCase c : suite.cases()) {
                boolean ok = evaluate(c, sut, r);
                (ok ? pass : fail).merge(c.id(), 1, Integer::sum);
            }
        var byTest = new TreeMap<String, Double>();
        var unstable = new ArrayList<String>();
        byTest.forEach((id, p) -> {
            int total = p + fail.getOrDefault(id, 0);
            double distinctOutcomes = (p > 0 ? 1 : 0) + (p < total ? 1 : 0);
            double f = distinctOutcomes / 2.0;                     // 0 = stable, 1 = coin
            byTest.put(id, f);
            if (f > 0) unstable.add(id);
        });
        return new FlakinessReport(byTest, unstable);
    }
}
```

An unstable blocking test is worse than no test: the team learns to ignore red builds.
Unstable tests get removed from the blocking suite until their nondeterminism is fixed.

## 10. Safety Suite

```java
public record SafetyReport(double refusalDisallowed, double overRefusalBenign,
                           double jailbreakSuccess, double refusalConsistency,
                           WilsonInterval refusalCI) {

    public static SafetyReport evaluate(List<String> disallowed, List<String> benignLookalikes,
                                        List<String> jailbreaks, SafetyFn fn) {
        long refused = disallowed.stream().filter(fn::refuses).count();
        long over    = benignLookalikes.stream().filter(fn::refuses).count();
        long jail    = jailbreaks.stream().filter(s -> !fn.refuses(s)).count();
        double consistency = consistency(disallowed, fn, PARAPHRASES);
        return new SafetyReport(refused / (double) disallowed.size(),
                                over / (double) benignLookalikes.size(),
                                jail / (double) jailbreaks.size(),
                                consistency, Wilson.wilson(refused, disallowed.size(), 1.96));
    }
}
```

All four numbers in one record, with a confidence interval on the primary metric. There
is no way to construct this object that reports only refusal rate.

## 11. Abstention Metrics

```java
public record AbstentionReport(double declineRate, double falseDeclineRate,
                               double coverage, double accuracy, double expectedCorrect) {

    public static AbstentionReport of(List<Outcome> outcomes) {
        long unanswerable = outcomes.stream().filter(o -> !o.answerable()).count();
        long declinedUnans = outcomes.stream().filter(o -> !o.answerable() && o.declined()).count();
        long answerable = outcomes.size() - unanswerable;
        long declinedAns  = outcomes.stream().filter(o -> o.answerable() && o.declined()).count();
        long answered     = outcomes.stream().filter(o -> o.answerable() && !o.declined()).count();
        long correct      = outcomes.stream().filter(o -> o.answerable() && !o.declined() && o.correct()).count();

        double decline = unanswerable == 0 ? 0 : declinedUnans / (double) unanswerable;
        double falseDecline = answerable == 0 ? 0 : declinedAns / (double) answerable;
        double coverage = outcomes.isEmpty() ? 0 : answered / (double) answerable;
        double accuracy = answered == 0 ? 0 : correct / (double) answered;
        return new AbstentionReport(decline, falseDecline, coverage, accuracy, coverage * accuracy);
    }
}
```

`expectedCorrect = coverage * accuracy` is included because it is the number the
operating-point decision actually needs, and reporting coverage alone invites the wrong
choice.

## 12. Judge Calibration

```java
public record Calibration(double agreement, int n, List<String> disagreements,
                          boolean usable, String suspensionReason) {

    public static Calibration measure(List<Labelled> items, Judge judge, double minAgreement) {
        long agree = items.stream().filter(i -> judge.verdict(i) == i.gold()).count();
        double a = agree / (double) items.size();
        return new Calibration(a, items.size(),
                items.stream().filter(i -> judge.verdict(i) != i.gold()).toList(),
                a >= minAgreement,
                a < minAgreement ? "judge agreement " + f(a) + " below " + minAgreement
                                 + "; judge metrics suspended" : null);
    }

    /** Agreement attenuates observed effect sizes; it is a correction, not a gate. */
    public double attenuation() { return Math.max(0, 2 * agreement - 1); }
}
```

`attenuation()` makes the correction explicit: a judge at 0.78 agreement attenuates
measured deltas by a factor of 0.56, so a 3-point measured win is really a 5-point win
and a 1-point difference is noise.

## Self-Check

1. Why does `ScriptedLlmClient` throw on exhaustion?
2. What does `EvalConfig.key()` make checkable?
3. Why does `replaceGold` throw?
4. What does a mutation survivor tell you?
5. Why is `attenuation()` computed rather than just thresholded?