# CODE DEEP DIVE — Reading the Machinery

Six places where the code tells you something the documentation does not.

## 1. The Kafka producer's durability path

What `acks=all` + `enable.idempotence=true` actually guarantees, traced:

```
producer.send(record)
  -> partitioner picks partition p, leader L
  -> append to L's log            (L fsyncs per its own config)
  -> followers replicate           (R - 1 followers)
  -> acks collected from ISR
  -> if the leader dies and p is not in the ISR of the *new* leader,
     the record can be lost even with acks=all
```

So `acks=all` means "all in-sync replicas", not "all replicas". `min.insync.replicas`
is what protects against losing data when a follower is lagging. The
configuration that actually provides durability is three settings together:

```
acks=all
min.insync.replicas=2      # with RF=3
enable.idempotence=true
```

Without the second, `acks=all` can be satisfied by one replica and the write
succeeds even though a single node loss loses the record.

Idempotence's scope is also worth knowing: it dedupes retries from **one
producer session** within `max.in.flight.requests` ordering. It does not
dedupe across producer restarts unless you set a transactional id, and it does
not help if your application publishes the same logical event twice.

## 2. Flink's checkpoint barrier, step by step

This is the mechanism behind every exactly-once claim, so it is worth being
precise.

```
1. Source injects a checkpoint barrier into the stream at time T.
2. Barrier flows downstream through operators. Each operator:
     a. snapshots its state
     b. forwards the barrier
3. Sink receives the barrier, flushes, and pre-commits.
4. Checkpoint is marked complete when ALL barriers are received.
5. On completion, the coordinator persists the checkpoint metadata.
6. On recovery, state is restored from the last COMPLETED checkpoint.
```

Three consequences that show up in production:

- **Unaligned checkpoints** exist because step 2 can stall: if a slow task is
  still holding buffered records, the barrier queues behind them. Unaligned
  mode ships the in-flight buffers as part of the snapshot instead of waiting.
- **Checkpoint duration is state-dependent.** A 900GB heap-state job cannot
  checkpoint in 30s; the same job on an incremental RocksDB backend can.
- **A checkpoint that is never completed provides no protection.** "Checkpoint
  success rate 78%" means 22% of your recovery points do not exist, even though
  the job is "running".

## 3. A table format's transaction log

Both major open formats solve the same problem: multiple writers to object
storage without a distributed lock.

Delta's mechanism:

```
writer A: read snapshot v41 -> write data file A -> commit v42 (atomic rename of 42.json)
writer B: read snapshot v41 -> write data file B -> commit v42
         -> rename fails: FileAlreadyExists
         -> ConcurrentModificationException -> re-read v42, re-apply, retry
```

The atomic rename is the commit. That is why it is a rename and not a write:
object storage gives you atomic single-object replacement, and everything else
is built on it.

The failure mode to know: **optimistic concurrency means writers conflict, and
the resolution is retry**. Two jobs MERGEing the same partitions hourly will
conflict repeatedly. The fix is partition ownership, not more retries.

## 4. Spark's shuffle, and why fusion is the point

A shuffle is: hash-partition, serialize, write to disk, then read and
desaggregate. It is the most expensive operation in the engine.

```
map side:   row -> hash(key) -> partition p -> write p
reduce side: read all p files -> deserialize -> aggregate
```

The cost is `2 x network + 2 x disk`. Everything in Catalyst's optimizer is
aimed at removing shuffles:

- **Predicate pushdown** removes rows before the exchange.
- **Broadcast hash join** replaces a shuffle with a broadcast (cheap when one
  side fits in memory).
- **AQE** coalesces post-shuffle partitions and can convert SMJ to BHJ at
  runtime, and can split skewed partitions.
- **Whole-stage codegen** fuses operators so intermediate results never
  materialize.

The diagnostic habit: read the physical plan and count exchanges. Two
exchanges for a query that could have one is the most common avoidable cost.

## 5. Incremental aggregation and why it is not free

`partial -> shuffle -> final` is not only about network. It is about
**serialization volume**, and it interacts with skew.

```java
// Without partial aggregation: every reducer reads raw values
reduceByKey -> sum(raw)
// With it: the map side aggregates first, so the shuffle carries n/m partials
map-side partial sum -> shuffle -> sum(partials)
```

Cost model: with `m` mappers and shuffle size `S`, partial aggregation ships
roughly `min(n, m * distinct_keys_per_mapper) / n * S`. With high skew, one
key's partials dominate anyway, which is why you also need salting or
pre-aggregation at the source.

The trap: partial aggregation **changes the accumulator type**, and a
floating-point accumulator is order-dependent. `sum` of doubles under
partial aggregation is not bit-identical to a non-partial sum. If you need
determinism, use integer or decimal accumulators. This is the same root cause
as the Beam cross-runner divergence in lab 12.

## 6. Back-pressure: what actually happens

When a downstream operator is slower than upstream, the runtime must stop
upstream. The mechanisms differ and so do the symptoms:

| Mechanism | Where | Symptom when saturated |
|---|---|---|
| bounded buffer + block | Flink network stack | `subtask is busy` backpressure metric rises |
| credit-based flow control | Kafka consumers | `poll()` blocks, lag grows |
| task not scheduled | YARN/K8s queue | queued for minutes, DAG serialization climbs |
| connection pool | JDBC sinks | pool exhausted, timeouts, not backpressure |

The mental model: back-pressure is *correct behaviour*. A pipeline that never
applies back-pressure has unbounded queues somewhere, and that is worse — it
converts a throughput problem into a latency problem and then an OOM. When you
see lag grow with healthy CPU, the bottleneck is downstream I/O, and the fix is
to make the downstream faster or buffer on purpose with a stated bound.

## 7. Bounded queue sizing, concretely

```java
int bufferSize = (int) Math.min(maxBatch, (int) (targetLatency.toMillis()
        * throughputPerSecond / 1000 / recordsPerMessage));
```

Too small: you flush constantly, so per-request overhead dominates and
throughput collapses. Too large: you batch well but add `bufferSize /
throughput` of latency. The usual answer is to size for throughput, then state
the resulting latency as an SLO.

## 8. Idempotency: four mechanisms, pick one

```java
// 1. Natural key + upsert. Best when you have one.
ON CONFLICT (business_key) DO UPDATE SET ... WHERE excluded.version > t.version;

// 2. Monotonic position. Best when the source has a sequence (LSN, offset).
if (event.position > lastApplied.get(key)) apply(event);

// 3. Dedup window. When the source can re-deliver inside a known bound.
if (!seen.add(key + position)) return;      // TTL'd set

// 4. Idempotency key at the API. When the sink is an external service.
POST /payments  Idempotency-Key: <event-id>
```

Each has a failure mode: (1) needs a natural key, (2) needs ordered delivery,
(3) needs a bounded window, (4) needs the sink to cooperate. Choose
deliberately; "it is idempotent" is not an answer without a mechanism.

## 9. Reading a plan like an operator

```
$ ...  explain
== Physical Plan ==
AdaptiveSparkPlan (14)
+- == Final Plan ==
   * HashAggregate (8)                                 <- the work
   +- AQEShuffleRead (6)
      +- ShuffleQueryStage (5), Statistics(...)        <- shuffle 1
         +- * HashAggregate (4)
            +- AQEShuffleRead (2)
               +- ShuffleQueryStage (3)                <- shuffle 2
                  +- Scan parquet orders
```

Read it top-down as: *what is aggregated, from what, after how many network
hops, scanning how much data*. Two shuffle stages in a two-table join where one
side is 12k rows means a broadcast join was missed. That is the whole skill.

## 10. Things that look like bugs and are not

- Non-deterministic output order in a distributed job. There is no defined
  order; add a sort if you need one.
- `NaN` in a double aggregate from `0/0`. Guard the denominator.
- A float aggregate differing between runs or runners. Accumulation order.
- Empty partitions in a window. A window with no events does not fire.
- Records appearing after a watermark that already passed. That is what
  "late" means.
