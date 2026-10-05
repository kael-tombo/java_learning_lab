# FLASHCARDS — 60 Cards

Format: **Q** — front. **A** — back. One card per line pair; study 20/day.

---

## Time (1)

**Q:** Event time vs processing time — when is each correct?
**A:** Event time for any business-correct number; processing time only for
operational metrics about the pipeline itself.

**Q:** What is a watermark?
**A:** A promise from the runtime about how much lateness to expect:
`watermark = max_event_time_seen - out_of_orderness_bound - delay`. Events
after it are late.

**Q:** Is a watermark a guarantee?
**A:** No. It is a bound based on an assumption about producers. Events still
arrive after it, and a restart can move it backwards.

**Q:** Why set per-source watermarks rather than one global bound?
**A:** Lateness is a property of the producer. One producer flushes in 2s
(playback events), another every 20 min (ad logs). A single bound is wrong for
one of them.

**Q:** What does `withIdleness` do?
**A:** Stops an idle partition from holding back the global watermark, which
otherwise freezes all output.

**Q:** Allowed lateness vs a too-late path.
**A:** Within the bound, emit a correction. Beyond it, route to reconciliation
(a batch pass), because corrections nobody can reconcile are just noise.

**Q:** What breaks when you move from processing to event time, and why does
the number change?
**A:** Late records land in the correct window instead of the next one, so
historical numbers shift. It is usually a correctness fix, not a regression.

---

## State (2)

**Q:** The cost formula for keyed state.
**A:** `keys x value_size x (1 + overhead)`. Overhead factor is real: map
entries and serialized bytes are not the same thing.

**Q:** `ListState` of history vs bucketed aggregates — which and why?
**A:** Aggregates. History is O(n) per event and grows without bound; a
bucketed counter is O(1) and TTL-bounded. This is the 2.4TB-to-340GB fix.

**Q:** What does incremental checkpointing track?
**A:** Changed state only (new SST files), not total state. Checkpoint cost
stops scaling with total size.

**Q:** Why does a 900GB job need RocksDB over heap state?
**A:** Incremental checkpoints. A full snapshot every 30s of 900GB is not a
plan; the same job with incremental RocksDB checkpoints in ~12s.

**Q:** What is a key group?
**A:** The unit of state assignment. `keyGroupCount = parallelism * slotsPerTask`.
Rescaling redistributes key groups, and state redistribution is a full read.

**Q:** Transient vs non-transient field state?
**A:** `transient` fields are not checkpointed. Use it for things reconstructible
from state, never for correctness-relevant values.

**Q:** When is a `ListState` the right choice?
**A:** When the value is small and fixed (e.g. last 3 events), or when a
`ListState` is paired with a TTL. Never "all events, scan per element".

---

## Delivery (3)

**Q:** The four delivery semantics.
**A:** at-most-once, at-least-once, effectively-once (at-least-once + idempotent
sink), exactly-once (transactional sink or source+sink pair).

**Q:** Does Kafka give exactly-once to your HTTP sink?
**A:** No. Exactly-once covers the pipeline, not an external API. Use an
idempotency key at the API.

**Q:** Four ways to make a sink idempotent.
**A:** natural key + upsert; monotonic position (LSN/offset) check; bounded
dedup window; idempotency key at the API.

**Q:** Ordering guarantee in Kafka.
**A:** Within a partition only. Cross-partition ordering needs one partition
(no parallelism) or a design that does not need it (sequence + reorder).

**Q:** `acks=all` plus RF 3 — is that durable?
**A:** Only with `min.insync.replicas=2`. `acks=all` means "all in the ISR", so
without it a lagging replica can be excluded and later become leader.

**Q:** Idempotent producer scope.
**A:** One producer session, within `max.in.flight.requests` ordering. Not
across restarts (unless transactional) and not across application-level
duplicate publishes.

**Q:** What does a rebalance cost, and how do you reduce it?
**A:** A stop-the-world pause while the group re-assigns partitions. Reduce with
static membership (`group.instance.id`), incremental cooperative
assignment, and processing off the poll thread.

---

## Schema (4)

**Q:** The three compatibility directions.
**A:** BACKWARD (new readers read old data), FORWARD (old readers read new
data), FULL (both). A topic that is read and written needs FULL.

**Q:** Which changes are safe without coordination?
**A:** Adding a nullable field, or widening a type. Everything else is breaking.

**Q:** Why is a rename breaking even though the data is identical?
**A:** Readers still reference the old name, and a permissive deserializer
will not fail — it will silently produce nulls.

**Q:** What must a schema registry actually enforce?
**A:** Compatibility at commit time, so a breaking change cannot reach
production. A registry that only warns is documentation.

**Q:** Snapshot-then-stream in CDC — the classic bug.
**A:** Starting the stream at "now" after the snapshot loses rows changed
during it. Record the LSN before reading, buffer, then drain.

---

## Partitioning & Scale (5)

**Q:** Two constraints on partition count.
**A:** Bandwidth (`throughput x size x headroom / per-broker`) and consumer
parallelism. Take the max; almost everyone computes only bandwidth.

**Q:** Cardinality rule for partition columns.
**A:** Never partition on a high-cardinality column. Use time (low-medium) plus
a bucket transform for the high-cardinality filter column.

**Q:** What is skew, and what is the cheap fix?
**A:** One key carrying a disproportionate share of a partition's work. Fix:
pre-aggregate at the source if the hot key is itself a sum; otherwise salt
deterministically.

**Q:** Diagnose skew from metrics.
**A:** max task time / median task time > 5 within a stage.

**Q:** What is back-pressure, and is it a bug?
**A:** A downstream-limited upstream being slowed deliberately. It is correct
behaviour; the alternative is unbounded queues, which converts a throughput
problem into OOM.

**Q:** Little's law.
**A:** `L = lambda x W`. In-flight items = arrival rate x time in system. Size
workers so utilization stays below 0.7.

**Q:** Why 0.7?
**A:** Queue delay grows non-linearly as utilization approaches 1, and the
service-time *tail* makes the mean a bad estimate. 0.7 is the conventional
ceiling for a tail-sensitive workload.

---

## Storage (6)

**Q:** Data files vs metadata files in a table format.
**A:** Data files hold rows (Parquet). Metadata files hold the manifest list
and manifests describing which files are live — the difference between O(1)
planning and listing the whole table.

**Q:** Manifest summaries vs file statistics.
**A:** Two pruning levels: skip a whole manifest by partition range, then skip
individual files by column min/max.

**Q:** Hidden partitioning.
**A:** Partitioning by a transform of a column so `WHERE ts >= X` prunes
without the user writing a partition predicate. It is why re-partitioning does
not break queries.

**Q:** Small files: why and what fixes them.
**A:** Listing and task-scheduling overhead. Fix: compaction to a target file
size, and never repartition to a tiny target.

**Q:** Target file size guidance.
**A:** 128MB-1GB. Below 128MB task overhead dominates; above 1GB you lose
read parallelism.

**Q:** Delta vs Iceberg, one line each.
**A:** Delta: JSON transaction log, ACID, time travel, MERGE-centric, from
Spark. Iceberg: Avro metadata, snapshots, hidden partitioning, first-class row
deletes, multi-engine.

---

## Correctness (7)

**Q:** Point-in-time correctness.
**A:** For a label at `label_ts`, only feature rows with `event_ts <= label_ts`
are visible. Violating it leaks the future and inflates offline metrics.

**Q:** What is an independent source for reconciliation?
**A:** One that does not share code with the pipeline. Two pipelines sharing a
library agreeing proves nothing.

**Q:** Tolerance in a reconciliation.
**A:** An explicit business number (e.g. 0.5% contractual), not "close
enough". Without a stated tolerance the check is decoration.

**Q:** Invariant vs expectation.
**A:** An invariant is a relation that must always hold (parts sum to the
total). An expectation is a per-row check. Invariants are cheaper and catch
structural bugs.

**Q:** The declared grain.
**A:** The level of detail a fact row represents. Two grains in one table is
the most common modelling error, and it makes every aggregate ambiguous.

**Q:** The rounding incident class.
**A:** Sum integer minor units, scale once, at the boundary. Rounding inside an
aggregation is a systematic bias that every distribution check passes.

---

## Cost (8)

**Q:** The four cost lines in a cloud warehouse.
**A:** Storage, bytes scanned, compute, and requests (plus egress).

**Q:** Which line can you actually move?
**A:** Bytes scanned and compute. Storage follows from retention choices;
requests follow from file counts.

**Q:** Highest-leverage analytics cost move.
**A:** Pre-aggregation. It turns an expensive question into a cheap one,
permanently.

**Q:** Cost of deleting one row from a plain Parquet file.
**A:** A full rewrite of the file. Which is why Iceberg equality deletes exist.

**Q:** Clustering trade-off.
**A:** Faster reads with pruning, at the cost of write amplification and a
rewrite. Only worth it for read-heavy tables, and only on low-to-medium
cardinality columns.

**Q:** Idle warehouse time.
**A:** Pure waste. Auto-suspend and auto-resume are usually the single largest
saving available in a Snowflake-style estate.

---

## Reliability (9)

**Q:** Backfill requirements.
**A:** Isolated (separate pool, shadow table or branch), verified
(reconciliation), and restartable. If you cannot backfill safely, you cannot
deploy safely.

**Q:** Why backfills surface bugs that normal runs do not.
**A:** They recompute with today's code against historical data, so any
non-determinism or point-in-time assumption breaks.

**Q:** Error budget vs fixed threshold.
**A:** A budget is spent by failures and refills over the SLO window. A fixed
threshold either fires constantly or never. Burn-rate routing is the practical
form: page fast, ticket slow, stay silent inside budget.

**Q:** MTTD vs MTTR vs MTTU.
**A:** Detect, resolve, and *understand*. The third is what determines whether
the same incident recurs.

**Q:** What makes an alert actionable?
**A:** A named dataset, the likely cause, the first command, and a runbook
link. Ten pages saying "error" are worth less than one page that names the
cause.

**Q:** Purge vs logical delete for erasure.
**A:** Purge. A `deleted_at` flag or a filtered query leaves the personal data
present, which fails the requirement.

---

## Governance (10)

**Q:** Default-deny classification.
**A:** Unclassified columns are RESTRICTED, not PUBLIC. Classification that
depends on someone remembering to tag a column will be incomplete within a
month.

**Q:** Why store classification evidence?
**A:** Because the auditor's question is "how do you know", and at audit time
the sample data is gone. Evidence is written at classification time.

**Q:** Exception expiry must re-block. Why?
**A:** Otherwise the exception is a permanent undocumented bypass,
indistinguishable from no control. Expiry that does not bite is not a control.

**Q:** The six governance problem areas.
**A:** Classification, access, lineage, retention, deletion, and evidence.
Map your regulatory regimes onto controls, not programmes.

**Q:** What is lineage used for operationally?
**A:** Impact analysis before a change, and erasure scope. Without it, "delete
this person's data" is unanswerable.

**Q:** Data contract vs documentation.
**A:** A contract is executed — evaluated in the pipeline, failing a build. A
document is reviewed once.

---

## Synthesis (mixed)

**Q:** Batch or streaming? The decision rule.
**A:** Match the latency requirement. If the requirement is "hourly", build
batch. Do not build a stream for a batch requirement.

**Q:** New column, nullable, on a streaming table.
**A:** Safe, with schema-on-read so late-arriving fields do not require a
restart. A *required* new column is a breaking change.

**Q:** A pipeline succeeds and the number is wrong. What is missing?
**A:** Data-level monitoring. Task success and data correctness are different
claims, and only one of them is instrumented by default.

**Q:** What is the honest limit of distribution monitoring?
**A:** Small consistent biases, logically wrong-but-plausible aggregates, and
stale-but-well-shaped reference data. For those you need reconciliation,
invariants, and freshness on reference data.

**Q:** Why does a "metrics" layer matter?
**A:** Two dashboards computing revenue slightly differently, both "correct",
is an unresolvable argument. Define once, read everywhere.

**Q:** The one-sentence definition of production data engineering.
**A:** Moving data correctly, on time, at a known cost, with the ability to
prove it was correct and to rebuild any past answer.
