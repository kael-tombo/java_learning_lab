# Model Monitoring - Quiz

## Question 1
Why monitor a model in production?
A) For aesthetics
B) Models degrade silently as data shifts — you cannot know performance dropped without measuring inputs and outputs
C) It is faster
D) It changes dtypes

**Answer**: B

## Question 2
What is data drift?
A) A slow model
B) The distribution of input features changes over time — the model was trained on a different distribution
C) A metric
D) A plot

**Answer**: B

## Question 3
What is concept drift?
A) A slow model
B) The relationship between inputs and the target changes — the same input now has a different label
C) A metric
D) A plot

**Answer**: B

## Question 4
Why can't accuracy be monitored directly for many models?
A) It is faster
B) Labels arrive late or never — so you monitor proxy signals: feature distributions, prediction distribution, and feedback
C) It changes dtypes
D) It is a metric

**Answer**: B

## Question 5
What is a drift detector?
A) A model
B) A statistical test comparing training vs production feature distributions, with an alert threshold
C) A metric
D) A plot

**Answer**: B

## Question 6
Why track prediction distribution?
A) For aesthetics
B) A shift in the predicted class balance often precedes a performance drop — an early warning
C) It is faster
D) It changes dtypes

**Answer**: B

## Question 7
What is a feedback loop in monitoring?
A) A plot
B) Using delayed true labels to compute offline metrics — join predictions with outcomes by an id and a window
C) A metric
D) A speed

**Answer**: B

## Question 8
Why is a sudden drop in one feature's missingness rate suspicious?
A) It is faster
B) A data pipeline change may have zeroed out a feature — the model sees different inputs than it expects
C) It changes dtypes
D) It is a metric

**Answer**: B

## Question 9
Why set thresholds on drift metrics?
A) For aesthetics
B) To trigger re-evaluation or retraining when the distribution shifts materially — but too sensitive causes alert fatigue
C) It is faster
D) It changes dtypes

**Answer**: B

## Question 10
What is prediction latency monitoring?
A) A plot
B) A spike in latency can indicate a resource bottleneck or a degraded dependency — monitor p95/p99, not just mean
C) A metric
D) A speed

**Answer**: B

## Question 11
Why segment monitoring by slice?
A) For aesthetics
B) Aggregate metrics hide a drifting subgroup — a global model can look fine while failing on one slice
C) It is faster
D) It changes dtypes

**Answer**: B

## Question 12
What is a validation schema for incoming data?
A) A plot
B) A contract that rejects malformed or out-of-range inputs before they reach the model — fail fast
C) A metric
D) A speed

**Answer**: B

## Question 13
Why monitor model input vs training data distribution?
A) For aesthetics
B) A large divergence predicts degradation — the model is extrapolating outside its training support
C) It is faster
D) It changes dtypes

**Answer**: B

## Question 14
What is a ground-truth delay handling strategy?
A) Ignore it
B) Use the feedback window to compute recent metrics — and treat earlier windows as the most mature estimate
C) Speed up
D) Change dtypes

**Answer**: B

## Question 15
Why is silent failure the worst failure mode?
A) It is faster
B) The system keeps producing outputs that are wrong but plausible — undetected drift corrupts downstream decisions
C) It changes dtypes
D) It is a metric

**Answer**: B
