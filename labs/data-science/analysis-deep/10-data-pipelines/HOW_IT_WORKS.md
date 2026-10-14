# How Data Pipelines Work

## 1. Ingest with keys and timestamps

Every record arrives with a stable key (order id) and event time.
Keys enable idempotent sinks; event time (vs arrival time) enables
correct windows when data runs late. Records lacking either get them
at the gate or get rejected - no keyless appends into served tables.

## 2. Validate before transforming

Row counts, schema subset check, null rates run on the raw landing
before any business logic. Bad input quarantined here never becomes a
mysterious downstream metric dip needing a postmortem.

## 3. Transform deterministically

Same input, same output, every run: no wall-clock calls, no unordered
iteration in business logic. Determinism is what makes replay a test
rather than a gamble - assert it by double-running staging.

## 4. Sink idempotently

Merge by key (PipeIdem pattern), never blind append, into the serving
store. Retry any failed batch fearlessly: the fixed-point property
makes the second attempt a no-op, as the demo's replay row shows.

## 5. Evolve schemas additively

New optional fields flow freely; type changes and renames go through
versioned migration with dual reads. The compat check runs in CI on
every schema pull request - mechanical enforcement, not convention docs.

## 6. Orchestrate as a DAG

Nodes own retries and timeouts; edges carry data contracts (schema +
freshness SLA). Failures quarantine the node output and page with the
node name - nobody debugs "the pipeline," they debug ExtractOrders.

## 7. Replay, backfill, audit

New logic replays history into staging, diffs against production, then
promotes. Every run logs code version, input range, row counts, and
check outcomes - the audit trail that makes month-old numbers
defensible.
