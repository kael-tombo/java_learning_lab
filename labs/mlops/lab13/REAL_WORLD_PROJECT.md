# REAL_WORLD_PROJECT — Training Platform Throughput Recovery

**Track:** mlops  |  **Lab:** lab13  |  **Level:** Advanced

> Companion notes to the runnable lab. Everything here is grounded in the source under `src/`, so a claim you cannot reproduce is a claim you do not ship.

| Doc | Read it when you want |
|---|---|
| `THEORY.md` | the mental model and the assumptions |
| `MATH_FOUNDATION.md` | the formulas, the derivations, the numerical traps |
| `CODE_DEEP_DIVE.md` | the Java implementation, line by line |
| `EXERCISES.md` | deliberate practice, one deliverable at a time |
| `QUIZ.md` | to find the gaps before an interview |
| `FLASHCARDS.md` | spaced repetition on the day before a review |
| `VISION.md` | the career-level context and the anti-patterns to avoid |
| `MINI_PROJECT.md` | a self-contained build you finish in one sitting |
| `REAL_WORLD_PROJECT.md` | the production system, on-call runbook included |

## 1. Scenario

A recommendation team grew from 4 to 32 GPUs and training time went from 40 minutes to 3 hours. Nobody can say which of the four candidate models to use, and the cluster is oversubscribed by experiments nobody can attribute.

**You are the on-call engineer.** The system below is the one you inherit, not a greenfield toy - the interesting work is in the seams.

## 2. Numbers That Matter

| Quantity | Value |
|---|---|
| Fleet | 32 accelerators across 3 nodes, shared by 2 teams |
| Baseline | 4 devices: 40 minutes per full training run |
| Now | 32 devices: 3 hours per run, with no accuracy loss yet proven |
| Models | 4 candidates in an internal bake-off |
| Constraint | weekly release depends on a trained candidate by Wednesday |

## 3. Target Architecture

```text
 single-device profile per candidate (compute vs comm)
     |
 arithmetic intensity + all-reduce volume per step
     |
 +---+---+--------+-----------+
 |           |        |           |
 data      model    pipeline   mixed precision
 parallel parallel  + overlap   + ZeRO
     |           |        |           |
     +-----+-----+--------+-----------+
                 |
      device-count sweep: speedup, efficiency, comm ratio
                 |
        recommended config per candidate + capacity model
                 |
   quota per team + cost per run + effective batch contract
```

## 4. Component Responsibilities

### 4.1 Baseline profiling

- Per-candidate single-device profile: step time, memory, arithmetic intensity
- Measured interconnect bandwidth between nodes, not the vendor number
- Memory budget for all four terms per candidate
- Baseline loss curve in fp32 as the correctness reference for every optimisation

### 4.2 Parallelism experiments

- Device-count sweep per candidate reporting speedup, efficiency and comm ratio
- Pipeline schedule with microbatch sweep and measured bubble ratio
- All-reduce overlap implemented and the hidden fraction reported
- Mixed precision and optimiser sharding validated against the fp32 baseline

### 4.3 Capacity and attribution

- Per-team quota and priority so a bake-off cannot starve the release path
- Cost per run computed from measured device-hours, attributed by team
- Idle detection on quota, with reserved capacity for the weekly release
- Effective batch contract validated at startup so runs stay comparable

### 4.4 Release discipline

- One recommended configuration per candidate, chosen by the numbers
- Weekly release path reserved with a fixed schedule and priority
- Bake-off results published with speedup, efficiency and convergence
- Runbook covering regression on loss curve or throughput

## 5. Delivery Timeline

| When | Milestone |
|---|---|
| Week 1 | Baseline profiling per candidate plus measured interconnect bandwidth |
| Week 2 | Device-count sweep with speedup, efficiency and communication ratio |
| Week 3-4 | Pipeline scheduling, all-reduce overlap, mixed precision and sharding, each validated |
| Week 5 | Per-team quota, priority and cost attribution; reserve the release path |
| Week 6 | Publish the recommended configuration per candidate; re-measure the weekly release |

## 6. Runbook (copy-paste)

```bash
# Single-device profile per candidate
curl -s localhost:8080/train/profile?candidate=dlrm | jq '{stepMs,flops,bytesMoved,intensity}'

# Device-count sweep with efficiency and comm ratio
curl -s 'localhost:8080/train/sweep?candidate=dlrm' | jq '.[] | {devices,speedup,efficiency,commRatio}'

# Effective batch validation at run start
curl -s 'localhost:8080/train/config?runId=r-221' | jq '{devices,microBatch,gradAccum,effectiveBatch,dtype}'

# Queue state per team on the shared pool
curl -s 'localhost:8080/train/queue' | jq '.[] | {team,quota,used,pending,priority}'

# Reserve the release path for the weekly window
curl -XPOST localhost:8080/train/reserve -d '{"team":"recsys","window":"wed-06-to-wed-14"}'
```

## 7. Observability and SLOs

- Throughput: step time per candidate per device count, with efficiency and comm ratio.
- Correctness: loss curves match the fp32 baseline within a stated tolerance for every optimised configuration.
- Capacity: release path completes within its window every week.
- Fairness: per-team queue wait time, with the release path exempt and visible.
- Cost: device-hours and cost per run attributed by team.

## 8. Failure Modes and the Rollback Plan

| Failure | Detection | Response |
|---|---|---|
| Scaling out makes training slower | Communication dominates for these candidates | Report the comm ratio; revert to fewer devices or overlap the reduce |
| Mixed precision diverges in one candidate | Unstable loss scale | Use dynamic loss scaling; keep fp32 as the baseline and block promotion on divergence |
| A bake-off starves the release path | No reservation or priority | Reserve the release window with a fixed priority and alert when the queue exceeds a threshold |
| Effective batch differs between the bake-off and the release run | Accumulation settings differ | Validate the effective batch at startup and fail fast on mismatch |
| Nobody can attribute GPU cost | No team tags or measurement | Attribute device-hours per run and publish per-team cost |

## 9. Prevention Backlog

- Sequence-parallel attention for long-context candidates.
- Automated regression comparing each optimised run against the fp32 loss baseline.
- Per-model capacity models derived from measured efficiency curves.
- Spot and reserved capacity mix driven by the weekly release cadence.
- Expert parallelism evaluation for mixture-of-experts candidates.

## 10. Postmortem Outline (skeleton)

1. **Impact** - who was hurt, for how long, in which numbers.
2. **Timeline** - detection, diagnosis, mitigation, resolution (UTC).
3. **Detection gap** - which signal should have fired first?
4. **Root cause** - the mechanism, not the person.
5. **What went well** - the thing that shortened the incident.
6. **Action items** - owner, date, and the alert or test that proves each one.

## 11. Sourced field notes (fetched Oct 2026 — verify before citing)

- **MLflow — Tracking and Model Registry documentation**: https://mlflow.org/docs/latest/ml/tracking/
  Reference model for experiment/run/metric lineage and the registry lifecycle (the vocabulary this lab re-implements in Java).
- **Kubernetes — ConfigMaps and Secrets**: https://kubernetes.io/docs/concepts/configuration/configmap/
  How configuration is injected into scheduled workloads — the practical lineage story for a DAG run that must be reproducible months later.
- **DVC — data and model versioning**: https://dvc.org/doc/user-guide
  Content-addressed versioning of datasets and model binaries; the standard way to make a data snapshot referenceable in a run record.

> The deliverable is a bake-off that concludes with a recommended configuration per candidate, a release path that always finishes, and a team that can explain why 32 GPUs were slower than 4.
