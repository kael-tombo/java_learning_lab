# Infrastructure as Code for ML - Vision & Where This Is Going

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

## 1. The Future State

ML infrastructure as code converges with workload orchestration: cluster autoscaling, quota-aware scheduling and GPU sharing become policy expressed in code. The frontier is policy-as-code checks that prevent the expensive mistakes at plan time rather than auditing them afterwards.

The test of that future state is boring: a new engineer ships a change to infrastructure as code for ml on day two without asking anyone where the magic lives.

## 2. What "Good" Looks Like in Practice

- Every production resource traces to a reviewed code change.
- Plans separate creates from destroys, and stateful destroys fail validation without recovery evidence.
- Cost and purpose tags are mandatory at plan time.
- Drift is detected on a schedule and reported with owners.

## 3. Capability Ladder

| Level | Capability | You can... |
|---|---|---|
| L1 | Codify | Express compute, storage and networking as code. |
| L2 | Review | Reviewable plans with a named reviewer and separated destroys. |
| L3 | Govern | Quotas, priorities, mandatory tags and least-privilege credentials. |
| L4 | Prevent | Policy-as-code checks, drift attribution and stateful recreate drills. |

## 4. Behaviours to Build

Review the plan, not the intent. Treat a stateful destroy as an incident until proven safe. Report drift instead of correcting it blindly.

## 5. Anti-Vision (the failure mode we are avoiding)

- One console-created bucket that nothing knows about.
- Code copied per environment with values edited by hand.
- An apply run directly from a laptop with no plan review.
- GPU quota nobody has looked at in a year.

## 6. Technology Shifts That Change the Work

1. Cluster autoscaler with quota-aware scheduling and GPU time-slicing.
1. Policy-as-code suites enforcing tags, encryption and network posture at plan time.
1. Spot and reserved capacity mixed predictably with cost modelled in code.
1. Infrastructure cost modelled per experiment so GPU spend attributes to modelling decisions.

## 7. Your 30/60/90 Commitment

- **30 days.** Express a training platform as code and produce a reviewable plan with separated destroys.
- **60 days.** Add quotas, priorities, mandatory tags and drift attribution with owners.
- **90 days.** Add policy-as-code checks and run a stateful recreate drill with measured RTO.

## 8. How To Tell You Are Actually Getting Better

- Every production resource traces to a reviewed change.
- A plan makes its destroys impossible to miss.
- I can separate drift from intended change.
- Every GPU hour is attributable to a team.

## 9. Principles That Should Not Change

- **Express ML infrastructure as versioned, reviewable configuration** Express ML infrastructure as versioned, reviewable configuration
- **Separate environment configuration from resource topology** Separate environment configuration from resource topology
- **Model GPU** Model GPU and CPU pools with quota, priority and cost awareness

> Infrastructure as code is really review made possible; a plan you did not read is still an unreviewed change.
