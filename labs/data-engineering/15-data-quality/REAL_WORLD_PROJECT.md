# Data Quality (Advanced) — REAL WORLD PROJECT

## Context

A gaming company publishes live event and revenue metrics to 12 internal
dashboards and 3 external partners. A 3% revenue overstatement from a rounding
change in one aggregation shipped for 19 days, was noticed by a partner's
analyst, and became a contractual incident. The current stack catches schema
breaks and row-count drops; it cannot catch a value that is wrong in a
plausible way. You own the trustworthiness program.

## Scale & Constraints

| Dimension | Value |
|---|---|
| Tables | 2,400; 140 published as "certified" metrics |
| Volume | 60B events/day, 2.1PB |
| Consumers | 12 internal dashboards, 3 partners (contractual accuracy terms) |
| Current checks | 1,400 row-count/null rules, 0 distribution rules, 0 reconciliations |
| Incident | 19 days, 3% overstatement, contractual credit issued |
| Requirement | partner-reported metrics must reconcile to the penny |
| Constraint | no additional load budget on the production pipeline |

## Architecture (target)

```
                 contract per published metric
                 (schema + semantics + SLA + owner + consumers)
                              |
sources -> pipeline -> certified table -> semantic layer -> consumers
                              |
        +---------------------+---------------------+
        |                     |                     |
   per-run checks     metric monitors         reconciliations
   (existing)         (freshness/volume/     (source vs warehouse
                       distribution/seasonal)  vs payment processor)
        |                     |                     |
        +---------------------+---------------------+
                              |
                    trust score per metric + error budget
                              |
                   dashboards / alerting / partner reports
```

## Key Implementation — the three capability gaps

**Gap 1: no distributional monitoring.** Every incident in the last 18 months
was a value change, not a row-count change. So the monitors added are
distributional, on the published metrics, not on the tables.

```java
/**
 * The monitor set per certified metric, chosen because each catches a class
 * of failure the others miss:
 *
 *   FRESHNESS    - the pipeline stopped
 *   VOLUME       - partial load
 *   DISTRIBUTION - the shape changed (a filter silently dropped a region)
 *   SEASONAL     - a value shifted against its own weekly pattern
 *   RECONCILED   - the number disagrees with an independent source
 */
public record MetricMonitorSet(String metric, List<Monitor> monitors) {}

public final class MonitorFactory {
    public MetricMonitorSet forRevenue(long dailySeasonalPeriod) {
        return new MetricMonitorSet("revenue_gross_daily", List.of(
            new FreshnessMonitor(Duration.ofHours(4)),
            new VolumeMonitor(min = 0.85, max = 1.15, window = Duration.ofDays(28)),
            new DistributionMonitor(columns = List.of("currency", "region", "platform"),
                                    maxPopulationShift = 0.05),
            new SeasonalResidualMonitor(period = dailySeasonalPeriod,
                                        onCallZ = 5.0, ticketZ = 3.5),
            new ReconciliationMonitor(
                    independentSource = "payment_processor_settlement",
                    tolerance = 0.000001,       // contractual: to the penny
                    lag = Duration.ofDays(2)))); // settlement is T+2
    }
}
```

**Gap 2: no reconciliation against an independent source.** The 3% incident
would have been caught within two days by comparing the warehouse's revenue
against the payment processor's settlement file, which is a different system
entirely. This is now the highest-severity monitor in the program.

```java
/**
 * Independent-source reconciliation. The value of this check is precisely
 * that the two sides do not share code, so a shared bug cannot hide in both.
 *
 * Tolerance comes from the partner contract, not from observed drift.
 * Observed drift is a diagnostic: if it is much larger than the contract
 * tolerance, the pipeline has a real (if small) problem.
 */
public final class IndependentReconciliation {
    public record Report(String metric, Instant day, double warehouseTotal,
                         double processorTotal, double contractTolerance,
                         double observedDriftPpm, boolean breach, boolean driftGrowing) {}

    public Report run(String metric, Instant day) {
        double warehouse = warehouse.total(metric, day);
        double processor = processorFile.total(metric, day);        // T+2, so lag 2 days
        double drift = processor == 0 ? 0 : abs(warehouse - processor) / processor;
        double ppm = drift * 1_000_000;
        boolean growing = historicalPpm(metric, days = 14)
                              .monotonicIncreasing() && ppm > thresholdPpm();
        return new Report(metric, day, warehouse, processor, contractTolerance, ppm,
                drift > contractTolerance, growing);
    }
}
```

**Gap 3: metrics had no contract, so nobody knew what "correct" meant.** Each
of the 140 certified metrics now has a versioned contract, and a metric cannot
be published without one.

```java
/**
 * The rounding incident, and what a contract prevents. The bug:
 *   warehouse:  SUM(amount_cents) / 100.0            (double, then rounded)
 *   processor:  sum of integer cents                  (exact)
 * Over 3% of rows had sub-cent remainders, and the rounding direction was
 * systematically up. Every check passed: schema identical, row counts
 * identical, nulls zero, and the value was within 3% of last week.
 *
 * A contract states the semantic: revenue is the sum of integer minor units,
 * divided once, at the boundary. Stating it turns an invisible convention into
 * a testable rule.
 */
public record RevenueContract(int version) implements DataContract {
    public List<SemanticRule> semantics() { return List.of(
        new SemanticRule("minor_unit_integrity",
                "revenue is accumulated in integer minor units (cents) and scaled once",
                batch -> allCentsAreIntegral(batch), Severity.BLOCK),
        new SemanticRule("no_rounding_before_aggregation",
                "no ROUND() inside any aggregation; rounding happens only at presentation",
                batch -> noRoundInsideAgg(batch), Severity.BLOCK),
        new SemanticRule("fx_application_point",
                "FX is applied at transaction time, using the stored fx_rate; never re-derived",
                batch -> fxRateIsStoredAndUsed(batch), Severity.BLOCK)
    );}
}
```

## The Trust Model

A single "data quality score" is not credible to a partner, so trust is
published as dimensions with the weights shown, and a partner-facing statement
of exactly what is measured.

| Dimension | Weight | What it protects against | Evidence |
|---|---|---|---|
| Freshness | 0.30 | serving stale data as current | last successful run per partition |
| Reconciliation | 0.30 | values that are wrong in a plausible way | processor settlement diff |
| Contract conformance | 0.20 | convention drift, unstated semantics | rule pass rate, weighted by severity |
| Distribution stability | 0.15 | a filter silently dropping a segment | population stability per dimension |
| Volume within band | 0.05 | partial loads | 28-day band |

```java
public enum Severity { SILENT, TICKET, PAGE }

public final class TrustEngine {
    /**
     * A certification has a life. Re-certification is scheduled, not triggered
     * by a complaint: the 19-day incident existed because nothing forced a
     * re-examination of the revenue metric's contract.
     */
    public record Certification(String metric, int contractVersion, Instant certifiedAt,
                               Instant reviewDue, List<String> certifyingChecks) {
        boolean current(Instant now) { return now.isBefore(reviewDue); }
    }

    public static final Duration RECERTIFY_INTERVAL = Duration.ofDays(90);

    public Severity evaluate(TrustScore score, double burnRate, boolean knownIssue) {
        if (knownIssue) return Severity.SILENT;             // logged, not delivered
        if (score.errorBudgetRemaining() < 0) return Severity.PAGE;
        if (burnRate > 6) return Severity.TICKET;
        return Severity.SILENT;
    }
}
```

## Failure Modes and the Runbook

1. **Alert fatigue.** Symptom: engineers mute the quality channel. Fix: severity
   tiers with an explicit `SILENT` state; a suppressed alert is logged so the
   suppression is auditable, and every `SILENT` decision is reviewed monthly.
2. **Contract written but not enforced.** Symptom: a metric drifts, the contract
   exists, and nobody gated on it. Fix: contracts are evaluated in the pipeline,
   not reviewed; a contract is code that runs.
3. **Reconciliation unavailable at the required latency.** Symptom: the T+2
   settlement check only runs for recent days, so a 3% drift is confirmed 2 days
   late. Fix: accept a partial-day reconciliation against the payment gateway's
   same-day capture feed for faster signal, with the T+2 file as the authority.
4. **Seasonality change breaks the seasonal monitor.** Symptom: a permanent alert
   after a business model change. Fix: a monitor re-baselining workflow that
   requires an owner sign-off and records the reason; never auto-rebaseline.
5. **Contract version drift across consumers.** Symptom: two dashboards compute
   revenue slightly differently and both are "correct". Fix: the semantic layer
   is the only allowed source; a certified metric is read, never recomputed.
6. **Partner disputes a number the pipeline says is right.** Symptom: an argument
   with no evidence. Fix: point-in-time reproducibility — reconstruct the metric
   at the partner's query timestamp from an immutable snapshot, and produce the
   contract version, the check results, and the run ID that produced it.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Data contracts formalize the agreement between a data producer and its
  consumers, covering schema, semantics, and service levels, and are the
  current direction of travel for pipeline reliability.
  - Reference: https://datacontract.com/
  - Reference: https://github.com/great-expectations/great_expectations
- dbt tests (uniqueness, not-null, relationships, accepted values) and its
  metrics layer are the common implementation of contract-like assertions in
  the SQL transformation ecosystem.
  - Reference: https://docs.getdbt.com/docs/build/data-tests
  - Reference: https://docs.getdbt.com/docs/build/metrics-intro
- OpenLineage and table formats with time travel support the point-in-time
  reproducibility needed to answer "what did this metric say at 09:14 on
  the 3rd, from the data we had then".
  - Reference: https://openlineage.io/docs/
  - Reference: https://iceberg.apache.org/docs/latest/

## Deliverables
- [ ] Monitor set per certified metric, with the failure class each catches
- [ ] Independent-source reconciliation against payment settlement, with contract tolerances
- [ ] Versioned data contracts for the 140 certified metrics, enforced in the pipeline
- [ ] Trust model with published weights and a re-certification schedule
- [ ] Severity routing including a logged `SILENT` state and a monthly review
- [ ] Point-in-time reproducibility tool for partner disputes
- [ ] Postmortem of the 19-day 3% incident with the fix set
- [ ] Runbook for the six failure modes
