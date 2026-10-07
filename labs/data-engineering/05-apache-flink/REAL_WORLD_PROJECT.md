# Apache Flink — REAL WORLD PROJECT

## Context

A payments company processes card authorizations and settlement events. A
latency requirement (< 200ms p99 for a risk score) plus an audit requirement
(exactly-once ledger) rules out both a batch approach and a naive
processing-time Flink job. You own the streaming risk engine that consumes
Kafka and writes a ledger table.

## Scale & Constraints

| Dimension | Value |
|---|---|
| Input | 22k events/sec peak, 1.9B events/day |
| Partitions | 512 on the auth topic, keyed by `card_token` |
| Latency SLO | p99 < 200ms, hard fail > 1s |
| Correctness | ledger must be exactly-once, gap-free per `auth_id` |
| State | ~900GB keyed state, 30-day TTL |
| Recovery | RTO < 5 min, RPO = 0 (no acknowledged event may be lost) |
| Deployment | Flink on Kubernetes, 3 AZs |

## Architecture

```
producers (auth gateways) -> Kafka auth topic (512 partitions, key=card_token)
                                      |
                         Flink risk job (p=96)
                         - keyBy(card_token): velocity, geo, device
                         - session windows, timers
                                      |
                     +----------------+----------------+
                     |                                 |
          TwoPhaseCommitSink                 Kafka rules topic
          (ledger staging -> commit)        (downstream models, ML features)
                     |
              ledger (Postgres)  |  audit log (immutable object store)
```

## Key Implementation — idempotent ledger with a seen-set

Exactly-once delivery to an external system requires the sink to cooperate.
The pattern: stage the write, record the transaction in Flink's checkpoint
metadata, and commit only after the checkpoint completes.

```java
public class LedgerTwoPhaseCommitSink extends TwoPhaseCommitSinkFunction<LedgerEntry, Transaction> {

    @Override
    public Transaction beginTransaction() {
        long txId = txnIdSeq.incrementAndGet();
        try (Connection c = dataSource.getConnection()) {
            c.setAutoCommit(false);
            c.createStatement().execute(
                    "CREATE TABLE IF NOT EXISTS ledger_staging (tx_id BIGINT, auth_id VARCHAR(64), ...)");
            c.commit();
        }
        return new Transaction(txId);
    }

    @Override
    public void invoke(Transaction transaction, LedgerEntry entry, Context context) {
        // Idempotency: primary key (auth_id, version). A replay of the same auth_id
        // updates instead of inserting, so even a duplicated event cannot double-book.
        stage(transaction.txId(), entry);
    }

    @Override
    public void commitTransaction(Transaction transaction) {
        promoteStagedToLedger(transaction.txId());   // single atomic SQL transaction
    }

    @Override
    public void abortTransaction(Transaction transaction) {
        deleteStaged(transaction.txId());
    }
}
```

## Time and Watermark Policy

The risk engine must judge a transaction by when it *happened*, not when it was
processed, otherwise a retry after a network blip looks like a fresh attempt.

```java
WatermarkStrategy<AuthEvent> wm = WatermarkStrategy
        .<AuthEvent>forBoundedOutOfOrderness(Duration.ofSeconds(2))   // tight: p99 budget is 200ms
        .withTimestampAssigner((e, ts) -> e.occurredAt().toEpochMilli())
        .withIdleness(Duration.ofSeconds(15));     // an idle partition must not hold the watermark

// Any event older than the watermark is dropped from the risk path but written to
// a late-topic for reconciliation. Dropping silently is how risk numbers go missing.
```

## State Sizing

```
state_bytes ~= keys * avg_value_size * (1 + overhead_factor)
900GB ~= 4.1B card_tokens (30d) * ~180B per (counters + timers) * 1.22
```

Two consequences that shaped the design:

1. **TTL on every keyed state entry.** 30-day TTL is a correctness requirement
   (PCI scope) *and* the lever that keeps state bounded.
2. **RocksDB incremental checkpoints.** Full snapshots of 900GB every 30s is not
   a plan; incremental uploads only changed SST files, so checkpoint duration
   fell from minutes (unusable) to ~12s.

## Failure Modes and the Runbook

1. **Checkpoint duration exceeds the interval.** Symptom: continuous checkpoint
   failures, growing checkpoint backlog. Fix: raise the interval first (state
   volume is the driver), verify RocksDB incremental is on, then split the job.
2. **Watermark stalls.** Symptom: results stop advancing despite traffic. Cause:
   an idle or slow partition. Fix: `withIdleness` so a dead partition does not
   pin the global watermark; alert on `currentOutputWatermark` vs wall clock.
3. **Back-pressure / subpartition queue full.** Symptom: consumer lag grows while
   TaskManager CPU is fine. Cause: a slow external call inside the process function.
   Fix: never call blocking services in the pipeline; use async I/O or a side output.
4. **TaskManager OOM on RocksDB.** Symptom: managed-memory exhaustion. Fix: tune
   the RocksDB write buffer / block cache ratio, and check for a growing list state.
5. **Rescaling from p=96 to p=192.** Symptom: a cold-start delay while state is
   redistributed. Fix: savepoint, rescale, restore; key groups re-assign but state
   redistribution is a full read, so budget the window.
6. **Broker-side retention shorter than recovery needs.** Symptom: a restored job
   cannot catch up past retention. Fix: retention >= worst-case RTO + catch-up time.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Flink provides stateful stream processing with checkpointing and recovery:
  consistent snapshots let a job restore from the last completed checkpoint, and
  end-to-end exactly-once relies on the sink committing with the checkpoint.
  - Reference: https://flink.apache.org/what-is-flink/
  - Reference: (link removed)
  - Reference: (link removed)
- Kafka consumer groups partition the work; each partition is consumed by exactly
  one member, and committed offsets define the restart position.
  - Reference: https://kafka.apache.org/documentation/#intro_concepts_and_terms
  - Reference: https://kafka.apache.org/documentation/#consumerconfigs

## Deliverables
- [ ] Two-phase-commit ledger sink with an idempotency proof
- [ ] Watermark policy document: ordering assumption, idleness, late-data path
- [ ] State sizing calculation and the TTL policy that makes it hold
- [ ] Crash + broker-failover + rescale test scripts with measured RTO
- [ ] Runbook for all six failure modes
- [ ] p99 latency budget breakdown from broker to ledger commit
