# 04-decision-trees - Decision Trees
## Overview
Greedy recursive splitting: pick the feature/threshold minimizing weighted child impurity (Gini or entropy), stop on purity, depth, or min-samples rules.
## Key formulas
- Gini = 1 - sum_k p_k^2; entropy = -sum_k p_k log2 p_k.
- Split score = (nL/n) I(L) + (nR/n) I(R).
## What the snippets show
- Cml04A: impurity table (pure node 0, [1,1] max at 0.5/1.0).
- Cml04B: exhaustive split search picks t=2.5 with score 0.0.
## Try it
Change y to [0,1,0,1,1] and confirm no split reaches 0.
## Formula reference
- Gini = 1 - sum p^2; entropy = -sum p log2 p; misclassification = 1 - max p.
- Information gain = I(parent) - weighted child impurities.
- Gain ratio divides by split entropy (counters many-valued bias).
## Worked example
- Parent [2,3] (2 zeros, 3 ones): Gini = 1 - 0.16 - 0.36 = 0.48.
- Split at 2.5: left [2,0] pure, right [0,3] pure; gain = 0.48 - 0 = 0.48.
- Entropy parent: -(0.4 log2 0.4 + 0.6 log2 0.6) = 0.9710.
## Pitfalls
- Greedy splits overfit; limit depth or require min samples per leaf.
- Gini vs entropy rarely changes the tree; prefer speed (Gini, no logs).
- High-cardinality features bias gain; use gain ratio.
## Connections
- Forests average many such trees to cut variance.
- Boosting fits residuals of shallow trees sequentially.
## Exercises
1. Relabel y = [0,1,0,1,1] and find the new best split.
2. Compute information gain for t = 2.5 in nats.
3. Grow depth-2 on 6 points and count leaves.
