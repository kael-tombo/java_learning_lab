# Lab 06: AI Pipeline Orchestration — Exercises

Difficulty: (E) easy, (M) medium, (H) hard. Java 21, no external deps.

---

## Exercise 1: Typed Stage Contract (E)

Define `Stage<I,O>` and `StageResult<T>` (ok/failed with classification). Implement two
stages and chain them.

**Verify**: a typed stage cannot accept the wrong input type at compile time.

---

## Exercise 2: Error Policy (M)

Implement fail / skip / retry / degrade policies and apply each to a different stage.

**Verify**: a 10% upstream failure rate behaves differently per policy, as declared.

---

## Exercise 3: Type-Driven Router (M)

Route by input type to a stage, replacing a chain of `if` statements.

**Verify**: adding a new type requires adding a binding, not editing a switch.

---

## Exercise 4: Fan-Out / Fan-In (M)

Run `n` items through a stage concurrently with bounded concurrency; aggregate results
and failures.

**Verify**: partial failure rate reported; the aggregate policy is honoured.

---

## Exercise 5: Bounded Executor and Backpressure (M)

Implement per-stage concurrency and queue limits with rejection.

**Verify**: queue depth never exceeds the limit; rejection is counted, not swallowed.

---

## Exercise 6: Stage Cache (E)

Cache keyed by `(stage, inputHash, configHash)`. Verify invalidation on a config change.

---

## Exercise 7: Idempotency and Retry (H)

Verify retries only occur for idempotent stages; a non-idempotent failure is not retried.

---

## Exercise 8: Timeout Enforcement (M)

Per-stage timeout with a virtual clock; verify a slow stage fails without blocking
others.

---

## Exercise 9: Per-Stage Metrics (M)

Latency percentiles, error counts by class, throughput, cache hit rate, sizes.

**Verify**: `sum(stage latencies)` is within tolerance of total; the bottleneck is
identifiable.

---

## Exercise 10: DAG Execution (H)

Build a DAG with parallel branches; compute the critical path; verify total latency
follows it.

---

## Exercise 11: Saga with Compensation (H)

Two write stages where the second can fail; implement compensation for the first.

**Verify**: after a failure the system is in the pre-run state.

---

## Exercise 12: PipelineSpec and Versioning (M)

Compute a pipeline spec hash from stage names, versions, and config hashes. Verify a
config change changes it and invalidates downstream caches.

---

## Exercise 13: Property-Based Tests (M)

Invariants: no null outputs, bounded sizes, no PII patterns in emitted records. Run
over generated inputs.

---

## Exercise 14: Golden Tests (M)

Record input/output pairs for 20 cases; detect unintended behaviour changes.

---

## Exercise 15: Bottleneck Analysis (H)

Given per-stage metrics, compute utilization and identify the bottleneck; propose
concurrency or batching changes and predict the effect.

---

## Stretch A: Streaming Pipeline (H)

Emit results as they complete instead of at the end; measure time-to-first-result.

---

## Stretch B: Checkpointing (H)

Checkpoint mid-pipeline; resume without re-running completed stages.

---

## Stretch C: Adaptive Concurrency (H)

Adjust per-stage concurrency from observed latency and queue depth; report the
stability.

---

## Stretch D: Pipeline Diffing (M)

Given two `PipelineSpec`s, report which stages changed and predict the impact.

---

## Stretch E: Backpressure Strategies (M)

Compare reject, block, and shed strategies under overload; report goodput.

---

## Stretch F: Nested Pipelines (M)

Compose a sub-pipeline as a stage; verify metrics and errors propagate with context.

---

## Stretch G: Deterministic Replay (H)

Record the clock, seeds, and config; replay a run and verify byte-identical outputs.

---

## Stretch H: Circuit Breaker Per Stage (H)

Open a stage's breaker on sustained failures; verify fallbacks and recovery.