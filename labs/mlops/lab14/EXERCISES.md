# AutoML Pipelines - Exercises

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

## How To Work These

Work in order. Each exercise builds the next; do not skip ahead.
Every exercise ends with a *deliverable* you can show someone - code that compiles, a number you can defend, or a table you can regenerate.

Run the lab as you go:

```bash
cd lab14
javac -d out $(Get-ChildItem -Recurse -Filter *.java src | ForEach-Object { $_.FullName })
java -cp out AutoMLLab
```

## Exercise 1: Grid, random and Bayesian search

**Task.** Three strategies, one objective.

**Steps**
- Implement a log-scaled search space.
- Implement grid and random search with pruning.
- Implement a simple surrogate with expected improvement.
- Compare trials-to-target across the three.

**Deliverable.** A comparison with a trials-to-target table.

## Exercise 2: Successive halving budget

**Task.** Spend the budget where it matters.

**Steps**
- Implement rungs with a configurable reduction factor.
- Allocate a fixed budget and report per-rung spend.
- Compare against uniform allocation at the same total budget.
- Show the win rate at the final rung.

**Deliverable.** An allocation comparison with a win rate.

## Exercise 3: Selection bias, quantified

**Task.** See the illusion you are avoiding.

**Steps**
- Simulate trials from a known true best with known noise.
- Compute best-of-10 versus best-of-100 reported scores.
- Evaluate on a fresh sample to get the honest number.
- Report the bias as a function of trial count.

**Deliverable.** A bias curve showing how more trials inflate the reported gain.

## Exercise 4: Search space design

**Task.** Constraint before you search.

**Steps**
- Design a space for learning rate, depth, regularisation and subsample.
- Log-transform where appropriate and justify each range.
- Prune dominated configurations.
- Show the budget saving from pruning.

**Deliverable.** A documented space with a measured budget saving.

## Exercise 5: Noise and repeated seeds

**Task.** Make sure you are not selecting noise.

**Steps**
- Run the top configurations with 5 seeds each.
- Report mean and standard deviation.
- Show configurations whose apparent gap vanishes under repetition.
- Adopt a selection rule requiring a minimum margin.

**Deliverable.** A variance table and an adopted selection rule.

## Exercise 6: Nested validation

**Task.** An honest final estimate.

**Steps**
- Implement an outer fold and an inner tuning loop.
- Report the inner-selected score and the outer-holdout score.
- Compare with selecting on a single split.
- Quantify the optimism removed.

**Deliverable.** A nested result with the optimism quantified.

## Exercise 7: Early stopping on a noisy metric

**Task.** Do not stop on a spike.

**Steps**
- Implement smoothed and raw stopping rules.
- Simulate noisy objective curves.
- Compare how often each rule stops early on a losing configuration.
- Adopt a rule with measured behaviour.

**Deliverable.** A stopping-rule comparison.

## Exercise 8: Tuning report

**Task.** Communicate the result honestly.

**Steps**
- Publish the search space, budget, strategy and all trials.
- Report the selected score and the holdout score separately.
- Include the baseline and a variance estimate.
- Write the recommendation and its caveats.

**Deliverable.** A tuning report a reviewer would accept.


---

## Self-Check Before You Move On

- [ ] My search space is log-scaled where it should be.
- [ ] My reported improvement is not selection bias.
- [ ] My budget was allocated, not spent uniformly.
- [ ] I compare against a sensible baseline.
