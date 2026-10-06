# Lab 06: AI Pipeline Orchestration — Mini Project

## Project: Pipeline Framework with Metrics, Caching, and DAG Execution

Build a pipeline orchestration framework in Java 21 — typed stages, error policies,
bounded executors, caching, DAG execution with critical-path analysis, sagas, metrics
— and then optimize a real pipeline with the measurements it produces.

## Goal

A framework where every stage is testable in isolation, failures follow declared
policies, and the bottleneck is identified by measurement rather than intuition.

## Requirements

### Phase 1: Stage Contract
- [ ] `Stage<I,O>` with version, config hash, policy, timeout, max attempts.
- [ ] `StageResult<T>` with typed `Failure` and a degraded flag.
- [ ] Six stages of a document-QA pipeline: ingest, validate, chunk, embed, answer,
      emit.

### Phase 2: Error Policies
- [ ] fail / skip / retry / degrade applied to different stages.
- [ ] Fault injection: 10% transient, 5% data, 1% policy failure rates.
- [ ] Verify each stage follows its declared policy.

### Phase 3: Execution
- [ ] Bounded executor with per-stage concurrency and queue limits.
- [ ] Explicit rejection under overload; rejection counted.
- [ ] Per-stage timeouts with a virtual clock.
- [ ] Idempotency guard preventing retries on side-effecting stages.

### Phase 4: Caching
- [ ] Cache keyed by `(stage, version, configHash, inputHash)`.
- [ ] Verify invalidation when a config hash changes.
- [ ] Refuse to cache stages declaring clock/randomness use.
- [ ] Per-stage hit rates reported.

### Phase 5: Routing and Parallelism
- [ ] Type-driven router replacing an `if/else` chain.
- [ ] Fan-out/fan-in with partial-failure policies.
- [ ] DAG execution with critical-path computation.
- [ ] Verify parallelism actually overlaps.

### Phase 6: Metrics and Bottleneck Analysis
- [ ] Per-stage latency percentiles, errors, retries, hit rates, sizes.
- [ ] Verify stage latency sum is within tolerance of wall clock.
- [ ] Critical path plus utilization; produce an optimization target list.
- [ ] Make one optimization and measure the predicted vs actual effect.

### Phase 7: Side Effects
- [ ] Saga with two write stages and LIFO compensation.
- [ ] Verify the system returns to its pre-run state on failure.

### Phase 8: Spec and Reproducibility
- [ ] `PipelineSpec` hash and diff between versions.
- [ ] Deterministic replay: record clock, seeds, config; verify identical output.

### Phase 9: Testing
- [ ] Property-based invariants over generated inputs.
- [ ] Golden tests for 20 cases.
- [ ] A deliberately regressed stage caught by the golden tests.

## Directory Layout

```
lab06/
  src/com/aiengineering/lab06/{stage,exec,route,cache,spec,metrics,test}/
  fixtures/golden.json
  out/metrics.json
  out/spec-diff.txt
  Main.java
  REPORT.md
```

## Milestones

1. **M1** — six stages with contracts; unit tested in isolation.
2. **M2** — fault injection; every stage follows its declared policy.
3. **M3** — bounded executor; overload rejected explicitly.
4. **M4** — cache with config-hash invalidation; hit rates reported.
5. **M5** — type router; adding a type needs no switch edit.
6. **M6** — DAG critical path; parallelism verified.
7. **M7** — metrics sum verified against wall clock.
8. **M8** — bottleneck identified; one optimization measured.
9. **M9** — saga compensation verified.
10. **M10** — deterministic replay byte-identical.
11. **M11** — property and golden tests; regressed stage caught.
12. **M12** — report written.

## Acceptance Criteria

- [ ] Each stage runs standalone with no pipeline present.
- [ ] Fault injection matches the declared policy per stage class.
- [ ] Non-idempotent stages never retried.
- [ ] Queue depth never exceeds its limit; rejections counted.
- [ ] A config change invalidates downstream caches with no manual clear.
- [ ] Clock/randomness stages never cached.
- [ ] Critical path computed; off-path optimization provably changes nothing.
- [ ] Stage latency sum within 10% of wall clock.
- [ ] Optimization improves throughput as predicted.
- [ ] Saga leaves no partial state after a mid-run failure.
- [ ] Replay produces byte-identical output.
- [ ] Golden tests catch a deliberately regressed stage.

## Stretch Goals

- [ ] Adaptive concurrency from observed latency and queue depth.
- [ ] Streaming mode with time-to-first-result measurement.
- [ ] Checkpoint and resume mid-pipeline.
- [ ] Circuit breaker per stage with fallback.
- [ ] Nested sub-pipeline as a stage.
- [ ] Cost attribution per stage.
- [ ] Shape-drift alert on stage output sizes.
- [ ] Canary one stage and measure the delta.

## Failure Modes to Watch For

| Symptom | Likely cause |
|---------|--------------|
| Stage silently skipped | Error policy too lenient; failures not typed |
| Memory growth under load | Unbounded queue; no backpressure |
| Stale results after a config change | Missing configHash in the cache key |
| Duplicate side effects | Retry on a non-idempotent stage |
| Flaky tests | Hidden clocks or randomness in stages |
| Optimization had no effect | Optimized an off-critical-path branch |
| Metrics look free | A stage without instrumentation |
| Nondeterministic replay | Seed or clock not recorded |
| Partial state after failure | Saga without compensation |

## Definition of Done

`REPORT.md` contains: the pipeline anatomy diagram, the stage contract table, the error
policy matrix with fault-injection results, executor behaviour under overload, the cache
hit rates and invalidation test, the DAG critical-path analysis, the bottleneck report,
the optimization with predicted versus actual effect, the saga compensation evidence,
the pipeline spec diff, the deterministic replay verification, the property and golden
test results, and a "what we would add next" section.