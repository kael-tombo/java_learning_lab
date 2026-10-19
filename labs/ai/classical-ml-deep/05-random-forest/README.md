# 05-random-forest - Random Forest
## Overview
Bagging: train each tree on a bootstrap resample, split on random feature subsets, vote. Unsampled (out-of-bag, ~36.8% per tree) samples give a free validation estimate.
## Key formulas
- P(sample missed) = (1-1/n)^n -> 1/e ~= 0.368.
- Prediction = majority vote (classification) / mean (regression).
## What the snippets show
- Cml05A: three seed-7 bags with explicit OOB index lists.
- Cml05B: vote aggregation reaching 4/4.
## Try it
Tally OOB membership over many resamples and confirm the ~1/3 rate.
## Formula reference
- P(miss) = (1 - 1/n)^n -> 1/e ~= 0.368; OOB error averages unsampled predictions.
- Classification: majority vote; regression: mean; variance drops ~1/T for decorrelated trees.
- Feature subsampling mtry (often sqrt(p)) decorrelates trees.
## Worked example
- Tree 0 OOB [0,1,5]: 3/6 = 0.5 unsampled this draw (expectation ~0.368).
- Votes [1,1,0] -> 1; [0,0,0] -> 0: ties impossible with odd T.
- OOB error here 0/4 on the toy vote table.
## Pitfalls
- OOB optimistic if resampling leaks (duplicates across folds).
- Imbalanced data: majority vote favors the big class; stratify or weight.
- Variable importance biased to high-cardinality features.
## Connections
- Bagging contrasts with boosting (parallel variance cut vs sequential bias cut).
- OOB is the ancestor of cross-validation estimates.
## Exercises
1. Tally OOB rate over 1000 resamples vs 0.368.
2. Vote with T = 5 stumps on a new sample.
3. Compare single-tree vs forest error on noisy labels.
