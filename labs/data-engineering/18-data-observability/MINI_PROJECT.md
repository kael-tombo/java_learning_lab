# Data Observability — MINI PROJECT

## Project: Three-Pillar Monitor with Anomaly Detection and Drill-Down

Instrument a pipeline with freshness, volume, and distribution signals; detect
anomalies statistically; group them by dimension; and route actionable alerts.

### Scope
- `Signal` emission: freshness, volume (per partition), distribution (per column).
- Detector: robust z-score on a seasonal-naive residual, with a burn-rate router.
- Grouper: top contributing dimension values for a volume drop.
- Lineage: a table dependency graph used to name a likely upstream cause.
- Alerting: page / ticket / silence, with a known-issue suppression log.
- Report: MTTD, MTTR, false-positive rate, precision, per-monitor stats.

### Architecture

```
pipeline
  |-- emit(freshness, volume, distribution)  --> metrics store (per partition)
                                                    |
                                              [detector]
                                                    |
                                        (anomaly? severity?)
                                                   / \
                                        [grouper]  [lineage suggester]
                                              \      /
                                            [alert router] --> runbook link
```

### Implementation — signals

```java
public sealed interface Signal permits Freshness, Volume, Distribution {}

public record Freshness(String dataset, String partition, Instant expectedBy,
                        Instant lastSuccess) implements Signal {
    public Duration lateness() { return Duration.between(expectedBy, lastSuccess); }
    public boolean overdue(Duration slo) { return lastSuccess.isBefore(expectedBy.plus(slo)); }
}

public record Volume(String dataset, String partition, long rowCount,
                     long bytes, double distinctKeyRatio) implements Signal {}

public record Distribution(String dataset, String partition, String column,
                           double mean, double stddev, long nulls, long distinct,
                           Map<String, Long> topValues) implements Signal {}

/**
 * Column-level distribution summaries are cheap if the engine can compute them
 * in the same pass as the load. Emitting the top-k frequencies catches a class
 * of failure that means and stddev cannot: a new value appearing in a
 * categorical column.
 */
public record ColumnFingerprint(String dataset, String column, long rowCount,
                                long nulls, double min, double max, double mean,
                                double stddev, Map<String, Long> topValues,
                                int cardinalityBuckets) implements Signal {}
```

### Detector

```java
public record Anomaly(String dataset, String partition, String signalType,
                      double observed, double baseline, double robustZ,
                      Instant at, Severity severity, String explanation) {}

public enum Severity { SILENT, TICKET, PAGE }

public final class AnomalyDetector {
    private final int lookback;
    private final double pageZ, ticketZ;
    private final double minBaseline;

    public AnomalyDetector(int lookbackDays, double pageZ, double ticketZ) {
        this.lookback = lookbackDays;
        this.pageZ = pageZ;
        this.ticketZ = ticketZ;
        this.minBaseline = 5.0;         // below this, a zero is noise, not an outage
    }

    /**
     * Freshness: absolute and unambiguous. A daily table that has not landed by
     * expectedBy + 2h is late, whatever its history.
     */
    public Anomaly detectFreshness(Freshness f, Duration slo) {
        if (!f.overdue(slo)) return null;
        Duration late = Duration.between(f.expectedBy().plus(slo), f.lastSuccess());
        return new Anomaly(f.dataset(), f.partition(), "freshness",
                late.toMinutes(), 0, Double.MAX_VALUE, Instant.now(),
                late.toHours() > 6 ? Severity.PAGE : Severity.TICKET,
                "no successful load for " + late.toHours() + "h (SLO " + slo + ")");
    }

    /**
     * Volume: relative to a seasonal-naive baseline, with a robust scale.
     * A 30% drop on a Sunday is normal; the same drop on a Tuesday is not.
     */
    public Anomaly detectVolume(Volume v, List<Volume> history, int seasonality) {
        List<Volume> past = history.subList(Math.max(0, history.size() - lookback),
                                            history.size());
        if (past.size() < seasonality + 7) return null;

        List<Double> residuals = new ArrayList<>();
        for (int i = seasonality; i < past.size(); i++) {
            residuals.add(past.get(i).rowCount() - past.get(i - seasonality).rowCount());
        }
        double baseline = past.get(past.size() - seasonality).rowCount();
        if (baseline < minBaseline) return null;                    // too small to judge

        double mad = medianAbsoluteDeviation(residuals);
        double scale = mad == 0 ? 1.0 : 1.4826 * mad;
        double observed = v.rowCount();
        double z = (observed - baseline) / scale;

        if (Math.abs(z) < ticketZ) return null;
        return new Anomaly(v.dataset(), v.partition(), "volume", observed, baseline, z,
                Instant.now(), Math.abs(z) >= pageZ ? Severity.PAGE : Severity.TICKET,
                String.format("rows %,.0f vs baseline %,.0f (%.1f%% change, z=%.1f)",
                        observed, baseline, 100 * (observed - baseline) / baseline, z));
    }

    /**
     * Distribution: two checks, because mean/stddev miss shape changes.
     *   1. mean shift relative to the coefficient of variation
     *   2. new category appearance: a value in topValues not seen in the baseline
     */
    public Anomaly detectDistribution(ColumnFingerprint now, ColumnFingerprint baseline) {
        if (baseline.rowCount() < 100) return null;

        double cv = baseline.stddev() / Math.max(baseline.mean(), 1e-9);
        double meanShift = baseline.mean() == 0 ? 0
                : Math.abs(now.mean() - baseline.mean()) / Math.max(baseline.mean(), 1e-9);
        if (cv > 0.05 && meanShift > Math.max(0.25, 3 * cv)) {
            return new Anomaly(now.dataset(), now.partition(), "distribution:" + now.column(),
                    now.mean(), baseline.mean(), meanShift / Math.max(cv, 1e-9), Instant.now(),
                    Severity.TICKET, String.format("mean moved %.1f%% (baseline CV %.1f%%): "
                            + "%.4f -> %.4f", 100 * meanShift, 100 * cv, baseline.mean(), now.mean()));
        }

        Set<String> baselineTop = baseline.topValues().keySet();
        Set<String> newCategories = new LinkedHashSet<>(now.topValues().keySet());
        newCategories.removeAll(baselineTop);
        if (!newCategories.isEmpty() && now.rowCount() > baseline.rowCount() / 10) {
            return new Anomaly(now.dataset(), now.partition(), "distribution:" + now.column(),
                    newCategories.size(), baselineTop.size(), 0, Instant.now(), Severity.PAGE,
                    "new categories appeared: " + truncate(newCategories, 5));
        }
        return null;
    }
}
```

### Grouping: which subset is responsible

```java
public record Group(String dimension, String value, long rows,
                    double shareOfExpected, double contribution) {}

/**
 * "Volume is 40% down" is not actionable. "Volume is 40% down, and 96% of the
 * missing rows are in region=APAC" is. The grouper finds the subset whose
 * shortfall best explains the total.
 */
public final class AnomalyGrouper {
    public List<Group> explain(Volume total, Map<String, Map<String, Long>> breakdown,
                               Map<String, Long> expectedBreakdown) {
        long expectedTotal = expectedBreakdown.values().stream().mapToLong(Long::longValue).sum();
        List<Group> out = new ArrayList<>();
        long totalMissing = Math.max(0, expectedTotal - total.rowCount());

        breakdown.forEach((dim, values) -> {
            long dimExpected = expectedBreakdown.getOrDefault(dim, 0L);
            long dimActual = values.values().stream().mapToLong(Long::longValue).sum();
            long missing = Math.max(0, dimExpected - dimActual);
            if (missing == 0) return;
            out.add(new Group(dim, "(all)", missing,
                    expectedTotal == 0 ? 0 : (double) dimActual / dimExpected,
                    totalMissing == 0 ? 0 : (double) missing / totalMissing));
        });

        return out.stream()
                .sorted(Comparator.comparingDouble(Group::contribution).reversed())
                .limit(5)
                .toList();
    }

    /** Drill one level deeper: which values inside the responsible subset? */
    public List<Group> drill(Volume total, Map<String, Long> valueCounts,
                             Map<String, Long> expectedValues) {
        long expected = expectedValues.values().stream().mapToLong(Long::longValue).sum();
        return valueCounts.entrySet().stream()
                .map(e -> {
                    long exp = expectedValues.getOrDefault(e.getKey(), 0L);
                    long missing = Math.max(0, exp - e.getValue());
                    return new Group("value", e.getKey(), missing,
                            exp == 0 ? 0 : (double) e.getValue() / exp,
                            expected == 0 ? 0 : (double) missing / expected);
                })
                .filter(g -> g.rows() > 0)
                .sorted(Comparator.comparingDouble(Group::contribution).reversed())
                .limit(10)
                .toList();
    }
}
```

### Lineage-aware alerting and routing

```java
public final class LineageSuggester {
    /**
     * When bronze/orders is late, the alert for silver/orders is usually noise.
     * Suppress downstream alerts whose upstream is already paged, and say why.
     */
    public Optional<Anomaly> suppressIfUpstreamFailed(Anomaly a, Set<Anomaly> paged) {
        return upstreamOf(a.dataset()).stream()
                .map(d -> paged.stream()
                        .filter(p -> p.dataset().equals(d) && p.severity() == Severity.PAGE)
                        .findFirst())
                .flatMap(Optional::stream)
                .map(upstream -> new Anomaly(a.dataset(), a.partition(), a.signalType(),
                        a.observed(), a.baseline(), a.robustZ(), a.at(), Severity.SILENT,
                        "suppressed: upstream " + upstream.dataset() + " is failing: "
                                + upstream.explanation()));
    }
}

public final class AlertRouter {
    public enum Action { PAGE, TICKET, SILENT }

    public Action route(Anomaly a, boolean knownIssue) {
        if (knownIssue.suppresses(a)) return Action.SILENT;     // logged, not delivered
        return switch (a.severity()) {
            case PAGE -> Action.PAGE;
            case TICKET -> Action.TICKET;
            case SILENT -> Action.SILENT;
        };
    }
}
```

### Test It

```java
@Test void seasonalSundayDropIsNotAnAlert() {
    List<Volume> history = synthetic(28, base = 1_000_000, weeklyShape = true);
    Volume sunday = new Volume("orders", "2026-01-11", 700_000, 0, 0);
    assertNull(detector.detectVolume(sunday, history, 7));
}

@Test void realDropIsDetectedAndGrouped() {
    List<Volume> history = synthetic(28, base = 1_000_000, weeklyShape = true);
    Volume broken = new Volume("orders", "2026-01-13", 600_000, 0, 0);
    Anomaly a = detector.detectVolume(broken, history, 7);
    assertNotNull(a);
    var groups = grouper.explain(broken,
            Map.of("region", Map.of("NA", 600_000L, "APAC", 0L, "EU", 0L)),
            Map.of("region", 1_000_000L));
    assertEquals("region", groups.get(0).dimension());
    assertTrue(groups.get(0).contribution() > 0.9);
}

@Test void detectionQualityIsMeasured() {
    // Inject 10 known faults; measure detection rate and false positives
    QualityReport q = quality.evaluate(detector, store, injectedFaults(), days = 30);
    assertTrue(q.mttd().toMinutes() < 60);
    assertTrue(q.falsePositiveRate() < 0.05);
}
```

### Stretch
- Add cardinality drift detection (a join that suddenly fans out).
- Add a "column absent entirely" detector, which catches a broken projection.
- Add a backtest harness that replays a month of history to tune thresholds.

## Deliverables
- [ ] Signal model for the three pillars, emitted from a real pipeline with a cost note
- [ ] Detector: freshness (absolute), volume (seasonal + robust), distribution (shift + new category)
- [ ] Grouper and drill-down that attribute a shortfall to a subset
- [ ] Lineage-based downstream suppression with an explanation
- [ ] Alert router with page/ticket/silent and a suppression log
- [ ] Detection quality report: MTTD, MTTR, false-positive rate, precision
- [ ] Threshold backtest over a month of history
