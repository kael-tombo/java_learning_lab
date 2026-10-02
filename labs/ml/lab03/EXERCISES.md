# Decision Trees & Random Forests — Exercises

**Prerequisites:** Java 21+ with Apache Commons Math, or Python with `numpy`, `scikit-learn`, `pandas`.

---

## Exercise 1: Entropy, Gini, and Information Gain

**Objective:** Implement impurity measures and split evaluation from scratch.

**Tasks:**
1. Implement `entropy(y)` and `gini(y)` for binary and multi-class labels.
2. Implement `information_gain(y_parent, y_left, y_right)` using both entropy and Gini.
3. Test on simple cases:
   - Pure node: [0,0,0,0] → H=0, G=0
   - Balanced: [0,0,1,1] → H=1, G=0.5
   - Split: parent=[0,0,1,1], left=[0,0], right=[1,1] → IG=1 (entropy)
4. Generate 2D synthetic data with known split. Find best split threshold by brute force.
5. **Challenge:** Implement vectorized version using numpy histogram for O(n) split evaluation per feature.

**Expected Answer:** Entropy/Gini match theoretical values. Best split recovers true boundary. Vectorized version 10-100x faster.

---

## Exercise 2: Decision Tree from Scratch (Classification)

**Objective:** Build a complete CART decision tree classifier.

**Tasks:**
1. Implement `Node` class: feature_idx, threshold, left, right, value (class probs), impurity, n_samples.
2. Implement `best_split(X, y)`: loop features, find best threshold maximizing IG.
   - For each feature: sort unique values, test midpoints
   - Skip if min_samples_leaf violated
3. Implement recursive `build_tree(X, y, depth)` with stopping criteria:
   - max_depth, min_samples_split, min_samples_leaf, min_impurity_decrease
4. Implement `predict(X)` traversing tree.
5. Test on synthetic data (make_classification). Compare to sklearn DecisionTreeClassifier.
6. **Challenge:** Add `predict_proba` returning class probabilities at leaf.

**Expected Answer:** Tree achieves similar accuracy to sklearn. Predictions match. Tree depth controlled by stopping criteria.

---

## Exercise 3: Decision Tree Regression

**Objective:** Adapt tree for regression (MSE criterion).

**Tasks:**
1. Modify impurity to MSE: `mse(y) = mean((y - mean(y))²)`
2. Modify split criterion: weighted MSE reduction.
3. Leaf value = mean(y) (not class probabilities).
4. Test on synthetic regression data (make_regression).
5. Plot predictions vs true function. Observe piecewise constant approximation.
6. **Challenge:** Add MAE criterion (median at leaf). Compare robustness to outliers.

**Expected Answer:** Regression tree fits piecewise constant function. MSE splits minimize variance. MAE uses median, more robust.

---

## Exercise 4: Cost-Complexity Pruning (CCP)

**Objective:** Implement post-pruning with cost-complexity.

**Tasks:**
1. Grow full tree (no stopping criteria except min_samples_leaf=1).
2. Implement `compute_ccp_alphas(tree)`: bottom-up, compute effective α for each internal node:
   - α_eff = (R(t) − R(T_t)) / (leaves(T_t) − 1)
   - Where R(t) = impurity of node t, R(T_t) = total impurity of subtree
3. Generate sequence of subtrees by recursively pruning node with smallest α_eff.
4. For each α, compute tree size and training impurity.
5. Use k-fold CV to select best α. Plot CV error vs α.
6. **Challenge:** Plot the pruning path (tree size vs α).

**Expected Answer:** Sequence of nested subtrees. CV error U-shaped. Optimal α gives simpler tree with same/better test accuracy.

---

## Exercise 5: Random Forest from Scratch

**Objective:** Implement Random Forest classifier with bagging and feature subsampling.

**Tasks:**
1. Implement `bootstrap_sample(X, y)`: sample n indices with replacement.
2. Implement `RandomForest` class:
   - `fit(X, y)`: for each tree, bootstrap sample, train DecisionTree with max_features=mtry
   - `predict(X)`: majority vote across trees
   - `predict_proba(X)`: average class probabilities
3. Add OOB evaluation: for each tree, evaluate on out-of-bag samples.
4. Hyperparameters: n_estimators, max_depth, min_samples_leaf, max_features (mtry).
5. Test on classification dataset. Compare to sklearn RandomForestClassifier.
6. **Challenge:** Implement parallel training using thread pool.

**Expected Answer:** RF accuracy > single tree. OOB error ≈ CV error. Feature subsampling decorrelates trees.

---

## Exercise 6: Feature Importance

**Objective:** Compute and compare MDI and permutation importance.

**Tasks:**
1. **MDI (Mean Decrease Impurity):**
   - For each tree, accumulate weighted impurity decrease per feature
   - Average across trees. Normalize to sum to 1.
2. **Permutation Importance:**
   - For each feature: shuffle column in OOB/test data, measure accuracy drop
   - Repeat 10×, average.
3. Generate data with: 3 informative, 2 redundant (correlated), 5 noise features.
4. Plot both importance types. Compare rankings.
5. **Challenge:** Implement conditional permutation importance (handles correlated features better).

**Expected Answer:** MDI splits importance among correlated features. Permutation importance more reliable but noisy. Noise features near zero.

---

## Exercise 7: Hyperparameter Tuning

**Objective:** Tune Random Forest hyperparameters systematically.

**Tasks:**
1. Define parameter grid:
   - n_estimators: [50, 100, 200, 500]
   - max_depth: [5, 10, 20, None]
   - min_samples_leaf: [1, 2, 5, 10]
   - max_features: ['sqrt', 'log2', 0.3, 0.5]
2. Implement grid search with 5-fold CV (use OOB for speed).
3. Plot heatmaps: n_estimators vs max_depth, max_features vs min_samples_leaf.
4. Find best parameters. Evaluate on held-out test set.
5. **Challenge:** Implement random search and Bayesian optimization (using Optuna or simple GP).

**Expected Answer:** More trees → diminishing returns. max_depth controls overfitting. max_features trades bias/variance. min_samples_leaf regularizes.

---

## Exercise 8: Decision Boundaries Visualization

**Objective:** Visualize how trees partition feature space.

**Tasks:**
1. Generate 2D datasets: moons, circles, blobs (sklearn.datasets).
2. Train single DecisionTree (max_depth=2, 3, 5) and Random Forest.
3. Create meshgrid, predict on grid, plot decision boundaries with contourf.
4. Overlay training points colored by true class.
5. Compare: single tree (axis-aligned, boxy) vs RF (smoother, more complex).
6. **Challenge:** Animate tree growth: show boundaries at depth 1, 2, 3, ...

**Expected Answer:** Single tree: rectangular regions. RF: smoother boundaries approximating true shape. Depth controls granularity.

---

## Exercise 9: Handling Categorical Features

**Objective:** Explore strategies for categorical features in trees.

**Tasks:**
1. Create dataset with categorical feature (e.g., 10 categories) with different target rates.
2. Compare encodings:
   - One-hot (creates many binary features)
   - Ordinal (arbitrary ordering)
   - Target encoding (mean target per category, with smoothing)
   - Optimal binary partitioning (2^(k-1)-1 partitions)
3. Train trees with each encoding. Compare accuracy and tree size.
4. For optimal partitioning: implement search for best binary split of categories (try all 2^(k-1)-1 groupings for k≤8).
5. **Challenge:** Implement LightGBM-style categorical split: sort categories by target rate, treat as ordered.

**Expected Answer:** One-hot works but fragments splits. Target encoding powerful but leaks target info (need CV). Optimal partitioning finds best grouping but exponential.

---

## Exercise 10: End-to-End Random Forest Library

**Objective:** Build production-ready `RandomForest` class.

**Requirements:** Java class with:
- `fit(double[][] X, int[] y)` — classification
- `fit(double[][] X, double[] y)` — regression
- `predict(double[][] X)` — class or value
- `predictProba(double[][] X)` — class probabilities (classification)
- `score(double[][] X, int[] y)` — accuracy or R²
- `getFeatureImportanceMDI()` — mean decrease impurity
- `getFeatureImportancePermutation(double[][] X, int[] y)` — permutation importance
- `getOOBScore()` — out-of-bag error
- `getTrees()` — access individual trees for inspection
- Hyperparameters: `setNEstimators`, `setMaxDepth`, `setMinSamplesLeaf`, `setMaxFeatures`, `setMaxSamples`, `setCriterion` (gini/entropy/mse/mae)
- `crossValidate(k, paramGrid)` — CV with grid/random search
- Serialization: `save/load`

**Diagnostics:**
- `getOOBDecisionFunction()` — OOB predicted probabilities
- `getTreeDepths()` — depth of each tree
- `getLeafCounts()` — number of leaves per tree

**Tests:**
- Synthetic classification/regression
- UCI datasets (Iris, Wine, Breast Cancer, Boston Housing)
- Feature importance on correlated features
- OOB vs CV agreement
- Comparison with sklearn (if Python available)

**Bonus:** Add `partialDependence(feature_idx, X)` — PDP plots for feature effect visualization.