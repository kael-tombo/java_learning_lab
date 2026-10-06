# Feature Engineering - Quiz

## Question 1
Why is leakage the cardinal sin of feature engineering?
A) It slows training
B) Features that encode the label or future information inflate validation and fail in production
C) It uses more memory
D) It changes dtypes

**Answer**: B

## Question 2
Target encoding can leak when…
A) The category statistics are computed on the full training set including validation rows
B) It is slower
C) It uses the mode
D) It is applied to booleans

**Answer**: A — must compute encoding within folds or on out-of-fold data.

## Question 3
Why scale features before distance-based models (KNN, SVM, K-means)?
A) For aesthetics
B) Large-scale features dominate the distance — scaling gives each feature a fair vote
C) It speeds up training only
D) It removes outliers

**Answer**: B

## Question 4
Why standardize rather than normalize for linear models?
A) Linear models assume zero-mean features for stable gradient descent; normalization distorts variance
B) It is required by sklearn
C) It changes the labels
D) It is slower

**Answer**: A

## Question 5
What is a rolling window feature's main gotcha on time series?
A) It is slow
B) The window must be computed using only past data — a trailing (not centered) window, and no future bleed
C) It requires a DatetimeIndex
D) It changes dtype

**Answer**: B

## Question 6
Why might one-hot encoding hurt tree models on high-cardinality features?
A) It slows training only
B) It explodes dimensionality and trees must learn each level separately — target/hashing encoding often better
C) It leaks
D) It requires floats

**Answer**: B

## Question 7
What does polynomial feature expansion buy you?
A) Nonlinear interactions for linear models — at the cost of dimensionality and overfitting if unregularized
B) Faster training
C) Causation
D) Better plots

**Answer**: A

## Question 8
Why impute missing values with a tree-based imputer (IterativeImputer/KNNImputer) rather than median?
A) It is always better
B) It models relationships between columns, but must still be fit per-fold to avoid leakage
C) It is faster
D) It removes outliers

**Answer**: B

## Question 9
Why create a missingness indicator instead of imputing silently?
A) For aesthetics
B) Missingness itself may be predictive (MNAR); a single impute hides that signal
C) It speeds up training
D) It is required

**Answer**: B

## Question 10
Why hash-encode high-cardinality categoricals?
A) It is always exact
B) Fixed-size dense representation; collisions are possible and must be accepted as a bias
C) It leaks
D) It is slower

**Answer**: B

## Question 11
When is log-transform of a feature appropriate?
A) Always
B) When the feature is right-skewed and spans orders of magnitude — linear models behave, tree splits stabilize
C) For categorical features
D) For boolean features

**Answer**: B

## Question 12
Why compute features inside a `Pipeline` rather than ad hoc?
A) For aesthetics
B) The pipeline ensures the transform is fit on train only and reused identically at inference
C) It is slower
D) It changes the labels

**Answer**: B

## Question 13
What is feature staleness?
A) A feature that could not be updated at inference — train/serve skew from "computed offline vs online"
B) An old library
C) A stale plot
D) A deprecated model

**Answer**: A

## Question 14
Why beware of features derived from other model outputs?
A) Nothing
B) They double-count risk and make the system hard to debug — track lineage
C) They are slower
D) They change types

**Answer**: B

## Question 15
Why is "fit on train, transform on test" the rule?
A) Test set is smaller
B) Any statistic learned on test data leaks into the model
C) It is required by numpy
D) It improves metrics legitimately

**Answer**: B
