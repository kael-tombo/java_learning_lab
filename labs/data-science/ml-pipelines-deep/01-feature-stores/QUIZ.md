# Feature Stores - Quiz

## Question 1
Why does train/serve skew happen even when the same feature code exists?
A) The code is different
B) Training computes features offline on batch data; serving computes them online — different data timing or transforms cause skew
C) The model is different
D) The metric is different

**Answer**: B

## Question 2
What is the point of a feature store?
A) Store features forever
B) Centralize feature definitions so training and serving compute them identically, with online and offline views
C) Replace the database
D) Speed up training only

**Answer**: B

## Question 3
What is train/serve skew's worst symptom?
A) Slow training
B) A model that performs well offline but poorly in production — features seen at inference differ from training
C) A metric issue
D) A plot issue

**Answer**: B

## Question 4
Why separate online and offline stores?
A) For aesthetics
B) Offline (batch, high-throughput) for training; online (low-latency key-value) for serving — different access patterns
C) It is faster
D) It changes dtypes

**Answer**: B

## Question 5
Why is a point-in-time join critical for training data?
A) It is faster
B) The feature value must be the one available at the prediction time — not the latest — otherwise the model learns from future data
C) It changes dtypes
D) It leaks the seed

**Answer**: B

## Question 6
What is feature lineage in a feature store?
A) The line of code
B) Tracking which raw data, transforms, and models produced a feature — for audit and impact analysis
C) The metric
D) The plot

**Answer**: B

## Question 7
Why version feature definitions?
A) For aesthetics
B) A retrained model must use the same feature definitions as the deployed one — drift in the definition silently breaks comparability
C) It is faster
D) It changes dtypes

**Answer**: B

## Question 8
What is a feature view's TTL?
A) A metric
B) How long a feature value is considered fresh before it should be recomputed — staleness vs cost trade-off
C) A model
D) A plot

**Answer**: B

## Question 9
Why is a shared feature registry useful?
A) It speeds up
B) It prevents teams from re-computing the same features differently — one definition, reused
C) It changes dtypes
D) It is a plot

**Answer**: B

## Question 10
What is the materialization job's role?
A) To plot features
B) To periodically compute and write feature values into the offline (and online) stores
C) To train the model
D) To deploy

**Answer**: B

## Question 11
Why validate feature freshness in serving?
A) For aesthetics
B) A stale feature served as if current degrades predictions silently — alert when the last update exceeds the SLA
C) It is faster
D) It changes dtypes

**Answer**: B

## Question 12
What does a feature store do about schema evolution?
A) Rejects changes
B) Tracks feature schema versions — new versions are added alongside old, and consumers pin the version they expect
C) It changes dtypes
D) It is a metric

**Answer**: B

## Question 13
Why is duplication of feature code between training and serving the root cause of skew?
A) It is faster
B) Two implementations drift — different defaults, different windows, different handling of edge cases
C) It changes dtypes
D) It is a metric

**Answer**: B

## Question 14
What is an entity key in a feature store?
A) A primary key in a database
B) The identifier (e.g. user_id, item_id) that indexes feature values — defines the grain of features
C) A metric
D) A plot

**Answer**: B

## Question 15
Why monitor feature distributions in production?
A) For aesthetics
B) A shift in a feature's distribution signals changing inputs — early warning of train/serve skew or data bugs
C) It is faster
D) It changes dtypes

**Answer**: B
