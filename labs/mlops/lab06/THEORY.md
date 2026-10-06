# Kubernetes for ML

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

## 1. The Problem This Solves

A container image is not a service. Scheduling, probes, autoscaling and rolling updates are what turn a pod that starts into a service that stays up.

Every ML platform runs on Kubernetes, and the model-serving failure modes you learn here — probes, resources, disruption — are the ones that page you at 3 a.m.

## 2. Learning Objectives

- Write Deployment, Service and HPA manifests for a model server
- Set requests and limits so a burst throttles rather than OOMKills
- Design liveness and readiness probes that do not cause restart storms
- Choose a rolling update strategy that respects a latency SLO
- Explain why node affinity, topology spread and disruption budgets matter for inference
- Debug a pod that is scheduled but never becomes ready

## 3. Core Concepts

### 3.1 Three probes, three questions

Liveness asks 'is this process wedged' and failing it restarts the pod. Readiness asks 'can this serve' and failing it removes the pod from the Service without restarting. Startup gates slow boots. Conflating them is how you turn a load spike into a cluster-wide restart storm.

### 3.2 Requests drive scheduling, limits drive throttling

The scheduler places a pod based on requests, so under-requesting overcommits the node. The limit is a hard cap: exceeding memory gets you OOMKilled, exceeding CPU gets you throttled. Limits above requests let bursts through instead of throttling permanently.

### 3.3 Disruption budgets are a promise to the business

A PodDisruptionBudget sets a floor on available replicas during voluntary disruption such as a node drain. Without one, a cluster upgrade can take the whole model service down, and it will happen during working hours.

### 3.4 Topology spread and node affinity

Spreading replicas across zones protects against a zone outage. Node affinity pins GPU or high-memory inference nodes. Both matter for latency: a pod scheduled across zones adds network time to every prediction.

### 3.5 Autoscaling on the right signal

CPU is a poor proxy for inference load, because batched inference is bursty and CPU-throttled. Queue depth and in-flight requests track user experience more directly, so they scale earlier and avoid throttle-driven latency spikes.

### 3.6 Rolling update as a risk operation

maxUnavailable and maxSurge decide how much capacity disappears during a deploy. With a latency SLO in place, a slow rollout is safer than a fast one that removes capacity and drops requests.

## 4. Key Equations at a Glance

| Symbol | Name | Meaning |
|---|---|---|
| `utilisation = usage / request` | Overcommit check | sustained > 1 means the scheduler under-reserved |
| `effective capacity = sum(requests) <= allocatable` | Node fit | the actual scheduling constraint |
| `p99_relevant = probe + rollout + network` | Latency composition | budget each contributor |
| `min_available = replicas * (1 - disruption%)` | PDB floor | promise kept during drains |
| `scale_up = max(ceil(target / current), current + step)` | HPA behaviour | bounded by both |
| `rollout_capacity = maxUnavailable` | Deploy risk | capacity removed during update |

## 5. How the Pieces Fit Together

1. Set requests from measurement and limits above p99 for burst headroom.

2. Configure startup probe for slow boots, readiness for warm-up, liveness cheap and dependency-free.

3. Spread replicas across zones and pin to the right node pool.

4. Set a PodDisruptionBudget so drains cannot take the service down.

5. Autoscale on queue depth or in-flight requests, not CPU alone.

6. Roll out with explicit maxUnavailable and watch readiness failures during the rollout.

## 6. Assumptions and Invariants

- Readiness covers warm-up, so the Service never routes to a cold pod
- Liveness does no dependency work, so load spikes do not cause restarts
- Requests are measured, so the scheduler places pods correctly
- Replicas span at least two zones with a disruption budget
- Autoscaling reacts to a signal correlated with user-visible latency
- Rollout strategy is chosen with the latency SLO in mind

## 7. Failure Modes You Will Meet in Production

| Symptom | Root cause | Fix |
|---|---|---|
| Cluster restarts during an upgrade cause an outage | no PodDisruptionBudget | set a PDB with minAvailable above zero |
| Load spike causes every pod to restart | liveness probe touches a dependency | make liveness constant-time and dependency-free |
| Pods OOMKilled at peak despite a healthy heap | memory limit too close to the heap | leave native headroom; alert on RSS not heap |
| p99 spikes minutes after a deploy | rollout removed too much capacity at once | reduce maxUnavailable, or add surge capacity |
| Autoscaler reacts minutes late | scaling on CPU | scale on queue depth or in-flight requests |
| A node drain evicts an entire zone's replicas | no topology spread | spread replicas across zones explicitly |

## 8. Java Building Blocks

| API / class | Why it earns its place here |
|---|---|
| `/readyz readiness gate` | warm-up completion gates Service membership |
| `/healthz constant-time liveness` | never touch the model or a dependency in liveness |
| `/startupz for slow boots` | prevents liveness kills during long model loads |
| `Thread pool sized from requests` | so the JVM's thread budget matches the CPU limit |
| `Micrometer metrics for queue depth` | the autoscaling signal, exported as metrics |

## 9. Where This Sits in the Larger System

- **mlops/lab05** produces the image this lab deploys.
- **mlops/lab03** decides which version the Deployment points at.
- **mlops/lab08** instruments the probes and metrics this lab relies on.
- **mlops/lab12** manages the cluster and node pools as code.

## 10. Self-Assessment Before You Ship Anything

Score yourself 0-2 on each. Any zero below means you are not ready to operate this in production.

- [ ] 0 — cannot yet — Write Deployment, Service and HPA manifests for a model server
- [ ] 0 — cannot yet — Set requests and limits so a burst throttles rather than OOMKills
- [ ] 0 — cannot yet — Design liveness and readiness probes that do not cause restart storms
- [ ] 0 — cannot yet — Choose a rolling update strategy that respects a latency SLO
- [ ] 0 — cannot yet — Explain why node affinity, topology spread and disruption budgets matter for inference
- [ ] 0 — cannot yet — Debug a pod that is scheduled but never becomes ready

## 11. Summary Checklist

- [ ] Readiness gates on warm-up; liveness is constant-time.
- [ ] Requests are measured and limits leave native headroom.
- [ ] A PodDisruptionBudget keeps the service up during drains.
- [ ] Replicas span zones with explicit topology spread.
- [ ] Autoscaling uses a latency-correlated signal, not CPU alone.
- [ ] Rollout maxUnavailable is chosen against the latency SLO.
