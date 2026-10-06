# MINI_PROJECT — Kubernetes Deployment for a Model Server

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

**Brief.** Deploy a model server on Kubernetes with budgeted probes, measured resources, a disruption budget and a chaos test.

**Timebox.** 3–4 hours

## 1. Why This Project Exists

Manifests are where the lab05 image meets real scheduling, and where the three probe bugs live.

## 2. Requirements

- Deployment with startup, readiness and liveness probes, each with an explicit cost budget.
- Simulate a 25-second model load; verify startup holds off liveness and readiness flips after warm-up.
- Prove liveness is dependency-free by simulating a dependency outage.
- Requests and limits derived from a load test at 1x/2x/3x, verified with no permanent throttling.
- PodDisruptionBudget with a fraction and an absolute floor; verify a 3-node drain honours it.
- Topology spread across zones with verified replica distribution.
- Chaos test: kill 30% of pods at peak; measure time to full service and budget burn.

## 3. Build Order

| Step | Time | What you do | Done when |
|---|---|---|---|
| 1 | 30m | Typed manifest model plus validation rules | A validator that rejects bad manifests |
| 2 | 30m | Three probes with budgets; simulate cold start and warm-up | A probe simulation |
| 3 | 30m | Dependency outage simulation; assert no liveness failures | A restart-storm test |
| 4 | 30m | Load test and resource derivation | A sizing table |
| 5 | 30m | Rollout strategy with computed budget burn | A rollout plan |
| 6 | 30m | PDB plus topology spread; drain test | A drain that stays inside the SLO |
| 7 | 30m | Chaos test with time-to-recovery | A chaos report |

## 4. Architecture Sketch

```text
 model image (lab05)
        |
   DeploymentBuilder
   |- replicas (spread across zones)
   |- startup / readiness / liveness (budgeted)
   |- resources (from load test)
   |- strategy (maxUnavailable from error budget)
   |
   Service ----> HPA (queue depth) + PDB
        |
   simulation: cold start | dep outage | drain | chaos
        |
   report: readiness failures, budget burn, time-to-recovery
```

## 5. Implementation Notes

- Give every probe a cost budget field; a probe without one eventually gets made expensive.
- Simulate the dependency outage: it is the test that catches liveness bugs.
- The drain test is what proves the PDB is real rather than decorative.
- Measure budget burn during rollout, not just success.

## 6. Deliverables

1. Validated manifests plus a validator with named failure reasons.
1. Probe simulation covering cold start, warm-up and dependency outage.
1. Resource sizing table and rollout plan with budget burn.
1. Chaos report with time-to-recovery and the tuning it suggested.

## 7. Grading Rubric

| Dimension | Weight | What earns full marks |
|---|---|---|
| Correctness | 25% | Probes, resources and strategy valid and validated |
| Safety | 30% | PDB honoured on drain; no restart storm on dependency outage |
| Evidence | 25% | Resources and rollout derived from measurement |
| Resilience | 20% | Chaos test with time-to-recovery measured |

## 8. Stretch Goals

- Implement queue-depth autoscaling with a stabilisation window.
- Add a simulated zone outage and measure degradation versus recovery.
- Export metrics in Prometheus format and write alert rules.

## 9. Definition of Done

You are finished when every box below is checked, not when the code compiles.

- [ ] Deployment with startup, readiness and liveness probes, each with an explicit cost budget.
- [ ] Simulate a 25-second model load; verify startup holds off liveness and readiness flips after warm-up.
- [ ] Prove liveness is dependency-free by simulating a dependency outage.
- [ ] Requests and limits derived from a load test at 1x/2x/3x, verified with no permanent throttling.
- [ ] PodDisruptionBudget with a fraction and an absolute floor; verify a 3-node drain honours it.
- [ ] Topology spread across zones with verified replica distribution.
- [ ] A stranger can reproduce the reported numbers with one command
- [ ] The limitations section says what this cannot do
- [ ] At least one number is alerted on in production

## 10. Retrospective Template

- What worked:
- What surprised me:
- The one number I would alert on in production:
- What I would delete before shipping this to real users:
