# AutoML Pipelines - Mathematical Foundations

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

## Notation

| Symbol | Meaning |
|---|---|
| `trials for grid = prod(grid_i)` | Grid size - why it explodes with dimension |
| `expected_coverage gain ~ log(grid)/grid` | Random search coverage - better per trial than grid |
| `EI(x) = E[max(f(x) - f_best, 0)]` | Expected improvement - exploitation versus exploration |
| `UCB(x) = mean(x) + beta sigma(x)` | Upper confidence bound - explicit exploration weight |
| `rung_r evals budget: n, n r, n r^2, ...` | Successive halving - geometric resource allocation |
| `selected_score - holdout_score = optimism` | Selection bias - what nested validation removes |

## Why the Math Matters

Tuning is optimisation under a fixed budget plus the statistics of selecting the maximum of many noisy estimates; both halves have to be right or the reported improvement is fictional.


---

## 1. Search space size and why grid explodes

```text
grid trials = prod_i |grid_i|
random search coverage grows ~ log(N)/N in the important dimensions
Bayesian: trials needed ~ log(best region / total) rather than |space|
```

Grid cost is multiplicative in dimension, which is why teams hit a budget wall at four hyperparameters. Random and Bayesian methods buy efficiency by not insisting on coverage of unimportant regions.

**Worked example.** Five hyperparameters with 5 values each: grid is 3,125 trials. At 20 minutes per trial that is 43 days. Random search with 100 trials explores each dimension 20 times, which is usually enough to find the good region.


---

## 2. Expected improvement

```text
EI(x) = E[max(f(x) - f_best - xi, 0)]
for a GP posterior: EI decomposes into mean gain and variance gain
xi is the exploration knob trading off improvement against uncertainty
```

Expected improvement is the acquisition function that asks directly: how much better might this trial be? It spends trials where either the mean is good or the uncertainty is high.

**Worked example.** Two candidates with the same predicted mean of 0.90: one with sigma 0.01 and one with 0.15. EI is far higher for the uncertain one, so it gets the trial, which is exactly the behaviour you want early in a search.


---

## 3. Successive halving resource allocation

```text
bracket: n configs start with r0 resources
each rung: keep top 1/r, multiply resources by r
with eta = 4: keep 25%, resources x4
final rung: top configs get the full budget
```

Promoting early and killing late spends most of the budget on configurations that plausibly win. With a fixed budget this beats uniform allocation substantially, and it needs no surrogate model.

**Worked example.** Budget 100 trial-units over 25 configs, eta = 4: 25 get 1 unit (25 total), the best 6 get 4 (24), the best 1-2 get 16 (32), and the winner gets the remaining 19. A uniformly funded 4 configs would give each 25 units.


---

## 4. Selection bias in tuning

```text
selected = max over T trials of score_t
bias = E[selected] - E[true best on fresh data]
bias grows with T and with the noise in the score
```

Selecting the maximum of many noisy estimates is biased upward. The bias scales with the number of trials, so doubling the search inflates the reported improvement even with no real gain.

**Worked example.** Trial scores from a normal with sigma = 0.01 and a true best of 0.90: best of 10 trials averages 0.932, best of 100 averages 0.947. The reported gain inflates by 1.5 points purely from more trials.


---

## Cheat Sheet

- `trials for grid = prod(grid_i)` - Grid size
- `expected_coverage gain ~ log(grid)/grid` - Random search coverage
- `EI(x) = E[max(f(x) - f_best, 0)]` - Expected improvement
- `UCB(x) = mean(x) + beta sigma(x)` - Upper confidence bound
- `rung_r evals budget: n, n r, n r^2, ...` - Successive halving
- `selected_score - holdout_score = optimism` - Selection bias

## Numerical Traps

- Computing grid size multiplicatively and then wondering why the budget ran out.
- Searching a learning rate linearly instead of logarithmically.
- Reporting the best-of-N trial score as the model's performance.
- Stopping on the raw metric so noise decides the search.
- Comparing a tuned result against no baseline at all.

## Self-Check Problems

1. Compute grid size and estimate wall-clock for a given space and per-trial cost.
2. Compare random and grid coverage at a fixed budget for a five-dimensional space.
3. Implement expected improvement for a Gaussian process surrogate on a small problem.
4. Allocate a budget with successive halving across rungs and show the allocation.
5. Quantify selection bias for best-of-10 versus best-of-100 on synthetic trials.
