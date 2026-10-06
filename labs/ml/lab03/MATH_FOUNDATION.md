# Decision Trees & Random Forests - Mathematical Foundations

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

## Notation

| Symbol | Meaning |
|---|---|
| `H(S) = −Σ p(c) log₂ p(c)` | Entropy - uncertainty of the label distribution (bits) |
| `Gini(S) = 1 − Σ p(c)²` | Gini impurity - cheaper alternative, same split choices |
| `IG = impurity(S) − Σ (n_v/n) impurity(S_v)` | Information gain - drop in impurity from a split |
| `P(β) = 1/n Σ 1[yᵢ in bootstrap]` | Bootstrap sample - n draws with replacement from n rows |
| `Var(mean of B) = σ²/B` | Variance reduction - why averaging helps, only if trees differ |
| `OOB error` | Out-of-bag estimate - each row's error from trees that never saw it — free cross-validation |

## Why the Math Matters

Trees are greedy set partitions. Once you see a split as a conditional-probability lookup — P(y|x∈leaf) — the impurity criteria, the pruning rules and the importance scores all fall out of the same argument.


---

## 1. Entropy, Gini and information gain

```text
H(S) = -sum_c p_c log2 p_c        Gini(S) = 1 - sum_c p_c^2
IG(A) = impurity(S) - sum_v (n_v/n) impurity(S_v)
```

Impurity is 0 for a pure leaf and maximised for a uniform label distribution. Information gain is the expected impurity of the children subtracted from the parent, weighted by child size.

**Worked example.** S = {0,0,0,1}: H = 0.811 bits. Split x>2.5 gives leaves {0,0} and {0,1}: weighted child entropy = 0.25·0 + 0.75·0.918 = 0.689, so IG = 0.122 bits.


---

## 2. Bootstrap variance reduction

```text
Var(mean of B iid trees) = sigma^2 / B
with correlation rho: Var = sigma^2 (1 + (B-1)rho) / B
```

Perfect independence gives the 1/B law. Any correlation rho > 0 leaves an irreducible floor, which is why feature randomness matters more than raw tree count.

**Worked example.** sigma² = 0.25, B = 100. rho = 0 gives 0.0025; rho = 0.1 gives 0.0228 — nearly ten times the variance despite the same number of trees.


---

## 3. Leaf value estimators

```text
regression leaf: yhat = mean(y in leaf)
classification leaf: argmax_c p_c, p_c = n_c / n
```

A leaf is a conditional mean or mode under the fitted model. That is why trees are poor at extrapolation and why leaf variance tracks local noise.

**Worked example.** Leaf with targets [10, 12, 14]: prediction 12, local variance 4/3, local standard error 0.82 — a usable uncertainty estimate for free.


---

## 4. Bias-variance as trees grow

```text
train error decreases monotonically with depth
test error ~ bias(depth) + variance(depth) + sigma^2
```

Deep trees drive bias to near zero and variance up. The optimal depth is where validation loss turns up, and it usually sits far shallower than people expect.

**Worked example.** With n = 5,000, optimal max_depth is typically 4–6 and leaf size 20–40. Depth 20 fits the noise and doubles test error.


---

## 5. OOB error as cross-validation

```text
row i is in-bag for ~63.2% of trees (1 - (1 - 1/n)^n)
OOB_i = error of row i over trees where it is out-of-bag
```

Each row is naturally held out by the bootstrap, so one training run yields an out-of-sample estimate for every row at no extra compute. It is slightly pessimistic compared to k-fold.

**Worked example.** n = 1,000: expected in-bag trees ≈ 632, out-of-bag ≈ 368. OOB over 1,000 rows × 368 trees is a tight estimate, unlike 10-fold's 100 rows per fold.


---

## Cheat Sheet

- `H(S) = −Σ p(c) log₂ p(c)` - Entropy
- `Gini(S) = 1 − Σ p(c)²` - Gini impurity
- `IG = impurity(S) − Σ (n_v/n) impurity(S_v)` - Information gain
- `P(β) = 1/n Σ 1[yᵢ in bootstrap]` - Bootstrap sample
- `Var(mean of B) = σ²/B` - Variance reduction
- `OOB error` - Out-of-bag estimate

## Numerical Traps

- log(0) when a class is absent from a node — guard the log term.
- Using impurity decrease for importance instead of permutation, and reporting the biased number.
- Fixing the bootstrap seed across trees, which silently correlates them.
- Comparing a tree's OOB error to a linear model's test error without noting OOB is pessimistic.

## Self-Check Problems

1. Compute entropy and Gini for [0,0,0,1] and for [0,1], and say which one information gain prefers.
2. Find the threshold on a 10-point one-feature dataset that maximises IG; show it by hand.
3. Given sigma² = 0.25, B = 50, compute variance reduction for rho in {0, 0.05, 0.2, 0.5}.
4. Estimate the expected out-of-bag tree count for n = 10,000 and explain why OOB is pessimistic.
5. Show that with an ordinal encoding of {small, medium, large} as 0,1,2 the tree can only cut between groups, never within.
