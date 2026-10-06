# AutoML Pipelines - Flashcards (60 cards)

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

**Format.** Question (front) -> answer (back). Use for spaced repetition: day 0, day 1, day 3, day 7, day 21. Do not read the answer first.

| # | Front | Back |
|---|---|---|
| 1 | Why is random search better than grid search per trial? | Most hyperparameters are unimportant, and random sampling covers the important dimensions more evenly. |
| 2 | What is successive halving? | Give configurations increasing resources, promoting the best and killing the worst at each rung. |
| 3 | What does EI stand for in Bayesian optimisation? | Expected improvement, trading exploitation of good regions against exploring uncertain ones. |
| 4 | Why search learning rates on a log scale? | Orders of magnitude matter; a linear grid wastes resolution where the optimum is never. |
| 5 | What is validation overfitting? | Selecting the best of many trials on one split inflates the reported score by selecting noise. |
| 6 | How do you fix validation overfitting? | Nested cross-validation, or a final untouched holdout used exactly once. |
| 7 | Why prune the search space first? | Each removed dimension is budget you can spend on the dimensions that matter. |
| 8 | What does AutoML automate most valuably? | The tedious repetitive parts: search, early stopping and re-ranking, while judgement stays human. |
| 9 | What is Search strategies trade coverage for efficiency? | Grid search is exhaustive and deterministic but wastes budget in high-dimensional spaces. |
| 10 | What is Budget allocation is the real algorithm? | With a fixed trial budget, spending it uniformly wastes compute on clearly bad configurations. |
| 11 | What is Surrogate models and acquisition? | A Gaussian process or random forest surrogate predicts the objective from the trials so far. |
| 12 | What is Validation overfitting is the hidden cost? | Search dozens or hundreds of configurations against one validation split and you will select noise. |
| 13 | What is Constraint the space before searching? | Every unit of a pruned dimension is budget you do not spend. |
| 14 | What is Automating the pipeline, not just the model? | AutoML that ignores feature handling, leakage and evaluation protocol produces a fast wrong answer. |
| 15 | In this lab, what does `trials for grid = prod(grid_i)` mean? | Grid size: why it explodes with dimension |
| 16 | In this lab, what does `expected_coverage gain ~ log(grid)/grid` mean? | Random search coverage: better per trial than grid |
| 17 | In this lab, what does `EI(x) = E[max(f(x) - f_best, 0)]` mean? | Expected improvement: exploitation versus exploration |
| 18 | In this lab, what does `UCB(x) = mean(x) + beta sigma(x)` mean? | Upper confidence bound: explicit exploration weight |
| 19 | In this lab, what does `rung_r evals budget: n, n r, n r^2, ...` mean? | Successive halving: geometric resource allocation |
| 20 | In this lab, what does `selected_score - holdout_score = optimism` mean? | Selection bias: what nested validation removes |
| 21 | You see 'Selected score 4% better than baseline, holdout shows nothing' in production. What is the cause and the fix? | validation overfitting from many trials Fix: nested validation or a final untouched holdout |
| 22 | You see 'Grid search consumes the whole budget on three hyperparameters' in production. What is the cause and the fix? | exhaustive product of dimensions Fix: random search or Bayesian optimisation with early stopping |
| 23 | You see 'Learning rate searched on a linear scale from 1e-6 to 1' in production. What is the cause and the fix? | resolution wasted where it does not matter Fix: log-scale search over plausible decades |
| 24 | You see 'Search stops when a metric plateaus' in production. What is the cause and the fix? | stopping on the mean hides variance Fix: stop on a smoothed metric and repeat seeds |
| 25 | You see 'Best config overfits the validation fold' in production. What is the cause and the fix? | single-split selection Fix: nested cross-validation or repeated holdout |
| 26 | You see 'AutoML result never compared to a baseline' in production. What is the cause and the fix? | no reference point Fix: always report against a tuned-by-hand or default configuration |
| 27 | Which Java API is the backbone of: search reproducibility without a global seed | `SplittableRandom for reproducible trial sampling` |
| 28 | Which Java API is the backbone of: the evaluation protocol as a swappable function | `Function<Double[], Double> for the objective` |
| 29 | Which Java API is the backbone of: demote the worst rung candidate | `PriorityQueue for early stopping in successive halving` |
| 30 | Which Java API is the backbone of: every trial logged with its budget consumed | `record Trial(String id, Map<String,Double> params, double score, int rung, long trialNanos)` |
| 31 | Which Java API is the backbone of: deterministic iteration for encoding | `TreeMap<String, Double> for surrogate parameter space` |
| 32 | Why does Search strategies trade coverage for efficiency matter operationally? | Grid search is exhaustive and deterministic but wastes budget in high-dimensional spaces. |
| 33 | Why does Budget allocation is the real algorithm matter operationally? | With a fixed trial budget, spending it uniformly wastes compute on clearly bad configurations. |
| 34 | Why does Surrogate models and acquisition matter operationally? | A Gaussian process or random forest surrogate predicts the objective from the trials so far. |
| 35 | Why does Validation overfitting is the hidden cost matter operationally? | Search dozens or hundreds of configurations against one validation split and you will select noise. |
| 36 | Why does Constraint the space before searching matter operationally? | Every unit of a pruned dimension is budget you do not spend. |
| 37 | Why does Automating the pipeline, not just the model matter operationally? | AutoML that ignores feature handling, leakage and evaluation protocol produces a fast wrong answer. |
| 38 | In the AutoML Pipelines pipeline, what happens next? Define the objective, the budget in trials or wall-clock, an... | Define the objective, the budget in trials or wall-clock, and the stopping rule. |
| 39 | In the AutoML Pipelines pipeline, what happens next? Constrain and transform the search space; prune dominated co... | Constrain and transform the search space; prune dominated configurations. |
| 40 | In the AutoML Pipelines pipeline, what happens next? Choose a strategy: random for cheap objectives, Bayesian whe... | Choose a strategy: random for cheap objectives, Bayesian when trials are expensive. |
| 41 | In the AutoML Pipelines pipeline, what happens next? Run with early stopping so bad configurations stop consuming... | Run with early stopping so bad configurations stop consuming budget. |
| 42 | In the AutoML Pipelines pipeline, what happens next? Re-rank with the full budget on the top configurations only.... | Re-rank with the full budget on the top configurations only. |
| 43 | In the AutoML Pipelines pipeline, what happens next? Estimate the improvement on an untouched holdout or nested c... | Estimate the improvement on an untouched holdout or nested cross-validation. |
| 44 | Exercise focus: Grid, random and Bayesian search | Three strategies, one objective. |
| 45 | Exercise focus: Successive halving budget | Spend the budget where it matters. |
| 46 | Exercise focus: Selection bias, quantified | See the illusion you are avoiding. |
| 47 | Exercise focus: Search space design | Constraint before you search. |
| 48 | Exercise focus: Noise and repeated seeds | Make sure you are not selecting noise. |
| 49 | Exercise focus: Nested validation | An honest final estimate. |
| 50 | State the Search space size and why grid explodes result for AutoML Pipelines. | Five hyperparameters with 5 values each: grid is 3,125 trials. At 20 minutes per trial that is 43 days. Random search with 100 trials explores each dimension 20 times, which is usually enough to find the good region. |
| 51 | State the Expected improvement result for AutoML Pipelines. | Two candidates with the same predicted mean of 0.90: one with sigma 0.01 and one with 0.15. EI is far higher for the uncertain one, so it gets the trial, which is exactly the behaviour you want early in a search. |
| 52 | State the Successive halving resource allocation result for AutoML Pipelines. | Budget 100 trial-units over 25 configs, eta = 4: 25 get 1 unit (25 total), the best 6 get 4 (24), the best 1-2 get 16 (32), and the winner gets the remaining 19. A uniformly funded 4 configs would give each 25 units. |
| 53 | State the Selection bias in tuning result for AutoML Pipelines. | Trial scores from a normal with sigma = 0.01 and a true best of 0.90: best of 10 trials averages 0.932, best of 100 averages 0.947. The reported gain inflates by 1.5 points purely from more trials. |
| 54 | When is Bayesian optimisation worth it? | When each trial is expensive, so the surrogate pays for itself in saved trials. |
| 55 | What is Hyperband? | Successive halving across multiple brackets to hedge the resource schedule you do not know in advance. |
| 56 | Why stop on a smoothed metric rather than the raw one? | Raw metrics are noisy; smoothing prevents stopping on a favourable spike. |
| 57 | Why repeat seeds? | Because the variance across seeds can exceed the difference between configurations you are trying to detect. |
| 58 | Assumption / invariant to defend: The objective is a single scalar computed on a fixed evaluation protoc... | The objective is a single scalar computed on a fixed evaluation protocol |
| 59 | Assumption / invariant to defend: The search space is log-transformed where appropriate and plausibly bo... | The search space is log-transformed where appropriate and plausibly bounded |
| 60 | Assumption / invariant to defend: The budget is fixed in trials or wall-clock and allocated non-uniforml... | The budget is fixed in trials or wall-clock and allocated non-uniformly |

## Deck Notes

- Rows are generated from this lab's own concepts, equations, failure modes and Java APIs - if you disagree with a card, fix the card.
- The last block of cards is deliberately operational: they are the questions a staff engineer gets asked in a design review.
