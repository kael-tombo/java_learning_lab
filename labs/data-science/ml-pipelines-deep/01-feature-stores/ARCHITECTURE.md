# Feature Stores — Architecture

## Components
1. Transform registry: versioned feature definitions and code pointers.
2. Offline store: append-only (entity, ts, value) history, scan-optimized.
3. Online store: entity-keyed latest values, lookup-optimized.
4. Materializer: streams offline rows into the online store.
5. Training builder: as-of join service producing versioned datasets.
6. Skew monitor: compares served vs recomputed vectors, owns alerts.
7. Metadata DB: owners, TTLs, schemas, backfill receipts.

## Data flow
Raw events -> versioned transforms -> offline log -> two sinks:
(a) training builder (as-of join at label times), (b) materializer
(upsert latest per entity) -> online reads at serving time.

## Key interfaces
- `getOnlineVector(entityId, versionSet)`: returns latest fresh fields.
- `buildTrainingSet(labels, versionSet)`: returns as-of-joined rows.
- `registerTransform(def, code)`: creates a new immutable version.
- `backfill(version, from, to)`: recompute plus validation receipt.

## Scaling notes
Offline grows with event volume times retention; partition by time and
entity hash. Online grows with entity count times feature width; shard
by entity id. The materializer is the hot path: it must be idempotent
on retries (upsert by (entity, ts), ignore older ts).

## Consistency choices
Training favors completeness and correctness (recompute allowed);
serving favors recency and availability (TTL-gated reads). The registry
plus shared transform code is what keeps the two consistent.

## Worked lookup example
Request vector for u1 at t=28 with TTL 30: candidate rows (10,1.0),
(20,2.0); row at 30 is future and excluded. Latest qualifying row is
(20,2.0), age 8, fresh, so the store returns 2.0. At t=100 the same
entity's latest row (30,3.0) has age 70, expired, so the field returns
missing and the declared imputation applies instead of a stale 3.0.
