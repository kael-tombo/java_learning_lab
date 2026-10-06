# Lab 06: AI Pipeline Orchestration — Theory

## 1. What a Pipeline Is

An AI pipeline is a chain of typed stages with an execution contract:

```
ingest -> validate -> transform -> feature -> infer -> post-process -> emit
```

Each stage declares its inputs, outputs, failure modes, latency, and cost. That
declaration is what makes the chain debuggable, testable, and swappable.

## 2. The Stage Contract

```java
interface Stage<I, O> {
    String name();
    O run(I input, StageContext ctx) throws StageException;
    default void validate(O output) {}                 // stage-local invariants
}
```

- **Typed in and out**: `Stage<String, List<Chunk>>`, not `Stage<Object, Object>`.
- **Errors as typed values**: a stage returns a `StageResult<T>` with a failure
  classification rather than throwing.
- **Pure where possible**: no hidden I/O, no clocks, no randomness. Then tests need no
  mocks.
- **Idempotent** where possible so retries are safe.

## 3. Composition Patterns

| Pattern | When | Trade-off |
|---------|------|-----------|
| Linear chain | Fixed sequence | Simple; no branching |
| DAG | Dependencies, parallel branches | Needs a scheduler |
| Fan-out/fan-in | Independent work, aggregate | Partial failures |
| Map-reduce | Many items, one answer | Two phases |
| Conditional branch | Type-based routing | Requires routing logic |
| Saga | Multi-step writes with compensation | Complex; needed for side effects |

**Type-driven dispatch** beats `if (type.equals(...))` chains: define the input type
each stage accepts and let the router select on it. Adding a stage becomes adding a
binding, not editing a switch.

## 4. Execution Contracts

Three things must be decided per stage:

1. **Error policy**: fail, skip, retry, or continue with a degraded value. Different
   stages need different answers — a parse failure in post-processing is recoverable; a
   missing model is not.
2. **Timeout and retry**: bounded, with jitter; only idempotent stages retry.
3. **Partial results**: does a 10% failure rate mean the pipeline fails, or emit the 90%?

Deciding these once, declaratively, prevents per-implementation improvisation.

## 5. Parallelism and Backpressure

Stages have different parallelism characteristics. A transformation is embarrassingly
parallel; an inference stage is bounded by model capacity. The pipeline needs a
bounded executor with per-stage limits:

```java
record StageLimits(int maxConcurrency, int queueDepth, boolean idempotent) {}
```

Unbounded queues are the failure mode: a slow downstream stage turns into unbounded
upstream memory growth and then an OOM. Backpressure (reject or block) must be explicit.

## 6. Caching

Cache per stage, keyed by `(stageName, inputHash, configHash)`:

- Deterministic stages (transform, embed) cache perfectly.
- Non-deterministic ones (sampling, "creative" transforms) must not cache, or must cache
  the seed.
- Cache invalidation flows from upstream: a config change bumps `configHash`, invalidating
  everything downstream automatically.
- Report hit rate per stage; a 0% hit rate on an expensive stage is a bug.

## 7. Observability

Per-stage, per-run:

```
stage latency (p50/p95/p99), error count by class, throughput,
cache hit rate, input/output sizes, downstream rejection count
```

The critical derived metric is **bottleneck attribution**: which stage consumes the
budget. Almost always the answer is "the one nobody instrumented", because stages
without metrics look free.

## 8. Testing Stages

Because stages are pure and typed, testing is cheap:

- Unit: each stage in isolation with hand-built inputs.
- Property: invariants that must hold for all inputs (no `null` outputs, sizes bounded,
  no PII in outputs).
- Golden: recorded input/output pairs to catch unintended behaviour changes.
- Contract: the consumer's expectations about the producer's output.

## 9. Versioning the Pipeline

The pipeline itself is an artifact:

```
PipelineSpec {
  stages: [name, version, configHash]
  schemaVersion
  modelVersions
  indexVersions
}
```

A change to any stage changes `PipelineSpec`; responses record it, so a quality drop is
attributable to a stage rather than to "the system".

## 10. Failure Modes

| Failure | Symptom | Cause | Fix |
|---------|---------|-------|-----|
| Silent stage skip | Missing fields downstream | Error policy too lenient | Typed failures, no silent skips |
| Unbounded queue | Memory growth under load | No backpressure | Bounded executors |
| Cache staleness | Wrong results after a config change | Missing configHash in the key | Include configHash |
| Retry storm | Load multiplies | Retrying non-idempotent stages | Retry only idempotent |
| Nondeterminism in tests | Flaky failures | Hidden clocks/randomness | Inject clocks and seeds |
| Monolith stage | One slow change blocks everything | No stage boundaries | Split by responsibility |
| Unattributed latency | Nobody knows the bottleneck | Missing per-stage metrics | Instrument every stage |
| Version drift | Quality change, no changelog | Unversioned stage config | `PipelineSpec` in every response |

## 11. Design Rules

1. Every stage declares inputs, outputs, error policy, timeout, retry, and limits.
2. Errors are typed values, classified by recoverability.
3. No unbounded queues; backpressure is explicit.
4. Cache keys include config hashes so invalidation is automatic.
5. Per-stage metrics from day one.
6. `PipelineSpec` recorded with every result.
7. Stages are pure where possible so they can be tested without mocks.

## Key Equations

```
T_total = sum_i T_i  (sequential)  or  sum over critical path (DAG)
throughput = 1 / max_i (T_i / concurrency_i)
cost = sum_i cost_i(in_i, out_i)
cache_hit_rate_i = hits_i / requests_i
p95_total <= sum_i p95_i          (worst case; independence makes it loose)
```