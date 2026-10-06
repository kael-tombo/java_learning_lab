# MINI_PROJECT — Production ML Architecture with a Failure Story

**Track:** mlops  |  **Lab:** lab15  |  **Level:** Advanced

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

**Brief.** Design the full architecture, allocate budgets, build a degradation ladder, and chaos-test every dependency.

**Timebox.** 4–5 hours

## 1. Why This Project Exists

This is the capstone for the track: every earlier lab contributes a component, and this one makes them behave as a system when things fail.

## 2. Requirements

- Three paths drawn separately: batch training, online serving, delayed feedback.
- Every dependency edge carries a metric, an SLO, an owner and a failure mode; a validator rejects incomplete edges.
- Latency budget allocated per dependency with enforced timeouts.
- Degradation ladder ordered by quality cost, traversable inside the detection cycle.
- Consistency choice per interaction with reasons; verify one behaviour end to end.
- Rollout stages (shadow, canary, ramp) with guardrails and a timed pre-authorised rollback.
- Chaos-test three dependencies and measure detection and mitigation time.
- Unit economics: cost per 1,000 decisions including amortised training.

## 3. Build Order

| Step | Time | What you do | Done when |
|---|---|---|---|
| 1 | 35m | Draw the three paths; add owners, SLOs and failure modes | A validated architecture spec |
| 2 | 30m | Latency budget allocation with enforced timeouts | A budget per dependency |
| 3 | 35m | Degradation ladder ordered by quality cost | An ordered, traversable ladder |
| 4 | 30m | Consistency choices with one verified behaviour | A consistency table and a test |
| 5 | 35m | Rollout stages and a timed pre-authorised rollback | A rollout plan with timing |
| 6 | 35m | Chaos test three dependencies; measure response | A chaos report |
| 7 | 30m | Unit economics model on the dashboard | Cost per 1,000 decisions |

## 4. Architecture Sketch

```text
 BATCH PATH                      ONLINE PATH
 ingest -> validate -> featurise -> train -> eval -> registry
                              |                  |
                        feature store       model artefact
                              |                  |
 SERVING PATH  <--------------+------------------+
 request -> features -> inference -> decision -> log
                |          |          |
             (timeout)  (bulkhead)  (degradation ladder)
                              |
 FEEDBACK PATH  <-------------+
 decisions + outcomes -> quality + drift -> trigger -> retrain
```

## 5. Implementation Notes

- Write the failure behaviour for each edge before writing the happy-path description.
- A degradation rung that takes longer than your detection cycle is decorative.
- Measure detection and mitigation per edge; the slowest one is your next week's work.
- Cost per decision is what connects the architecture choices to a budget conversation.

## 6. Deliverables

1. Validated architecture spec with owners, SLOs and failure modes.
1. Latency and availability budgets with enforcement.
1. Degradation ladder with quality cost per rung, tested.
1. Chaos report with measured response times plus a unit economics model.

## 7. Grading Rubric

| Dimension | Weight | What earns full marks |
|---|---|---|
| Completeness | 30% | Every edge has metric, SLO, owner and failure mode |
| Degradation | 25% | Ladder ordered, traversable, and tested to terminal behaviour |
| Budgets | 20% | Latency and availability allocated and enforced |
| Operations | 15% | Timed pre-authorised rollback and chaos measurements |
| Economics | 10% | Cost per 1,000 decisions modelled |

## 8. Stretch Goals

- Add multi-region read paths with a documented failover order.
- Add an exploration budget to the feedback loop.
- Add cost-aware routing between model tiers by per-decision value.

## 9. Definition of Done

You are finished when every box below is checked, not when the code compiles.

- [ ] Three paths drawn separately: batch training, online serving, delayed feedback.
- [ ] Every dependency edge carries a metric, an SLO, an owner and a failure mode; a validator rejects incomplete edges.
- [ ] Latency budget allocated per dependency with enforced timeouts.
- [ ] Degradation ladder ordered by quality cost, traversable inside the detection cycle.
- [ ] Consistency choice per interaction with reasons; verify one behaviour end to end.
- [ ] Rollout stages (shadow, canary, ramp) with guardrails and a timed pre-authorised rollback.
- [ ] A stranger can reproduce the reported numbers with one command
- [ ] The limitations section says what this cannot do
- [ ] At least one number is alerted on in production

## 10. Retrospective Template

- What worked:
- What surprised me:
- The one number I would alert on in production:
- What I would delete before shipping this to real users:
