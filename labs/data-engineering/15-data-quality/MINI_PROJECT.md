# Data Quality (Advanced) — MINI PROJECT

## Project: Quality Contracts + Anomaly Detection + Trust Score

Move beyond per-run assertions: a contract engine, statistical anomaly
detection over seasonal series, cross-system reconciliation, and a published
trust score with error budgets.

### Scope
- `DataContract`: schema, semantics, invariants, SLAs, owners, version.
- Anomaly detection: robust z-score (MAD) + STL-lite seasonal decomposition
  + EWMA, applied to volume and key business metrics.
- Reconciliation: compare two independent sources with a tolerance band.
- Trust score: composite of freshness, volume, distribution, and contract
  conformance, with an error budget.
- Alert router: page / ticket / silent by burn rate.

### Architecture

```
sources -> [contract validation] -> table -> [metrics collectors]
              |                       |            |
        enforce/reject         trust score     anomaly detection
              |                       |            |
              +-----------> [dashboard + alerts + error budget]
```

### Implementation — contracts

```java
public record DataContract(
        String name, int version, Owner owner,
        SchemaSpec schema,
        List<SemanticRule> semantics,
        List<Sla> slas,
        List<String> consumers,
        Instant effectiveFrom
) {
    public record Sla(SlaKind kind, double targetPct, Duration window, Severity severity) {}
    public enum SlaKind { FRESHNESS, COMPLETENESS, VALIDITY, VOLUME_WITHIN_BAND, CONSISTENCY }
    public record Owner(String team, String oncall, String slack) {}
}

public final class ContractEngine {
    public ContractReport validate(DataContract c, Batch b) {
        List<Violation> v = new ArrayList<>();
        for (SemanticRule r : c.semantics()) {
            Object observed = r.evaluate(b);
            if (!r.satisfiedBy(observed)) {
                v.add(new Violation(r.id(), r.description(), observed, r.expected(),
                        c.slas().stream().filter(s -> s.kind() == r.slaKind())
                               .findFirst().map(s -> s.severity()).orElse(Severity.WARN)));
            }
        }
        return new ContractReport(c.name(), c.version(), v,
                v.stream().noneMatch(x -> x.severity() == Severity.BLOCK));
    }
}
```

### Anomaly detection that survives seasonality

```java
/**
 * Why not a simple z-score on a raw series: Black Friday, month-end, and
 * billing cycles make the "normal" range enormous, and a plain threshold
 * either fires every December or never fires.
 *
 * Approach:
 *   1. seasonal-naive baseline: value[t] is compared to value[t-7] (weekly)
 *      for a daily series, which captures the weekly shape for free
 *   2. residual = actual - baseline
 *   3. robust scale via MAD (median absolute deviation), not stddev, so one
 *      historical spike does not inflate the threshold forever
 *   4. EWMA over the residual for gradual drift
 */
public record Anomaly(Instant at, double value, double baseline, double robustZ,
                      double residual, Direction direction, Severity severity) {}

public final class AnomalyDetector {
    private static final int WINDOW = 56;          // 8 weeks of daily history
    private static final double ON_CALL_Z = 5.0;    // page
    private static final double TICKET_Z = 3.5;    // ticket

    public List<Anomaly> detect(List<TimePoint> series, int seasonality) {
        List<Anomaly> out = new ArrayList<>();
        if (series.size() < WINDOW + seasonality) return out;

        // 1. seasonal-naive residuals
        List<Double> residuals = new ArrayList<>();
        for (int i = seasonality; i < series.size(); i++) {
            residuals.add(series.get(i).value() - series.get(i - seasonality).value());
        }

        // 2. robust scale on the residual history
        double mad = medianAbsoluteDeviation(residuals.subList(0, residuals.size() - 1));
        double scale = 1.4826 * mad;                // consistent estimator for normal sigma
        if (scale == 0) scale = meanAbsolute(residuals) * 1.2533;

        // 3. EWMA on the residual for drift
        double ewma = 0, lambda = 0.2;
        for (int i = seasonality; i < series.size(); i++) {
            double residual = series.get(i).value() - series.get(i - seasonality).value();
            ewma = lambda * residual + (1 - lambda) * ewma;
            double z = scale == 0 ? 0 : (residual - ewma) / scale;
            if (Math.abs(z) >= TICKET_Z) {
                out.add(new Anomaly(series.get(i).at(), series.get(i).value(),
                        series.get(i - seasonality).value(), z, residual,
                        z > 0 ? Direction.HIGH : Direction.LOW,
                        Math.abs(z) >= ON_CALL_Z ? Severity.BLOCK : Severity.WARN));
            }
        }
        return out;
    }

    static double medianAbsoluteDeviation(List<Double> xs) {
        if (xs.isEmpty()) return 0;
        double med = median(xs);
        List<Double> dev = xs.stream().map(x -> Math.abs(x - med)).sorted().toList();
        return median(dev);
    }
}
```

The MAD choice matters more than it looks. One incident that spiked volume
40% three months ago permanently widens a stddev-based threshold; the median
absolute deviation barely moves.

```java
public final class Reconciliation {
    /**
     * Reconcile two independent sources. The tolerance must be an explicit
     * business number, not "close enough" - otherwise the check is decoration.
     */
    public record Result(String metric, double sourceA, double sourceB,
                         double absDiff, double relDiff, boolean withinTolerance,
                         String explanation) {}

    public Result compare(String metric, double a, double b, double tolerance,
                          String sourceAName, String sourceBName) {
        double abs = Math.abs(a - b);
        double rel = a == 0 ? (b == 0 ? 0 : Double.POSITIVE_INFINITY) : abs / Math.abs(a);
        boolean ok = rel <= tolerance;
        return new Result(metric, a, b, abs, rel, ok,
                ok ? "" : sourceAName + "=" + a + " vs " + sourceBName + "=" + b
                        + "; rel=" + fmt(rel) + " exceeds tolerance " + tolerance);
    }
}
```

### Trust score with an error budget

```java
public record DimensionScore(Dimension dimension, double score, double target,
                             String detail) {}

public enum Dimension { FRESHNESS, COMPLETENeness, VALIDITY, CONSISTENCY, VOLUME }

public record TrustScore(String table, double composite, DimensionScore[] dimensions,
                         double errorBudgetRemaining, Instant computedAt) {
    public boolean publishable() { return composite >= 0.98; }
}
```

```java
public final class TrustScoreCalculator {
    /**
     * A composite score is a communication device, not an objective truth.
     * Weighting is a judgement call and must be published alongside the score,
     * otherwise a 0.97 will be read as "97% correct", which it is not.
     */
    private static final Map<Dimension, Double> WEIGHTS = Map.of(
            Dimension.FRESHNESS, 0.30,     // stale data is worse than imperfect data
            Dimension.VALIDITY, 0.25,
            Dimension.COMPLETENess, 0.20,
            Dimension.CONSISTENCY, 0.15,
            Dimension.VOLUME, 0.10);

    public TrustScore compute(String table, List<DimensionScore> dims) {
        double weighted = dims.stream()
                .mapToDouble(d -> d.score() * WEIGHTS.getOrDefault(d.dimension(), 0.0))
                .sum();
        double budget = errorBudget(table).remainingFraction();
        return new TrustScore(table, weighted, dims.toArray(DimensionScore[]::new),
                budget, Instant.now());
    }
}
```

### Alert routing by burn rate

```java
public enum Action { PAGE, TICKET, SILENT }

public final class AlertRouter {
    /** Burn rate = how fast the error budget is being consumed vs the SLO window. */
    public Action route(double burnRate, boolean isKnownIssue) {
        if (isKnownIssue) return Action.SILENT;     // a suppressed alert, logged not deleted
        if (burnRate > 14) return Action.PAGE;        // 14.4x = 1% budget in 1 hour
        if (burnRate > 6) return Action.TICKET;       // 6x = 1% budget in ~2.5 hours
        return Action.SILENT;
    }
}
```

### Test It

```java
@Test void seasonalSpikeIsNotAnAnomaly() {
    List<TimePoint> s = synthetic(120, base = 1000, weeklyShape = true);
    assertTrue(detector.detect(s, 7).isEmpty());        // normal Saturday spike: no alert
}

@Test void gradualDriftIsDetected() {
    List<TimePoint> s = synthetic(120, base = 1000, weeklyShape = true);
    s.subList(100, 120).forEach(t -> t.setValue(t.value() * 1.08));   // 8% drift
    List<Anomaly> a = detector.detect(s, 7);
    assertFalse(a.isEmpty());
    assertTrue(a.stream().allMatch(x -> x.direction() == Direction.HIGH));
}

@Test void errorBudgetStopsThePaging() {
    router.route(20, false);      // PAGE
    router.route(3, false);       // SILENT
    router.route(20, true);       // SILENT (known issue, still logged)
}
```

### Stretch
- Add a two-way reconciliation between a warehouse mart and a source system.
- Add a "who is affected" query: given a contract violation, list the consumers.
- Add a review workflow: a low trust score opens a ticket with the owner.

## Deliverables
- [ ] Contract engine with schema, semantics, SLAs, and BLOCK/WARN severities
- [ ] Anomaly detector with seasonal-naive baseline + MAD + EWMA
- [ ] Tests for seasonal spikes, gradual drift, and sudden drops
- [ ] Reconciliation harness with explicit business tolerances
- [ ] Trust score with published weights and an error budget
- [ ] Alert router with page/ticket/silent and a known-issue suppression log
- [ ] Affected-consumers lookup for a violation
