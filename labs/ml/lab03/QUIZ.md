# Decision Trees & Random Forests — Quiz (10 Questions)

**Instructions:** Answer each question. Correct answers and explanations follow.

---

### Q1: What is the difference between ID3, C4.5, and CART?
A) They are the same algorithm with different names
B) ID3: information gain (categorical only); C4.5: gain ratio (handles continuous); CART: Gini impurity (binary splits, regression)
C) ID3 is for regression; C4.5/CART for classification
D) C4.5 uses entropy; CART uses variance

**Answer: B** — ID3: categorical features, information gain. C4.5: gain ratio (penalizes many-valued features), handles continuous via discretization, pruning. CART: binary splits, Gini impurity (classification) or MSE (regression), cost-complexity pruning.

---

### Q2: What is entropy for a binary classification node?
A) H = −p log₂(p) − (1−p) log₂(1−p)
B) H = p(1−p)
C) H = 1 − p² − (1−p)²
D) H = |p − 0.5|

**Answer: A** — Entropy measures impurity. For binary: H(p) = −p log₂ p − (1−p) log₂(1−p). Maximum at p=0.5 (H=1). Minimum at p=0 or 1 (H=0). For K classes: H = −Σ pₖ log₂ pₖ.

---

### Q3: What is Gini impurity?
A) G = 1 − Σ pₖ²
B) G = −Σ pₖ log pₖ
C) G = Σ pₖ(1−pₖ)
D) Both A and C

**Answer: D** — Gini = 1 − Σ pₖ² = Σ pₖ(1−pₖ). For binary: G = 2p(1−p). Computationally faster than entropy (no log). Similar splitting behavior. CART default.

---

### Q4: What is information gain?
A) IG = H(parent) − Σ (n_child/n_parent) × H(child)
B) IG = H(parent) + H(child)
C) IG = H(parent) / H(child)
D) IG = Gini(parent) − Gini(child)

**Answer: A** — Weighted average of child impurities subtracted from parent impurity. For a split s: IG(s) = H(Y) − Σᵥ (|Dᵥ|/|D|) H(Y|X=s=v). Maximize IG to choose split.

---

### Q5: What is gain ratio (C4.5)?
A) GR = IG / SplitInfo where SplitInfo = −Σ (|Dᵥ|/|D|) log₂(|Dᵥ|/|D|)
B) GR = IG × SplitInfo
C) GR = IG + SplitInfo
D) GR = IG − SplitInfo

**Answer: A** — SplitInfo = entropy of split distribution. Penalizes splits with many outcomes (e.g., ID on unique ID column). Gain Ratio = IG / SplitInfo. C4.5 uses this to avoid bias toward high-cardinality features.

---

### Q6: How does CART handle continuous features?
A) Discretizes them into bins
B) Considers all possible thresholds: xⱼ ≤ t vs xⱼ > t
C) Uses entropy to bin them
D) Cannot handle continuous features

**Answer: B** — For continuous X, CART sorts values and considers midpoints between adjacent values as thresholds. Best threshold maximizes impurity reduction. O(n log n) per feature.

---

### Q7: What is the stopping criteria for tree growth?
A) Max depth, min samples per leaf, min impurity decrease, max leaf nodes
B) Only max depth
C) Only when all leaves are pure
D) When accuracy reaches 100%

**Answer: A** — Common stopping criteria: max_depth, min_samples_split, min_samples_leaf, min_impurity_decrease, max_leaf_nodes. Prevents overfitting. Alternative: grow full tree then prune.

---

### Q8: What is cost-complexity pruning (CCP)?
A) Prune nodes that don't improve validation accuracy
B) Minimize R_α(T) = R(T) + α × |leaves| where R(T) = total impurity
C) Remove all nodes with depth > max_depth
D) Randomly prune 10% of nodes

**Answer: B** — CCP (CART): sequence of subtrees T₀ ⊃ T₁ ⊃ ... by recursively collapsing weakest link (node with smallest effective α). Choose α via cross-validation. α=0: full tree. α→∞: root only.

---

### Q9: What is bagging (Bootstrap Aggregating)?
A) Train trees on bootstrap samples, average predictions
B) Train one tree on full data, perturb it
C) Boost trees sequentially
D) Average features before training

**Answer: A** — Bagging: sample n observations with replacement (bootstrap), train tree on each. For classification: majority vote. For regression: average. Reduces variance. Trees are independent → parallelizable.

---

### Q10: What is the key difference between Random Forest and Bagging?
A) Random Forest uses different algorithm
B) Random Forest subsamples features at each split (mtry = √p for classification, p/3 for regression)
C) Bagging uses more trees
D) Random Forest doesn't use bootstrap

**Answer: B** — Random Forest = Bagging + random feature subsampling at each split. Decorrelates trees further → lower variance. mtry (max_features) is key hyperparameter. Also provides OOB (out-of-bag) error estimate.