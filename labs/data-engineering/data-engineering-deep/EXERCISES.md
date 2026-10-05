# EXERCISES — 24 Graded Problems

Level 1: mechanics. Level 2: reasoning. Level 3: judgement.
Solutions are sketched; full answers are in the accompanying test suite.

## Level 1 — Mechanics

### E1. Size a topic
A service produces 8,000 events/sec at 1.2KB each, 3 brokers, comfortable
limit 35MB/s per broker, max consumer parallelism 48, want 3x growth
headroom. How many partitions, and what replication factor?

<details><summary>Solution</summary>
bandwidth: 8000 * 1200 / 1048576 = 9.2 MB/s
needed = ceil(9.2 * 3 / (35 * 3)) = 1
parallelism needs 48 -> partitions = 48
RF: 3 brokers in production, cross-AZ -> RF 3, min.insync.replicas 2.
Answer: 48 partitions, RF 3. Note that bandwidth was irrelevant here.
</details>

### E2. Convert processing time to event time
A job aggregates by `processing_time` and reports 6% fewer orders than the
batch job. Name two distinct causes and the fix for each.

<details><summary>Solution</summary>
(a) Late-arriving orders cross a window boundary, so they land in the next
hour. Fix: event time with a watermark plus a correction/restatement path.
(b) Restarts and replays duplicate or drop events under at-least-once. Fix:
idempotent keyed upsert.
Distinguishing them: (a) shows up as a *shift* in the time series, (b) as a
*drift* that grows with restart count.
</details>

### E3. Little's law sizing
A consumer processes 3,000 records/sec with 4ms of work per record. How many
in-flight records must the system hold, and is a pool of 40 safe?

<details><summary>Solution</summary>
L = lambda * W = 3000 * 0.004 = 12 in flight.
Pool of 40 gives utilization 12/40 = 0.3. Safe.
But use p99 service time, not the mean: if p99 is 40ms, L = 120 and
utilization is 3.0 — the pool is the bottleneck, not the work. Always size
from the tail.
</details>

### E4. Write an idempotent upsert
Give the SQL and the Java for a sink that must survive re-delivery of the same
`event_id` with an increasing `lsn`.

<details><summary>Solution</summary>
```sql
MERGE INTO t USING s ON t.event_id = s.event_id
WHEN MATCHED AND s.lsn > t.lsn THEN UPDATE SET ...
WHEN NOT MATCHED THEN INSERT ...
```
```java
if (event.lsn() <= lastApplied.getOrDefault(event.eventId(), -1L)) return; // stale
```
The `s.lsn > t.lsn` guard is what makes re-delivery in *either* order safe.
</details>

### E5. Backoff arithmetic
A caller has a 2s timeout. A downstream call has a 300ms timeout and full
jitter with base 100ms, cap 2s. How many retries fit?

<details><summary>Solution</summary>
Worst-case with 2 retries: 2*300ms + backoff(0, 200) + backoff(0, 400) = 600 + 300 = 900ms. Fits.
With 4 retries: 1200 + (200+400+800+1600)/2 expected = 1200 + 1500 = 2700ms. Does not fit.
Answer: 2-3 retries. If you need more, raise the caller timeout or use a
circuit breaker to fail fast rather than retrying into a doomed budget.
</details>

### E6. State sizing
40M entities, 24 online features, 26 bytes per value, RF 2, 70% target
utilization. Nodes of 32GB?

<details><summary>Solution</summary>
raw = 40e6 * 24 * 26 = 24.96e9 = 25GB
cluster = 25 * 2 / 0.7 = 71.4GB
nodes = ceil(71.4 / 32) = 3 nodes
Add one for headroom during rebalance: 4 in practice.
</details>

## Level 2 — Reasoning

### E7. Diagnose a Spark regression
A groupBy job went from 4 min to 70 min after an unrelated schema addition.
Stages are: one 4s, one 68s, one 2s. What is your hypothesis and your first
measurement?

<details><summary>Solution</summary>
Hypothesis: key skew, not the schema. The schema addition widened a row and
pushed a previously-boundary key over a threshold, or the new column changed
a partition key.
First measurement: per-task metrics for the 68s stage, look at max/median
ratio. If > 5x, it is skew. Then check the key distribution for that date
range — look for a category that only appears on Tuesdays.
The general lesson: schema changes are correlated with data changes, and the
schema is the visible part.
</details>

### E8. Watermark stalled, traffic is fine
The live dashboard froze for 6 minutes. The consumer group is healthy, lag is
low, CPU is low. Where do you look?

<details><summary>Solution</summary>
Watermark is per-partition-source. A partition that is idle (no events) holds
the global watermark back unless you configure idleness. Low lag + low CPU +
no output = the watermark is not advancing.
Fix: `withIdleness(...)` so an idle partition stops holding the watermark.
Also check: a slow serialization in the source, and a downstream operator
that is not emitting (an empty window does not fire).
</details>

### E9. Delete cost
You must delete 1 row from a 1M-row Parquet file in a plain folder. What
happens, and what is the alternative in a table format?

<details><summary>Solution</summary>
Plain files: the file must be rewritten minus the row, so you pay a 1M-row
rewrite to remove 1 row. This is the argument for table formats.
Delta: `DELETE` still rewrites affected files, so the same cost applies —
but the *scope* can be bounded by partition, and the log records it.
Iceberg: equality delete files, so the cost is proportional to the number of
erased keys, not the file size. Compaction later reclaims space.
Answer: the alternative that actually helps is Iceberg equality deletes, or
partition-level drops.
</details>

### E10. "Streaming says 4% less than billing"
A live revenue feed is 4% below the hourly batch at peak, and only at peak.
Three hypotheses, ranked, with the test for each.

<details><summary>Solution</summary>
(a) Watermark too tight for a late-flushing producer at peak. Test: compare
arrival-time minus event-time distribution at peak vs off-peak. If peak
arrival lag is much higher, the bound is wrong for that source.
(b) The window finalizes before the peak-hour events land, so they are counted
in the next hour. Test: shift the finalization lag and see if the gap moves
rather than disappears.
(c) Back-pressure / dropped records at peak. Test: compare producer success
count, broker-side accepted count, and consumer processed count. If accepted
< sent, it is upstream, not the job.
</details>

### E11. Pick the join strategy
Facts: 1.1B rows. Dimensions: 12k, 40M, 900M rows. What strategy for each,
and what do you set to stop it choosing wrong?

<details><summary>Solution</summary>
1.1B x 12k -> broadcast hash join (dimension fits easily in memory).
1.1B x 40M -> sort-merge join with both sides partitioned by the key.
1.1B x 900M -> sort-merge, large; consider pre-aggregating the fact or
restructuring.
Set `spark.sql.autoBroadcastJoinThreshold` explicitly. The default silently
falls back from a "broadcast" join that does not fit, and you get a 10x slower
stage with no error.
</details>

### E12. Point-in-time join leak
A churn model's offline AUC dropped from 0.79 to 0.71 after a refactor that
should have changed nothing. Name the most likely cause and the test.

<details><summary>Solution</summary>
Most likely: the refactor changed a label/feature join from a point-in-time
as-of join to a "latest value" join — or the reverse, removing an as-of
constraint. This is the most common cause of large, unexplained AUC movement
and it is usually a fix, not a regression.
Test: a leak test. Build a fixture where a feature row exists both before and
after the label timestamp, with a distinct value after; assert the training
row uses the earlier value. Run it in CI.
</details>

### E13. Cost forensics
Monthly cost rose 40% with no data growth. Give the first three queries to run.

<details><summary>Solution</summary>
1. Credits by query tag and warehouse: which workload grew? (One query.)
2. Idle warehouse time: credits consumed by up-but-unused warehouses.
3. Bytes scanned by query: is a scan-based bill growing, meaning someone is
reading more data per question?
If the bill is storage-dominated instead, the query is different: what grew in
storage, and what retention class is it in.
The point of the ordering: isolate the *line item* before looking at queries.
</details>

### E14. Exactly-once claim
A job reads Kafka and POSTs to a payments API. The team claims exactly-once
because the source is exactly-once-capable. What is wrong?

<details><summary>Solution</summary>
The guarantee covers the pipeline, not the external API. Exactly-once requires
the sink to participate — a transactional sink, or an idempotency key at the
API. Kafka cannot make an HTTP POST happen once.
Correct design: send `Idempotency-Key: <event-id>`, and make the API
deduplicate. Then delivery semantics stop mattering for correctness, which is
the better place to be.
</details>

## Level 3 — Judgement

### E15. Batch or streaming
Three candidate workloads. Choose and justify in 3 sentences each:
(a) daily revenue close for finance; (b) fraud scoring on card authorizations;
(c) a dashboard of weekly active users, refreshed hourly.

<details><summary>Solution</summary>
(a) Batch. A daily close needs completeness, not latency, and batch is easier
to make correct and to reconcile.
(b) Streaming. The decision must happen in <200ms, so there is no choice.
(c) Either; choose batch. Hourly freshness does not require a stream, and
batch is cheaper and simpler. Do not build a streaming pipeline for a
requirement that says "hourly".
</details>

### E16. Partition scheme
Fact table: 90M rows/day, filters always include `event_date` and
`country` (180 values), sometimes `channel` (6). Propose a spec and justify.

<details><summary>Solution</summary>
`days(event_date), bucket[16](country_hash)`.
Partitioning by `country` alone gives 180 partitions/day — 180 files, small.
Partitioning by `channel` gives 6 files of 15M rows each — too large and it
does not help a `country` filter much (no pruning without min/max stats).
`bucket[16]` on country gives roughly 11 per country value, bounded, with
pruning for country filters and no tiny files. Never partition by a
high-cardinality column.
</details>

### E17. A metric nobody trusts
Finance has stopped using the revenue mart because they once found it
disagreed with the ledger and nobody could explain why. What do you do first?

<details><summary>Solution</summary>
First: restore trust by making the number reconcilable. Build the
reconciliation against an independent source and show the diff daily. Do not
start by rewriting the mart; a rewrite without a reconcilable target just
produces a differently-wrong number.
Second: publish the metric contract (minor units, rounding point, FX
application) and enforce it in the pipeline.
Third: when it disagrees, be able to say which side is right and why. That is
the actual deliverable: a process, not a number.
</details>

### E18. Exception expiry
A `BLOCK`-level exception for 12 datasets expires in 9 days. Nobody owns the
renewal. What happens, and what should you have built?

<details><summary>Solution</summary>
If the enforcement is real, expiry re-blocks the 12 datasets and something
breaks. If the enforcement is fake, the exception was a permanent undocumented
bypass — which is the more common and more serious case.
Should have built: an expiry that re-blocks, a reminder 30 days ahead to the
requester and the dataset owner, a compensating-control requirement, and a
metric on exception age so sprawl is visible before it matters.
</details>

### E19. Retain or delete
7-year retention is required for financial records. 3 years of that data has
never been queried. What is the storage plan, and what is the risk?

<details><summary>Solution</summary>
Plan: keep hot for 90 days, then move to a cold storage class with
irregular-access characteristics, and keep an Iceberg/Parquet copy plus a
manifest so it is discoverable. Not deleting is not free, but the cost of cold
storage for unread data is low; the cost of *not* having it during an audit is
unbounded.
Risk to name: cold storage retrieval latency during an audit, and retrieval
fees. Mitigate by rehearsing one retrieval per quarter, with a stated SLA.
</details>

### E20. What do you monitor first?
Pick the first three signals for a new pipeline, in order, with a threshold
basis for each.

<details><summary>Solution</summary>
1. Freshness — absolute, from the source's SLA, not from a schedule
   assumption. Unambiguous, so it goes first.
2. Volume — relative to a seasonal-naive baseline with a robust scale
   (1.4826 * MAD). Catches partial loads and silent filters.
3. Reconciliation against an independent source — the only check that
   catches a value that is wrong in a plausible way. If there is no
   independent source yet, building one is a project, so start with the
   first two and queue the third.
Not first: row-level validation of every column. Expensive, and it catches
less than these three.
</details>

## Level 4 — Synthesis

### E21. Design a 3-source join at 10k events/sec
Sources: orders (Kafka, 40 partitions), inventory (batch every 5 min), pricing
(third-party API, 50 rps limit, 200ms p99). Requirements: p99 < 300ms,
exactly-once into a warehouse table, hourly reconciliation.

<details><summary>Solution</summary>
- Join inventory via a broadcast state (it is small, and it updates every 5
  min) — no shuffle.
- Pricing: never call the API in the pipeline. Materialize pricing to a local
  lookup every 5 min (50 rps x 300s = 15,000 calls, well within the limit) and
  broadcast it. This is the key move: the API is a batch source, not a
  streaming one.
- Exactly-once: two-phase-commit sink, or a staging table with an LSN guard
  and a commit flip.
- Latency budget: Kafka poll 50ms + processing 100ms + sink commit 100ms =
  250ms, leaving 50ms of headroom.
- Reconciliation: hourly, event-time bounded, against a batch job.
</details>

### E22. Post-mortem structure
A pipeline silently dropped 1.2M rows over 3 days. Write the post-mortem
outline, and state which parts are facts versus hypotheses.

<details><summary>Solution</summary>
Facts: row counts per partition per run (from the load log), the filter change
timestamp, the code version, which consumers were affected.
Hypotheses: why the change was merged without a test, why no monitor fired,
why reconciliation did not catch it.
Sections: impact (rows, revenue, downstream), timeline (UTC), root cause chain
(not a single cause — usually three), what made it invisible (missing
detection), what made it possible (the change), detection improvements
(specific), and prevention (specific). Every action needs an owner and a date;
an action without a date is a wish.
</details>

### E23. Migration with no downtime
Convert 40 tables from raw Parquet to a table format while analysts query
them daily. Describe the sequence and how you verify each step.

<details><summary>Solution</summary>
1. Inventory consumers from query logs. Any table with an unknown consumer set
   does not start.
2. Shadow write: the pipeline writes both formats for one release cycle.
3. Verify: row count and checksum per partition, automated, and a report.
4. Switch reads for one consumer group at a time, with the old path still
   present and a config flag.
5. Hold the source read-only for 30 days. This is what makes rollback a
   metadata change.
6. Delete the old copy only after the full retention of the change window.
Do not do steps 3-5 in one release; the verification is the point.
</details>

### E24. The honest limits question
Name three classes of data bug that distribution monitoring cannot catch, and
for each, what you need instead.

<details><summary>Solution</summary>
1. A small, consistent bias (0.4% from a rounding change). Distributions look
   normal; only a comparison to an independent authority catches it. Need:
   cross-system reconciliation.
2. A logically wrong but plausible aggregate (a join that fans out, so counts
   are inflated, with the shape intact). Need: invariants — the sum of parts
   equals the total, and a grain declaration checked against the actual grain.
3. A value that is correct but too old to use (a reference table that stopped
   updating). Freshness on *reference* data, which is a different SLO from
   freshness on the fact.
Stating these limits is more valuable than claiming coverage, because it
tells the team what to fund next.
</details>
