# Distributed ID Generation - Real World Project

## Project: Replacing Sequential IDs Without Breaking External Contracts

### Objective
Migrate a production database from auto-increment integers to a globally unique,
roughly ordered ID scheme across a live system — keeping URLs valid, foreign keys intact,
and inserts as fast as before.

### Why This Is a Real Problem
Sequential IDs leak business volume, are enumerable by customers, and are impossible to
generate in more than one place. But they are also B-tree friendly and embedded in every
cached page and external webhook. The migration is mostly about the second list.

### Architecture Overview
```
  App ─▶ ID service (Snowflake: epoch | worker | seq)
            │  worker IDs leased from Zookeeper/etcd with TTL
            ▼
  Postgres (BIGINT PK, keep existing IDs)
  External URLs: /orders/{id} — old and new IDs both resolve
```

### Phase 1: Inventory the Coupling (Week 1)
1. Find every place an ID appears in an external contract: URLs, API responses, webhooks,
   invoices, exported CSVs, log lines someone greps, support scripts
2. Find every place IDs are parsed, assumed sequential, or used for pagination
3. Record current insert throughput and index depth — that is the bar to hold
4. Check whether IDs are ever exposed in a form users can enumerate; this sets the security
   requirement, not just the aesthetics

### Phase 2: Choose and Justify (Week 2)
1. Requirements: unique across regions, roughly time-ordered, no coordination on the hot
   path, ≤16 bytes, enumerable-safe
2. Compare candidates against measured insert throughput on your actual index type:
   - `BIGINT` Snowflake: fastest, sequential inserts, needs a worker-ID source
   - `UUID` v7: no worker-ID source, 16 bytes, requires a compatible Postgres version
   - `ULID` stored as text: convenient, larger, worse for indexes
3. Run the benchmark on a copy of production-sized data — the differences are workload-specific
4. Write the ADR, including the rejection reasons for the schemes you did not pick

### Phase 3: Worker-ID Safety (Week 3)
1. Do **not** use `hostId % 1024` — it silently collides across hosts
2. Lease worker IDs from an existing coordination service (ZooKeeper/etcd ephemeral
   sequential node, or a DB lease) with renewal and a TTL
3. Assert lease liveness at startup and refuse to start without a valid lease
4. Handle the clock-backwards case explicitly; decide whether to fail the request or wait
5. Add a startup check: if the local clock is more than N seconds off the lease authority,
   refuse to start

### Phase 4: Rollout (Week 4)
1. Add the new column, populate for new rows only — no backfill of existing rows
2. Application reads either column, writes the new one; dual-read with new preferred
3. Foreign keys to the new column on newly created tables only
4. Verify: no duplicate IDs (unique index will tell you), no URL breakage, insert throughput
   within 10% of baseline
5. Publish a changelog entry with the new format for API consumers

### Phase 5: Clean Up (Week 5+)
1. Stop relying on auto-increment; drop the sequence where safe
2. Remove dual-read paths once all consumers are migrated
3. Add an alert on ID generator collisions and on clock skew
4. Document the epoch, worker-ID source, and the maximum IDs-per-millisecond capacity

### Deliverables
1. ID scheme ADR with measured insert benchmarks on production-sized data
2. Worker-ID leasing implementation with TTL renewal and liveness assertions
3. Rolling migration with dual-read and a verification report
4. Operational doc: capacity math, clock-skew alert, and what to do if the lease is lost

### Success Criteria
- Zero duplicate IDs over the first 30 days, enforced by a unique index
- Insert throughput within 10% of the sequential-ID baseline
- No broken external URLs or webhook payloads
- No worker-ID reuse, verified by lease history audit

### Sourced field notes (fetched Oct 2026 — verify before citing)
- RFC 9562 (UUID revision), via IETF —
  https://www.rfc-editor.org/rfc/rfc9562.html
  Use for: the authoritative definition of UUIDv7 including the monotonicity method and the
  recommended random bit allocation. This is the correct citation for UUIDv7 semantics rather
  than any blog describing them.
- Amazon DynamoDB Developer Guide, "Core components of Amazon DynamoDB" —
  https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.CoreComponents.html
  Use for: partition-key design guidance and hot-partition avoidance — the same skew logic
  that makes random UUID partition keys a poor choice for a distributed store.

### Estimated Time
5-6 weeks part-time