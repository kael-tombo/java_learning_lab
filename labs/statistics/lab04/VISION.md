# ANOVA - Vision & Where This Is Going

**Track:** statistics  |  **Lab:** lab04  |  **Level:** Intermediate

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

ANOVA persists as the workhorse for comparing groups, increasingly alongside mixed-effects models that handle nesting, repeated measures and varying variance structure. The discipline that matters is reporting effect sizes and controlling multiplicity, not memorising tables.

The test of that future state is boring: a new engineer ships a change to anova on day two without asking anyone where the magic lives.

## 2. What "Good" Looks Like in Practice

- Variance decompositions are verified by the summing identity.
- Every omnibus test is reported with an effect size and an interval.
- Post-hoc methods are chosen for the comparison structure and declared.
- Assumption checks determine the test, not a footnote.

## 3. Capability Ladder

| Level | Capability | You can... |
|---|---|---|
| L1 | Test | One-way ANOVA table, F, df and p-value. |
| L2 | Quantify | Eta-squared and a confidence interval on it. |
| L3 | Localise | Tukey, Bonferroni or Scheffe with a declared method. |
| L4 | Adapt | Welch, mixed effects, and rank-based alternatives as needed. |

## 4. Behaviours to Build

Report magnitude with every test. Control the family-wise error rate rather than comparing everything. Check assumptions and let them pick the method.

## 5. Anti-Vision (the failure mode we are avoiding)

- A bare 'F(2, 27) = 4.1, p < .05, significant' with no effect size.
- Twenty pairwise t-tests after a significant omnibus.
- A two-way analysis with the interaction dropped to make main effects look clean.
- Classical F-tests on variances differing by an order of magnitude.

## 6. Technology Shifts That Change the Work

1. Mixed-effects models replacing fixed-effect ANOVA for nested and repeated designs.
1. Variance-component estimation with heteroscedasticity-robust standard errors.
1. Automatic reporting of effect sizes with confidence intervals in statistical software.
1. Multiplicity control framed as expected false discoveries rather than family-wise error.

## 7. Your 30/60/90 Commitment

- **30 days.** Implement the one-way table with the decomposition asserted and effect size attached.
- **60 days.** Implement Tukey, Bonferroni and Scheffe and compare their conservatism.
- **90 days.** Add Welch's ANOVA, a two-way design with interaction, and assumption-driven test selection.

## 8. How To Tell You Are Actually Getting Better

- I can build an ANOVA table by hand.
- My omnibus tests always carry an effect size.
- My post-hoc method matches the comparison structure.
- Assumption checks choose the test rather than decorate the report.

## 9. Principles That Should Not Change

- **Compute one-way** Compute one-way and two-way ANOVA tables by hand
- **Read the F-statistic** Read the F-statistic and its degrees of freedom correctly
- **Explain why post-hoc comparisons need their own correction** Explain why post-hoc comparisons need their own correction

> A significant F-test tells you something differed; the effect size and the post-hoc detail tell you whether anyone should care.
