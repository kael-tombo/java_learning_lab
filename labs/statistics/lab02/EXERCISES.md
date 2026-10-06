# Probability Distributions - Exercises

**Track:** statistics  |  **Lab:** lab02  |  **Level:** Foundational

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
cd lab02
javac -d out $(Get-ChildItem -Recurse -Filter *.java src | ForEach-Object { $_.FullName })
java -cp out com.statistics.lab02.ProbabilityDistributions
```

## Exercise 1: Implement the four distributions

**Task.** PDF, CDF and PMF for each.

**Steps**
- Implement normal, binomial, Poisson and exponential.
- Compute CDFs without lookup tables.
- Verify each distribution sums or integrates to one.
- Compare against known reference values.

**Deliverable.** A verified distribution suite.

## Exercise 2: Numerical stability

**Task.** Break and fix the direct formulas.

**Steps**
- Evaluate a Poisson tail at large lambda.
- Show factorial overflow and fix it with log space.
- Show normal tail cancellation with 1 - Phi.
- Fix both with the gamma and erfc forms.

**Deliverable.** A stability report with before/after values.

## Exercise 3: Seeded sampling and validation

**Task.** Make simulation trustworthy.

**Steps**
- Implement samplers for all four distributions.
- Verify moments against theory with a sampling-aware tolerance.
- Verify with a goodness-of-fit check.
- Show identical output for identical seeds.

**Deliverable.** Validated, reproducible samplers.

## Exercise 4: Normal approximation with validity checks

**Task.** Know when it is allowed.

**Steps**
- Compare the binomial CDF to its normal approximation across n and p.
- Implement the continuity correction.
- Implement and test the np >= 5 validity gate.
- Find where the approximation fails and explain why.

**Deliverable.** An approximation comparison with a working validity gate.

## Exercise 5: Central limit theorem demonstration

**Task.** See non-normal data become normal in the mean.

**Steps**
- Sample lognormals and heavily skewed data.
- Show the sample distribution is skewed at n = 10.
- Show the sample mean approaches normal by n = 1000.
- Report skewness against n against theory.

**Deliverable.** A CLT demonstration with a skewness-versus-n curve.

## Exercise 6: Poisson overdispersion

**Task.** Find the violated assumption.

**Steps**
- Generate hourly counts with a time-varying rate.
- Compute the dispersion ratio.
- Show the Poisson overstates extreme quantiles.
- Fit a negative binomial and compare.

**Deliverable.** A dispersion analysis with an alternative model.

## Exercise 7: Exponential backoff simulation

**Task.** Connect distributions to a real design choice.

**Steps**
- Simulate retries against exponential versus fixed backoff.
- Model a dependency that fails for a window then recovers.
- Compare total requests and time to recovery.
- Recommend a policy with numbers.

**Deliverable.** A backoff simulation with a recommendation.

## Exercise 8: Monte Carlo with intervals

**Task.** Estimate quantities with no closed form.

**Steps**
- Estimate a tail probability or integral by sampling.
- Repeat the estimate across independent seeds.
- Report the interval and its width.
- Show the interval narrows as sqrt(r).

**Deliverable.** A Monte Carlo report with intervals and a convergence check.


---

## Self-Check Before You Move On

- [ ] I classified the variable before choosing a distribution.
- [ ] My tails are computed in log space.
- [ ] I checked for overdispersion before trusting Poisson.
- [ ] My simulation is reproducible and validated.
