# AutoML Pipelines

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

## 1. The Problem This Solves

Choosing hyperparameters by hand is a search problem, and doing it badly wastes cluster time while quietly overfitting the validation set.

Automated tuning is table stakes, and the interesting part is not the search algorithm: it is budget allocation, early stopping and the statistical discipline that stops you selecting noise.

## 2. Learning Objectives

- Implement grid, random and Bayesian hyperparameter search
- Allocate budget across configurations with early stopping
- Recognise overfitting to the validation set and choose a protocol that avoids it
- Explain surrogate-model based optimisation and its acquisition functions
- Constrain a search space sensibly and prune it with successive halving
- Report tuning results with an honest estimate of the achieved improvement

## 3. Core Concepts

### 3.1 Search strategies trade coverage for efficiency

Grid search is exhaustive and deterministic but wastes budget in high-dimensional spaces. Random search covers a space better per trial because most hyperparameters are unimportant. Bayesian optimisation uses a surrogate to concentrate trials where the objective looks good.

### 3.2 Budget allocation is the real algorithm

With a fixed trial budget, spending it uniformly wastes compute on clearly bad configurations. Successive halving and Hyperband promote promising runs early and kill bad ones late, which is where most of the efficiency comes from in practice.

### 3.3 Surrogate models and acquisition

A Gaussian process or random forest surrogate predicts the objective from the trials so far. The acquisition function trades exploitation (high predicted mean) against exploration (high uncertainty), usually expected improvement or upper confidence bound.

### 3.4 Validation overfitting is the hidden cost

Search dozens or hundreds of configurations against one validation split and you will select noise. The selected score becomes optimistic. Nested cross-validation or a final untouched holdout is the only honest estimate.

### 3.5 Constraint the space before searching

Every unit of a pruned dimension is budget you do not spend. Log-transform positive-skewed hyperparameters, restrict learning rates to plausible ranges, and prune clearly dominated configurations before launching.

### 3.6 Automating the pipeline, not just the model

AutoML that ignores feature handling, leakage and evaluation protocol produces a fast wrong answer. The valuable automation is the parts that are tedious and error-prone, while judgement stays human.

## 4. Key Equations at a Glance

| Symbol | Name | Meaning |
|---|---|---|
| `trials for grid = prod(grid_i)` | Grid size | why it explodes with dimension |
| `expected_coverage gain ~ log(grid)/grid` | Random search coverage | better per trial than grid |
| `EI(x) = E[max(f(x) - f_best, 0)]` | Expected improvement | exploitation versus exploration |
| `UCB(x) = mean(x) + beta sigma(x)` | Upper confidence bound | explicit exploration weight |
| `rung_r evals budget: n, n r, n r^2, ...` | Successive halving | geometric resource allocation |
| `selected_score - holdout_score = optimism` | Selection bias | what nested validation removes |

## 5. How the Pieces Fit Together

1. Define the objective, the budget in trials or wall-clock, and the stopping rule.

2. Constrain and transform the search space; prune dominated configurations.

3. Choose a strategy: random for cheap objectives, Bayesian when trials are expensive.

4. Run with early stopping so bad configurations stop consuming budget.

5. Re-rank with the full budget on the top configurations only.

6. Estimate the improvement on an untouched holdout or nested cross-validation.

## 6. Assumptions and Invariants

- The objective is a single scalar computed on a fixed evaluation protocol
- The search space is log-transformed where appropriate and plausibly bounded
- The budget is fixed in trials or wall-clock and allocated non-uniformly
- Final performance is estimated on data not used for selection
- Every trial's configuration, code version and data version is logged
- The result is compared against a sensible baseline, not against nothing

## 7. Failure Modes You Will Meet in Production

| Symptom | Root cause | Fix |
|---|---|---|
| Selected score 4% better than baseline, holdout shows nothing | validation overfitting from many trials | nested validation or a final untouched holdout |
| Grid search consumes the whole budget on three hyperparameters | exhaustive product of dimensions | random search or Bayesian optimisation with early stopping |
| Learning rate searched on a linear scale from 1e-6 to 1 | resolution wasted where it does not matter | log-scale search over plausible decades |
| Search stops when a metric plateaus | stopping on the mean hides variance | stop on a smoothed metric and repeat seeds |
| Best config overfits the validation fold | single-split selection | nested cross-validation or repeated holdout |
| AutoML result never compared to a baseline | no reference point | always report against a tuned-by-hand or default configuration |

## 8. Java Building Blocks

| API / class | Why it earns its place here |
|---|---|
| `SplittableRandom for reproducible trial sampling` | search reproducibility without a global seed |
| `Function<Double[], Double> for the objective` | the evaluation protocol as a swappable function |
| `PriorityQueue for early stopping in successive halving` | demote the worst rung candidate |
| `record Trial(String id, Map<String,Double> params, double score, int rung, long trialNanos)` | every trial logged with its budget consumed |
| `TreeMap<String, Double> for surrogate parameter space` | deterministic iteration for encoding |

## 9. Where This Sits in the Larger System

- **mlops/lab13** supplies the training loop that trials are timed against.
- **mlops/lab07** runs the tuning job in CI on small budgets.
- **labs/ml/lab10** supplies the evaluation protocol a tuning objective depends on.
- **mlops/lab03** registers the tuned artefact with its configuration.

## 10. Self-Assessment Before You Ship Anything

Score yourself 0-2 on each. Any zero below means you are not ready to operate this in production.

- [ ] 0 — cannot yet — Implement grid, random and Bayesian hyperparameter search
- [ ] 0 — cannot yet — Allocate budget across configurations with early stopping
- [ ] 0 — cannot yet — Recognise overfitting to the validation set and choose a protocol that avoids it
- [ ] 0 — cannot yet — Explain surrogate-model based optimisation and its acquisition functions
- [ ] 0 — cannot yet — Constrain a search space sensibly and prune it with successive halving
- [ ] 0 — cannot yet — Report tuning results with an honest estimate of the achieved improvement

## 11. Summary Checklist

- [ ] My search space is log-transformed and plausibly bounded.
- [ ] My budget is fixed and allocated non-uniformly with early stopping.
- [ ] My final number comes from data not used for selection.
- [ ] Every trial is logged with configuration, code and data version.
- [ ] I report against a baseline, not against nothing.
- [ ] I check variance with repeated seeds rather than trusting a single score.
