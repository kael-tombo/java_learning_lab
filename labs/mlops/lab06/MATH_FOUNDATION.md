# Kubernetes for ML - Mathematical Foundations

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

## Notation

| Symbol | Meaning |
|---|---|
| `utilisation = usage / request` | Overcommit check - sustained > 1 means the scheduler under-reserved |
| `effective capacity = sum(requests) <= allocatable` | Node fit - the actual scheduling constraint |
| `p99_relevant = probe + rollout + network` | Latency composition - budget each contributor |
| `min_available = replicas * (1 - disruption%)` | PDB floor - promise kept during drains |
| `scale_up = max(ceil(target / current), current + step)` | HPA behaviour - bounded by both |
| `rollout_capacity = maxUnavailable` | Deploy risk - capacity removed during update |

## Why the Math Matters

Scheduling is a bin-packing problem with a hidden cost, and probes are recurring load that has to be budgeted rather than assumed free.


---

## 1. Node fit and overcommit

```text
pod fits node iff sum(requests) <= node allocatable
utilisation = usage / request
sustained utilisation > 1 on CPU => guaranteed throttling
```

The scheduler packs by requests, not by usage. Under-requesting lets the node accept pods it cannot actually run, and the overshoot shows up as throttling rather than as a scheduling failure.

**Worked example.** Node: 4 CPU, 2.5 GiB allocatable. Six pods requesting 500m CPU each fit by request (3.0 > 2.5 fails, so five fit). If each actually uses 700m, total demand is 4.2 CPU against 2.5 allocatable: sustained throttling.


---

## 2. Probe budget decomposition

```text
p99_request = network + queue + inference + probe_overhead
liveness overhead must be << error budget per minute
```

Probes consume capacity and add traffic. If probe frequency times cost is a meaningful share of the budget, the probe itself becomes part of the load problem.

**Worked example.** 40 pods, liveness every 10 s, 5 ms per probe: 200 probes/s at 5 ms = 1 CPU second per second across the fleet. If each probe did a model call at 30 ms instead, it would be 6 CPU seconds per second — a self-inflicted load.


---

## 3. Rollout capacity and error budget

```text
during rollout available = replicas - maxUnavailable
error_budget_burn = (maxUnavailable / replicas) x window / monthly_budget
rule of thumb: keep maxUnavailable <= 10% of replicas
```

A rollout temporarily removes capacity. If that exceeds the remaining error budget, the deploy itself causes the outage it was meant to prevent.

**Worked example.** 40 replicas, maxUnavailable 4: 10% of capacity for the rollout duration. A 4-minute rollout on a 30-day budget burns 10% x (4/43200) = 0.001% — negligible. maxUnavailable 20 (50%) for the same window burns 0.0046%.


---

## 4. Disruption budget arithmetic

```text
PDB: minAvailable = ceil(replicas x availability_target)
allowed_evictions = replicas - minAvailable
node drain of 3 nodes must satisfy this simultaneously
```

A budget is a promise about concurrent disruption. Node upgrades drain several nodes at once, so the budget has to hold while all of those evictions are in flight, not one at a time.

**Worked example.** 12 replicas across 3 zones, target 0.8: minAvailable = 10, so at most 2 pods may be unavailable at once. A drain touching 3 nodes cannot proceed in parallel; the upgrade serialises or waits.


---

## Cheat Sheet

- `utilisation = usage / request` - Overcommit check
- `effective capacity = sum(requests) <= allocatable` - Node fit
- `p99_relevant = probe + rollout + network` - Latency composition
- `min_available = replicas * (1 - disruption%)` - PDB floor
- `scale_up = max(ceil(target / current), current + step)` - HPA behaviour
- `rollout_capacity = maxUnavailable` - Deploy risk

## Numerical Traps

- Setting limits equal to requests and causing permanent throttling.
- Checking liveness against a dependency and creating restart storms.
- No PDB, so a routine node drain becomes an outage.
- Scaling on CPU when inference is batched and bursty.
- maxUnavailable set to a percentage without checking the resulting capacity loss.

## Self-Check Problems

1. Given a node's allocatable resources and pod requests, compute how many pods fit and the overcommit if each uses 40% more CPU than requested.
2. Compute the fleet-wide cost of a 30 ms liveness probe every 10 s across 200 pods, and compare to a 5 ms constant-time check.
3. Choose maxUnavailable and maxSurge for 60 replicas against a monthly error budget, and compute the burn.
4. Design a PodDisruptionBudget for 12 replicas across 3 zones with an 0.8 availability target, and check a 3-node drain.
5. Design readiness and liveness probes for a 25-second model load, stating period, failure threshold and budget impact.
