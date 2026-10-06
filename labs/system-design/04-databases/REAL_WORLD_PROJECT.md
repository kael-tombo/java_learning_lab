# Database Design - REAL WORLD PROJECT

## Project: Multi-Tenant B2B Analytics SaaS Data Layer

**Time**: 2-3 weeks (team of 3)

**Scenario**: A B2B analytics product. 4,000 tenants, wildly skewed: the top
5 tenants are ~55% of query volume. Each tenant uploads up to 40 GB of
event data per day. Customers ask for: (a) sub-second dashboards, (b) exports
that never miss a row, (c) the ability to delete all data for a tenant within
24 hours for GDPR erasure.

### Step 1: Access Patterns Before Schema

Document the top 20 queries with their measured frequency and p95 latency. From
that, derive the model:

| Query | Frequency | Latency target | Must be single-shard? |
|-------|-----------|----------------|-----------------------|
| Dashboard: last 30 days metrics for tenant T | 400k/day | p95 < 800 ms | yes |
| Time-series point lookup (tenant, metric, ts) | 6M/day | p95 < 50 ms | yes |
| Upload batch status | 900k/day | p95 < 100 ms | yes |
| Cross-tenant export (admin only) | 40/day | < 60 min | no, allowed fan-out |
| Tenant delete | 5/day | < 24 h | no, bulk path |

Everything except the admin export **must** be tenant-scoped. That single fact
determines the shard key.

### Step 2: Sharding Strategy and the Skew Problem

```
Shard key: hash(tenant_id) -> 32 logical shards on 8 physical clusters
Key insight: the 5 largest tenants are ~2% of tenants but ~55% of traffic.
```

A plain tenant-hash gives you an unusable hot shard. Implement **tiered
placement**:

```
Tier A (> 2% of traffic):  dedicated cluster, own replicas, own cache
Tier B (0.1% - 2%):       shared cluster, hashed
Tier C (< 0.1%):          shared cluster, hashed, aggressively cached
```

Build the tier classifier on a nightly job over the last 7 days of per-tenant
QPS with hysteresis (promote at >2.5%, demote at <1.5%) so a tenant cannot
oscillate between tiers daily.

**Deliverable:** a distribution report — traffic share by tier, p95 latency per
tier, and the point at which Tier A stops paying for its own cluster.

### Step 3: Hot Path: Query Store vs. Live Scan

Raw event scans will never hit the latency target. Build a pre-aggregated
**query store**:

```
raw events (object storage, append-only, partitioned by tenant+day)
        -> streaming rollup (1-min and 1-hour buckets)
        -> query store (time-series columns, partitioned by tenant + day)
        -> per-tenant cache of the last hour's buckets
```

Define the consistency story honestly: dashboards are **eventually consistent
with a stated bound** ("data complete to within 90 seconds"), while
**exports are batch and strongly consistent** (read from raw, with a
watermark the export job respects). Write both promises into the product docs.

### Step 4: Schema Migrations That Survive Release Trains

You have 30+ engineers and continuous deployment. Every migration must be
backward compatible with the oldest deployed binary (24 h minimum) and with
the currently running backfill.

Run the expand/migrate/switch/contract sequence for two real changes:

1. `events.raw_payload JSONB` -> `payload_bytes BYTEA` + `schema_id INT`
   (compresses payload ~4x and enables routing by schema version).
2. Split `tenants.plan TEXT` into a `subscription` table (adds plan history,
   which is needed for correct billing anyway).

For each: measure backfill throughput on production-shaped data, define batch
size from observed lock-wait latency, and implement the continuous diff job as
a real alert rather than a one-off script.

**Hard gate:** the contract phase checks the query-log access analytics for
references to the dropped column and refuses to run if any exist. Demonstrate
this gate catching a real stale reference.

### Step 5: Bulk Isolation and the Right to Erasure

Tenant deletion is the hardest requirement because it crosses every store:
raw objects, rollups, query store, cache, backups, and derived exports.

Design:
- A `tenant_deletion_queue` with per-tenant saga state (see lab
  07-transactions), one idempotent step per store.
- Soft-delete markers read by every query path (so nothing new lands mid-delete).
- Crypto-shredding for backups: per-tenant data key wrapped by a tenant key
  held in a separate KMS boundary; erasure = delete the tenant key, which
  makes every backup copy of that tenant unreadable. This is the only approach
  that meets a 24 h bound when backups have a 35-day retention.

Write the runbook and prove the 24 h bound by executing a full deletion for a
test tenant in staging, with timings per step.

### Step 6: Failure Drills

1. **Kill a replica** during a backfill. Verify the backfill pauses rather than
   double-applying, and that the migration state survives.
2. **Throttle one shard to 5% CPU**. Verify the dashboard shows degraded mode
   instead of hanging, and that the alerting fires on symptoms.
3. **Replay a bad migration**: intentionally corrupt 5,000 rows, verify the
   diff job catches it within its cycle, and verify the remediation is a
   re-run, not a hand-written fix.

### Deliverables

1. Access-pattern inventory with measured frequencies and latency targets.
2. Tiered sharding design plus a tier-classification job with hysteresis.
3. Query store architecture with a written staleness bound per surface.
4. Two production-grade migrations with measured backfill throughput.
5. Idempotent tenant-erasure saga with a proven 24 h bound.
6. Three failure drills with timelines and the runbooks they changed.

### Grading Rubric

| Dimension | Weak | Strong |
|-----------|------|--------|
| Sharding | Single hash, hot tenant ignored | Tiered, hysteresis, measured skew |
| Consistency | "Eventually consistent" | Per-surface bound, watermark for exports |
| Migration | Script with a calendar gate | Access-log gate, resumable, diff job |
| Erasure | `DELETE FROM` and hope | Saga + crypto-shredding, proven bound |
| Operations | No drills | Drills with timelines and updated runbooks |

## Sourced field notes (fetched Oct 2026 — verify before citing)

- Kubernetes documentation — StatefulSet, stable network identities and
  ordered rollout semantics; the canonical reference for sharding a database
  across predictable, addressable pods.
  https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/
- Kubernetes documentation — Storage concepts: persistent volumes,
  volume claims, and access modes; the vocabulary behind per-tenant storage
  isolation.
  https://kubernetes.io/docs/concepts/storage/

Both are versioned living docs. Pin the doc version you actually read, and
re-verify the StatefulSet rollout guarantees (OrderedReady vs Parallel) before
relying on them for an ordered migration.