# Lab 06: AI Pipeline Orchestration — Real-World Project

## Project: Production Data and Inference Pipeline Platform

Design and build the orchestration layer that runs a company's AI data and inference
pipelines: typed stages with declared contracts, bounded execution, caching,
observability, versioning, backfills, and operational ownership.

## Context

Pipelines are where AI systems become reliable — or where a silent data bug becomes a
six-month incident nobody can trace. The framework's job is to make every stage
inspectable, versioned, and independently testable.

## Sourced field notes (fetched Oct 2026 — verify before citing)

- "Hidden Technical Debt in Machine Learning Systems" (Sculley et al., submitted 12 Mar
  2015) — https://arxiv.org/abs/1503.05638 — takeaway for this lab: configuration,
  data collection, feature extraction, and serving skew are distinct debt classes, and
  each needs its own versioned artifact and monitoring — the structure this platform
  enforces with stage configs, data lineage, and `PipelineSpec` records.
- "Data Cascades in High-Stakes AI" (Sambasivan et al., submitted 21 Nov 2021) —
  https://arxiv.org/abs/2011.13515 — takeaway for this lab: upstream collection and
  annotation decisions cascade into every downstream prediction, which is why this
  platform versions upstream data contracts and monitors their downstream effects
  rather than treating data quality as a one-time ingestion concern.

## System Architecture

```
   SOURCES (uploads | db views | api | streams | manual)
        |
   +----v----------------------------------------------------------------+
   |  SCHEDULER / TRIGGER PLANE                                         |
   |  cron | webhook | queue | backfill | manual | DAG dependencies      |
   +----+----------------------------------------------------------------+
        |
   +----v----------------------------------------------------------------+
   |  EXECUTION PLANE                                                   |
   |  +-----------+   +-----------+   +-----------+   +--------------+ |
   |  | ingest    |-->| validate  |-->| transform |-->| features     | |
   |  | immutable |   | schema    |   | determin. |   | determin.    | |
   |  +-----------+   +-----------+   +-----------+   +------+-------+ |
   |  bounded concurrency | per-stage queue limit | backpressure        |
   |  error policy per stage | retries on idempotent only                 |
   |  timeout per stage | circuit breaker per stage                      |
   |  +-----------+                            +--------------+          |
   |  | embed     |---------------------------->| infer        |          |
   |  | cacheable |   (parallel branch)          | batched      |          |
   |  +-----------+                            +------+-------+          |
   |                                                 |                  |
   |  +-----------+   +-----------+                  |                  |
   |  | emit      |<--| post      |<-----------------+                 |
   |  | validate  |   | process   |                                        |
   |  +-----------+   +-----------+                                        |
   +----+----------------------------------------------------------------+
        |
   +----v----------------------------------------------------------------+
   |  CROSS-CUTTING                                                      |
   |  StageCache (stage,version,configHash,inputHash)                   |
   |  StageMetrics | PipelineSpec | DeadLetter | Lineage | Cost          |
   +----+----------------------------------------------------------------+
        |
   +----v----------------------------------------------------------------+
   |  OPERATIONS                                                         |
   |  dashboards | alerts | backfill tooling | incident runbooks         |
   +---------------------------------------------------------------------+
```

## Component Specs

### 1. Trigger Plane
- Triggers: cron, webhook, queue, manual, DAG dependency, and **backfill** (reprocess a
  date range after a code change).
- Idempotent triggers: a repeated fire for the same window is a no-op, keyed by
  `(pipeline, window)`.
- Concurrency per pipeline: no two runs for the same partition overlap.
- Backpressure: a full queue delays triggers rather than dropping them, and the delay
  is alerted.

### 2. Stage Contracts
Every stage declares:
```
inputs / outputs (typed) | version | configHash | error policy per failure class
timeout | max attempts | idempotent flag | cacheable flag | cost model
```
- Failures are typed: `TRANSIENT`, `DATA`, `POLICY`, `PERMANENT`, `SCHEMA`.
- Policy per class: transient retries, data degrades, policy/permanent fail.
- Side-effecting stages declare non-idempotent and are never silently retried; they
  verify state or use idempotency keys.

### 3. Execution Plane
- Per-stage bounded concurrency and queue depth; explicit rejection and alerting.
- Per-stage thread pool so a stuck stage cannot starve the pipeline.
- Timeouts with interruption of the stage's pool.
- Circuit breakers per stage: sustained failure opens the breaker, the pipeline falls
  back or fails fast, and the alert fires.
- **Global retry budget**: a shared token bucket so retries during an incident cannot
  amplify load across stages.
- Dead-letter queue for items no policy can handle, with replay tooling.

### 4. Caching
- Key: `(stageName, version, configHash, inputHash)`.
- Config-hash changes invalidate the stage and everything downstream automatically.
- Never cache stages declaring clock or randomness use, unless a seed is part of the
  input.
- Hit rate monitored per stage; a 0% hit rate on an expensive deterministic stage is an
  alert.
- Cache sizing bounded with eviction; eviction does not invalidate correctness.

### 5. Parallelism and Composition
- Parallel branches join on completion; the critical path is computed and reported.
- Sub-pipelines are stages with their own metrics; errors carry stage context.
- Fan-out/fan-in with a declared partial-failure policy per join.
- Sagas for multi-step writes with LIFO compensation.

### 6. Versioning and Lineage
- `PipelineSpec` = schema version + per-stage name, version, config hash. Recorded with
  every output and diffable between runs.
- Data contracts versioned upstream: schema, semantics, and expected distributions.
- Lineage: each output record carries the input ids and the spec hash that produced it.
- Backfill runs carry the **new** spec and produce new outputs alongside old ones.

### 7. Observability
Per stage: latency percentiles, error counts by class, retries, suppressed retries,
cache hits, items in/out, queue depth, rejections, cost.
Per pipeline: wall-clock versus the sum of stage times (an instrumentation sanity check),
success rate, freshness of the latest successful run, backlog age.
Alerts: stage error rate, retry storm (global budget consumption), queue depth,
freshness breach, dead-letter growth, cost anomaly, a pipeline whose spec changed without
a changelog entry.

### 8. Cost Attribution
- Compute cost per stage, tokens per stage, and external API calls per stage.
- Cost per produced record and cost per downstream inference.
- The stage with the largest share is the optimization target; frequently the boring
  one (re-embedding after a config change).

### 9. Testing
- Unit tests per stage with hand-built inputs; stages must be pure enough to need no
  mocks.
- Property tests for invariants: no nulls, bounded sizes, no PII in outputs, schema
  conformance.
- Golden tests per stage, with a regression suite that catches unintended changes.
- Integration test of the whole pipeline on a fixed corpus.
- Chaos: stage timeouts, downstream 5xx, malformed records, clock skew.

### 10. Operations
- Dashboards per pipeline and per stage.
- Runbooks: freshness breach, stage error spike, retry storm, dead-letter growth,
  cost anomaly, backfill overruns.
- Ownership: one team per pipeline; one oncall rotation for the execution plane.
- Change management: stage version bumps go through review with a changelog and a
  backfill plan.

## Non-Functional Targets

| Metric | Target |
|--------|--------|
| Pipeline success rate | >= 99% (excluding upstream outages) |
| Freshness of the latest run | Within the declared SLA per pipeline |
| Stage latency sum vs wall clock | Within 10% |
| Retry amplification during incidents | <= 1.2x |
| Dead-letter rate | < 0.1% |
| Pipeline replay determinism | Byte-identical for pure stages |
| Cost attribution completeness | 100% of stages |
| Alert time-to-detect | < 15 min |
| Time-to-contain (drill) | < 60 min |
| Backfill throughput | >= 5x realtime for bulk stages |

## Failure Modes and Mitigations

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| Silent data corruption | Property/golden tests | Schema + property invariants per stage |
| Unbounded queue growth | Queue depth alert | Bounded executors, backpressure |
| Retry storm | Global retry budget metric | Shared budget, jitter, breakers |
| Cache staleness | Hit-rate collapse alert | configHash in key |
| Off-path optimization | Latency unchanged | Critical-path reporting |
| Stale pipeline output | Freshness alert | Freshness SLA per pipeline |
| Backfill overwrites live data | Lineage check | Write to a new version namespace |
| Dead-letter growth | DLQ depth alert | Replay tooling plus a schema fix |
| Cost anomaly | Per-stage cost alert | Attribution at stage granularity |
| Config change without a changelog | Spec diff alert | Review gate on version bumps |
| Upstream contract change | Distribution shift monitor | Versioned data contracts |
| Duplicate side effects | Idempotency key log | Verify state before retry |
| Unattributed latency | Stage metrics present from day one | Instrumentation is a launch requirement |

## Milestones

- **M1** — stage contract framework and six production stages.
- **M2** — execution plane with bounded executors, timeouts, breakers.
- **M3** — typed failures and per-stage error policies; fault-injection suite.
- **M4** — global retry budget and backpressure.
- **M5** — stage cache with config-hash invalidation; hit-rate alerting.
- **M6** — DAG execution, critical path, sagas.
- **M7** — `PipelineSpec`, diffing, lineage records.
- **M8** — observability dashboards and alerts; instrumentation sanity check.
- **M9** — cost attribution per stage.
- **M10** — backfill tooling with namespace isolation.
- **M11** — chaos suite.
- **M12** — runbooks and first drill.

## Deliverables

1. Orchestration framework and pipeline definitions.
2. Execution plane with policies, breakers, and budgets.
3. Caching, spec versioning, and lineage.
4. Dashboards, alerts, runbooks.
5. `REPORT.md` — critical path analysis, bottleneck report, cost attribution, SLOs.
6. `PIPELINE_RUNBOOK.md` — triage per alert class.

## Definition of Done

- [ ] All stage latency sums within 10% of wall clock across production pipelines.
- [ ] Retry amplification during a chaos test <= 1.2x.
- [ ] A config change invalidates caches with no manual operation.
- [ ] Dead-lettered items replayable.
- [ ] Backfill produces new versions without overwriting live data.
- [ ] Cost attributed to 100% of stages.
- [ ] A freshness breach detected by alert before a user reported it.
- [ ] Drill exercises time-to-detect and time-to-contain within targets.