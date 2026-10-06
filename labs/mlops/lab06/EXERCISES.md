# Kubernetes for ML - Exercises

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

## How To Work These

Work in order. Each exercise builds the next; do not skip ahead.
Every exercise ends with a *deliverable* you can show someone - code that compiles, a number you can defend, or a table you can regenerate.

Run the lab as you go:

```bash
cd lab06
javac -d out $(Get-ChildItem -Recurse -Filter *.java src | ForEach-Object { $_.FullName })
java -cp out KubernetesLab
```

## Exercise 1: Write and validate the manifests

**Task.** Deployment, Service, HPA, PDB and ConfigMap.

**Steps**
- Build a Deployment with strategy and probes.
- Add a Service and an HPA on queue depth.
- Add a PDB with a fraction and an absolute floor.
- Write validation that rejects incomplete manifests.

**Deliverable.** A set of manifests plus a validator that rejects bad ones.

## Exercise 2: Probe design and simulation

**Task.** Prove liveness cannot cause a restart storm.

**Steps**
- Simulate a 25-second model load.
- Verify startup probe holds off liveness, then readiness flips.
- Simulate a dependency outage and assert no liveness failures.
- Compute the fleet cost of each probe design.

**Deliverable.** A probe simulation with a cost comparison.

## Exercise 3: Resources from a load test

**Task.** Derive, do not guess.

**Steps**
- Load test at 1x/2x/3x and record p99 CPU and RSS.
- Derive requests from p99 and limits with headroom.
- Verify no permanent throttling at 2x.
- Verify memory stays inside the limit at 3x.

**Deliverable.** A sizing table derived from measurement.

## Exercise 4: Rollout safety

**Task.** Deploy without causing the outage you were preventing.

**Steps**
- Define maxUnavailable and maxSurge from the error budget.
- Compute the capacity loss during a rollout.
- Simulate a rollout and watch readiness failures.
- Adjust until the burn is negligible.

**Deliverable.** A rollout plan with a computed budget burn.

## Exercise 5: Autoscaling on the right signal

**Task.** Move off CPU.

**Steps**
- Implement an HPA on CPU and simulate a burst.
- Measure detection latency.
- Implement a queue-depth policy and re-measure.
- Compare p99 during scale-up for both.

**Deliverable.** A comparison showing which signal reacts first.

## Exercise 6: Disruption and drains

**Task.** Make upgrades boring.

**Steps**
- Define a PDB and verify a 3-node drain honours it.
- Show what happens without one.
- Add topology spread and verify replica distribution.
- Time a full upgrade under the budget.

**Deliverable.** A drain test proving the service stays up.

## Exercise 7: Never-ready debugging

**Task.** The most common Kubernetes ML failure.

**Steps**
- Reproduce a pod stuck not-ready (bad readiness path).
- Reproduce a crash loop (OOMKilled vs app crash vs probe failure).
- Distinguish each from events and logs.
- Write a triage runbook.

**Deliverable.** A triage runbook that names the cause from evidence.

## Exercise 8: Chaos test the service

**Task.** Break it on purpose.

**Steps**
- Kill 30% of pods during peak.
- Measure time to full service and the latency spike.
- Verify no error budget breach with the PDB in place.
- Document what to tune.

**Deliverable.** A chaos report with time-to-recovery and the tuning it suggested.


---

## Self-Check Before You Move On

- [ ] I can explain readiness versus liveness without notes.
- [ ] My requests come from a measurement.
- [ ] A node drain cannot take my service down.
- [ ] My autoscaler reacts before users feel latency.
