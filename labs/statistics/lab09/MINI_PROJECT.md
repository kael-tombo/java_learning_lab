# MINI_PROJECT — Rank-Based Analysis with Exact Inference

**Track:** statistics  |  **Lab:** lab09  |  **Level:** Advanced

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

**Brief.** Analyse four designs with the correct rank test, handle ties, use exact nulls where needed, and report effect sizes.

**Timebox.** 3 hours

## 1. Why This Project Exists

Rank tests are easy to apply wrongly: wrong test for the design, ties ignored, asymptotic p-values on tiny samples.

## 2. Requirements

- Ranking with average ranks and the tie correction, verified by hand.
- Mann-Whitney, Wilcoxon signed-rank, Kruskal-Wallis and Friedman, each matched to a design.
- Exact null enumeration for small samples compared against asymptotic p-values.
- Tie demonstration showing how ignoring ties changes the result.
- Probability of superiority as an effect size with an interval.
- Corrected pairwise follow-up after a significant omnibus.
- Power comparison against the parametric equivalent under skew.

## 3. Build Order

| Step | Time | What you do | Done when |
|---|---|---|---|
| 1 | 30m | Ranking with ties, verified by hand | A verified ranking |
| 2 | 30m | Mann-Whitney with exact enumeration | A test with both p-value paths |
| 3 | 25m | Wilcoxon signed-rank with zero and tie handling | A paired test |
| 4 | 30m | Kruskal-Wallis with corrected pairwise follow-up | An omnibus plus localisation |
| 5 | 20m | Friedman on a blocked design | A blocked rank test |
| 6 | 25m | Tie demonstration and exact-versus-asymptotic table | A comparison table |
| 7 | 30m | Power comparison and report | A power table and a report |

## 4. Architecture Sketch

```text
 four designs
  independent 2-group      -> Mann-Whitney
  paired                    -> Wilcoxon signed-rank
  independent k-group       -> Krkal-Wallis + corrected pairs
  blocked k-treatment       -> Friedman
     |
 [1] rank with average ranks + tie correction
 [2] exact null enumeration (n <= ~20) | asymptotic above
 [3] probability of superiority with interval
 [4] tie demonstration: ignoring ties inflates significance
 [5] power comparison vs parametric under skew
     |
 report: statistic, exact/asymptotic flag, effect size, what it does not support
```

## 5. Implementation Notes

- Verify the ranking by hand on a tied example before anything else; every test depends on it.
- Show the exact-versus-asymptotic gap at small n; it is the most persuasive argument for enumeration.
- Follow a significant omnibus with corrected pairs, or the localisation claim is unsupported.
- Report the probability of superiority; it communicates better than any rank statistic.

## 6. Deliverables

1. Verified ranking with tie correction.
1. Four rank tests matched to their designs, with exact and asymptotic paths.
1. Exact-versus-asymptotic comparison table and a tie demonstration.
1. Effect sizes with intervals plus a power comparison.

## 7. Grading Rubric

| Dimension | Weight | What earns full marks |
|---|---|---|
| Correctness | 30% | Ranking, ties, statistic and exactness all correct |
| Design matching | 20% | Each test matched to the correct design |
| Uncertainty | 25% | Effect sizes with intervals; exact where needed |
| Localisation | 15% | Corrected pairwise follow-up after an omnibus |
| Reporting | 10% | Null stated accurately; limits of the interpretation clear |

## 8. Stretch Goals

- Add Dunn's test for post-omnibus localisation.
- Add Cliff's delta with a bootstrap interval.
- Add a permutation framework that subsumes the four tests.

## 9. Definition of Done

You are finished when every box below is checked, not when the code compiles.

- [ ] Ranking with average ranks and the tie correction, verified by hand.
- [ ] Mann-Whitney, Wilcoxon signed-rank, Kruskal-Wallis and Friedman, each matched to a design.
- [ ] Exact null enumeration for small samples compared against asymptotic p-values.
- [ ] Tie demonstration showing how ignoring ties changes the result.
- [ ] Probability of superiority as an effect size with an interval.
- [ ] Corrected pairwise follow-up after a significant omnibus.
- [ ] A stranger can reproduce the reported numbers with one command
- [ ] The limitations section says what this cannot do
- [ ] At least one number is alerted on in production

## 10. Retrospective Template

- What worked:
- What surprised me:
- The one number I would alert on in production:
- What I would delete before shipping this to real users:
