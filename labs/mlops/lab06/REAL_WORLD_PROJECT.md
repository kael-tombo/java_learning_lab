# REAL_WORLD_PROJECT — Kubernetes Inference Platform for 40 Models

**Track:** mlops  |  **Lab:** lab06  |  **Level:** Advanced

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

A platform team serves 40 models from one Kubernetes cluster shared with batch jobs. Quarterly node upgrades have twice taken the fraud model offline, and last month a feature-store blip restarted every serving pod simultaneously.

**You are the on-call engineer.** The system below is the one you inherit, not a greenfield toy - the interesting work is in the seams.

## 2. Numbers That Matter

| Quantity | Value |
|---|---|
| Models | 40 models, 6 teams, one shared cluster |
| Cluster | 3 zones, mixed node pools including GPU inference |
| SLOs | p99 < 40 ms per model; availability 99.95% per model |
| Incidents | 2 upgrades caused outages; 1 dependency blip caused a fleet restart |
| Shared load | batch jobs compete with inference for node capacity |

## 3. Target Architecture

```text
 inference node pools (zone A/B/C) + batch pool
        |
   Deployments (40 models) with startup/readiness/liveness probes
   PDB per model  |  topologySpread across zones  |  node affinity by pool
        |
   Services (40) --> Ingress/Gateway
        |
   HPA on queue depth per model + KEDA-style scaling on backlog
        |
   metrics: readiness failures, throttle ratio, queue depth, RSS
        |
   upgrade runbook: cordon -> drain -> verify PDB -> uncordon, per model
```

## 4. Component Responsibilities

### 4.1 Per-model deployment standard

- Shared manifest builder: probes, resources, spread, affinity, strategy derived from a load profile
- Validation gate in CI rejecting manifests without probes, resources or a PDB
- Model-specific budgets: p99 latency, memory ceiling, minimum replicas
- Image digest and model version from the registry recorded in annotations

### 4.2 Cluster sharing and scheduling

- Separate node pools for inference and batch with resource quotas, so batch cannot starve serving
- Priority classes: serving above batch; batch is evicted before serving
- Topology spread across zones with a PDB per model holding one zone's worth
- Batch jobs submit to a queue that is automatically scaled down at serving peak

### 4.3 Autoscaling and protection

- HPA on queue depth or in-flight requests per model, with a stabilisation window
- Minimum replicas per model sized to survive one zone's loss
- Autoscaler prioritised over batch; queue pre-warm for known traffic events
- Rollout strategy per model, tuned to its own error budget

### 4.4 Upgrade and incident process

- Cordon-and-drain upgrades honouring each model's PDB, one zone at a time
- Pre-upgrade check: headroom for the drained zone's minimum replicas
- Dependency-outage drill proving liveness does not restart serving pods
- Runbook with time-to-safe measured and published after each drill

## 5. Delivery Timeline

| When | Milestone |
|---|---|
| Week 1-2 | Mandate the manifest standard through a CI gate; migrate 10 models to it |
| Week 3 | Separate node pools with quotas and priority classes; verify batch cannot starve serving |
| Week 4 | Queue-driven autoscaling with minimum replicas sized per model |
| Week 5-6 | Migrate the remaining 30 models; add topology spread and per-model PDBs |
| Week 8 | Run a full zonal upgrade dry run and a dependency-outage drill; publish results |

## 6. Runbook (copy-paste)

```bash
# Per-model serving state, readiness and queue depth
kubectl get deploy -o json | jq -r '.items[] | {name, ready:.status.readyReplicas, unavailable:.status.unavailableReplicas}'

# Verify each model's PDB before a drain
for m in $(kubectl get pdb -o name); do kubectl get $m -o json | jq '{name:.metadata.name,minAvailable:.spec.minAvailable}'; done

# Drain a node honouring PDBs (one zone at a time)
kubectl cordon node-17 && kubectl drain node-17 --ignore-daemonsets --timeout=600s

# Confirm serving is unaffected after eviction begins
curl -s localhost:9090/metrics | grep -E 'inference_queue_depth|serving_5xx_ratio'

# Dependency-outage drill: verify no serving pods restart
kubectl exec deploy/fraud-scorer -- curl -s localhost:8080/healthz
```

## 7. Observability and SLOs

- SLO: p99 latency and availability per model against its own budget.
- Upgrade safety: zero model availability breaches during node upgrades.
- Probe health: readiness failure rate and liveness restart counts per model.
- Throttling: CPU throttle ratio per model; sustained throttle is a sizing bug.
- Capacity: minimum replicas sufficient to lose one zone; verified by drill.

## 8. Failure Modes and the Rollback Plan

| Failure | Detection | Response |
|---|---|---|
| Node upgrade drops a model below its SLO | PDB absent or minimum replicas below one zone | Hold the drain, add replicas, then resume; require a dry run before future upgrades |
| Every serving pod restarts during a feature-store blip | liveness probe checks a dependency | Remove the dependency from liveness; run the outage drill to prove it |
| Batch jobs starve serving at month-end | Shared pool without priority classes | Priority classes and quotas; batch suspended when serving queue depth grows |
| p99 grows minutes after a traffic event | Autoscaling on CPU | Scale on queue depth; pre-warm for known events |
| A model never becomes ready after a node pool change | Affinity or resource requests no longer fit | Check events and scheduler messages; re-plan requests for the new pool |

## 9. Prevention Backlog

- Autoscale batch to zero outside business hours to protect serving capacity.
- Automated upgrade dry-run pipeline producing a readiness report per model.
- Per-model capacity model: minimum replicas derived from one-zone-loss math.
- Dependency-outage drill in CI so a liveness probe can never depend again.
- Topology-aware routing so inference stays inside a zone.

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

> The deliverable is 40 models on a shared cluster where a node upgrade and a dependency blip both become non-events, because the probes, budgets and disruption policies were designed for them.
