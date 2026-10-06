# Infrastructure as Code for ML - Exercises

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

## How To Work These

Work in order. Each exercise builds the next; do not skip ahead.
Every exercise ends with a *deliverable* you can show someone - code that compiles, a number you can defend, or a table you can regenerate.

Run the lab as you go:

```bash
cd lab12
javac -d out $(Get-ChildItem -Recurse -Filter *.java src | ForEach-Object { $_.FullName })
java -cp out InfrastructureAsCodeLab
```

## Exercise 1: Generate and review a plan

**Task.** The plan is the artifact.

**Steps**
- Emit HCL for pools, buckets, IAM and networking.
- Produce a typed plan diff separating creates, updates and destroys.
- Add a destroy of a stateful resource and confirm review blocks it.
- Verify the HCL is deterministic.

**Deliverable.** A plan diff that makes destroys impossible to miss.

## Exercise 2: Topology versus configuration

**Task.** Stop copying code between environments.

**Steps**
- Split one resource set into topology and environment config.
- Deploy to two environments from the same topology.
- Confirm only configuration differs.
- Add a test asserting no environment values appear in topology.

**Deliverable.** A clean separation with a test enforcing it.

## Exercise 3: Drift detection and attribution

**Task.** Find what the code does not know about.

**Steps**
- Detect missing, extra and modified resources.
- Attribute each to an owner from a registry.
- Create a manual resource and confirm it appears as EXTRA with UNKNOWN owner.
- Write the drift report format.

**Deliverable.** A drift report with owners.

## Exercise 4: Quota and priority

**Task.** Turn contention into a queue.

**Steps**
- Define quotas per team pool.
- Add priority classes with serving above batch.
- Simulate demand above quota and show admission and queueing.
- Show that serving preempts rather than starves.

**Deliverable.** A quota simulation with priority behaviour.

## Exercise 5: Cost attribution and idle detection

**Task.** Find the money.

**Steps**
- Aggregate cost by team tag over a period.
- Allocate cost by quota share and report both views.
- Detect pools idle at under 20% of quota for 7 days.
- Produce a recommendation with estimated savings.

**Deliverable.** A cost report with an idle-quota recommendation.

## Exercise 6: Stateful recreate drill

**Task.** Prove the restore path.

**Steps**
- Define RPO and RTO for a feature store.
- Write a plan that destroys it and confirm the acknowledgement requirement.
- Run the restore in a sandbox and time it.
- Document the runbook.

**Deliverable.** A timed restore drill.

## Exercise 7: Policy as code

**Task.** Encode organisational rules.

**Steps**
- Add checks for mandatory tags, encryption and no public access.
- Show a violating plan being blocked.
- Show the fix in code and the plan passing.
- Report the check results per resource.

**Deliverable.** A policy check suite with a demonstrated block.

## Exercise 8: Full IaC walkthrough

**Task.** Provision a platform as code.

**Steps**
- Emit code for a training pool, a feature store, a model bucket and IAM roles.
- Produce and review the plan.
- Apply in a sandbox environment.
- Introduce drift and detect it on the schedule.

**Deliverable.** A provisioned sandbox with drift detection demonstrated.


---

## Self-Check Before You Move On

- [ ] Every production resource traces to a reviewed code change.
- [ ] A plan makes its destroys impossible to miss.
- [ ] I can tell drift from intended change.
- [ ] Every GPU hour is attributable to a team.
