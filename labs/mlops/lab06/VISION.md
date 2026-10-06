# Kubernetes for ML - Vision & Where This Is Going

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

## 1. The Future State

Inference platforms converge on queue-aware autoscaling, disaggregated serving, and GPU sharing with predictable latency. Kubernetes remains the substrate, so the probe, resource and disruption discipline stays the load-bearing skill.

The test of that future state is boring: a new engineer ships a change to kubernetes for ml on day two without asking anyone where the magic lives.

## 2. What "Good" Looks Like in Practice

- Probes are three, distinct, budgeted, and liveness is dependency-free.
- Requests come from measured p99 and limits leave headroom.
- A disruption budget protects the service during every drain.
- Autoscaling reacts to a signal correlated with user-visible latency.

## 3. Capability Ladder

| Level | Capability | You can... |
|---|---|---|
| L1 | Deploy | Deployment, Service, probes and resources that work. |
| L2 | Size | Requests and limits derived from a load test. |
| L3 | Protect | PDB, topology spread, and a rollout strategy tied to the SLO. |
| L4 | Operate | Queue-aware autoscaling, chaos drills, and a never-ready triage runbook. |

## 4. Behaviours to Build

Treat probes as budgeted components. Size resources from measurement. Assume every drain will happen at the worst time and make it boring.

## 5. Anti-Vision (the failure mode we are avoiding)

- A liveness probe that queries the feature store.
- Equal requests and limits with no memory headroom.
- No PDB before enabling cluster autoscaler or node upgrades.
- Scaling on CPU alone and watching p99 spike minutes after the burst.

## 6. Technology Shifts That Change the Work

1. KEDA and queue-depth-driven autoscaling for inference workloads.
1. GPU sharing and disaggregated prefill/decode scheduling for latency.
1. Topology-aware routing to keep inference traffic inside a zone.
1. Serverless inference for spiky and low-duty-cycle models.

## 7. Your 30/60/90 Commitment

- **30 days.** Write validated manifests for a model server with all three probes.
- **60 days.** Derive requests and limits from a load test and verify burst behaviour.
- **90 days.** Add PDB, topology spread, queue-driven autoscaling and a chaos drill with time-to-recovery.

## 8. How To Tell You Are Actually Getting Better

- I can explain readiness versus liveness without notes.
- My requests come from a measurement.
- A node drain cannot take my service down.
- My autoscaler reacts before users feel latency.

## 9. Principles That Should Not Change

- **Write Deployment, Service** Write Deployment, Service and HPA manifests for a model server
- **Set requests** Set requests and limits so a burst throttles rather than OOMKills
- **Design liveness** Design liveness and readiness probes that do not cause restart storms

> Kubernetes does not make serving reliable; the probe, resource and disruption decisions you make inside it do.
