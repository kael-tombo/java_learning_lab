# Data Warehousing — REAL WORLD PROJECT

## Context

A subscription media company grew its analytics warehouse from 200GB to 14TB.
The BI tool now has a 45-second median query time, monthly warehouse spend
tripled, and two analysts were told to stop using ad-hoc SQL. You own the
remediation: modelling, physical design, and cost.

## Scale & Constraints

| Dimension | Value |
|---|---|
| Fact rows | 6.2B `fact_play_event`, 1.1B `fact_subscription_event` |
| Dimensions | 30, incl. 4 SCD2 |
| Concurrent analysts | 60 peak, mostly dashboard refreshes |
| Query SLO | p95 < 10s for dashboards, < 60s for ad-hoc |
| Retention | 25 months hot, then archive |
| Budget | flat, no headroom this fiscal year |
| Compliance | geo-restricted content rows must be filtered by entitlement |

## Architecture

```
lake (raw parquet, partitioned by event_date)
  |
curate (conformed, deduped, entitlement-stamped)
  |
marts
  |-- fact_play_event      PARTITION BY event_date, CLUSTER BY (title_sk, country)
  |-- fact_subscription    SCD-style additive measures
  |-- agg_title_daily      refreshed incrementally, 1/40th the rows
  |-- agg_channel_daily    pre-joined for dashboard-only consumers
  |
semantic layer -> dashboards / ad-hoc SQL / reverse ETL
```

## Key Implementation — physical design decisions with numbers

| Decision | Option A | Option B chosen | Why |
|---|---|---|---|
| Clustering key | none | `(title_sk, country)` | 92% of queries filter both; measured 6x less bytes scanned |
| Partition | month | day | intra-month partitions were 4TB each, exceeding 1B-row file targets |
| Aggregate | none | `agg_title_daily` | 1.1B -> 28M rows, dashboard p95 41s -> 4.2s |
| Compression | gzip | zstd + dictionary | 610GB -> 240GB, no query regression |
| Materialized | view | table refreshed hourly | view recomputed the 40x join on every refresh |

```java
public final class PartitionPolicy {
    // One day x one country-cluster per file keeps files ~180MB: parallel, mergeable,
    // and under the object-store multipart threshold. Bigger files starve the cluster;
    // smaller files create millions of tiny reads and metadata overhead.
    static final LocalDate HOT_RETENTION_MONTHS_DAYS = 25 * 30;
    static final int TARGET_FILE_MB = 180;

    public static boolean isHot(Instant eventTime, Instant now) {
        return eventTime.isAfter(now.minusSeconds(HOT_RETENTION_MONTHS_DAYS));
    }
}
```

## Entropy and Ad-Hoc Access

`title_sk` is heavily skewed: one title is 4% of all rows. Without
skew handling, the reducer for that key becomes the straggler for the whole
query. Two mitigations, both cheap:

```java
// Mitigation 1: salt the hot key deterministically so work spreads across executors.
long salted = mix64(titleSk ^ (regionHash * 0x9E3779B97F4A7C15L));

// Mitigation 2: pre-split the hot fact into a separate physical table, so
// skew is contained to one partition family that can be scaled alone.
boolean isHotKey(long titleSk) { return hotKeySet().contains(titleSk); }
```

## Cost Model for the Warehouse

The bill is driven by three lines; you can only move two of them.

```
monthly cost = storage_GB * rate_storage
             + bytes_scanned_by_queries * rate_scan
             + compute_slot_hours * rate_compute
```

The lever that matters is **bytes scanned per question**. The team cut it 71%
with three changes alone: partition pruning, the pre-aggregates, and replacing
6 dashboard queries with 1 aggregate query. Compute hours fell only 12% —
which is why "just add cache" was the wrong first instinct.

## Failure Modes and the Runbook

1. **Small-file explosion** after a backfill with 1-minute partitions. Symptom:
   metadata latency dominates. Fix: compact to target file size, and block
   future writes at the target partition granularity.
2. **Statistics drift** on a high-cardinality `title_sk`. Symptom: bad plans
   only for certain date ranges. Fix: nightly `ANALYZE` on hot partitions.
3. **Dashboard fan-out** — 60 analysts each refreshing a raw-fact query at
   09:00. Symptom: queue depth spikes, SLO breach. Fix: move dashboards to
   `agg_*` tables and stagger refresh by department.
4. **Entitlement leak** — geo-restricted rows served to a user without the
   license. Symptom: audit finding. Fix: entitlement applied in `curate` and
   re-verified by a row-level test in CI.
5. **Cost regression** from one analyst's `SELECT *` without a date filter.
   Symptom: scan-based bill jumps 5x. Fix: query cost guardrails, per-team
   budgets, and a default `event_date` partition requirement enforced by lint.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Snowflake separates storage from compute: warehouses (compute clusters) are
  independent of stored data, which is why eliminating bytes scanned and
  sizing warehouses are two separate cost levers.
  - Reference: (link removed)
  - Reference: https://docs.snowflake.com/en/guides-overview-cost
- Star schema and dimensional modeling are the canonical structure for
  analytics: facts at a declared grain joined to denormalized dimensions.
  - Reference: https://en.wikipedia.org/wiki/Star_schema
  - Reference: https://docs.starburst.io/latest/index.html

## Deliverables
- [ ] Dimensional model document with grain statements and SCD2 policy
- [ ] Physical design table: partitions, clustering, compression, target file size
- [ ] Before/after benchmark for 6 real dashboard queries (time + bytes)
- [ ] Cost model spreadsheet with three levers and a measured plan
- [ ] Skew-handling plan for the 4 hottest title keys
- [ ] Runbook for the five failure modes, including a compaction procedure
