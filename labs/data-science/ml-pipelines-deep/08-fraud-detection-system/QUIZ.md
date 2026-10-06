# Fraud Detection System - Quiz

## Question 1
Why is fraud detection a severe class-imbalance problem?
A) Fraud is common
B) Legitimate transactions vastly outnumber fraudulent ones — a model predicting "legit" for everything scores high accuracy but catches zero fraud
C) It is fast
D) It changes dtypes

**Answer**: B

## Question 2
What metric is most informative for fraud detection?
A) Accuracy
B) Precision-recall AUC or F1 at a chosen threshold — accuracy is meaningless under extreme imbalance
C) Mean squared error
D) R-squared

**Answer**: B

## Question 3
Why tune the fraud decision threshold?
A) For aesthetics
B) A low threshold catches more fraud but blocks more legitimate users; a high threshold does the opposite — pick the point that balances cost
C) It is faster
D) It changes dtypes

**Answer**: B

## Question 4
What is the cost asymmetry in fraud?
A) The costs are equal
B) A false negative (missed fraud) loses money; a false positive (blocked legitimate user) erodes trust — the threshold should reflect both
C) False positives are more costly
D) False negatives are free

**Answer**: B

## Question 5
Why is a rule-based layer useful alongside an ML model?
A) Rules are always better
B) Hard rules encode known red flags (e.g. shipping to a blacklisted address) and let analysts override; the model scores the gray area
C) Rules are faster
D) Rules replace ML

**Answer**: B

## Question 6
What is a velocity feature?
A) A slow model
B) A count/rate of events per user in a time window — sudden spikes (many transactions in a minute) are a strong fraud signal
C) A metric
D) A plot

**Answer**: B

## Question 7
Why is a time-based train/test split required?
A) For aesthetics
B) Fraud patterns evolve — training on future data leaks, and a random split gives an overoptimistic estimate
C) It is faster
D) It changes dtypes

**Answer**: B

## Question 8
What is a chargeback rate?
A) A metric that measures disputed transactions — the operational KPI a fraud model should move
B) A plot
C) A speed
D) A dtype

**Answer**: A

## Question 9
Why is online inference latency critical in fraud?
A) It is not
B) The decision must be made at transaction time — a slow model delays the decline and may let the fraud settle
C) It changes dtypes
D) It is a metric

**Answer**: B

## Question 10
What is a feedback loop problem in fraud?
A) It is fast
B) The model only sees labels for the transactions it allowed — blocked ones may have been wrongly blocked; the training data is biased by its own decisions
C) It changes dtypes
D) It is a metric

**Answer**: B

## Question 11
Why monitor false-positive rate by customer segment?
A) For aesthetics
B) A global FP rate can hide a segment (e.g. legitimate power users) that is disproportionately blocked
C) It is faster
D) It changes dtypes

**Answer**: B

## Question 12
What is a shadow-mode for a new fraud model?
A) A dark model
B) Run the new model alongside the old one, log divergence, and only route decisions once its behavior is validated
C) A plot
D) A metric

**Answer**: B

## Question 13
Why is concept drift severe in fraud?
A) It is not
B) Fraudsters adapt — a model trained on last month's attacks misses this month's new pattern; regular retraining is required
C) It is faster
D) It changes dtypes

**Answer**: B

## Question 14
What does a precision-recall curve help you choose?
A) The model
B) The operating point (threshold) that balances catching fraud vs blocking customers
C) The metric
D) The plot

**Answer**: B

## Question 15
Why is interpretability important to analysts reviewing flagged transactions?
A) For aesthetics
B) An analyst needs a reason to approve/decline and to audit the model — a black-box score slows review and invites bias
C) It is faster
D) It changes dtypes

**Answer**: B
