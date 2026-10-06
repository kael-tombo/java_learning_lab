# MINI_PROJECT — Budgeted Hyperparameter Search with Honest Reporting

**Track:** mlops  |  **Lab:** lab14  |  **Level:** Advanced

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

**Brief.** Compare grid, random and Bayesian search under a fixed budget, then report the result honestly.

**Timebox.** 4 hours

## 1. Why This Project Exists

Tuning is where teams most often fool themselves. This project makes the self-deception measurable.

## 2. Requirements

- Log-scaled, bounded search space with pruning and a stated justification per range.
- Grid, random and a simple Bayesian search with expected improvement, at equal trial budget.
- Successive halving allocation compared against uniform at the same total budget.
- Trials-to-target comparison across strategies.
- Selection bias quantified: best-of-N reported score versus fresh-sample truth.
- Final estimate from a holdout not used for selection, plus variance across 5 seeds.
- Tuning report: space, budget, strategy, all trials, baseline, honest final number.

## 3. Build Order

| Step | Time | What you do | Done when |
|---|---|---|---|
| 1 | 30m | Search space design with log scaling and pruning | A justified, pruned space |
| 2 | 40m | Implement grid, random and Bayesian search | Three strategies, one objective |
| 3 | 35m | Successive halving vs uniform allocation | An allocation comparison |
| 4 | 30m | Trials-to-target at equal budget | A comparison table |
| 5 | 30m | Selection bias simulation and quantification | A bias curve |
| 6 | 30m | Final holdout estimate with 5-seed variance | An honest final number |
| 7 | 30m | Publish the tuning report | A report a reviewer accepts |

## 4. Architecture Sketch

```text
 space (log-scaled, pruned) --> objective (fixed protocol)
     |
  +--+-----------+------------+
  |                          |
 grid / random          Bayesian surrogate
 at equal budget         + expected improvement
  |                          |
  +------------+-------------+
               |
        successive halving vs uniform
               |
        trials-to-target comparison
               |
   best-of-N reported score vs fresh-sample truth  (selection bias)
               |
   final holdout + 5-seed variance --> tuning report
```

## 5. Implementation Notes

- Use one objective function for every strategy; changing the protocol mid-comparison invalidates it.
- Trials-to-target is the fair comparison at equal budget, not best score at whatever cost each incurred.
- Simulate the selection bias so the number is memorable rather than abstract.
- Report the baseline and the holdout score; a tuned number alone is uninterpretable.

## 6. Deliverables

1. Justified, pruned search space with per-range rationale.
1. Three strategies at equal budget with a trials-to-target comparison.
1. Allocation comparison between successive halving and uniform.
1. Selection bias curve plus a tuning report with holdout and variance.

## 7. Grading Rubric

| Dimension | Weight | What earns full marks |
|---|---|---|
| Design | 25% | Log scaling, bounds and pruning justified |
| Comparison fairness | 25% | Equal budget, one objective, trials-to-target metric |
| Budget allocation | 20% | Successive halving demonstrably better than uniform |
| Honesty | 20% | Selection bias quantified; holdout and variance reported |
| Communication | 10% | A complete, reviewable tuning report |

## 8. Stretch Goals

- Add Hyperband brackets and compare against single-bracket halving.
- Add warm-starting from a previous run's trials.
- Add a multi-objective variant producing a Pareto front over accuracy and latency.

## 9. Definition of Done

You are finished when every box below is checked, not when the code compiles.

- [ ] Log-scaled, bounded search space with pruning and a stated justification per range.
- [ ] Grid, random and a simple Bayesian search with expected improvement, at equal trial budget.
- [ ] Successive halving allocation compared against uniform at the same total budget.
- [ ] Trials-to-target comparison across strategies.
- [ ] Selection bias quantified: best-of-N reported score versus fresh-sample truth.
- [ ] Final estimate from a holdout not used for selection, plus variance across 5 seeds.
- [ ] A stranger can reproduce the reported numbers with one command
- [ ] The limitations section says what this cannot do
- [ ] At least one number is alerted on in production

## 10. Retrospective Template

- What worked:
- What surprised me:
- The one number I would alert on in production:
- What I would delete before shipping this to real users:
