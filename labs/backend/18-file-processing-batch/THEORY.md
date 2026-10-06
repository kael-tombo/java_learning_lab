# Theory: Spring Batch File Processing

## The Chunk Processing Model

Spring Batch's core idea is that a job is a sequence of steps, and most steps
are **chunk-oriented**: read N items, optionally transform them, write them,
commit a transaction. The chunk size (`chunk(500)`) is the unit of work. If the
write of any item in the chunk fails, the whole chunk rolls back and — depending
on restart configuration — the job resumes from the last committed chunk. This
is why batch writers must be **idempotent or transactional**: a job killed
mid-chunk will re-read and re-write that chunk on restart.

## JobRepository and JobRun Evidence

`JobRepository` (backed by `BATCH_JOB_INSTANCE`, `BATCH_JOB_EXECUTION`,
`BATCH_STEP_EXECUTION` tables) records every run. Without this metadata there
is no restartability: a failed 4M-row CSV import would re-process every row
from line one. Two subtle rules:

- The same `JobInstance` (same job + job parameters hash) can only be re-run
  if its previous execution failed or was stopped. Re-submitting identical
  parameters after a successful run throws
  `UnexpectedJobExecutionException`. Timestamps or run-ids in job parameters
  are the standard escape hatch — and a classic bug, since it makes "same
  data" produce a new instance and defeats restartability.
- `JobExecutionContext` must be serializable; putting a live
  `ResultSet`/open `FileChannel` in it corrupts restart state.

## Readers, Processors, Writers

- `FlatFileItemReader`: streams lines through a `LineTokenizer` +
  `BeanWrapperFieldSetMapper`. It holds a file cursor and is thread-confined;
  parallel reads require `MultiResourceItemReader` partitioning, not sharing
  one reader across threads.
- `ItemProcessor`: pure transformation/validation; returning `null` filters
  the item out of the write. It has no transactional guarantees of its own —
  side effects here are not rolled back.
- `ItemWriter`: `JdbcBatchItemWriter` executes JDBC batch inserts and participates
  in the chunk transaction; `JpaItemWriter` flushes the persistence context.

## Fault Tolerance

Chunk-level `skip` counts items that may fail (bad rows), `retry` handles
transient faults (lock timeouts, deadlocks), and `skipLimit`/`retryLimit`
bound how much failure is tolerated before the job itself fails. Sensible
defaults matter: an unbounded skip turns data corruption into silent row loss;
a zero skip turns one malformed row in a 10M-row file into a total job failure
at 3 AM. The failed rows should be written to an error-file (skip listener)
with cause, key, and line number — a skip without a record is silent data loss.

## Scaling

Beyond larger chunks: **partitioning** splits input files or row ranges into
steps executed in parallel (possibly remote), each with its own reader
instance. **Multi-threaded steps** share one reader/writer pair and need
thread-safe writers. The common production bug is parallelizing without
checking uniqueness constraints: two partitions writing the same natural key
fail with duplicate-key exceptions the retry logic happily retries forever.

## Failure Modes in Production

- Out-of-memory from a chunk size larger than `-Xmx` headroom, or from a
  `Reader` that eagerly loads (e.g. `List`-backed readers on CSV files).
- Non-idempotent writer + restart = duplicate rows in the target table.
- Deadlock from two batch jobs (or job + OLTP traffic) locking the same rows
  in different order; surfaced as retry storms on `SQLException`.
- Locking: Spring Batch's `JobExecution` lock means overlapping schedules of
  the same job fail with `JobExecutionAlreadyRunningException` — silently
  skipped runs that look like success in monitoring dashboards.

## References

- Spring Batch Reference Guide (v5.x, "Chunk-Oriented Processing")
- JSR 352 Batch Applications for the Java Platform
