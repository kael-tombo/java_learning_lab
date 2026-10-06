# Model Serving - Quiz

## Question 1
Why is batch inference different from online inference?
A) They are the same
B) Batch scores many rows offline; online scores one request at a time under a latency budget — different optimizations
C) Batch is faster
D) Online is slower

**Answer**: B

## Question 2
Why is a model artifact versioned with its preprocessing?
A) For aesthetics
B) Serving with a different preprocessing version than training causes silent skew — the artifact must carry its transformers
C) It is faster
D) It changes dtypes

**Answer**: B

## Question 3
What is a latency budget?
A) A metric
B) The maximum time a prediction is allowed to take — constrains feature lookup, model, and network calls
C) A plot
D) A speed

**Answer**: B

## Question 4
Why is autoregressive generation (LLMs) a special serving challenge?
A) It is faster
B) Each token depends on previous — can't parallelize across tokens; use KV caching and continuous batching
C) It changes dtypes
D) It is a metric

**Answer**: B

## Question 5
What is a shadow model?
A) A dark model
B) A candidate model running alongside production, logging predictions but not serving them — a zero-risk evaluation
C) A plot
D) A metric

**Answer**: B

## Question 6
Why is a canary deployment useful?
A) It is faster
B) It routes a small fraction of traffic to the new model — catches regressions before full rollout
C) It changes dtypes
D) It is a metric

**Answer**: B

## Question 7
Why is model warm-up important?
A) For aesthetics
B) First requests trigger lazy loading/JIT compilation — warm up with dummy calls so the first real request meets the latency budget
C) It is faster
D) It changes dtypes

**Answer**: B

## Question 8
What is a feature store's role at serving time?
A) To train
B) To provide precomputed features with low-latency lookup, ensuring training/serving consistency
C) To plot
D) To change dtypes

**Answer**: B

## Question 9
Why is a timeout on model inference essential?
A) For aesthetics
B) A hanging inference can exhaust the thread pool and take down the service — fail fast and degrade gracefully
C) It is faster
D) It changes dtypes

**Answer**: B

## Question 10
What is the risk of a model that is too large to serve?
A) It is slow
B) It may not fit in memory or meet latency, even if offline accuracy is high — size is a production constraint
C) It changes dtypes
D) It is a metric

**Answer**: B

## Question 11
Why is input validation at the serving endpoint important?
A) For aesthetics
B) Malformed inputs cause cryptic model errors — validate shape and ranges early and return a clear 400
C) It is faster
D) It changes dtypes

**Answer**: B

## Question 12
What is A/B serving?
A) Two servers
B) Routing a fraction of users to each model variant to measure the business impact — online evaluation
C) A plot
D) A metric

**Answer**: B

## Question 13
Why pin the preprocessing library version at serving?
A) For aesthetics
B) A different version can produce different transformed features — the model will see unexpected inputs
C) It is faster
D) It changes dtypes

**Answer**: B

## Question 14
What is a fallback model?
A) A second server
B) A simpler, faster model used when the primary model fails or is down — graceful degradation
C) A plot
D) A metric

**Answer**: B

## Question 15
Why is observability of the model server important?
A) For aesthetics
B) Latency, error rate, and feature distributions must be monitored — you cannot debug what you cannot see
C) It is faster
D) It changes dtypes

**Answer**: B
