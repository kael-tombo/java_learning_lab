# MINI_PROJECT — Model A/B Test with Sequential Inference

**Track:** mlops  |  **Lab:** lab10  |  **Level:** Advanced

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

**Brief.** Design and run a live-style A/B test with power, SRM checks, sequential inference and guardrails.

**Timebox.** 3–4 hours

## 1. Why This Project Exists

Every model promotion eventually becomes a live experiment. Doing this once properly is worth more than any additional offline metric.

## 2. Requirements

- Pre-registered plan: primary metric, MDE, alpha, power, horizon and stopping rule.
- Stateless stable assignment on user id with an exposure ramp.
- SRM check before every metric read, with an injected assignment bug proving it works.
- Two-proportion analysis with pooled SE and effect intervals.
- Sequential inference with alpha control; demonstrate the false positive inflation and the fix.
- At least 3 guardrails with non-inferiority bounds and a demonstrated stop.
- Decision memo with the effect in business units.

## 3. Build Order

| Step | Time | What you do | Done when |
|---|---|---|---|
| 1 | 30m | Power, MDE and horizon; write the pre-registered plan | A plan document with numbers |
| 2 | 25m | Stateless hash assignment with exposure ramp | A deterministic assignment function |
| 3 | 25m | SRM check plus an injected assignment bug | A test proving detection |
| 4 | 30m | Two-proportion analysis with effect intervals | Verified statistics |
| 5 | 40m | Simulator; measure peeking inflation and sequential correction | A false positive comparison |
| 6 | 30m | Guardrails; simulate primary win with guardrail breach | A demonstrated stop |
| 7 | 30m | Decision memo in business units | A memo, not a p-value |

## 4. Architecture Sketch

```text
 traffic -> arm(userId) via stable hash (exposure ramp)
      |
  +---+---+
  |       |
control  treatment            (SRM check FIRST)
  |       |
  +---+---+
      |
  primary metric + 3 guardrails
      |
  sequential boundaries (alpha spending) + non-inferiority guardrails
      |
  decision: effect + interval -> business units -> recommendation
```

## 5. Implementation Notes

- Write the plan before writing the simulator; otherwise you will rationalise whatever you get.
- Inject an assignment bug deliberately; SRM checks that have never fired are untested.
- Measure the peeking inflation on a null-effect simulation so the number is memorable.
- The decision memo must be writable without reference to p-values.

## 6. Deliverables

1. Pre-registered plan with sample size, MDE and horizon.
1. Analysis module with SRM check and effect intervals, verified.
1. Peeking versus sequential false positive comparison.
1. Guardrail demonstration and a decision memo in business units.

## 7. Grading Rubric

| Dimension | Weight | What earns full marks |
|---|---|---|
| Design | 30% | Pre-registered plan with real power and MDE arithmetic |
| Correctness | 20% | Assignment stable, SRM detected when injected, pooled SE used |
| Inference | 25% | Sequential alpha control demonstrated with a measurement |
| Protection | 15% | Guardrails with a demonstrated stop |
| Decision | 10% | Memo in business units |

## 8. Stretch Goals

- Add ratio metrics with delta-method variance.
- Add interference-aware cluster randomisation for a marketplace simulation.
- Add a bandit allocation policy and compare decisions made to decision quality.

## 9. Definition of Done

You are finished when every box below is checked, not when the code compiles.

- [ ] Pre-registered plan: primary metric, MDE, alpha, power, horizon and stopping rule.
- [ ] Stateless stable assignment on user id with an exposure ramp.
- [ ] SRM check before every metric read, with an injected assignment bug proving it works.
- [ ] Two-proportion analysis with pooled SE and effect intervals.
- [ ] Sequential inference with alpha control; demonstrate the false positive inflation and the fix.
- [ ] At least 3 guardrails with non-inferiority bounds and a demonstrated stop.
- [ ] A stranger can reproduce the reported numbers with one command
- [ ] The limitations section says what this cannot do
- [ ] At least one number is alerted on in production

## 10. Retrospective Template

- What worked:
- What surprised me:
- The one number I would alert on in production:
- What I would delete before shipping this to real users:
