# Bayesian Statistics - Exercises

**Track:** statistics  |  **Lab:** lab06  |  **Level:** Advanced

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
cd lab06
javac -d out $(Get-ChildItem -Recurse -Filter *.java src | ForEach-Object { $_.FullName })
java -cp out com.statistics.lab06.BayesianStatistics
```

## Exercise 1: Conjugate beta-binomial

**Task.** The arithmetic, then the intuition.

**Steps**
- Implement the conjugate update and the posterior mean.
- Compute an HDI from sampled draws.
- Compare equal-tailed and HDI on a skewed posterior.
- Interpret a prior as pseudo-counts.

**Deliverable.** A conjugate implementation with an HDI.

## Exercise 2: Prior sensitivity

**Task.** Does the prior matter here?

**Steps**
- Run the analysis under three defensible priors.
- Compare posteriors and conclusions.
- Compute prior weight as a function of n.
- Find the n at which the prior stops mattering.

**Deliverable.** A sensitivity table with a justified conclusion.

## Exercise 3: Prior predictive checks

**Task.** Test the model before the data.

**Steps**
- Simulate datasets from the prior.
- Compare simulated to observed summaries.
- Show a bad prior failing the check.
- Adjust the prior and re-check.

**Deliverable.** A prior predictive report.

## Exercise 4: MCMC with diagnostics

**Task.** Do not trust unverified draws.

**Steps**
- Implement a seeded sampler for a simple posterior.
- Compute R-hat across chains and effective sample size.
- Show a deliberately poorly mixed sampler failing.
- Summarise only after diagnostics pass.

**Deliverable.** A sampler with enforced diagnostics.

## Exercise 5: Posterior comparison

**Task.** Answer the decision question.

**Steps**
- Sample two posteriors for competing designs.
- Compute P(A > B) with a Monte Carlo interval.
- Compare with a naive point-estimate comparison.
- Write the recommendation.

**Deliverable.** A comparison with a decision probability.

## Exercise 6: Posterior predictive checking

**Task.** Test the model, not just the parameters.

**Steps**
- Simulate y from the posterior.
- Compare a test statistic of simulated to observed.
- Detect a model misspecification this way.
- Revise the model and re-check.

**Deliverable.** A predictive check that catches a misspecification.

## Exercise 7: Credible versus confidence

**Task.** Make the distinction concrete.

**Steps**
- Compute both intervals for the same data.
- Explain each in one sentence a stakeholder understands.
- Show where they differ and why.
- Report both correctly in a written summary.

**Deliverable.** A comparison write-up.

## Exercise 8: Full Bayesian analysis

**Task.** An end-to-end report.

**Steps**
- State the question as a probability about a parameter.
- Choose and justify the prior; run sensitivity and predictive checks.
- Compute the posterior and summarise with an HDI.
- Answer the decision question and write limitations.

**Deliverable.** A complete Bayesian report.


---

## Self-Check Before You Move On

- [ ] My prior has a stated rationale and I varied it.
- [ ] My chains converged before I summarised them.
- [ ] My interval says what it is: a credible interval.
- [ ] My decision is a probability, not a point comparison.
