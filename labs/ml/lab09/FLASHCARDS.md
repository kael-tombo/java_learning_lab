# Gradient Boosting - Flashcards (60 cards)

**Track:** ml  |  **Lab:** lab09  |  **Level:** Advanced

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
| 1 | What is gradient boosting, formally? | Stage-wise functional gradient descent: each new weak learner fits the negative gradient of the loss with respect to the current prediction. |
| 2 | How does it differ from AdaBoost? | AdaBoost reweights samples; gradient boosting fits gradients directly, which works for any differentiable loss. |
| 3 | What does the learning rate do? | Scales each weak learner's contribution. Small η needs more rounds but generalises better. |
| 4 | Why shallow trees? | Depth controls the interaction order per tree; boosting adds depth across rounds, so depth 1–3 is usually enough. |
| 5 | Why is early stopping essential? | Training loss falls monotonically while validation loss turns; without stopping you ship the overfit tail. |
| 6 | What does stochastic gradient boosting sample? | A fraction of rows per tree, decorrelating the trees like feature randomness does in forests. |
| 7 | Why is boosting explainable? | The model is an exact sum of trees, so per-feature contributions add up to the prediction (treeSHAP). |
| 8 | Why is exact split search too slow at scale? | It sorts and considers every distinct value per feature per node; histogram binning reduces this to a few hundred bins. |
| 9 | What is Stage-wise additive fitting? | Fₘ(x) = Fₗ₋₁(x) + η hₘ(x). |
| 10 | What is The learning rate is the real hyperparameter? | η scales every weak learner's contribution. |
| 11 | What is Gradient boosting versus AdaBoost? | AdaBoost reweights misclassified samples and fits a classifier on the reweighted set. |
| 12 | What is Early stopping and the eval set? | Boosting overfits monotonically on training loss while validation loss turns. |
| 13 | What is Subsampling as stochastic regularisation? | Stochastic gradient boosting samples a fraction of rows per tree. |
| 14 | What is Additivity makes it explainable? | Because the model is a sum of trees, a prediction decomposes exactly into per-feature contributions. |
| 15 | In this lab, what does `Fₘ(x) = Fₗ₋₁(x) + η hₘ(x)` mean? | Boosting update: add a weak learner, scaled |
| 16 | In this lab, what does `rᵢ = yᵢ − F(xᵢ)` mean? | Residual (squared error): negative gradient for least squares |
| 17 | In this lab, what does `gᵢ = pᵢ − yᵢ (log loss)` mean? | Negative gradient (logistic): the analogue for classification |
| 18 | In this lab, what does `η ∈ (0, 1]` mean? | Learning rate: shrinkage; small η needs more rounds |
| 19 | In this lab, what does `v(x) = Σ_{m} η Tₘ(x)` mean? | Ensemble value: sum of tree outputs, exactly additive |
| 20 | In this lab, what does `early stop at argmin_m val_loss(m)` mean? | Early stopping: the standard safeguard |
| 21 | In this lab, what does `SHAP_i ≈ γ^T E[\|S ∪ {i}\|]` mean? | TreeSHAP: exact additive attribution for tree ensembles |
| 22 | You see 'Train loss keeps falling, validation loss turns at round 40' in production. What is the cause and the fix? | training continued past the optimum Fix: early stop on validation loss and ship the best round |
| 23 | You see 'The model is worse than a random forest' in production. What is the cause and the fix? | depth too large and η too small, or no subsampling Fix: try depth 2–3, η 0.05–0.1, subsample 0.8 |
| 24 | You see 'SHAP values sum to something other than the prediction' in production. What is the cause and the fix? | missing the baseline expectation term Fix: use the tree_path_dependent method and verify the additivity identity |
| 25 | You see 'Predictions change after deploy' in production. What is the cause and the fix? | categorical encoding or scaling done outside the estimator Fix: version preprocessing inside the model artifact |
| 26 | You see 'Training is slow on 5M rows' in production. What is the cause and the fix? | exact splits on all features Fix: histogram binning: pre-bucket features into 64–256 bins |
| 27 | You see 'Boosting importance looks like importance' in production. What is the cause and the fix? | correlated features split credit arbitrarily Fix: use SHAP values on held-out data, not gain-based importance |
| 28 | Which Java API is the backbone of: histogram binning turns split search into integer counting | `int[] binIndex per feature` |
| 29 | Which Java API is the backbone of: SHAP value computation over tree paths | `PriorityQueue<Double> leafValues` |
| 30 | Which Java API is the backbone of: the classic boosting inner loop | `Arrays.sort on per-feature histograms` |
| 31 | Which Java API is the backbone of: per-tree row subsampling that stays reproducible | `SplittableRandom` |
| 32 | Which Java API is the backbone of: cheap first pass before investing in SHAP | `double[][] featureImportance by gain` |
| 33 | Why does Stage-wise additive fitting matter operationally? | Fₘ(x) = Fₗ₋₁(x) + η hₘ(x). |
| 34 | Why does The learning rate is the real hyperparameter matter operationally? | η scales every weak learner's contribution. |
| 35 | Why does Gradient boosting versus AdaBoost matter operationally? | AdaBoost reweights misclassified samples and fits a classifier on the reweighted set. |
| 36 | Why does Early stopping and the eval set matter operationally? | Boosting overfits monotonically on training loss while validation loss turns. |
| 37 | Why does Subsampling as stochastic regularisation matter operationally? | Stochastic gradient boosting samples a fraction of rows per tree. |
| 38 | Why does Additivity makes it explainable matter operationally? | Because the model is a sum of trees, a prediction decomposes exactly into per-feature contributions. |
| 39 | In the Gradient Boosting pipeline, what happens next? Split into train/validation/test; the validation split drive... | Split into train/validation/test; the validation split drives early stopping and is not the test set. |
| 40 | In the Gradient Boosting pipeline, what happens next? Initialise F₀ with a constant (mean target, or log-odds for ... | Initialise F₀ with a constant (mean target, or log-odds for logistic loss). |
| 41 | In the Gradient Boosting pipeline, what happens next? For each round m: compute negative gradients, fit a shallow ... | For each round m: compute negative gradients, fit a shallow tree on them, update F ← F + η hₘ. |
| 42 | In the Gradient Boosting pipeline, what happens next? Track validation loss every round; keep the best round.... | Track validation loss every round; keep the best round. |
| 43 | In the Gradient Boosting pipeline, what happens next? Sweep η and depth jointly, and pick the pair with the best v... | Sweep η and depth jointly, and pick the pair with the best validation loss at a comparable round count. |
| 44 | In the Gradient Boosting pipeline, what happens next? Fit the final model with the chosen M, then extract SHAP val... | Fit the final model with the chosen M, then extract SHAP values for explanations and importance. |
| 45 | Exercise focus: Boosting from scratch, squared error | Implement the full loop by hand once. |
| 46 | Exercise focus: Functional gradients for three losses | Show the framework generalises. |
| 47 | Exercise focus: Tune eta and rounds jointly | Refuse the one-knob-at-a-time trap. |
| 48 | Exercise focus: Early stopping, properly | Ship the best round and prove it. |
| 49 | Exercise focus: AdaBoost versus gradient boosting | Implement the reweighting variant and compare. |
| 50 | Exercise focus: Histogram binning | Make it fast enough to matter. |
| 51 | State the From residuals to functional gradients result for Gradient Boosting. | y = [1, 3, 5], F = [1, 1, 1]. Residuals = [0, 2, 4]; the next tree fits them and F becomes [1, 3, 5]. Squared loss drops from 20/3 to 0. |
| 52 | State the Shrinkage as regularisation result for Gradient Boosting. | eta = 1.0 reaches train error 0 in 6 rounds but test error 0.24. eta = 0.05 needs 120 rounds and reaches test error 0.11. |
| 53 | State the Early stopping as a bias-variance knob result for Gradient Boosting. | Validation loss by round: 50 → 0.21, 100 → 0.14, 200 → 0.13, 400 → 0.18. Best round 200; without early stopping you ship round 400 at 0.18. |
| 54 | State the Histogram binning cost result for Gradient Boosting. | 5M rows × 50 features: exact search visits ~250M candidate splits per level; histogram visits 5M × 256 = 1.28B per level but with contiguous memory and no sorting — net 10–50x faster in practice. |
| 55 | State the Additivity and TreeSHAP result for Gradient Boosting. | For a 20-feature tree ensemble, TreeSHAP is O(TLD²) versus sampling-based methods at ~200 evaluations; the additivity identity holds to 1e-9. |
| 56 | State the Stochastic gradient boosting result for Gradient Boosting. | On a noisy tabular dataset, rho = 0.8 with depth 3 improves test error from 0.17 to 0.14 while allowing eta = 0.1 (faster convergence than eta = 0.03). |
| 57 | How do you choose the number of rounds? | From validation loss with a patience window; ship the best round, not the last. |
| 58 | What is the initial prediction F₀? | The value that minimises the loss with no features: the mean for squared error, the log-odds for logistic loss. |
| 59 | When does boosting beat a random forest? | On medium-sized tabular data with strong signal in a few features, and when you need the additive explanations. |
| 60 | What causes a boosting model to underfit? | Too few rounds, too small a learning rate, too shallow trees, or unscaled/unsuitable features. |

## Deck Notes

- Rows are generated from this lab's own concepts, equations, failure modes and Java APIs - if you disagree with a card, fix the card.
- The last block of cards is deliberately operational: they are the questions a staff engineer gets asked in a design review.
