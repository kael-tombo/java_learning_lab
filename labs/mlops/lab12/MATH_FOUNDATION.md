# Infrastructure as Code for ML - Mathematical Foundations

**Track:** mlops  |  **Lab:** lab12  |  **Level:** Intermediate

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
| `plan = f(code, state) -> resource_changes` | Plan semantics - the reviewable artifact |
| `drift = actual - desired` | Drift - difference between code and reality |
| `cost = sum(gpu_hours x rate + storage_gb x rate)` | Cost model - tagged per resource |
| `quota_used = sum(active_requests)` | Quota - the queueing constraint |
| `recovery_time = RTO, recovery_point = RPO` | Stateful SLOs - what recreate must preserve |
| `apply = state := plan` | Apply - atomic by region, reviewed before running |

## Why the Math Matters

Infrastructure as code is a diff between a desired state and an actual state; the mathematics is set difference, cost accounting and recovery-time arithmetic.


---

## 1. Plan, drift and the apply contract

```text
desired = f(code, config)
actual = g(cloud API)
plan = diff(desired, actual)
drift = actual - desired
apply: state := plan, atomic per region
```

Separating desired, actual and plan is what makes review possible. The plan is the only thing a human needs to read, and it is the artifact that gets attached to the change record.

**Worked example.** Desired: 3 node pools, 2 buckets, 1 private subnet. Actual: those plus a manually created 4th pool. Plan shows zero creates and zero destroys; drift reports the extra pool with no owner, which is a conversation, not an automatic delete.


---

## 2. GPU cost attribution

```text
cost = sum over resources of (hours x rate)
allocated_cost = cost x team_share / total_team_hours
idle detection: allocated < 0.2 of quota for 7 days
```

Cost tags turn an opaque cloud bill into a per-team number. Idle detection on quota rather than usage is what finds pools that are provisioned but abandoned.

**Worked example.** Pool quota 40 A10G-hours per day, average usage 6. Idle for 7 days: the quota costs roughly 34 x 0.55 USD per hour x 24 = about 450 USD per day that nobody is using.


---

## 3. Quota and queueing behaviour

```text
admitted = min(requests, quota - used)
wait increases sharply as utilisation approaches 1
priority classes partition the capacity
```

A quota turns unbounded contention into bounded queueing. Priority classes let interactive work preempt batch without either starving, which is what makes a shared cluster survivable.

**Worked example.** Quota 8, demand 12: 8 admitted, 4 queued. With serving at priority 1 and batch at 3, the 4 queued are batch jobs; under heavy batch load serving preempts rather than queueing.


---

## 4. Stateful recreate and RPO/RTO

```text
recreate_time = provision + restore
RPO = data lost on destroy, RTO = time to usable
plan must show: restore source, verified at, data loss window
```

For stateful resources the plan has to state the recovery properties, not just that a resource will be replaced. Any plan that destroys something holding production data should fail validation without an explicit acknowledgement.

**Worked example.** Feature store with 6-hour snapshots: RPO 6 hours, restore 40 minutes. A plan destroying it should require an acknowledgement naming the snapshot and its age, not a bare 'yes'.


---

## Cheat Sheet

- `plan = f(code, state) -> resource_changes` - Plan semantics
- `drift = actual - desired` - Drift
- `cost = sum(gpu_hours x rate + storage_gb x rate)` - Cost model
- `quota_used = sum(active_requests)` - Quota
- `recovery_time = RTO, recovery_point = RPO` - Stateful SLOs
- `apply = state := plan` - Apply

## Numerical Traps

- Reading only the creates in a plan and missing the destroys.
- Applying infrastructure changes with no review step at all.
- Correcting drift automatically and deleting a manual emergency fix.
- Setting quotas without priority classes, so one team starves another.
- Treating a cost bill as an accounting problem rather than a design signal.

## Self-Check Problems

1. Write a plan diff for a desired/actual pair including a manual resource, and classify each line as intended or drift.
2. Compute a per-team GPU allocation from tagged usage and quota, and identify idle quota.
3. Size a quota for a workload with peak demand and explain the queueing behaviour as utilisation rises.
4. Write RPO and RTO for a feature store and state what a recreate plan must display.
5. Design a drift report per team, including who owns each diverged resource.
