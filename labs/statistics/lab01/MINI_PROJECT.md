# MINI_PROJECT — Distribution-Aware Summary Report

**Track:** statistics  |  **Lab:** lab01  |  **Level:** Foundational

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

**Brief.** Build a summariser that detects shape, picks the right summary family, flags outliers and reports per segment.

**Timebox.** 3 hours

## 1. Why This Project Exists

Almost every bad analytical report fails at this step: quoting a mean for a skewed variable, or deleting the rows that mattered.

## 2. Requirements

- Full summary: mean, median, mode, sample and population variance, sd, IQR, range.
- Welford streaming variance verified against a two-pass computation and against the naive formula on adversarial data.
- Shape statistics: skewness, excess kurtosis, p50/p90/p99, histogram with a declared bin width.
- 1.5 IQR fence flagging rows with a data-quality explanation for each.
- Automatic summary-family selection: symmetric reports mean ± sd, skewed reports percentiles.
- Per-segment summaries alongside every aggregate, plus a Simpson's paradox demonstration.
- A report tool whose output states the divisor, quantile convention and any flags.

## 3. Build Order

| Step | Time | What you do | Done when |
|---|---|---|---|
| 1 | 30m | Centre and dispersion with n−1; verify by hand | A verified Summary implementation |
| 2 | 30m | Welford versus naive on adversarial data | A measured precision comparison |
| 3 | 30m | Shape statistics and a bin-width sensitivity check | A shape report |
| 4 | 30m | IQR fence with row-level data-quality inspection | A flag report with causes |
| 5 | 25m | Automatic summary-family selection rule | A documented rule and its output |
| 6 | 25m | Segment reporting plus a Simpson's paradox demo | A reversal demonstration |
| 7 | 20m | Report tool with conventions stated | A defensible report |

## 4. Architecture Sketch

```text
 raw data
    |
 [1] stable pass (Welford): mean, variance
 [2] order statistics: median, quartiles, p90, p99
 [3] mode counts | density shape
 [4] skewness + excess kurtosis
    |
 shape classification --> SYMMETRIC: report mean +/- sd
                        --> SKEWED:    report p50/p90/p99
 [5] IQR fence --> flagged rows (kept, annotated, cause per row)
    |
 [6] per-segment summaries + aggregate reversal check
    |
 report with divisor, quantile convention, flags
```

## 5. Implementation Notes

- Build the adversarial dataset for the naive formula deliberately; large mean, small spread.
- Check bin-width sensitivity before claiming any mode from a histogram.
- Annotate every flagged row with a suspected cause rather than deleting it.
- The reporting rule must be written down and applied automatically, not decided per report.

## 6. Deliverables

1. Verified summary implementation with a precision comparison table.
1. Shape report with bin-width sensitivity analysis.
1. Flag report with a suspected cause for every flagged row.
1. Report tool with stated conventions and per-segment context.

## 7. Grading Rubric

| Dimension | Weight | What earns full marks |
|---|---|---|
| Correctness | 30% | Divisors, stability and quantiles verified |
| Shape awareness | 25% | Shape statistics and the summary-family rule applied |
| Outlier handling | 20% | Flagged rows retained, annotated and explained |
| Honesty | 15% | Conventions stated; segment context present |
| Communication | 10% | Report is readable and cannot mislead |

## 8. Stretch Goals

- Add robust alternatives (trimmed mean, MAD) and compare sensitivity.
- Add histogram-free mode estimation via kernel density.
- Add streaming mode estimation for large categorical streams.

## 9. Definition of Done

You are finished when every box below is checked, not when the code compiles.

- [ ] Full summary: mean, median, mode, sample and population variance, sd, IQR, range.
- [ ] Welford streaming variance verified against a two-pass computation and against the naive formula on adversarial data.
- [ ] Shape statistics: skewness, excess kurtosis, p50/p90/p99, histogram with a declared bin width.
- [ ] 1.5 IQR fence flagging rows with a data-quality explanation for each.
- [ ] Automatic summary-family selection: symmetric reports mean ± sd, skewed reports percentiles.
- [ ] Per-segment summaries alongside every aggregate, plus a Simpson's paradox demonstration.
- [ ] A stranger can reproduce the reported numbers with one command
- [ ] The limitations section says what this cannot do
- [ ] At least one number is alerted on in production

## 10. Retrospective Template

- What worked:
- What surprised me:
- The one number I would alert on in production:
- What I would delete before shipping this to real users:
