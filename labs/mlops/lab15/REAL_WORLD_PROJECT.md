# REAL_WORLD_PROJECT — Recommendation Platform Architecture Overhaul

**Track:** mlops  |  **Lab:** lab15  |  **Level:** Advanced

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

A commerce platform serves 40M sessions a day from a recommendation service. During a Black Friday incident the feature store went down and scoring failed for 22 minutes, because no degradation path existed beyond an error page.

**You are the on-call engineer.** The system below is the one you inherit, not a greenfield toy - the interesting work is in the seams.

## 2. Numbers That Matter

| Quantity | Value |
|---|---|
| Traffic | 40M sessions/day, peak 12k QPS on the recommendation path |
| SLO | p99 < 120 ms per recommendation slot; availability 99.95% |
| Incident | 22-minute scoring outage from a feature store dependency |
| Architecture today | single service, hard dependency on feature store and registry |
| Constraint | no full rewrite; the path is evolved with guardrails |

## 3. Target Architecture

```text
 catalog + events --> ingest --> validate --> featurise --> train --> eval
     |                              (registry)         |
     |                                    |          |
     |                            OFFLINE store        |
     |                                    |          |
     |                            ONLINE store (ttl)  |
     |                                    |          |
 page render --> edge cache --> recommender service ---> model artefact (cached locally)
     |                                 |        |        |
     |                          bulkhead  timeout  degradation ladder
     |                                 |        |        |
     +--> decision log ---------------+--------+--------+
                                        |
        outcomes (orders, clicks) --> feedback path (hours)
                                        |
                         quality + drift --> retrain trigger

  rollout: shadow -> canary 5% -> 25% -> 100%, rollback pre-authorised
```

## 4. Component Responsibilities

### 4.1 Serving path and degradation

- Model artefact cached locally so serving does not depend on the registry at request time
- Feature reads behind a timeout and a bulkhead, with a bounded feature set on the fast path
- Degradation ladder: full model, cached feature subset, baseline model, popular-items, then fail open with a documented banner
- Every rung logged and metered so degraded mode is visible on the dashboard, not inferred

### 4.2 Training and registry paths

- Batch path fully isolated from the serving path, with its own scaling and failure domain
- Promotion through the registry gate with shadow evaluation on a traffic slice
- Model artefacts versioned with feature-view versions for replay and disputes
- Backfill and retrain triggers driven by validated evidence

### 4.3 Feedback path and consistency

- Decision log with prediction id, score, model version and feature versions
- Outcomes joined by id with declared attribution windows for orders and clicks
- Per-interaction consistency policy: profile edits are read-your-writes, browse is eventually consistent
- Deliberate exploration budget so recommendations can learn new preference classes

### 4.4 Rollout, chaos and economics

- Shadow, canary and ramp stages with guardrails on CTR, GMV per session, latency and zero-result rate
- Pre-authorised rollback using the local model cache, with reasons recorded
- Chaos programme testing each dependency edge with measured detection and mitigation
- Unit economics dashboard: cost per 1,000 recommendation slots

## 5. Delivery Timeline

| When | Milestone |
|---|---|
| Week 1-2 | Add local model caching and feature-read timeouts; remove the registry from the hot path |
| Week 3-4 | Build and deploy the degradation ladder; verify each rung and the fail-open behaviour |
| Week 5 | Split the training path from serving scaling; add shadow scoring of a challenger |
| Week 6-7 | Decision log plus feedback join with declared attribution windows |
| Week 8-9 | Chaos programme per dependency edge; pre-authorised rollback drill; economics dashboard |

## 6. Runbook (copy-paste)

```bash
# Serving health: version, warm state, current rung
curl -s localhost:8080/recommender/health | jq '{modelVersion,warm,rung,featureStore}'

# Degradation events and how long each rung was active
curl -s 'localhost:8080/recommender/degradation?window=24h' | jq '.[] | {rung,started,durationSeconds,reason}'

# Latency breakdown per dependency in the read path
curl -s 'localhost:8080/recommender/latency?window=15m' | jq '{features,inference,queue,overhead}'

# Roll back to the previous model version (pre-authorised)
curl -XPOST localhost:8080/recommender/rollback -d '{"to":"recsys-v31","reason":"guardrail:ctr"}'

# Unit economics for the last 7 days
curl -s 'localhost:8080/recommender/economics?window=7d' | jq '{slots,costPerThousand,gmvPerSession}'
```

## 7. Observability and SLOs

- SLO: p99 < 120 ms per slot; availability 99.95%; zero minutes of scoring outage.
- Resilience: maximum time at each degradation rung per month; chaos results per edge.
- Guardrails: CTR, GMV per session, zero-result rate and diversity during every rollout stage.
- Business: GMV per session versus the pre-overhaul period, with intervals.
- Economics: cost per 1,000 slots, tracked against incremental GMV.

## 8. Failure Modes and the Rollback Plan

| Failure | Detection | Response |
|---|---|---|
| Feature store outage causes scoring failures | No degradation path | Move to the cached feature subset rung within the timeout; log and meter the rung |
| A rollout improves CTR but drops GMV per session | Proxy metric optimised in isolation | Guardrails on both; pause the ramp and evaluate jointly |
| Users see stale recommendations after a profile edit | Eventual consistency assumed | Read-your-writes for profile interactions, implemented and verified |
| The model cannot learn a new preference class | Feedback loop with no exploration | Deliberate exploration budget plus shadow scoring of alternatives |
| Black Friday peak exceeds the degradation ladder's traversal time | Detection slower than assumed | Pre-scale, warm the pool, and rehearse the ladder under a load drill |

## 9. Prevention Backlog

- Multi-region read paths with a documented failover order and rehearsal.
- Cost-aware routing between model tiers by per-slot value.
- Automated guardrail evaluation per rollout stage with promotion criteria.
- Diversity metrics as a hard guardrail against homogenised recommendations.
- Quarterly architecture review re-checking that every edge still has a failure behaviour.

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

> The deliverable is a recommendation platform where a feature store outage costs you a rung rather than 22 minutes, every dependency has a tested failure behaviour, and rollback is a command rather than a war room.
