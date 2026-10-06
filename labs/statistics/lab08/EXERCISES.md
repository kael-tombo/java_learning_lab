# Experimental Design - Exercises

**Track:** statistics  |  **Lab:** lab08  |  **Level:** Advanced

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
cd lab08
javac -d out $(Get-ChildItem -Recurse -Filter *.java src | ForEach-Object { $_.FullName })
java -cp out com.statistics.lab08.ExperimentalDesign
```

## Exercise 1: Sample size for means and proportions

**Task.** The arithmetic behind power.

**Steps**
- Implement both sample size formulas.
- Compute n for a realistic conversion target.
- Show how n changes with the effect size.
- Verify the computed n reaches the target power in simulation.

**Deliverable.** A verified sample size calculator.

## Exercise 2: Blocking and variance reduction

**Task.** Quantify the gain.

**Steps**
- Simulate units with a known within-block correlation.
- Analyse blocked and unblocked.
- Compare variances and required n.
- Compute the reduction factor.

**Deliverable.** A blocking gain demonstration.

## Exercise 3: Factorial design analysis

**Task.** Main effects and interaction.

**Steps**
- Design a 2x2 with replication.
- Compute main effects and the interaction contrast.
- Construct data with a significant interaction.
- Show why marginal means mislead.

**Deliverable.** A factorial analysis with an interaction story.

## Exercise 4: Confounding demonstration

**Task.** What no sample size can fix.

**Steps**
- Construct a confounded design and estimate.
- Show that two coefficient pairs fit identically.
- Add within-cell replication and show identifiability returns.
- Explain the implication for observational work.

**Deliverable.** An identifiability demonstration.

## Exercise 5: Power curves

**Task.** Design against a range of effects.

**Steps**
- Compute power across a grid of effect sizes.
- Plot power against n.
- Mark the n for 80% power at several effects.
- Report the achievable MDE at your n.

**Deliverable.** Power curves with a marked operating point.

## Exercise 6: Simulation study

**Task.** Validate the design end to end.

**Steps**
- Simulate the whole study under the design.
- Estimate coverage and power across many replications.
- Compare with the analytic calculation.
- Report any discrepancy and explain it.

**Deliverable.** A simulation validating the analytic power.

## Exercise 7: Pre-specified analysis plan

**Task.** Decide before data.

**Steps**
- Write the estimand, hypotheses and contrasts.
- Specify the model and the decision rule.
- Specify what happens for each outcome, including inconclusive.
- Store the plan with a timestamp and commit it.

**Deliverable.** A committed analysis plan.

## Exercise 8: Full design review

**Task.** Critique a real study.

**Steps**
- Take a real or realistic study description.
- Identify the estimand, unit and design.
- Find at least three flaws: confounding, power, blocking.
- Write the redesign with computed sample size.

**Deliverable.** A critique with a powered redesign.


---

## Self-Check Before You Move On

- [ ] My estimand is written and estimable.
- [ ] My sample size came from a power calculation.
- [ ] I blocked on the dominant nuisance variance.
- [ ] I test the interaction before reporting main effects.
