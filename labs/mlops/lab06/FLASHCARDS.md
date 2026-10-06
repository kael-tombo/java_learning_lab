# Kubernetes for ML - Flashcards (60 cards)

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

**Format.** Question (front) -> answer (back). Use for spaced repetition: day 0, day 1, day 3, day 7, day 21. Do not read the answer first.

| # | Front | Back |
|---|---|---|
| 1 | What is the difference between readiness and liveness? | Readiness removes a pod from the Service without restarting it; liveness failing restarts the pod. |
| 2 | Why must liveness not check dependencies? | A dependency blip would restart every pod, converting an outage into a restart storm. |
| 3 | What do requests control? | Scheduling: the scheduler reserves that much CPU and memory, so under-requesting overcommits the node. |
| 4 | What do limits control? | Hard caps: exceeding memory is an OOMKill, exceeding CPU is throttling, which shows up as latency. |
| 5 | Why limits above requests? | So a burst throttles briefly instead of being throttled permanently, and memory has headroom for native allocation. |
| 6 | What is a PodDisruptionBudget for? | Keeping a floor on available replicas during voluntary disruption such as node drains. |
| 7 | Why spread replicas across zones? | A zone outage or drain would otherwise take out every replica serving that zone. |
| 8 | Why is CPU a poor autoscaling signal for inference? | Batched inference is bursty and CPU-throttled, so CPU lags the latency users feel. |
| 9 | What is Three probes, three questions? | Liveness asks 'is this process wedged' and failing it restarts the pod. |
| 10 | What is Requests drive scheduling, limits drive throttling? | The scheduler places a pod based on requests, so under-requesting overcommits the node. |
| 11 | What is Disruption budgets are a promise to the business? | A PodDisruptionBudget sets a floor on available replicas during voluntary disruption such as a node drain. |
| 12 | What is Topology spread and node affinity? | Spreading replicas across zones protects against a zone outage. |
| 13 | What is Autoscaling on the right signal? | CPU is a poor proxy for inference load, because batched inference is bursty and CPU-throttled. |
| 14 | What is Rolling update as a risk operation? | maxUnavailable and maxSurge decide how much capacity disappears during a deploy. |
| 15 | In this lab, what does `utilisation = usage / request` mean? | Overcommit check: sustained > 1 means the scheduler under-reserved |
| 16 | In this lab, what does `effective capacity = sum(requests) <= allocatable` mean? | Node fit: the actual scheduling constraint |
| 17 | In this lab, what does `p99_relevant = probe + rollout + network` mean? | Latency composition: budget each contributor |
| 18 | In this lab, what does `min_available = replicas * (1 - disruption%)` mean? | PDB floor: promise kept during drains |
| 19 | In this lab, what does `scale_up = max(ceil(target / current), current + step)` mean? | HPA behaviour: bounded by both |
| 20 | In this lab, what does `rollout_capacity = maxUnavailable` mean? | Deploy risk: capacity removed during update |
| 21 | You see 'Cluster restarts during an upgrade cause an outage' in production. What is the cause and the fix? | no PodDisruptionBudget Fix: set a PDB with minAvailable above zero |
| 22 | You see 'Load spike causes every pod to restart' in production. What is the cause and the fix? | liveness probe touches a dependency Fix: make liveness constant-time and dependency-free |
| 23 | You see 'Pods OOMKilled at peak despite a healthy heap' in production. What is the cause and the fix? | memory limit too close to the heap Fix: leave native headroom; alert on RSS not heap |
| 24 | You see 'p99 spikes minutes after a deploy' in production. What is the cause and the fix? | rollout removed too much capacity at once Fix: reduce maxUnavailable, or add surge capacity |
| 25 | You see 'Autoscaler reacts minutes late' in production. What is the cause and the fix? | scaling on CPU Fix: scale on queue depth or in-flight requests |
| 26 | You see 'A node drain evicts an entire zone's replicas' in production. What is the cause and the fix? | no topology spread Fix: spread replicas across zones explicitly |
| 27 | Which Java API is the backbone of: warm-up completion gates Service membership | `/readyz readiness gate` |
| 28 | Which Java API is the backbone of: never touch the model or a dependency in liveness | `/healthz constant-time liveness` |
| 29 | Which Java API is the backbone of: prevents liveness kills during long model loads | `/startupz for slow boots` |
| 30 | Which Java API is the backbone of: so the JVM's thread budget matches the CPU limit | `Thread pool sized from requests` |
| 31 | Which Java API is the backbone of: the autoscaling signal, exported as metrics | `Micrometer metrics for queue depth` |
| 32 | Why does Three probes, three questions matter operationally? | Liveness asks 'is this process wedged' and failing it restarts the pod. |
| 33 | Why does Requests drive scheduling, limits drive throttling matter operationally? | The scheduler places a pod based on requests, so under-requesting overcommits the node. |
| 34 | Why does Disruption budgets are a promise to the business matter operationally? | A PodDisruptionBudget sets a floor on available replicas during voluntary disruption such as a node drain. |
| 35 | Why does Topology spread and node affinity matter operationally? | Spreading replicas across zones protects against a zone outage. |
| 36 | Why does Autoscaling on the right signal matter operationally? | CPU is a poor proxy for inference load, because batched inference is bursty and CPU-throttled. |
| 37 | Why does Rolling update as a risk operation matter operationally? | maxUnavailable and maxSurge decide how much capacity disappears during a deploy. |
| 38 | In the Kubernetes for ML pipeline, what happens next? Set requests from measurement and limits above p99 for burst... | Set requests from measurement and limits above p99 for burst headroom. |
| 39 | In the Kubernetes for ML pipeline, what happens next? Configure startup probe for slow boots, readiness for warm-u... | Configure startup probe for slow boots, readiness for warm-up, liveness cheap and dependency-free. |
| 40 | In the Kubernetes for ML pipeline, what happens next? Spread replicas across zones and pin to the right node pool.... | Spread replicas across zones and pin to the right node pool. |
| 41 | In the Kubernetes for ML pipeline, what happens next? Set a PodDisruptionBudget so drains cannot take the service ... | Set a PodDisruptionBudget so drains cannot take the service down. |
| 42 | In the Kubernetes for ML pipeline, what happens next? Autoscale on queue depth or in-flight requests, not CPU alon... | Autoscale on queue depth or in-flight requests, not CPU alone. |
| 43 | In the Kubernetes for ML pipeline, what happens next? Roll out with explicit maxUnavailable and watch readiness fa... | Roll out with explicit maxUnavailable and watch readiness failures during the rollout. |
| 44 | Exercise focus: Write and validate the manifests | Deployment, Service, HPA, PDB and ConfigMap. |
| 45 | Exercise focus: Probe design and simulation | Prove liveness cannot cause a restart storm. |
| 46 | Exercise focus: Resources from a load test | Derive, do not guess. |
| 47 | Exercise focus: Rollout safety | Deploy without causing the outage you were preventing. |
| 48 | Exercise focus: Autoscaling on the right signal | Move off CPU. |
| 49 | Exercise focus: Disruption and drains | Make upgrades boring. |
| 50 | State the Node fit and overcommit result for Kubernetes for ML. | Node: 4 CPU, 2.5 GiB allocatable. Six pods requesting 500m CPU each fit by request (3.0 > 2.5 fails, so five fit). If each actually uses 700m, total demand is 4.2 CPU against 2.5 allocatable: sustained throttling. |
| 51 | State the Probe budget decomposition result for Kubernetes for ML. | 40 pods, liveness every 10 s, 5 ms per probe: 200 probes/s at 5 ms = 1 CPU second per second across the fleet. If each probe did a model call at 30 ms instead, it would be 6 CPU seconds per second — a self-inflicted load. |
| 52 | State the Rollout capacity and error budget result for Kubernetes for ML. | 40 replicas, maxUnavailable 4: 10% of capacity for the rollout duration. A 4-minute rollout on a 30-day budget burns 10% x (4/43200) = 0.001% — negligible. maxUnavailable 20 (50%) for the same window burns 0.0046%. |
| 53 | State the Disruption budget arithmetic result for Kubernetes for ML. | 12 replicas across 3 zones, target 0.8: minAvailable = 10, so at most 2 pods may be unavailable at once. A drain touching 3 nodes cannot proceed in parallel; the upgrade serialises or waits. |
| 54 | What is a startup probe for? | Allowing long cold starts without liveness killing the pod mid-load. |
| 55 | How do you make a rollout safer? | Reduce maxUnavailable, increase maxSurge, and watch readiness failures during the rollout. |
| 56 | What causes p99 spikes minutes after a deploy? | The rollout removing too much capacity at once, leaving the Service short. |
| 57 | What does node affinity buy you? | Pinning inference pods to node pools with the right hardware or memory profile. |
| 58 | When do you need a disruption budget above replicas? | Never: it blocks all voluntary disruption, so choose a fraction with an absolute floor. |
| 59 | Assumption / invariant to defend: Readiness covers warm-up, so the Service never routes to a cold pod... | Readiness covers warm-up, so the Service never routes to a cold pod |
| 60 | Assumption / invariant to defend: Liveness does no dependency work, so load spikes do not cause restarts... | Liveness does no dependency work, so load spikes do not cause restarts |

## Deck Notes

- Rows are generated from this lab's own concepts, equations, failure modes and Java APIs - if you disagree with a card, fix the card.
- The last block of cards is deliberately operational: they are the questions a staff engineer gets asked in a design review.
