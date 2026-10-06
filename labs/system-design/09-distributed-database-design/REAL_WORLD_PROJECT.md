# Distributed Database Design - REAL WORLD PROJECT

## Project: Multi-Region SaaS Data Layer with Compliance Constraints

**Time**: 3-4 weeks (team of 4)

**Scenario**: A B2B analytics SaaS expanding from one region to three.
Requirements in tension, all of them real:

- 2,800 tenants, top 5 are ~55% of query volume.
- EU tenant data must never leave the EU region (residency).
- Dashboards must render in under 800 ms p95 from any region.
- Nightly exports must be complete and exactly-once.
- No tenant may see another's data (isolation is contractual, not technical).

### Step 1: Residency as a Partitioning Constraint

Region placement cannot be a routing optimisation — it is a legal boundary.

```
region_eu:   tenants whose data_residency = EU
region_us:   tenants whose data_residency = US
region_apac: tenants whose data_residency = APAC
```

Design:

- **Shard key includes region**: `hash(region, tenant_id)`.
- The router **rejects** cross-region access rather than falling back to a
  remote region. Required test: an EU tenant id resolved against the US router
  must throw, not silently succeed.
- Replica placement is constrained by the same rule: EU replicas never leave
  the EU region, which means EU availability is capped by EU AZ count. State
  that cost explicitly.

**Deliverable:** a residency decision record listing which operations are
legal, which are rejected, and the resulting availability ceiling per region.

### Step 2: Tiered Sharding (the skew problem is the design)

A plain tenant hash produces an unusable hot shard. Implement three tiers with
hysteresis:

```
Tier A (> 2.5% of 7-day traffic): dedicated cluster, own replicas, own cache
Tier B (0.1% - 2.5%):             shared cluster, hashed by tenant
Tier C (< 0.1%):                  shared cluster, hashed, aggressively cached
```
Promote at >2.5%, demote at <1.5%. Promotions/demotions are themselves data
moves, so require: shadow traffic verification, a bounded migration window, and
a rollback. Build a nightly classifier and a migration job.

**Deliverable:** traffic share by tier, p95 latency per tier, the point where
Tier A stops paying for its own cluster, and a runbook for a promotion.

### Step 3: Read Paths With Explicit Staleness Contracts

Three surfaces, three guarantees — written down and agreed with product:

| Surface | Mechanism | Staleness bound | Reads served by |
|---------|-----------|-----------------|-----------------|
| Dashboard tiles | pre-aggregated rollup store | complete to within 90 s | replicas, cached 30 s |
| Raw query explorer | columnar store, direct | 5 s | replicas with version check |
| Exports | raw partition scan | zero (batch, watermark-enforced) | primary |

Implement the version check: every replica read response carries the applied
index, and clients may pass `min_index` to block until caught up. Measure
actual staleness in production and alert when the *measured* p99 exceeds the
promised bound — a promise you do not measure is a lie you are telling.

### Step 4: Online Schema Migrations Under Continuous Deployment

Perform two real migrations while 30+ engineers deploy continuously:

1. `raw_payload JSONB` -> `payload_bytes BYTEA` + `schema_id INT`
2. `tenants.plan TEXT` -> `subscription` table (adds plan history for billing)

Rules, all enforced in code:
- Backward compatible with the oldest deployed binary for at least one full
  release window.
- Backfill resumable from a checkpoint table, batch size tuned from observed
  lock-wait latency.
- Continuous diff job as a first-class alerting component, not a one-off.
- **Contract phase gated on access analytics**, never on a calendar date.
  Build the gate, and demonstrate it refusing to run while a stale reference
  exists.

**Deliverable:** per-phase durations, batch-size tuning evidence, and the diff
job's alert history.

### Step 5: Isolation That Is Enforced, Not Assumed

Tenant isolation fails at three points: cache keys, export jobs, and admin
tooling. Address each:

- **Cache**: `tenant:{id}:` prefix enforced in the cache client itself, not at
  call sites. Write a test that calls the cache directly with a crafted key
  and is rejected.
- **Exports**: run in the tenant's region, watermark-enforced, and audit-logged
  with the requesting principal.
- **Admin tooling**: every admin query requires an explicit tenant scope; a
  query without one fails closed. Add a lint/test that no repository method can
  build an unscoped query.

**Required:** a red-team pass where you deliberately attempt cross-tenant reads
through all three paths and record how each is stopped.

### Step 6: Exactly-Once Exports at Scale

Exports are 40/day but each is 100k-10M rows. Design:

- Idempotent export job keyed on `(tenant, date, request_id)` with a `UNIQUE`
  constraint.
- Snapshot isolation so the export is internally consistent, taken at a
  watermark that advances only after the export commits.
- Chunked, resumable generation into object storage with a manifest.
- Completion recorded via the transactional outbox, so a crash after upload
  cannot produce a "missing" export.

**Required:** kill the export worker at 8 different points and prove that
re-running produces exactly one correct artifact.

### Step 7: Failure Drills

1. **Kill an entire region.** Verify reads and writes for that region's tenants
   fail cleanly (no cross-region fallback — that would breach residency), and
   that other regions are unaffected. Measure recovery.
2. **Slow one shard to 5% capacity.** Verify dashboards show degraded mode
   rather than hanging, and that alerting fires on symptoms.
3. **Promote a Tier A tenant** while it is under peak load. Verify shadow
   verification, zero downtime, and rollback.
4. **Replay a corrupted migration.** Inject 5,000 bad rows, verify the diff
   job catches them and remediation is a re-run.

### Deliverables

1. Residency decision record with per-region availability ceilings.
2. Tiered sharding with hysteresis, shadow-verified promotions, and runbook.
3. Read paths with written staleness bounds plus measured-vs-promised
   monitoring.
4. Two production migrations with per-phase timings and an access-log-gated
   contract phase.
5. Tenant isolation enforced at cache, export, and admin layers, plus a red-team
   report.
6. Exactly-once export design validated by 8 kill-point tests.
7. Four drill reports with timelines and the runbooks they changed.

### Grading Rubric

| Dimension | Weak | Strong |
|-----------|------|--------|
| Residency | "Region-aware routing" | Router *rejects* cross-region; ceiling stated |
| Skew | Single hash, hot tenant ignored | Tiered with hysteresis and shadow verification |
| Staleness | "Eventually consistent" | Per-surface bound, measured against promise |
| Migrations | Calendar-gated | Access-log gated, resumable, diff job alerting |
| Isolation | WHERE tenant_id = ? | Enforced in the cache client and repository API |
| Exports | "Make it idempotent" | Watermark + manifest + 8 kill-point proofs |

## Sourced field notes (fetched Oct 2026 — verify before citing)

- Kubernetes documentation — StatefulSets and the guarantees around stable
  network identity, ordered pod rollout, and per-pod storage; the standard
  reference when a shard is a pod with its own persistent volume and its own
  ordered failover.
  https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/
- Kubernetes documentation — Sharding and topology spread constraints, which
  encode the "spread tenants across failure domains" requirement that residency
  and tiering both depend on.
  https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/

Both are versioned living documents. Pin the doc version you read and re-verify
the exact constraint field names, which have changed across Kubernetes
releases.