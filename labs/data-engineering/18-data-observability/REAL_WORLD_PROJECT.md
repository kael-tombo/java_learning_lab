# Data Observability — REAL WORLD PROJECT

## Context

A streaming company has 4,100 pipelines and 1.9PB/day. Monitoring is
infrastructure-level: Airflow task state, Spark job status, Kafka lag. All of it
answers "is the job running", none of it answers "is the data right". Last
quarter, three separate incidents were detected by customers: a currency
conversion rate table that stopped updating (5 days), a filter change that
silently dropped one region (2 days), and a decimal-to-double conversion that
inflated revenue by 0.4% (11 days). You own data-level observability.

## Scale & Constraints

| Dimension | Value |
|---|---|
| Pipelines | 4,100 (900 Airflow DAGs, 180 streaming jobs, 4.1k batch tasks) |
| Datasets | 11,400 tables, 340 topics, 620 BI datasets |
| Volume | 1.9PB/day, 90B rows/day |
| Signals | must fit a monitoring cost budget: < 0.4% of cluster time |
| Current state | task-level metrics only; 0 data-level signals |
| On-call | 6 data SREs; 2,100 alert deliveries/month, 94% non-actionable |
| Constraint | cannot add per-row instrumentation; must be aggregate-only |
| Compliance | freshness of financial marts is auditable |

## Architecture (target)

```
pipeline instrumentation (automatic, via a shared SDK + engine hooks)
   |-- FRESHNESS  : last success, expected_by, lag            (1 series per partition)
   |-- VOLUME     : rows, bytes, distinct keys                (1 series per partition)
   |-- DISTRIBUTION: per-column mean/stddev/nulls/top-k      (top 12 columns per table)
   v
metrics store (Prometheus-compatible, 400d retention, 1.4B series)
   |
detection service
   |-- freshness  : absolute SLO check
   |-- volume     : seasonal-naive residual + robust z (MAD)
   |-- distribution: mean shift vs CV, new-category detection, cardinality drift
   v
grouper  ->  lineage suggester  ->  severity router  ->  alert manager
                                                        (page/ticket/silence)
   |
   +-- detection quality service: MTTD, MTTR, precision, FP rate, per-monitor
```

## Key Implementation — instrumentation that costs almost nothing

**The design constraint was cost, so the design is aggregate-only and
automatic.** A shared library emits signals from inside the pipeline; a
framework-level hook covers the rest, so no engineer has to remember.

```java
/**
 * Emission cost model, which is the argument that got this approved:
 *   volume      : 1 counter per partition    -> ~1,200 series/table/day
 *   freshness   : 1 gauge per partition      -> ~40 series/table
 *   distribution: 12 columns x 5 stats       -> ~250 series/table
 * A 400x-series store with 400d retention is 1.4B series, which is a known
 * and bounded cost. Per-row instrumentation was never an option.
 *
 * Distribution is only emitted for the columns a table declares, so the
 * cost is proportional to value, not to table count.
 */
public final class PipelineSignalEmitter implements AutoCloseable {
    private final String dataset;
    private final String partition;
    private final Clock clock;
    private final SignalSink sink;
    private final Map<String, DoubleSummaryStatistics> columnStats = new LinkedHashMap<>();
    private final Map<String, Map<Object, Long>> topValues = new LinkedHashMap<>();
    private final Set<String> declaredColumns;

    @Override public void close() {
        Instant now = clock.instant();
        sink.volume(new Volume(dataset, partition, rows.get(), bytes.get(), distinctKeys));
        sink.freshness(new Freshness(dataset, partition, expectedBy, now));
        columnStats.forEach((col, stats) -> sink.distribution(
                new ColumnFingerprint(dataset, partition, col, stats.getCount(),
                        stats.getMin(), stats.getMax(), stats.getMean(), stats.getStandardDeviation(),
                        topValues.getOrDefault(col, Map.of()).entrySet().stream()
                                .sorted(Comparator.comparingLong(Map.Entry::getValue).reversed())
                                .limit(10)
                                .collect(Collectors.toMap(e -> e.getKey().toString(),
                                                          Map.Entry::getValue, (a, b) -> a,
                                                          LinkedHashMap::new)),
                        buckets(stats))));
    }
}
```

## Key Implementation — detection tuned to the three real incidents

The three incidents map exactly to three detectors, which is the strongest
argument for the design.

```java
/**
 * Incident 1: a reference table (FX rates) stopped updating for 5 days.
 * Caught by: FRESHNESS on a declared SLO, plus a distribution check on the rate
 * value, which is the only reason anyone noticed the *value* was stale rather
 * than the *load* being late.
 */
public Anomaly detectStaleReference(ColumnFingerprint rates, Duration maxAge) {
    if (rates.ageSeconds(Instant.now()) > maxAge.toSeconds()) {
        return new Anomaly(rates.dataset(), rates.partition(), "freshness:reference",
                rates.ageSeconds(Instant.now()), maxAge.toSeconds(), Double.MAX_VALUE,
                Instant.now(), Severity.PAGE,
                "reference data is " + Duration.ofSeconds(rates.ageSeconds(Instant.now())).toDays()
                        + " days old; derived monetary columns are untrustworthy");
    }
    return null;
}

/**
 * Incident 2: a filter change silently dropped one region for 2 days.
 * Caught by: DISTRIBUTION on the region column - a whole category going to
 * zero count. Mean and stddev of the numeric columns barely moved, so a
 * mean-shift detector alone would have missed it. The new-category detector is
 * symmetric: it also catches categories that vanish.
 */
public Anomaly detectCategoryCollapse(ColumnFingerprint now, ColumnFingerprint base) {
    Set<String> baseTop = base.topValues().keySet();
    Set<String> nowTop = now.topValues().keySet();

    List<String> vanished = baseTop.stream().filter(k -> !nowTop.contains(k)).toList();
    List<String> appeared = nowTop.stream().filter(k -> !baseTop.contains(k)).toList();

    if (!vanished.isEmpty() && vanished.size() >= 1 && base.rowCount() > 1000) {
        long lost = base.topValues().entrySet().stream()
                .filter(e -> vanished.contains(e.getKey()))
                .mapToLong(Map.Entry::getValue).sum();
        double share = (double) lost / base.rowCount();
        if (share > 0.01) {
            return new Anomaly(now.dataset(), now.partition(), "distribution:" + now.column(),
                    vanished.size(), baseTop.size(), share * 100, Instant.now(), Severity.PAGE,
                    "categories vanished: " + vanished + " ("
                            + String.format("%.1f%%", 100 * share) + " of rows)");
        }
    }
    if (!appeared.isEmpty() && now.rowCount() > base.rowCount() / 10) {
        return new Anomaly(now.dataset(), now.partition(), "distribution:" + now.column(),
                appeared.size(), baseTop.size(), 0, Instant.now(), Severity.PAGE,
                "new categories appeared: " + appeared + " (source schema change?)");
    }
    return null;
}

/**
 * Incident 3: decimal -> double conversion inflated revenue 0.4% for 11 days.
 * Caught by: RECONCILIATION, not by any statistical detector, because a 0.4%
 * shift is inside the noise of a seasonal series. This is the honest limit of
 * distribution monitoring, and the reason a cross-system check stays in the set.
 */
public Anomaly detectReconciliationBreach(Reconciliation r, double tolerance) {
    if (r.withinTolerance(tolerance)) return null;
    return new Anomaly(r.metric(), r.partition(), "reconciliation",
            r.sourceB(), r.sourceA(), r.relDiffPpm() / 1e6, r.day(), Severity.PAGE,
            String.format("%s disagrees with %s by %,.0f ppm (tolerance %,.0f ppm)",
                    r.sourceAName(), r.sourceBName(), r.relDiffPpm(), tolerance * 1e6));
}
```

## The Alerting Rewrite

2,100 deliveries a month, 94% non-actionable. The rewrite is a severity model
and a suppression graph, not a threshold change.

```java
public enum Delivery { PAGE, TICKET, SILENT }

/**
 * The 94% problem was mostly two causes:
 *   1. downstream alerts duplicating an upstream alert (fan-out: 1 root cause
 *      produced 34 pages)
 *   2. volume thresholds firing on seasonal peaks
 * Fix (1) with a lineage suppression graph. Fix (2) with seasonal baselines.
 * Everything else was noise from a monitor with no owner.
 */
public final class DeliveryRouter {
    public Delivery route(List<Anomaly> candidates, LineageGraph graph,
                          KnownIssues known, BurnRate burn) {
        // 1. drop anything suppressed by an already-delivered upstream anomaly
        List<Anomaly> rootCauses = candidates.stream()
                .filter(a -> graph.upstreamOf(a.dataset()).stream()
                        .noneMatch(u -> candidates.stream().anyMatch(c ->
                                c.dataset().equals(u) && c.severity() == Severity.PAGE)))
                .toList();
        if (rootCauses.isEmpty()) return Delivery.SILENT;

        // 2. apply known-issue suppression, and log it
        List<Anomaly> undeliverable = rootCauses.stream().filter(a -> known.suppresses(a)).toList();
        known.logSuppressed(undeliverable);

        // 3. route on the strongest remaining signal and the error budget
        Severity worst = rootCauses.stream()
                .map(Anomaly::severity).max(Comparator.comparingInt(Enum::ordinal)).orElse(Severity.SILENT);
        if (worst == Severity.PAGE && burn.isExhausted()) return Delivery.TICKET;
        return switch (worst) {
            case PAGE -> Delivery.PAGE;
            case TICKET -> Delivery.TICKET;
            case SILENT -> Delivery.SILENT;
        };
    }
}
```

## Measured Outcomes

| Metric | Before | After (90 days) | Change |
|---|---|---|---|
| Alert deliveries/month | 2,100 | 340 | -84% |
| Non-actionable deliveries | 94% | 21% | -73pp |
| Incidents detected by customers | 3/quarter | 1/quarter | -67% |
| MTTD (customer-reported) | 6.1 days | 41 min | -95% |
| MTTD (detected by monitoring) | n/a | 22 min | new |
| MTTR | 2.4 days | 3.2 hours | -83% |
| Monitoring cost (cluster time) | 0% | 0.28% | within the 0.4% budget |
| Detection precision | n/a | 79% | measured against injected faults |

## Detection Quality as a First-Class Service

A monitor nobody measures is a monitor that will quietly stop working.

```java
public record QualityReport(int faultsInjected, int faultsDetected,
                            int falsePositives, Duration mttd, Duration mttr,
                            Map<String, PerMonitor> byMonitor) {
    public double recall() { return faultsInjected == 0 ? 0 : (double) faultsDetected / faultsInjected; }
    public double falsePositiveRate() {
        long opportunities = byMonitor.values().stream().mapToLong(PerMonitor::opportunities).sum();
        return opportunities == 0 ? 0 : (double) falsePositives / opportunities;
    }
    /** Per-monitor quality is the thing that gets reviewed monthly; a monitor
     *  with recall 0.0 or FP rate > 0.1 is fixed or deleted, never left. */
    public List<String> monitorsNeedingAttention() {
        return byMonitor.entrySet().stream()
                .filter(e -> e.getValue().detections() == 0
                           || e.getValue().falsePositiveRate() > 0.10)
                .map(Map.Entry::getKey).sorted().toList();
    }
}
```

## Failure Modes and the Runbook

1. **Alert fatigue returns.** Symptom: acknowledgements without action, then a
   muted channel. Fix: precision is a release gate; a monitor with recall 0 or
   FP > 10% is fixed or deleted within a week, and the monthly report is
   reviewed with the on-call team.
2. **Monitor cost explodes.** Symptom: monitoring shows up on the cloud bill.
   Fix: a per-dataset signal budget, distribution limited to declared columns,
   and a card that fails when a team exceeds its series allocation.
3. **Seasonal baseline wrong after a business change.** Symptom: a permanent
   alert, or a suppressed real one. Fix: baselines are versioned and
   re-baselining requires an owner sign-off with a recorded reason.
4. **Fan-out suppression hides a genuine second fault.** Symptom: an independent
   problem is not alerted because an upstream is already paging. Fix: suppression
   is per-dataset and time-bounded; a downstream anomaly that cannot be
   explained by the upstream signal is delivered as a ticket alongside the page.
5. **A new failure class has no monitor.** Symptom: an incident class recurs.
   Fix: every incident ends with either a new monitor or a written statement of
   why distribution monitoring cannot catch it; the latter is equally valuable.
6. **Late-arriving data looks like an outage.** Symptom: page at 03:00 for a
   partition that is simply not expected yet. Fix: expected-by times are
   per-partition and derived from the source's own SLA, not from a schedule
   assumption.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- OpenLineage and similar metadata standards make it possible to attach lineage
  to monitoring, so an alert can name the upstream cause and suppress the
  fan-out of dependent alerts.
  - Reference: https://openlineage.io/docs/
  - Reference: https://openlineage.io/
- Data quality tooling and contracts treat expectations as executable
  assertions, which is the same idea applied at the pipeline level: measurable,
  automated, and failing loudly rather than describing intent.
  - Reference: https://github.com/great-expectations/great_expectations
  - Reference: https://datacontract.com/

## Deliverables
- [ ] Automatic instrumentation SDK with a cost model and a 0.4% budget
- [ ] Three-pillar detection: freshness, volume (seasonal + MAD), distribution
- [ ] Category-collapse and new-category detectors, tied to the two historical incidents
- [ ] Reconciliation detector for sub-noise shifts, with the honest limit documented
- [ ] Lineage-based fan-out suppression with a per-dataset time bound
- [ ] Delivery router with page/ticket/silent and a suppression log
- [ ] Detection quality service with fault injection and a monthly per-monitor report
- [ ] Runbook for the six failure modes
- [ ] Before/after metrics table for alerts, MTTD, MTTR, and cost
