# Data Quality (Foundations) — REAL WORLD PROJECT

## Context

A health-insurance payer loads claims daily. Two incidents in the last year
went undetected for 2-11 days: a provider system began sending negative claim
amounts (networks savings, misinterpreted as errors) and a coordinate-system
migration introduced invalid ZIPs. Both surfaced as a reconciliation
break with a payer, not from the data. You own a quality layer that catches
this class of problem within the load, and an SLO that makes "trustworthy"
measurable.

## Scale & Constraints

| Dimension | Value |
|---|---|
| Tables | 1,400 in the warehouse, ~90 in the clinical/claims tier |
| Daily volume | 210M claim rows, 4.1B retained |
| Late arrival | up to 30 days for out-of-network claims |
| Regulatory | CMS, HIPAA, state filing; rejections must be traceable |
| Constraint | checks must add < 3% to a 6-hour load window |
| Ownership | 2 data engineers, 40 upstream source systems |

## Architecture

```
40 source systems
   |
bronze (raw + ingest metadata: source, batch_id, received_at, checksum)
   |
quarantine layer ------> reprocess queue (7d SLA) ------> back to bronze
   |
silver (conformed) -- validation runs HERE (post-transform, pre-serve)
   |
gold (marts) -- continuous, lightweight monitors only

observability: per-table quality score -> freshness/volume/validity SLIs
```

**Why the checks live in silver, not on the source.** Inline checks on 40
heterogeneous feeds either block a good source because one is broken, or let a
bad one through because the others are fine. Validating the conformed layer
gives one place to reason about, and the bronze layer keeps the raw bytes for
reprocessing.

## The Expectation Library as Contract

```java
public sealed interface ClaimExpectation permits Monetary, Referential,
        Temporal, Categorical, Volume, CrossTable {}

public record Monetary(String column, MoneyPolicy policy) implements ClaimExpectation {
    /**
     * Negative claim amounts are not always errors: adjudication writes
     * adjustments and reversals. So this is a two-part rule:
     *   - flagged as NEGATIVE_ALLOWED_ONLY_WITH_REASON when amount < 0
     *   - BLOCK when amount < 0 AND reason_code not in the adjustment set
     */
    public Result evaluate(Claim c) {
        if (c.amount().signum() >= 0) return Result.ok();
        return ADJUSTMENT_REASONS.contains(c.reasonCode())
                ? new Result(true, Severity.WARN, "adjustment row", c.amount())
                : new Result(false, Severity.BLOCK,
                        "negative amount without adjustment reason: " + c.reasonCode(), c.amount());
    }
}
```

## Cost-Conscious Validation Strategy

Full validation of 210M rows per column is not affordable at the observed cost
per row, so the placement is deliberate.

| Check class | Method | Why |
|---|---|---|
| Schema, types, nullability | metadata-level, free | engine rejects; catches drift immediately |
| Volume, distinct counts | aggregate, ~free | single scan, engine-optimized |
| Range / set / regex | pushed into the same scan as validation | one pass for load *and* check |
| Referential integrity | anti-join on a small dimension | dimension is 40k rows, broadcastable |
| Cross-table totals | aggregate reconciliation | cheap, catches whole-pipeline error |
| Row-level semantic rules | **1% deterministic sample** | 2.1M rows; semantic rules are the expensive part |
| Streaming anomaly detection | reservoir + bounds, continuous | catches shift without a full scan |

```java
/** Deterministic sampling: the same rows every run, so a failure is reproducible. */
public final class DeterministicSampler {
    public static boolean selected(long rowId, int perMille) {
        long mixed = mix64(rowId ^ 0x5DEECE66DL);      // not rowId % 1000
        return mixed % 1000 < perMille;                // spread across the whole keyspace
    }
    static long mix64(long z) {
        z = (z ^ (z >>> 30)) * 0xBF58476D1CE4E5B9L;
        z = (z ^ (z >>> 27)) * 0x94D049BB133111EBL;
        return z ^ (z >>> 31);
    }
}
```

## Quality SLIs and the SLO

An SLO forces a decision about what is acceptable, which is what makes the
work stick.

```java
public enum Sli { COMPLETENESS, VALIDITY, FRESHNESS, CONSISTENCY, VOLUME }

public record QualitySlo(String table, Sli sli, double targetPct, Duration window) {}

public static final List<QualitySlo> CLAIMS_SLOS = List.of(
    new QualitySlo("claims.silver", Sli.COMPLETENESS, 99.95, Duration.ofDays(30)),
    new QualitySlo("claims.silver", Sli.VALIDITY,     99.99, Duration.ofDays(1)),
    new QualitySlo("claims.silver", Sli.FRESHNESS,    99.00, Duration.ofDays(1)),
    new QualitySlo("claims.silver", Sli.CONSISTENCY, 99.90, Duration.ofDays(1))
);

public enum ErrorBudgetPolicy { PAGE, TICKET, SILENT }

public ErrorBudgetPolicy actionFor(double burnRate) {
    if (burnRate > 14) return ErrorBudgetPolicy.PAGE;     // fast burn: page
    if (burnRate > 6)  return ErrorBudgetPolicy.TICKET;    // slow burn: ticket
    return ErrorBudgetPolicy.SILENT;                       // within budget
}
```

The `SILENT` state is the important one. A quality system that pages on every
threshold breach gets muted within a week, and then it is worthless.

## The Two Incidents, Retrospectively

**Negative amounts, undetected 11 days.** Root cause chain: provider system
change -> unrecognized reason code -> rule set had no "unknown reason" default
-> the validator only checked `amount >= 0` on the gold mart, which was
populated by an adjustment join that silently dropped rows. Fixes: (1) a default
`BLOCK` on unrecognized reason codes so new codes are caught on day one, (2)
checks moved to silver, before the mart, (3) a cross-table total reconciliation
that would have fired within a day.

**Invalid ZIPs, undetected 2 days.** Root cause: a coordinate migration upstream,
and the ZIP check was validating format but not referential validity against
the ZIP table, and the ZIP table was itself stale. Fixes: referential check
against a monthly-refreshed ZIP dimension, plus a freshness SLO on that
dimension — a stale reference table is a data quality bug too.

## Failure Modes and the Runbook

1. **Quarantine backlog grows.** Symptom: reprocessed rows exceed 7d SLA. Cause:
   a systemic source defect. Fix: circuit-break the source, alert the owning
   team with a sample of rejected rows, and keep serving silver minus quarantine
   with a visible "incomplete" flag rather than blocking claims processing.
2. **False positive blocks a good load.** Symptom: overnight load stops at 02:00
   and dashboards go stale. Fix: severity tiers with a documented break-glass
   override that is logged and reviewed; a `BLOCK` rule that fired 3 times in a
   month without a real defect gets demoted to `WARN`.
3. **Baseline drift for a new table.** Symptom: PSI warnings from day one. Fix:
   bootstrap the baseline from 7 days of history, suppress drift for the window.
4. **Check cost regression.** Symptom: load window creeps from 6h to 6h40m. Fix:
   budget checks as a percentage of runtime in the load's own metrics; if over
   3%, move the expensive rule to sampling.
5. **Reference dimension staleness.** Symptom: escalating referential failures.
   Fix: freshness SLO on reference tables, and a paging path that treats a stale
   dimension as an incident rather than a data issue.
6. **Silently disabled checks.** Symptom: a rule nobody runs. Fix: a monthly
   inventory report of every check, its last run, and its last failure; an unused
   check is deleted, not kept.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Data contracts (schema, semantics, and quality expectations) formalize what
  producers owe consumers, which is the current direction of travel for making
  pipelines self-describing.
  - Reference: https://datacontract.com/
  - Reference: https://github.com/great-expectations/great_expectations
- OpenLineage is a standard for capturing lineage metadata across the data
  ecosystem, which is what makes impact analysis ("who breaks if this table
  changes?") answerable rather than tribal knowledge.
  - Reference: https://openlineage.io/
  - Reference: https://openlineage.io/docs/

## Deliverables
- [ ] Expectation library mapped to the 5 quality dimensions, with severity tiers
- [ ] Validation placement decision (bronze/silver/gold) with a written rationale
- [ ] Cost model showing checks under 3% of load runtime
- [ ] Four quality SLOs with an error-budget policy including a SILENT state
- [ ] Quarantine + reprocess loop with a 7-day SLA
- [ ] Postmortems for the two real incidents with the fix set
- [ ] Check inventory report (every check, last run, last failure)
