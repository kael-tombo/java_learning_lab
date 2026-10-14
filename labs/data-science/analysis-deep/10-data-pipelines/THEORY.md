# Data Pipeline Theory

## 1. Batch vs streaming

Batch processes bounded inputs on a schedule (hourly, daily): simple,
replayable, higher latency. Streaming processes unbounded event flows
continuously: fresh results, harder correctness (out-of-order events,
late data, state management). Choose by decision latency: daily
restocking needs batch; fraud interdiction needs streaming - and say
which you chose and why, since each heritage brings its failure modes.

## 2. Idempotency

An operation is idempotent if applying it twice equals applying it once
(upsert by key, write-if-unchanged, delete-if-present). Replay-safe
sinks make retries harmless: the PipeIdem demo merges batches by order
key so a replayed batch changes nothing (rows stay 3, values intact).
Design sinks idempotent first; retries are inevitable.

## 3. Delivery semantics (conceptual, careful)

- At-least-once: every record arrives, duplicates possible. This is the
  widely documented default posture of common message queues - stated
  here as a general default only, with no vendor version claims.
- At-most-once: no duplicates, but records may be lost.
- Exactly-once: each record takes effect once. Achievable only as a
  joint property of source, transport, and an idempotent or
  transactional sink - never by the queue alone. Treat any stronger
  claim (naming versions or products) as out of scope for this lab.

## 4. Schema evolution

Additive changes (new optional field) keep old readers working:
COMPATIBLE in the PipeSchema demo. Type changes or renamed required
fields break readers: BREAKING. Rule: only additive-compatible changes
flow without coordination; everything else is a versioned migration
with a dual-read window.

## 5. Backfill and replay discipline

Reprocessing history (new logic, fixed bug) must be a first-class path:
same code, explicit range, quarantined output compared before swap.
Ad-hoc reruns against live tables double-count - replay writes to
staging, diffs against production, then promotes.

## 6. Data-quality checks

Row counts vs source, null rates per column, distribution drift of key
metrics vs a reference (PipeQuality: nullRate 0.333, drift 0.375 on toy
data). Fail the batch loudly on breach; quarantined data beats silent
corruption downstream.

## 7. Orchestration DAGs

Tasks as a directed acyclic graph: extract -> validate -> transform ->
serve, with retries per node and failure isolation. Acyclicity is the
whole point (no task waits on its own output); keep the DAG definable
without proprietary features so the pipeline is portable.
