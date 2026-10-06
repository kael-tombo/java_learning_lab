# Hypothesis Testing - Vision & Where This Is Going

**Track:** statistics  |  **Lab:** lab03  |  **Level:** Intermediate

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

Hypothesis testing shifts toward always-valid inference, estimation-first practice with intervals as the primary output, and causal designs that make the counterfactual explicit. The p-value survives as a technical detail rather than a headline.

The test of that future state is boring: a new engineer ships a change to hypothesis testing on day two without asking anyone where the magic lives.

## 2. What "Good" Looks Like in Practice

- Hypothesis, direction, alpha and sample size are pre-registered.
- Every result carries an effect size and an interval.
- Non-significant results report power rather than claiming no effect.
- Multiple looks and comparisons are corrected.

## 3. Capability Ladder

| Level | Capability | You can... |
|---|---|---|
| L1 | Test | Pick the right test, compute the statistic and the p-value. |
| L2 | Report | Attach effect size, interval and assumptions. |
| L3 | Design | Pre-register power, direction and the stopping rule. |
| L4 | Control | Sequential inference, multiplicity correction, permutation alternatives. |

## 4. Behaviours to Build

Estimate first and test second. Report intervals, not verdicts. Design the test before looking, and treat a non-significant result as a power question rather than a finding.

## 5. Anti-Vision (the failure mode we are avoiding)

- '5% chance this is due to chance' in a slide deck.
- A p < 0.05 headline with no magnitude.
- 'No significant difference, so the features are equivalent'.
- A metric watched daily with a stop at first significance.

## 6. Technology Shifts That Change the Work

1. Estimation-first reporting with intervals as the headline.
1. Always-valid confidence sequences replacing fixed-horizon significance.
1. Frequentist and Bayesian convergence on posterior intervals for well-specified models.
1. Equivalence and non-inferiority designs replacing 'not significant' conclusions.

## 7. Your 30/60/90 Commitment

- **30 days.** Implement t, z and chi-square tests with effect sizes attached.
- **60 days.** Add confidence intervals and report power for every inconclusive result.
- **90 days.** Add sequential inference and multiplicity correction, and pre-register a real analysis.

## 8. How To Tell You Are Actually Getting Better

- I can state what my p-value means without hedging.
- My reports never show a p-value without an effect size.
- I report power when a result is inconclusive.
- My tests are pre-registered with a sample size from power.

## 9. Principles That Should Not Change

- **State null** State null and alternative hypotheses precisely, including direction
- **Compute t, z** Compute t, z and chi-square statistics with correct degrees of freedom
- **Compute p-values without a lookup table** Compute p-values without a lookup table and interpret them correctly

> A p-value without an interval is a verdict without a measurement, and it is not evidence that anything matters.
