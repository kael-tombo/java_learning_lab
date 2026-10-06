# Anomaly Detection - Quiz

## Question 1
Why is anomaly detection inherently imbalanced?
A) It is always fast
B) Anomalies are rare by definition — accuracy is meaningless; use precision/recall or PR-AUC
C) It is signed
D) It changes dtype

**Answer**: B

## Question 2
What is the main challenge with anomaly detection labels?
A) They are too many
B) They are scarce or unreliable — unsupervised methods dominate, but thresholds are arbitrary
C) They are continuous
D) They are always correct

**Answer**: B

## Question 3
Why is a univariate threshold (e.g. 3σ) often insufficient?
A) It is too fast
B) Anomalies can be multivariate (a combination of individually normal values) or context-dependent (normal at noon, anomalous at 3am)
C) It is signed
D) It changes dtype

**Answer**: B

## Question 4
What does isolation forest exploit?
A) The number of trees
B) That anomalies are few and different — they get isolated in fewer partitions, giving shorter path lengths
C) The number of features
D) The labels

**Answer**: B

## Question 5
Why tune the contamination parameter carefully?
A) It is signed
B) It sets the expected fraction of anomalies — too high flags normal behavior, too low misses real ones
C) It is faster
D) It changes the dtype

**Answer**: B

## Question 6
Why is anomaly detection under concept drift hard?
A) It is slower
B) "Normal" distribution shifts — old thresholds flag new behavior as anomalous, or miss drifted anomalies; needs periodic revalidation
C) It is signed
D) It changes dtype

**Answer**: B

## Question 7
What is a contextual anomaly?
A) An outlier in the raw distribution
B) A value normal in one context but anomalous in another (e.g. high temperature in winter vs summer)
C) A type of outlier
D) A metric issue

**Answer**: B

## Question 8
Why is precision often low in deployed anomaly detection?
A) The model is slow
B) Rare events mean most flags are false positives — alarm fatigue; thresholds should trade off against operational cost
C) It is signed
D) It changes dtype

**Answer**: B

## Question 9
Why use log-transform before distance-based anomaly detection?
A) For aesthetics
B) Heavy-tailed features dominate Euclidean distance — log compresses scale differences
C) It is faster
D) It changes dtype

**Answer**: B

## Question 10
What is a collective anomaly?
A) A single outlier
B) A group of points that is anomalous together though individually normal (e.g. a burst of slow transactions)
C) A type of outlier
D) A metric issue

**Answer**: B

## Question 11
Why validate an anomaly detector with a holdout of labeled incidents rather than just reconstruction error?
A) It is faster
B) Reconstruction error on normal data doesn't prove it catches real anomalies — labeled incidents measure utility
C) It changes dtype
D) It is required

**Answer**: B

## Question 12
Why is a high anomaly rate period sometimes correct behavior?
A) The model is broken
B) A real shift or incident — investigate; do not auto-suppress or you mask real events
C) It is faster
D) It changes dtype

**Answer**: B

## Question 13
Why combine multiple anomaly signals (metric, log pattern, trace)?
A) It is faster
B) Each signal has different false-positive profiles — agreement raises confidence
C) It changes dtype
D) It is signed

**Answer**: B

## Question 14
What is a false positive cost in anomaly detection?
A) It is always low
B) An engineer investigates a non-issue — repeated FPs erode trust and cause ignored alerts (alarm fatigue)
C) It is faster
D) It changes dtype

**Answer**: B

## Question 15
Why is threshold tuning on a validation window important?
A) It is required by pandas
B) The anomaly score cutoff directly trades precision vs recall — tune it on held-out incidents, not the training data
C) It speeds up
D) It changes dtype

**Answer**: B
