# MINI_PROJECT — Powered Factorial Experiment with Blocking

**Track:** statistics  |  **Lab:** lab08  |  **Level:** Advanced

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

**Brief.** Design a blocked factorial experiment, size it from power, run it, and analyse it as pre-specified.

**Timebox.** 3–4 hours

## 1. Why This Project Exists

This is the design half of experimental work, and getting it right is what makes the analysis worth doing.

## 2. Requirements

- Estimand written and stored before the design is fixed.
- Sample size from a power calculation with an inflated pilot variance.
- Blocked factorial design with replication in every cell.
- Seeded randomisation with an assignment audit.
- Main effects and interaction, tested in that order.
- Power curve showing the achievable minimum detectable effect.
- Simulation validating the analytic power, plus a committed analysis plan.

## 3. Build Order

| Step | Time | What you do | Done when |
|---|---|---|---|
| 1 | 30m | Write the estimand; design refuses to exist without it | A committed estimand |
| 2 | 30m | Sample size with an inflated variance | A power calculation with inputs |
| 3 | 30m | Blocked 2x2 design with replication | A design object |
| 4 | 25m | Seeded randomisation with an arm-size audit | A reproducible assignment |
| 5 | 35m | Main effects then interaction; interpret conditionally | An analysis with an interaction story |
| 6 | 30m | Power curve and achievable minimum detectable effect | A design resolution table |
| 7 | 30m | Simulation validation and committed analysis plan | A validated plan |

## 4. Architecture Sketch

```text
 estimand (required field)
     |
 pilot variance --> inflated by a stated factor --> power calculation --> n per cell
     |
 blocked 2x2 factorial (machine x treatment), replication r
     |
 seeded randomisation within blocks + assignment audit
     |
 analysis: interaction first --> simple effects if significant
     |
 power curve + achievable MDE
     |
 simulation validating the analytic power; analysis plan committed before data
```

## 5. Implementation Notes

- Inflate the pilot variance by a stated factor and justify it; this is where studies are saved.
- Randomise within blocks, not across them, or blocking buys nothing.
- Test the interaction first; reporting marginal main effects when it matters is the classic error.
- Simulate the whole study to check the analytic power, which catches formula mistakes.

## 6. Deliverables

1. Estimand, design record and committed analysis plan.
1. Power calculation with the inflated variance and its justification.
1. Blocked factorial analysis with interaction and simple effects.
1. Power curve, achievable minimum detectable effect, and a simulation validation.

## 7. Grading Rubric

| Dimension | Weight | What earns full marks |
|---|---|---|
| Design | 30% | Estimand required; blocking and replication correct |
| Power | 25% | Sample size from an inflated variance; power curve and MDE |
| Randomisation | 15% | Seeded, audited, reproducible |
| Analysis | 20% | Interaction first; conditional interpretation |
| Verification | 10% | Simulation validating the analytic power |

## 8. Stretch Goals

- Add Latin square blocking for a positional nuisance variable.
- Add a response-surface analysis for a continuous factor.
- Add sequential design with an interim futility rule.

## 9. Definition of Done

You are finished when every box below is checked, not when the code compiles.

- [ ] Estimand written and stored before the design is fixed.
- [ ] Sample size from a power calculation with an inflated pilot variance.
- [ ] Blocked factorial design with replication in every cell.
- [ ] Seeded randomisation with an assignment audit.
- [ ] Main effects and interaction, tested in that order.
- [ ] Power curve showing the achievable minimum detectable effect.
- [ ] A stranger can reproduce the reported numbers with one command
- [ ] The limitations section says what this cannot do
- [ ] At least one number is alerted on in production

## 10. Retrospective Template

- What worked:
- What surprised me:
- The one number I would alert on in production:
- What I would delete before shipping this to real users:
