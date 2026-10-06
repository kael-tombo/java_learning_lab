# MINI_PROJECT — Multi-Group Comparison with Honest Reporting

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

**Brief.** Design a multi-group study, run the ANOVA with assumption checks, and localise differences with a declared post-hoc method.

**Timebox.** 3 hours

## 1. Why This Project Exists

Comparing groups is where statistical inflation hides: omnibus tests without effect sizes, and pairwise tests without correction.

## 2. Requirements

- One-way ANOVA computed by hand with the decomposition asserted.
- Effect size with a confidence interval for every test.
- Three post-hoc methods compared, with a simulation measuring family-wise error.
- Assumption checks that route to Welch or a rank-based alternative when violated.
- Two-way design with interaction, showing a case where main effects mislead.
- Power and minimum detectable effect for the chosen design.
- A report that localises differences and states limitations.

## 3. Build Order

| Step | Time | What you do | Done when |
|---|---|---|---|
| 1 | 30m | One-way table by hand with the identity asserted | A verified implementation |
| 2 | 25m | Effect size with an interval | Magnitude attached by construction |
| 3 | 35m | Tukey, Bonferroni, Scheffe plus a family-wise error simulation | A corrected comparison |
| 4 | 30m | Assumption checks routing to Welch | A violation demonstration |
| 5 | 30m | Two-way design with a significant interaction | An interaction story |
| 6 | 25m | Power and minimum detectable effect | A design table |
| 7 | 25m | Report with localisation and limitations | A defensible report |

## 4. Architecture Sketch

```text
 groups (k >= 3)
    |
 [1] SSB / SSW / SST with SST = SSB + SSW asserted
 [2] F, df, p  +  eta-squared with CI     (never alone)
 [3] assumption checks --> classical | Welch | rank-based
 [4] omnibus significant?
        | yes
 [5] post-hoc: Tukey | Bonferroni | Scheffe (declared)
 [6] two-way: SSA + SSB + SSAB + SSE, each tested
 [7] power + MDE for the design
    |
 report: which pairs differ, by how much, and what it costs
```

## 5. Implementation Notes

- Assert the decomposition identity; it catches transcription errors immediately.
- A family-wise error simulation makes the correction argument concrete.
- Construct data where the interaction is significant, because that is where analyses go wrong.
- Report pairwise differences with intervals, not just significance stars.

## 6. Deliverables

1. Verified ANOVA implementation with effect sizes and intervals.
1. Post-hoc comparison with a measured family-wise error rate.
1. Assumption-driven test selection demonstration.
1. Two-way analysis plus a report that localises differences.

## 7. Grading Rubric

| Dimension | Weight | What earns full marks |
|---|---|---|
| Correctness | 30% | Tables verified; degrees of freedom correct; decomposition asserted |
| Localisation | 25% | Post-hoc with a declared method and intervals |
| Rigor | 25% | Effect sizes, assumption routing, multiplicity control |
| Design | 20% | Power and MDE computed for the chosen design |

## 8. Stretch Goals

- Add mixed-effects modelling for a nested design.
- Add heteroscedasticity-robust standard errors and compare.
- Replace family-wise error with expected false discovery control and compare.

## 9. Definition of Done

You are finished when every box below is checked, not when the code compiles.

- [ ] One-way ANOVA computed by hand with the decomposition asserted.
- [ ] Effect size with a confidence interval for every test.
- [ ] Three post-hoc methods compared, with a simulation measuring family-wise error.
- [ ] Assumption checks that route to Welch or a rank-based alternative when violated.
- [ ] Two-way design with interaction, showing a case where main effects mislead.
- [ ] Power and minimum detectable effect for the chosen design.
- [ ] A stranger can reproduce the reported numbers with one command
- [ ] The limitations section says what this cannot do
- [ ] At least one number is alerted on in production

## 10. Retrospective Template

- What worked:
- What surprised me:
- The one number I would alert on in production:
- What I would delete before shipping this to real users:
