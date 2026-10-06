# Correlation & Regression - Exercises

**Track:** statistics  |  **Lab:** lab05  |  **Level:** Intermediate

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

## How To Work These

Work in order. Each exercise builds the next; do not skip ahead.
Every exercise ends with a *deliverable* you can show someone - code that compiles, a number you can defend, or a table you can regenerate.

Run the lab as you go:

```bash
cd lab05
javac -d out $(Get-ChildItem -Recurse -Filter *.java src | ForEach-Object { $_.FullName })
java -cp out com.statistics.lab05.CorrelationAndRegression
```

## Exercise 1: Correlation, both kinds

**Task.** Linear versus monotone.

**Steps**
- Implement Pearson with centred accumulation.
- Implement Spearman with tie-aware ranking.
- Compare on linear, curved and outlier-contaminated data.
- Explain each gap.

**Deliverable.** A correlation suite with interpretation.

## Exercise 2: Simple regression by hand

**Task.** The full arithmetic.

**Steps**
- Compute slope, intercept, residuals and R² by hand.
- Compute the standard error of the slope.
- Test the slope and construct a confidence interval.
- Verify against the code implementation.

**Deliverable.** A hand-verified regression.

## Exercise 3: Multiple regression with intervals

**Task.** More than one predictor.

**Steps**
- Build the design matrix with an intercept.
- Solve via the normal equation and via QR.
- Report coefficients with standard errors and intervals.
- Add a polynomial term and compare.

**Deliverable.** A multiple regression with a complete coefficient table.

## Exercise 4: Diagnostics

**Task.** Read the complaints.

**Steps**
- Plot residuals against fitted and against each predictor.
- Compute leverage, studentised residuals and Cook's distance.
- Identify the influential points.
- Refit without them and compare.

**Deliverable.** A diagnostics report with a refit comparison.

## Exercise 5: Multicollinearity and VIF

**Task.** See coefficients become unstable.

**Steps**
- Add a near-duplicate predictor and compute VIF.
- Show standard errors growing.
- Show sign flips across resamples.
- Show ridge stabilising estimates while keeping the sum stable.

**Deliverable.** A collinearity demonstration with a remedy.

## Exercise 6: Nonlinearity and transforms

**Task.** Repair the functional form.

**Steps**
- Fit a line to a parabola and inspect residuals.
- Add a quadratic term and show R² and residuals improve.
- Try a log transform on skewed data.
- Explain why R² alone would not have found it.

**Deliverable.** A form-selection demonstration.

## Exercise 7: Association versus causation

**Task.** Find the confounder.

**Steps**
- Construct data where a confounder drives both variables.
- Show the naive association is strong.
- Adjust for the confounder and show it collapse.
- Explain what regression can and cannot establish.

**Deliverable.** A confounding demonstration.

## Exercise 8: Full regression report

**Task.** Produce a defensible analysis.

**Steps**
- State the question and the estimand.
- Fit with intervals and diagnostics.
- Validate on held-out data and report validated error.
- Write limitations: extrapolation, confounding, omitted variables.

**Deliverable.** A report with an honest limitations section.


---

## Self-Check Before You Move On

- [ ] I plotted the data before fitting.
- [ ] My coefficients carry intervals.
- [ ] I inspected residual-versus-fitted for curvature.
- [ ] I do not make causal claims from observational data.
