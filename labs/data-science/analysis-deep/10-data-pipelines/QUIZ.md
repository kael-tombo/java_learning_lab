# Data Pipelines - Quiz

## Question 1
Why is an ETL pipeline's extract step often loosely coupled?
A) To be faster
B) Sources change schema and availability independently — fail fast and record provenance per source
C) To leak
D) To change dtypes

**Answer**: B

## Question 2
What is data lineage?
A) The line of code
B) The trace of where data came from and how it was transformed — essential for debugging and audits
C) The pipeline graph
D) The metric

**Answer**: B

## Question 3
Why make pipeline steps idempotent?
A) For aesthetics
B) Retries or re-runs must not duplicate data — use upserts/truncate-and-reload keyed by batch id
C) It is slower
D) It changes dtypes

**Answer**: B

## Question 4
Why track a watermark (last processed timestamp)?
A) For aesthetics
B) Incremental loads use it to process only new rows — but gaps cause duplicates or misses; make it part of a transaction
C) It speeds up
D) It changes dtypes

**Answer**: B

## Question 5
What is schema evolution?
A) A new schema design
B) Source schemas change over time (added/removed columns) — pipelines must handle additive changes gracefully
C) A metric
D) A plot

**Answer**: B

## Question 6
Why separate raw, staging, and curated layers?
A) For aesthetics
B) Raw preserves the source; staging cleans; curated is business-ready — each layer has different ownership and SLAs
C) It is faster
D) It changes dtypes

**Answer**: B

## Question 7
What is a data freshness SLA?
A) A model
B) The guarantee that data is no older than X — a metric stakeholders actually care about; monitor it
C) A plot
D) A metric that changes types

**Answer**: B

## Question 8
Why backfill carefully?
A) It is faster
B) Reprocessing history can overwrite curated corrections or break incremental state — version and audit it
C) It leaks
D) It changes dtypes

**Answer**: B

## Question 9
What does a dead-letter queue do in a streaming pipeline?
A) Deletes bad messages
B) Parks messages that fail processing so they don't block the stream — inspect and replay later
C) Speeds up
D) Changes types

**Answer**: B

## Question 10
Why monitor row counts and null rates at each step?
A) For aesthetics
B) A drop or null spike after a transform signals a breaking change upstream before it corrupts downstream
C) It is faster
D) It changes dtypes

**Answer**: B

## Question 11
Why is exactly-once delivery hard?
A) It is impossible
B) True exactly-once requires end-to-end idempotent writes with transactional checkpoints — most systems give at-least-once plus idempotency
C) It is faster
D) It changes dtypes

**Answer**: B

## Question 12
Why use partitioning in large batch jobs?
A) It is signed
B) Processing smaller independent slices reduces memory and lets you retry a slice instead of the whole job
C) It is faster
D) It changes dtypes

**Answer**: B

## Question 13
What is a slow-changing dimension's role in pipelines?
A) It is fast
B) It tracks how dimension attributes change over time — joining without it rewrites history incorrectly
C) It changes dtypes
D) It is a metric

**Answer**: B

## Question 14
Why alert on pipeline failures rather than relying on consumers to notice stale data?
A) For aesthetics
B) Silence is dangerous — absence of data is indistinguishable from a pipeline failure until someone notices; alert proactively
C) It is faster
D) It changes dtypes

**Answer**: B

## Question 15
Why version pipeline code and config?
A) For aesthetics
B) A data discrepancy next week must be reproducible against a known pipeline state — pinned deps and config make it auditable
C) It is faster
D) It changes dtypes

**Answer**: B
