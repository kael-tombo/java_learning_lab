# Decision Trees & Random Forests — Flashcards

**Format:** Question (front) → Answer (back). Use for spaced repetition.

---

### Card 1
**Q:** What is a decision tree?
**A:** Hierarchical model that recursively partitions feature space. Internal nodes = splits, leaves = predictions.

---

### Card 2
**Q:** What is the ID3 algorithm?
**A:** Uses information gain (entropy reduction) for splitting. Categorical features only. No pruning.

---

### Card 3
**Q:** What is C4.5?
**A:** ID3 successor. Gain ratio (penalizes many-valued features). Handles continuous features. Post-pruning.

---

### Card 4
**Q:** What is CART?
**A:** Classification and Regression Trees. Binary splits only. Gini impurity (classification) or MSE (regression). Cost-complexity pruning.

---

### Card 5
**Q:** What is entropy?
**A:** H = −Σ pₖ log₂ pₖ. Measures impurity. Max at uniform distribution. Min (0) at pure node.

---

### Card 6
**Q:** What is Gini impurity?
**A:** G = 1 − Σ pₖ² = Σ pₖ(1−pₖ). Faster to compute (no log). Similar to entropy.

---

### Card 7
**Q:** What is information gain?
**A:** IG = H(parent) − Σ (n_child/n_parent) × H(child). Weighted impurity reduction.

---

### Card 8
**Q:** What is gain ratio?
**A:** GR = IG / SplitInfo. SplitInfo = −Σ (|Dᵥ|/|D|) log₂(|Dᵥ|/|D|). Penalizes high-cardinality splits.

---

### Card 9
**Q:** How does CART split continuous features?
**A:** Sort values, consider midpoints between adjacent values as thresholds. Choose threshold maximizing IG.

---

### Card 10
**Q:** What are common stopping criteria?
**A:** max_depth, min_samples_split, min_samples_leaf, min_impurity_decrease, max_leaf_nodes.

---

### Card 11
**Q:** What is cost-complexity pruning?
**A:** Minimize R_α(T) = R(T) + α|leaves|. Sequence of subtrees. Choose α via CV.

---

### Card 12
**Q:** What is the "weakest link" in CCP?
**A:** Node with smallest effective α = (R(t) − R(Tₜ)) / (|leaves(Tₜ)| − 1). Collapse it first.

---

### Card 13
**Q:** What is bagging?
**A:** Bootstrap Aggregating. Train B trees on bootstrap samples. Average (regression) or majority vote (classification).

---

### Card 14
**Q:** What does bagging reduce?
**A:** Variance. Trees are independent → errors cancel out. Doesn't reduce bias.

---

### Card 15
**Q:** What is out-of-bag (OOB) error?
**A:** Error on samples not in bootstrap sample (~37% per tree). Unbiased estimate of test error without CV.

---

### Card 16
**Q:** What is Random Forest?
**A:** Bagging + random feature subsampling at each split (mtry). Further decorrelates trees.

---

### Card 17
**Q:** What is mtry (max_features)?
**A:** Number of features considered at each split. Classification: √p. Regression: p/3. Key hyperparameter.

---

### Card 18
**Q:** How does Random Forest reduce variance more than bagging?
**A:** Feature subsampling decorrelates trees. Lower correlation → lower ensemble variance.

---

### Card 19
**Q:** What is feature importance in Random Forest?
**A:** Mean decrease in impurity (MDI) across all splits. Or permutation importance (shuffle feature, measure accuracy drop).

---

### Card 20
**Q:** What is permutation importance?
**A:** For each feature: shuffle its values in OOB samples, compute accuracy drop. More reliable than MDI.

---

### Card 21
**Q:** What is the bias-variance tradeoff in trees?
**A:** Deep trees: low bias, high variance. Shallow/pruned: higher bias, lower variance. RF reduces variance without increasing bias much.

---

### Card 22
**Q:** What are the main RF hyperparameters?
**A:** n_estimators, max_depth, min_samples_leaf, max_features (mtry), max_samples (bootstrap size).

---

### Card 22
**Q:** What is the difference between classification and regression trees?
**A:** Classification: Gini/entropy, majority vote, predict class. Regression: MSE/MAE, average, predict continuous value.

---

### Card 23
**Q:** How does CART regression splitting work?
**A:** Minimize weighted MSE: Σ (nₗ/n) × MSEₗ. Prediction at leaf = mean of target values.

---

### Card 24
**Q:** What is the time complexity of training a decision tree?
**A:** O(n × p × log n) for sorted features. RF: O(B × n × mtry × log n). Parallelizable across trees.

---

### Card 25
**Q:** What is the difference between pre-pruning and post-pruning?
**A:** Pre-pruning: stop growing early (stopping criteria). Post-pruning: grow full tree, then prune back (CCP). Post-pruning generally better.

---

### Card 26
**Q:** What is a decision stump?
**A:** Tree with max_depth=1 (one split). Used as weak learner in boosting (AdaBoost, gradient boosting).

---

### Card 27
**Q:** Can decision trees capture linear relationships?
**A:** Not efficiently. Requires many splits to approximate line. Better for non-linear, interaction effects.

---

### Card 28
**Q:** What is the effect of correlated features on feature importance?
**A:** MDI importance gets split among correlated features. Permutation importance more robust but still affected.

---

### Card 29
**Q:** How does Random Forest handle missing values?
**A:** Surrogate splits (CART), or impute with median/mode, or treat "missing" as separate category.

---

### Card 30
**Q:** What is Extremely Randomized Trees (ExtraTrees)?
**A:** Random thresholds for splits (not optimized). Faster training, more randomization, sometimes better generalization.

---

### Card 31
**Q:** What is the OOB score used for?
**A:** Unbiased error estimate, hyperparameter tuning (no CV needed), feature importance (permutation on OOB).

---

### Card 32
**Q:** What is the relationship between n_estimators and error?
**A:** Error decreases as 1/√B initially, then plateaus. Diminishing returns after ~100-500 trees.

---

### Card 33
**Q:** What is the "curse of dimensionality" for trees?
**A:** In high dimensions, data becomes sparse. Trees overfit easily. RF helps by feature subsampling.

---

### Card 34
**Q:** How to interpret a decision tree?
**A:** Visualize tree (GraphViz). Root = most important feature. Path = decision rules. Depth = complexity.

---

### Card 35
**Q:** What is SHAP for tree models?
**A:** SHAP (SHapley Additive exPlanations). TreeSHAP computes exact Shapley values in O(2^depth) or O(depth²) approx. Consistent feature attribution.

---

### Card 36
**Q:** What are the limitations of decision trees?
**A:** Unstable (small data change → different tree), can't extrapolate, biased toward high-cardinality features, axis-aligned boundaries.

---

### Card 37
**Q:** What is the "best split" search for continuous features?
**A:** Sort feature values O(n log n). Evaluate all n−1 midpoints. Choose max IG. Can use histograms for speed.

---

### Card 38
**Q:** What is histogram-based splitting (LightGBM, XGBoost)?
**A:** Bin continuous features into discrete bins. Evaluate splits on bin boundaries. Much faster, slight precision loss.

---

### Card 39
**Q:** How does Random Forest handle categorical features?
**A:** One-hot encoding (high cardinality problematic), or optimal binary partitioning (2ᵏ⁻¹−1 partitions for k categories).

---

### Card 40
**Q:** When to use RF vs Gradient Boosting?
**A:** RF: parallelizable, robust, less tuning, good baseline. GB: often higher accuracy, sequential, more hyperparameters, prone to overfitting.