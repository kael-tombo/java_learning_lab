# Decision Trees & Random Forests

**Track:** ml  |  **Lab:** lab03  |  **Level:** Intermediate

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

Linear models assume the world is smooth. Trees let you carve the feature space with axis-aligned boxes and capture thresholds, interactions and non-monotone effects with no transformation.

Trees are the weak learner inside boosting (Lab 09) and the interpretable model of choice wherever an auditor asks 'why'.

## 2. Learning Objectives

- Compute entropy and Gini impurity and pick the split that maximises impurity reduction
- Implement CART regression and classification trees with a stopping rule
- Explain bagging: bootstrap resampling plus decorrelated feature subsets
- Read feature-importance numbers critically, including their bias
- Control overfitting with depth, min-samples and min-impurity thresholds
- Quantify the bias-variance trade-off as forest size grows

## 3. Core Concepts

### 3.1 Impurity and information gain

A leaf is pure when all labels match; impurity measures the opposite. Information gain IG(S,A) = impurity(S) − Σ_v (|S_v|/|S|)impurity(S_v). Entropy uses base-2 logs and is measured in bits; Gini is cheaper and usually picks the same splits, differing mainly on tiny datasets.

### 3.2 Greedy recursive partitioning

Trees are built top-down, greedily taking the best split at each node. This is not globally optimal — a split that looks terrible now may enable an excellent split later. It is fast and, in practice, good enough; nobody solves the optimal-decision-tree problem in production.

### 3.3 Overfitting and the stopping rule

An unrestricted tree memorises the training set: 100% train accuracy and a worse test score than a stump. Stop on max_depth, min_samples_split, min_samples_leaf or min_impurity_decrease. Validation curves, not intuition, should pick these.

### 3.4 Bagging and why it works

Each tree sees a bootstrap sample (n draws with replacement), so trees are diverse but individually high-variance. Averaging predictions cancels uncorrelated variance: variance of a mean of B independent trees with variance σ² is σ²/B. You cannot parallelise bagging without that independence.

### 3.5 Random forests and feature randomness

At each split, forests consider only a random subset of m features (typically √d). Without it, the strongest feature would be chosen at every node and all trees would be near-identical — low diversity, no variance reduction. This single change is why forests beat plain bagging.

### 3.6 Feature importance, honestly

Impurity-based importance (total impurity decrease, weighted by node size) biasedly favours high-cardinality features. Permutation importance on held-out data is the defensible default. Report permutation importance with error bars, or do not report importance at all.

## 4. Key Equations at a Glance

| Symbol | Name | Meaning |
|---|---|---|
| `H(S) = −Σ p(c) log₂ p(c)` | Entropy | uncertainty of the label distribution (bits) |
| `Gini(S) = 1 − Σ p(c)²` | Gini impurity | cheaper alternative, same split choices |
| `IG = impurity(S) − Σ (n_v/n) impurity(S_v)` | Information gain | drop in impurity from a split |
| `P(β) = 1/n Σ 1[yᵢ in bootstrap]` | Bootstrap sample | n draws with replacement from n rows |
| `Var(mean of B) = σ²/B` | Variance reduction | why averaging helps, only if trees differ |
| `OOB error` | Out-of-bag estimate | each row's error from trees that never saw it — free cross-validation |

## 5. How the Pieces Fit Together

1. Encode categoricals as ordinal splits or one-hot; decide explicitly, because a tree will exploit the encoding.

2. At each node, evaluate every candidate threshold on a random feature subset and take the best.

3. Split while depth/size/impurity rules allow; a pure node becomes a leaf.

4. Leaf value: mean target (regression) or majority class / class proportions (classification).

5. Grow B trees on bootstrap samples; average or majority-vote the predictions.

6. Read permutation importance on held-out data, then prune or re-fit if importance is diffuse.

## 6. Assumptions and Invariants

- Features are comparable or explicitly one-hot encoded; ordinal encoding of nominals invents order
- Splits are axis-aligned — rotation-sensitive, so scaling does not matter but geometry does
- Bootstrap diversity holds; correlated trees (highly collinear features) reduce the benefit
- Enough samples per leaf; otherwise leaves memorise noise
- Features are available at prediction time (a tree cannot invent a feature)
- Extrapolation is impossible: trees never predict outside the training range

## 7. Failure Modes You Will Meet in Production

| Symptom | Root cause | Fix |
|---|---|---|
| Train accuracy 100%, test accuracy poor | no stopping rule, pure leaves | cap depth, require min_samples_leaf, validate |
| Importance ranks a high-cardinality ID column first | impurity-based bias toward many distinct values | use permutation importance, or drop identifiers entirely |
| Adding 200 trees does not help | correlated trees limit the variance reduction | check pairwise tree correlation and try more feature randomness |
| Trees perform worse than the linear baseline | features are rotatable (PCA-style) and trees are axis-aligned | rotate/project features, or use an ensemble that is rotation-oblivious |
| Predicting outside the training range | trees cannot extrapolate | clip predictions, or model the extremes separately |
| Same result across runs after 'randomising' | bootstrap built from a shared Random seed | seed per tree, and assert run-to-run variance |

## 8. Java Building Blocks

| API / class | Why it earns its place here |
|---|---|
| `Arrays.sort on candidate thresholds` | sorting thresholds once per feature avoids O(n²) scans |
| `SplittableRandom` | per-tree bootstrap seeds make forests reproducible |
| `double[] / int[] parallel arrays` | zero-boxing feature access inside the hot split loop |
| `TreeMap<Integer, Double>` | weighted counts for class proportions at a leaf |
| `record Split(int feature, double threshold, double gain)` | an immutable, inspectable split record |

## 9. Where This Sits in the Larger System

- **Lab 04** (SVM) trades the axis-aligned boundary for a smooth maximum-margin one.
- **Lab 06** (Naive Bayes) is the generative counterpoint: model P(x|y) instead of splitting on x.
- **Lab 08** (PCA) is the standard answer to the rotation-sensitivity problem.
- **Lab 09** (Gradient Boosting) reuses trees as weak learners added sequentially.

## 10. Self-Assessment Before You Ship Anything

Score yourself 0-2 on each. Any zero below means you are not ready to operate this in production.

- [ ] 0 — cannot yet — Compute entropy and Gini impurity and pick the split that maximises impurity reduction
- [ ] 0 — cannot yet — Implement CART regression and classification trees with a stopping rule
- [ ] 0 — cannot yet — Explain bagging: bootstrap resampling plus decorrelated feature subsets
- [ ] 0 — cannot yet — Read feature-importance numbers critically, including their bias
- [ ] 0 — cannot yet — Control overfitting with depth, min-samples and min-impurity thresholds
- [ ] 0 — cannot yet — Quantify the bias-variance trade-off as forest size grows

## 11. Summary Checklist

- [ ] I can compute entropy and Gini by hand and show they pick the same split
- [ ] I can explain why feature-subset randomness is needed, not optional
- [ ] I can read OOB error and know it is nearly free cross-validation
- [ ] I can say why permutation importance beats impurity importance
- [ ] I know that trees cannot extrapolate
- [ ] I can pick depth/min-leaf from a validation curve
