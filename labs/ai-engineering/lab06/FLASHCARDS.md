# Lab 06: AI Pipeline Orchestration — Flashcards

| # | Front | Back |
|---|-------|------|
| 1 | Pipeline | Chain of typed stages with an execution contract |
| 2 | Stage contract | Inputs, outputs, error policy, timeout, retry, limits |
| 3 | Typed interfaces | Compile-time wiring safety |
| 4 | Errors as values | Typed failures enable per-stage policy |
| 5 | Recoverability classes | Transient, permanent, data, policy |
| 6 | Pure stages | No hidden clock/randomness/I/O; testable without mocks |
| 7 | Idempotent stages | Safe to retry |
| 8 | Linear chain | Fixed sequence |
| 9 | DAG | Dependencies, parallel branches |
| 10 | Fan-out/fan-in | Independent work, aggregate |
| 11 | Map-reduce | Many items, one answer |
| 12 | Saga | Side effects with compensation |
| 13 | Type-driven routing | Adding a stage = adding a binding |
| 14 | Error policies | fail / skip / retry / degrade |
| 15 | Policy per stage | Parse errors recoverable; missing model not |
| 16 | Partial results | Declared aggregate policy |
| 17 | Bounded concurrency | Prevents unbounded memory |
| 18 | Queue depth limit | Explicit rejection |
| 19 | Backpressure | Reject or block explicitly |
| 20 | Unbounded queue | OOM waiting to happen |
| 21 | Cache key | `(stage, inputHash, configHash)` |
| 22 | configHash | Automatic downstream invalidation |
| 23 | Non-deterministic stage | Do not cache, or cache the seed |
| 24 | Per-stage metrics | Latency, errors, throughput, hit rate, sizes |
| 25 | Bottleneck attribution | Who consumes the budget |
| 26 | Uninstrumented stage | Looks free; hides the bottleneck |
| 27 | sum vs wall clock | Verify instrumentation accuracy |
| 28 | Unit test | One stage, hand-built input |
| 29 | Property test | Invariants over generated inputs |
| 30 | Invariants | No nulls, bounded sizes, no PII |
| 31 | Golden test | Recorded input/output regression |
| 32 | Contract test | Consumer expectations of producer |
| 33 | PipelineSpec | Stage names, versions, config hashes |
| 34 | Spec hash | Attribute change to a stage |
| 35 | Critical path | DAG latency bound |
| 36 | Throughput | `1 / max(T_i / concurrency_i)` |
| 37 | Concurrency scaling | Helps only off the critical path |
| 38 | Streaming | Earlier first result, same cost |
| 39 | Checkpointing | Resume without redoing completed stages |
| 40 | Circuit breaker | Stop hammering a failing stage |
| 41 | Deterministic replay | Inputs + config + seeds + clocks |
| 42 | Virtual clock | Timeout tests without sleeping |
| 43 | Nested pipeline | Sub-pipeline as a stage; errors carry context |
| 44 | Cost model | Sum of per-stage costs |
| 45 | Token accounting | Per stage, not just per request |
| 46 | Shape drift | A stage silently changing output size |
| 47 | Schema versioning | Consumers tolerate changes |
| 48 | Null propagation | One null can kill a whole chain |
| 49 | Failure isolation | A stage failure must not corrupt shared state |
| 50 | Dead letter | Unprocessable items routed aside |
| 51 | Idempotency key | Dedupe retries of side effects |
| 52 | Stage ordering | Dependencies respected, not just listed |
| 53 | Config change blast | Invalidation cascade is a feature |
| 54 | Canary a stage | Swap one stage, measure the delta |
| 55 | Shadow a stage | Run both, compare outputs |
| 56 | Feature flag | Kill a stage without a deploy |
| 57 | Backfill | Reprocess historical inputs after a change |
| 58 | Data validation gate | Reject bad inputs early |
| 59 | Distribution shift alert | Input shape changes mid-flight |
| 60 | Ownership | One team per stage; one oncall for the pipeline |

## Self-Check

55+ = solid, 45-54 = redo Exercises 4 and 9, below that reread THEORY 1-8.