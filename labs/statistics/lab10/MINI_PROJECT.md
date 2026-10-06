# MINI_PROJECT — Power Analysis for a Real Decision

**Track:** statistics  |  **Lab:** lab10  |  **Level:** Advanced

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

**Brief.** Convert a business threshold into an effect size, size the study, and report the design's resolution honestly.

**Timebox.** 3 hours

## 1. Why This Project Exists

Power planning is where studies are won or wasted, and the MDE is what you report when a result comes back null.

## 2. Requirements

- Effect sizes: d, Hedges' g, r and a proportion measure, with a business translation.
- Required n per arm from alpha, power and an inflated variance.
- MDE for a grid of n, expressed in business units.
- Power curves across effect sizes and both sidednesses.
- Multiplicity pricing: required n for m = 1, 5, 10, 50.
- Post-hoc power critique with a retrospective alternative at the a priori effect.
- A design document with the power curve and decision rule.

## 3. Build Order

| Step | Time | What you do | Done when |
|---|---|---|---|
| 1 | 30m | Business threshold to effect size | A defensible planning effect |
| 2 | 30m | Pilot variance and documented inflation | A planning variance |
| 3 | 30m | Required n, horizon and MDE | A sized design |
| 4 | 30m | Power curves with operating points marked | A resolution chart |
| 5 | 30m | Multiplicity cost table | A pricing table |
| 6 | 30m | Post-hoc power critique | A demonstration plus a replacement |
| 7 | 30m | Design document | A reviewer-ready plan |

## 4. Architecture Sketch

```text
 business threshold (e.g. +2% conversion)
     |
 translate into the metric's sd units -> planning effect d
     |
 pilot variance --> inflate by a documented factor
     |
 alpha, power  ->  required n per arm  ->  horizon at traffic
     |                    |
 MDE at that n        power curves (effects x sidedness)
     |                    |
 multiplicity pricing (m = 1, 5, 10, 50) -> revised n
     |
 post-hoc power critique -> retrospective power at the a priori effect
     |
 design document: effect, n, horizon, MDE, curves, decision rule
```

## 5. Implementation Notes

- Start from the business threshold, not from a literature effect size; the translation is the deliverable.
- Record the inflation factor and its justification alongside the design.
- The MDE table is what you will quote if the result is null, so build it before you need it.
- Post-hoc power is a function of the p-value; demonstrate it and then supply the a-priori alternative.

## 6. Deliverables

1. Planning effect size with the business translation shown.
1. Required n, horizon and MDE table.
1. Power curves with operating points and a multiplicity cost table.
1. Design document with the decision rule and a post-hoc power critique.

## 7. Grading Rubric

| Dimension | Weight | What earns full marks |
|---|---|---|
| Translation | 25% | Business threshold converted to an effect size with reasoning |
| Sizing | 25% | Inflated variance, required n, horizon and MDE all correct |
| Curves | 20% | Power curves across effects and sidedness with marked points |
| Multiplicity | 15% | Required n growth priced honestly |
| Honesty | 15% | MDE reported; post-hoc power critiqued with a replacement |

## 8. Stretch Goals

- Add power for logistic regression and count outcomes.
- Add equivalence testing power, which inverts the framing.
- Add a budget optimiser allocating a fixed total across several endpoints.

## 9. Definition of Done

You are finished when every box below is checked, not when the code compiles.

- [ ] Effect sizes: d, Hedges' g, r and a proportion measure, with a business translation.
- [ ] Required n per arm from alpha, power and an inflated variance.
- [ ] MDE for a grid of n, expressed in business units.
- [ ] Power curves across effect sizes and both sidednesses.
- [ ] Multiplicity pricing: required n for m = 1, 5, 10, 50.
- [ ] Post-hoc power critique with a retrospective alternative at the a priori effect.
- [ ] A stranger can reproduce the reported numbers with one command
- [ ] The limitations section says what this cannot do
- [ ] At least one number is alerted on in production

## 10. Retrospective Template

- What worked:
- What surprised me:
- The one number I would alert on in production:
- What I would delete before shipping this to real users:
