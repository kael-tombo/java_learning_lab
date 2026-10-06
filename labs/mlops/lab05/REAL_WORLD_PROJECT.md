# REAL_WORLD_PROJECT — Real-Time Scoring Service at Peak

**Track:** mlops  |  **Lab:** lab05  |  **Level:** Intermediate

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

A fintech risk service scores 9,000 authorisations per second at peak with a p99 budget of 35 ms end to end, including features. Quarterly campaign peaks are 4x normal, and last Black Friday the service was OOMKilled twice.

**You are the on-call engineer.** The system below is the one you inherit, not a greenfield toy - the interesting work is in the seams.

## 2. Numbers That Matter

| Quantity | Value |
|---|---|
| Traffic | steady 1,800/s, peak 9,000/s during campaigns, 4x spikes |
| Latency budget | p99 < 35 ms end to end including feature fetch |
| Fleet | 60 pods, 2 CPU / 1.5 GiB each, autoscaled 30–120 |
| Model | gradient-boosted fraud model plus a rules engine in front |
| Failure history | 2 OOMKills at peak, cold starts visible as 900 ms p99 spikes |

## 3. Target Architecture

```text
  gateway -> rules engine (fast path)
                 |
          model server pods (HPA on queue depth)
                 |
        +--------+---------+------------------+
        |         |         |                  |
   features   model    batch queue       shadow scorer
   (online)  (hot)   (bounded, window)   (challenger)
        |         |         |
        +---------+---------+
                  |
       decision log (score, version, features)
                  |
        metrics: latency, queue depth, RSS, warm state

  rollout: canary 5% -> 25% -> 100%, rollback on guardrail breach
  campaigns: pre-scale + warm pool, verified by a load drill
```

## 4. Component Responsibilities

### 4.1 Image and JVM configuration

- Multi-stage image with a pinned JRE base by digest, under 150 MB
- MaxRAMPercentage set so RSS stays inside the 1.5 GiB limit with headroom
- Heap dumps on OOM and container event capture for evidence
- Image digest recorded with every deployment for provenance

### 4.2 Serving path and batching

- Rules engine as a fast path so most traffic never touches the model
- Bounded batch queue with a window sized from the 35 ms budget
- p99 measured end to end including feature fetch, not just inference
- Batching tuned per campaign based on observed queue depth

### 4.3 Warm-up, health and scaling

- Readiness gated on warm-up so pods never serve cold latency
- Liveness that is a constant-time response, never touching the model
- Autoscaling on queue depth as well as CPU, since inference is bursty
- Pre-warmed pool for known campaigns with a load drill beforehand

### 4.4 Rollout and rollback

- Canary rollout at 5/25/100 with guardrails on error rate and p99
- Automated rollback on guardrail breach; model version from the registry
- Decision log recording score, model version and feature versions
- Post-campaign review comparing projected versus actual peak behaviour

## 5. Delivery Timeline

| When | Milestone |
|---|---|
| Week 1-2 | Multi-stage image, container-aware JVM, readiness gated on warm-up; eliminate OOMKill under a 3x load drill |
| Week 3 | Batching with a budget-derived window; end-to-end p99 measured and reported |
| Week 4 | Autoscaling on queue depth; pre-warm pool and a campaign load drill |
| Week 5-6 | Canary rollout and automated rollback from the registry; drill it under load |
| Week 8 | Post-campaign review; document the capacity model |

## 6. Runbook (copy-paste)

```bash
# Serving health: version, warm state, queue depth
curl -s localhost:8080/health | jq '{modelVersion,warm,queueDepth,p99}'

# End-to-end latency percentiles including features
curl -s 'localhost:8080/metrics/latency?window=5m' | jq '.p50,.p95,.p99'

# Memory breakdown per pod (heap is not the whole story)
curl -s 'localhost:8080/metrics/memory' | jq '{heap,metaspace,stacks,direct,rss}'

# Roll back to the previous model version
curl -XPOST localhost:8080/admin/rollback -d '{"to":"fraud-gb-v18"}'

# Scale for an announced campaign and pre-warm
curl -XPOST localhost:8080/admin/prescale -d '{"peakQps":9000,"warmSeconds":600}'
```

## 7. Observability and SLOs

- SLO: p99 end-to-end < 35 ms at 9,000 QPS; availability 99.99%.
- Reliability: zero OOMKills; zero cold-start latency spikes in dashboards.
- Throughput: sustained QPS per pod at p99 budget, tracked as capacity.
- Safety: rollback time under 5 minutes, exercised at least quarterly.
- Business: fraud loss basis points, to confirm latency work did not cost accuracy.

## 8. Failure Modes and the Rollback Plan

| Failure | Detection | Response |
|---|---|---|
| OOMKilled pods during a campaign peak | Heap set close to the container limit | Pre-scale, reduce MaxRAMPercentage, and alert on RSS not heap |
| p99 spikes to 900 ms right after each deploy | Traffic hitting un-warmed pods | Readiness gated on warm-up; verify readiness probe failure count |
| Autoscaler scales on CPU and lags behind the burst | Inference is bursty and CPU lags | Scale on queue depth and p99; add pre-warm for known campaigns |
| Rules engine fallback rate spikes after a model rollback | Rollback to an older model with different score scale | Version the threshold with the model; verify calibration after rollback |
| Batch window too large under peak | Fixed window tuned for average traffic | Tune per campaign from observed p99; keep the window a config value |

## 9. Prevention Backlog

- Shadow scorer for the challenger model on a traffic slice, wired to the registry.
- Adaptive batch window driven by observed latency and queue depth.
- Load drill script run before every major campaign with a capacity report.
- Disaggregated latency (features vs inference vs queue) in the dashboard.
- Quarterly rollback drill under synthetic load with measured time-to-safe.

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

> The deliverable is 9,000 QPS inside a 35 ms budget with no OOMKills, no cold-start spikes, and a rollback that has been drilled under load rather than assumed.
