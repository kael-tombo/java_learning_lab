# Model Training Pipelines - Quiz

## Question 1
Why split into train/validation/test rather than just train/test?
A) For aesthetics
B) Validation tunes hyperparameters; test evaluates final generalization — keeping test out of the loop prevents optimistic estimates
C) It is faster
D) It changes dtypes

**Answer**: B

## Question 2
Why track experiments (config, metrics, artifacts)?
A) For aesthetics
B) Reproducibility and comparison — you cannot reason about a result without knowing the exact config that produced it
C) It is faster
D) It changes dtypes

**Answer**: B

## Question 3
What is a hyperparameter?
A) A feature
B) A setting chosen before training (learning rate, depth) — tuned on validation, not learned from data
C) A metric
D) A plot

**Answer**: B

## Question 4
Why cross-validate instead of a single split?
A) It is faster
B) A single split can be lucky — CV averages over multiple folds, giving a more stable estimate of generalization
C) It changes dtypes
D) It is required

**Answer**: B

## Question 5
Why use a fixed random seed?
A) For aesthetics
B) Reproducibility — rerunning with the same seed must give the same split/shuffle/initialization, or comparisons are meaningless
C) It is faster
D) It changes dtypes

**Answer**: B

## Question 6
What is early stopping?
A) Stopping the pipeline
B) Halting training when validation loss stops improving — a regularizer that prevents overfitting
C) A metric
D) A plot

**Answer**: B

## Question 7
Why is a validation set with a random split invalid for time series?
A) It is faster
B) Future data leaks into training — use a time-based split
C) It changes dtypes
D) It is required

**Answer**: B

## Question 8
What is the role of a pipeline object?
A) To plot
B) To bundle preprocessing + model so the transform is fit on train and applied identically at serving
C) To speed up
D) To change dtypes

**Answer**: B

## Question 9
Why is data leakage particularly insidious?
A) It is slow
B) It inflates validation metrics — the model looks great offline and fails in production
C) It changes dtypes
D) It is a metric

**Answer**: B

## Question 10
Why log model parameters and the training data version?
A) For aesthetics
B) A model artifact without its data version and code hash is not reproducible — you cannot audit why it behaves as it does
C) It is faster
D) It changes dtypes

**Answer**: B

## Question 11
What is a learning curve used for?
A) To plot
B) To see whether more data helps — a plateau suggests the model has converged; a gap suggests more data or more capacity
C) To speed up
D) To change dtypes

**Answer**: B

## Question 12
Why tune regularization strength?
A) For aesthetics
B) It trades bias vs variance — tune on validation to find the generalization sweet spot
C) It is faster
D) It changes dtypes

**Answer**: B

## Question 13
Why is a single "best" metric insufficient?
A) It is faster
B) Optimizing one metric can degrade another (e.g. precision vs recall) — track a vector of metrics
C) It changes dtypes
D) It is a plot

**Answer**: B

## Question 14
Why version the data snapshot used for training?
A) For aesthetics
B) The same code on different data gives different models — the data snapshot is part of the model's identity
C) It is faster
D) It changes dtypes

**Answer**: B

## Question 15
What is a shadow deployment?
A) A dark mode
B) Running a candidate model alongside the production model, comparing outputs without serving the new one — offline safety check
C) A plot
D) A metric

**Answer**: B
