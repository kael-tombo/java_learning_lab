# Non-Parametric Statistics - Vision & Where This Is Going

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

## 1. The Future State

Rank methods remain the default for ordinal, skewed and small-sample problems, with permutation tests providing a general framework and effect sizes becoming as routine as p-values. The discipline is matching the test to the design and handling ties exactly.

The test of that future state is boring: a new engineer ships a change to non-parametric statistics on day two without asking anyone where the magic lives.

## 2. What "Good" Looks Like in Practice

- Tests are matched to the design and measurement scale.
- Ties are handled with average ranks and a variance correction.
- Small samples use exact null distributions.
- Every rank test reports an effect size with an interval.

## 3. Capability Ladder

| Level | Capability | You can... |
|---|---|---|
| L1 | Rank | Ranking with average ranks and tie correction. |
| L2 | Test | Mann-Whitney, Wilcoxon, Kruskal-Wallis and Friedman. |
| L3 | Be exact | Exact null enumeration for small samples. |
| L4 | Quantify | Effect sizes with intervals and corrected pairwise follow-up. |

## 4. Behaviours to Build

Match the test to the design, handle ties exactly, use exact methods when n is small, and report an effect size. Do not call a rank test a test of medians without showing shapes match.

## 5. Anti-Vision (the failure mode we are avoiding)

- A median-difference claim from a Mann-Whitney test on skewed data.
- Ignoring ties, which makes p-values too small.
- An asymptotic p-value at n = 6.
- A significant omnibus with no corrected localisation.

## 6. Technology Shifts That Change the Work

1. Permutation tests as a general exact framework covering most designs.
1. Rank-based effect sizes such as Cliff's delta with confidence intervals.
1. Automatic test selection from the data scale, design and shape diagnostics.
1. Sensitivity reporting: how does the conclusion change across plausible analyses?

## 7. Your 30/60/90 Commitment

- **30 days.** Implement ranking with ties and verify the average-rank assignment.
- **60 days.** Implement the four rank tests with exact nulls for small samples.
- **90 days.** Add effect sizes with intervals, corrected pairwise follow-up, and a power comparison.

## 8. How To Tell You Are Actually Getting Better

- My test matches the design.
- My ranking handles ties.
- Small samples use exact p-values.
- Every rank test reports an effect size.

## 9. Principles That Should Not Change

- **Choose the correct rank-based test for each design** Choose the correct rank-based test for each design and data type
- **Implement Mann-Whitney, Wilcoxon signed-rank, Kruskal-Wallis** Implement Mann-Whitney, Wilcoxon signed-rank, Kruskal-Wallis and Friedman
- **Handle ties correctly in rank-based statistics** Handle ties correctly in rank-based statistics

> Switching to a rank test is not a fallback; it is the correct answer when the parametric assumptions never held.
