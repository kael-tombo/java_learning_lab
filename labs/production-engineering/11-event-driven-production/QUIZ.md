# Lab 11: Event-Driven Architecture & Kafka in Production — QUIZ

15 questions. Answer first. Target: 13/15.

---

**Q1. What does "delivery semantics" actually describe, and what are the three real options?**
- A) Network-level guarantees only
- B) At-most-once (messages may be lost), at-least-once (messages may be duplicated), exactly-once (no loss, no duplicates — achievable only within a Kafka transaction boundary; external side effects still need idempotency)
- C) Only two options exist
- D) Exactly-once is achievable for any side effect

**Answer: B** — Choose at-least-once plus idempotent consumers as the practical default. Exactly-once in Kafka means atomicity across partitions read/write and to Kafka; a database write or an HTTP call inside the same transaction needs idempotency or a distributed transaction.

---

**Q2. What problem does the Transactional Outbox pattern solve?**
- A) Slow consumers
- B) The dual-write problem: writing to the DB and publishing to Kafka are two systems with no shared transaction, so one succeeds and the other fails. Write the event to an outbox table in the same DB transaction, then publish asynchronously with a relay
- C) Partition skew
- D) Schema evolution

**Answer: B** — Without it, you either lose events (DB committed, publish failed) or publish phantom events (published, DB rolled back). The relay must be at-least-once, so consumers are still idempotent.

---

**Q3. Why must a consumer be idempotent if the outbox relay is at-least-once?**
- A) Because brokers can corrupt messages
- B) Because the relay can crash after publishing but before recording the position, and because consumer rebalances replay committed-but-uncommitted offsets — the same event will be delivered again
- C) Because of partition reordering
- D) Because producers may send duplicates

**Answer: B** — Idempotency key = `(consumer_group, topic_partition, offset)` or a business key in a dedup table; check-and-insert inside the same transaction as the state change.

---

**Q4. What does `enable.idempotence=true` on a Kafka producer give you, and what does it not give you?**
- A) Exactly-once end-to-end
- B) Idempotent production per partition (the broker rejects a duplicate sequence number), so a producer retry does not create a duplicate record — it does not deduplicate across application logic, across topics, or against external side effects
- C) Ordering guarantees
- D) Compression

**Answer: B** — Combine with `acks=all`, `retries>0`, and `max.in.flight.requests.per.connection=5` (or the idempotence constraint on in-flight requests) for the standard ordering-preserving configuration.

---

**Q5. Why can a consumer get a *rebalance storm*, and what parameters mitigate it?**
- A) It is caused by too many partitions
- B) When consumers are slow (processing exceeds `max.poll.interval.ms`) or sessions flap (`session.timeout.ms`), the coordinator repeatedly revokes and reassigns partitions. Mitigate with a longer `max.poll.interval.ms`, manual `assign()`/`assignPartitions` where possible, a static group membership (`group.instance.id`), and smaller poll batches
- C) It is caused by the producer's `linger.ms`
- D) It only happens on consumer restarts

**Answer: B** — The classic symptom is lag stops making progress while CPU is idle: consumers are stuck in rebalance, not processing.

---

**Q6. Why does increasing `max.poll.records` risk a rebalance storm?**
- A) It cannot cause one
- B) A bigger batch takes longer to process; if `processing_time > max.poll.interval.ms`, the consumer is kicked out mid-batch and rebalance repeats — the fix for throughput becomes the cause of the outage
- C) It increases network traffic proportionally
- D) It changes consumer group membership

**Answer: B** — Always pair batch size with `max.poll.interval.ms`, and prefer pause-and-persist processing with manual commits (`pause()` → process → `commitSync()` → `resume()`).

---

**Q7. What does a "hot partition" cost, and what are the mitigations?**
- A) Nothing, brokers balance automatically
- B) All traffic for one key lands on one partition, so that partition's broker caps throughput and one consumer does all the work; add random salting (key + random suffix) for volume-driven keys, expand the partition count, or split the stream
- C) It only affects latency
- D) It is a producer-side problem

**Answer: B** — Salting destroys per-key ordering. Use it only where ordering is not required; otherwise you must re-key and accept a two-phase or ordered-consumer design.

---

**Q8. Increasing partition count on an existing topic: what breaks?**
- A) Nothing; it is transparent
- B) Partitions are the unit of parallelism and are ordered only within a partition; adding partitions **destroys ordering across the new boundary** for existing keys (an old key's earlier messages can land in a different partition than later ones). Keys are re-hashed, so key-based ordering across the expansion point is not preserved
- C) Consumer offsets are invalidated
- D) Retention resets

**Answer: B** — Offsets are per `(group, topic, partition)`, so existing offsets survive; the risk is ordering. If ordering matters, drain the topic, add partitions, and re-seed, or introduce a new topic.

---

**Q9. When do you need a Dead Letter Queue, and what must it record?**
- A) Never; just log the failure
- B) When a poison message would otherwise block the partition forever. The DLT record must carry the original payload, the failure class, the attempt count, the original topic/partition/offset, the timestamp, and a correlation id — and it needs its own retention and alerting
- C) Only for schema errors
- D) DLTs are a broker feature

**Answer: B** — The common failure is a DLT that receives a bare message, so you cannot reproduce or attribute the failure. Also alert on DLT depth, not just rate: a growing DLT is a silent data-loss queue.

---

**Q10. Consumer lag: what does it measure and what are the misleading readings?**
- A) Lag = messages waiting to be consumed, i.e. consumer lag rate versus production rate; it is misleading when a consumer is paused or stuck in rebalance (lag grows with zero processing), and when retention is short enough that the oldest unread messages have already expired (data is *lost*, not just late)
- B) Lag = processing time
- C) Lag is always accurate
- D) Lag measures producer errors

**Answer: A** — Alert on `lag_growth_rate` and on `oldest_unconsumed_age` versus retention. Lag = 0 with an expired oldest offset means silent loss.

---

**Q11. Schema evolution with Avro/Schema Registry: which changes are compatible?**
- A) Any field change
- B) Adding a field with a default is backward-compatible; removing a field, renaming it, changing its type, or making an optional field required is not — and the allowed set depends on the registry's configured compatibility level (`BACKWARD`, `BACKWARD_TRANSITIVE`, `FULL`, `FORWARD`)
- C) Only adding fields is allowed, always
- D) Compatibility is not enforced

**Answer: B** — `FULL` is the safest default. Choose `BACKWARD_TRANSITIVE` deliberately when you have multiple versions of consumers reading the same topic, since `BACKWARD` alone does not guarantee an old reader can read new data.

---

**Q12. Event sourcing vs event-driven messaging: what is the difference?**
- A) They are synonyms
- B) Event-driven is about *transport and decoupling*; event sourcing is a *persistence decision* where the event log is the source of truth and state is a projection. You can use events without event sourcing (CQRS with a plain read model) and you should not adopt event sourcing without snapshotting and upcasters
- C) Event sourcing requires Kafka
- D) Event-driven requires CQRS

**Answer: B** — Adopting event sourcing adds permanent obligations: projections must be rebuildable, schemas must be upcastable, and every query may be a projection problem. Those are the costs to state in a decision record.

---

**Q13. What does "consumer group isolation" buy you, and what does it not protect you from?**
- A) It isolates CPU only
- B) A group gets its own offsets and its own partitions, so multiple teams can consume the same topic independently. It does *not* protect the broker or the topic from a single badly behaved group (one slow consumer only blocks its own partitions, but a large group can exhaust broker I/O and the group coordinator)
- C) It gives per-message guarantees
- D) It partitions by message content

**Answer: B** — Isolation is logical (offsets/assignments), not resource (I/O/CPU/page cache). Quota and separate topics are the resource controls.

---

**Q14. Why prefer a `Consumer` over a producer for backpressure?**
- A) Consumers are faster
- B) A consumer that cannot keep up simply stops committing offsets, so the broker retains the backlog and no data is lost; a slow *producer* blocks or accumulates in the client buffer, and a broker that runs out of disk is unrecoverable. Pull-based flow control gives you backpressure for free
- C) Consumers auto-scale
- D) Producers do not support batching

**Answer: B** — The corollary: capacity planning must assume the backlog is *storable*. `retention.bytes`/`retention.ms` must exceed your maximum tolerated outage duration × production rate.

---

**Q15. The single most common cause of a Kafka-related outage in a Java service is?**
- A) Broker hardware failure
- B) A consumer whose processing time exceeds `max.poll.interval.ms`, triggering endless rebalances so lag grows unbounded while CPU sits idle and the downstream data is silently falling behind — often triggered by a downstream slowdown that nobody alerted on
- C) A schema mismatch
- D) Too many partitions

**Answer: B** — The signature is "lag growing, consumer CPU ~0, no errors." Always alert on consumer lag growth *and* on processing-time vs poll-interval margin, and size the downstream so the margin is explicit.

---

## Scorecard
- 15–13: excellent — proceed to MINI_PROJECT and build a real event pipeline.
- 12–10: revisit consumer configs, outbox, and idempotency; redo EXERCISES 2–5.
- <10: re-read THEORY + `RAFT_CONSENSUS_ENGINE`-style mental model of the log, then retake in 48 hours.
