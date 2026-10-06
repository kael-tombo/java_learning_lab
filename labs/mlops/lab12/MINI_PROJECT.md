# MINI_PROJECT — ML Platform as Reviewed Code

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

**Brief.** Express a training and serving platform as code with reviewable plans, quotas, cost tags, drift detection and a recreate drill.

**Timebox.** 4 hours

## 1. Why This Project Exists

This is the substrate every ML team inherits. Building it once with review, policy and drift in mind prevents a class of outages that are invisible until they are expensive.

## 2. Requirements

- Emit code for a training pool, a feature store, a model bucket and IAM roles.
- Typed plan diff separating creates, updates and destroys, classified as intended or drift.
- Stateful destroy blocked without a recovery acknowledgement naming snapshot and age.
- Quotas and priority classes; simulate demand above quota.
- Cost allocation by team tag plus idle-quota detection with a savings estimate.
- Drift detection with owners, reporting rather than auto-correcting.
- A recreate drill in a sandbox with measured RTO.

## 3. Build Order

| Step | Time | What you do | Done when |
|---|---|---|---|
| 1 | 40m | Generate HCL for the platform; deterministic output | Reproducible code |
| 2 | 30m | Typed plan diff with creates/updates/destroys | A reviewable artifact |
| 3 | 30m | Stateful destroy validation with recovery evidence | A blocked plan you can show |
| 4 | 35m | Quotas, priorities, demand simulation | A queueing simulation |
| 5 | 35m | Cost allocation and idle-quota detection | A cost report with a saving |
| 6 | 30m | Drift detection with owner attribution | A drift report |
| 7 | 30m | Sandbox recreate drill with measured RTO | A timed drill |

## 4. Architecture Sketch

```text
 topology code (environment-agnostic)
    + environment config (values only)
    |
 desired = f(code, config)      actual = g(cloud API)
    |                                   |
    +------------> PlanDiff <-----------+
                     |
        +------------+------------+
        |                         |
   validates: tags,         classifies:
   encryption, RPO          intended vs drift
        |                         |
   blocks bad plan          drift report + owners
        |
 apply (reviewed) --> cost allocation + idle quota
```

## 5. Implementation Notes

- The plan diff is the deliverable; the HCL is just how you get there.
- Test the stateful destroy block by trying to destroy something holding data.
- Simulate demand above quota; the point is to see the queue, not the failure.
- Run the recreate drill in a sandbox, not in production, and time it.

## 6. Deliverables

1. Generated code plus a typed plan diff with separated destroys.
1. A blocked destructive plan with the reason it was rejected.
1. Quota simulation and cost report with idle-quota savings.
1. Drift report with owners plus a timed recreate drill.

## 7. Grading Rubric

| Dimension | Weight | What earns full marks |
|---|---|---|
| Correctness | 25% | Deterministic code, accurate diff, validation blocks bad plans |
| Reviewability | 25% | Destroys separated and stateful ones gated on recovery evidence |
| Policy | 20% | Tags, quotas, priorities and least privilege enforced |
| Operations | 20% | Drift attributed; cost and idle quota reported |
| Recovery | 10% | Recreate drill with measured RTO |

## 8. Stretch Goals

- Add plan-time cost estimation compared to last month's actuals.
- Add a policy-as-code suite for network posture and public access.
- Add a drift-to-ticket workflow with owner acknowledgement.

## 9. Definition of Done

You are finished when every box below is checked, not when the code compiles.

- [ ] Emit code for a training pool, a feature store, a model bucket and IAM roles.
- [ ] Typed plan diff separating creates, updates and destroys, classified as intended or drift.
- [ ] Stateful destroy blocked without a recovery acknowledgement naming snapshot and age.
- [ ] Quotas and priority classes; simulate demand above quota.
- [ ] Cost allocation by team tag plus idle-quota detection with a savings estimate.
- [ ] Drift detection with owners, reporting rather than auto-correcting.
- [ ] A stranger can reproduce the reported numbers with one command
- [ ] The limitations section says what this cannot do
- [ ] At least one number is alerted on in production

## 10. Retrospective Template

- What worked:
- What surprised me:
- The one number I would alert on in production:
- What I would delete before shipping this to real users:
