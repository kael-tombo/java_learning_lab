# Lab 11: Event-Driven Architecture & Kafka in Production — Flashcards

~60 cards. Most answers are a config key or a number.

---

## Log fundamentals

Q: What is a Kafka partition's guarantee?
A: Append-only, totally ordered per partition, replicated by the leader's ISR, and each record has an `(partition, offset)`.

Q: What is the role of the consumer offset?
A: The next record to consume. `enable.auto.commit=true` commits in the background and can **lose** messages (committed before processing); use `false` plus explicit `commitSync()` after processing.

Q: `acks=0/1/all` trade-off?
A: 0 = no acknowledgement (loss possible); 1 = leader ack (leader failure loses records); `all` = wait for the full ISR (strongest, standard choice).

Q: Minimum safe producer config?
A: `acks=all`, `retries>0`, `enable.idempotence=true`, `max.in.flight.requests.per.connection≤5`, a sensible `delivery.timeout.ms` larger than `request.timeout.ms`.

Q: What does `enable.idempotence=true` cover?
A: Duplicate suppression per (producer, partition) via sequence numbers, plus ordering guarantees for in-flight requests. Not end-to-end dedup, not external side effects.

Q: `linger.ms`?
A: Batching delay to fill a batch. Higher = better throughput, higher first-record latency. Typical 5–50 ms for throughput-oriented producers.

Q: `compression.type`?
A: `lz4` or `zstd` normally; `gzip` costs more CPU. Compression saves network, disk, and broker I/O — often the cheapest capacity win available.

Q: `batch.size` vs `buffer.memory`?
A: `batch.size` is the target batch size per partition; `buffer.memory` is the total per-partition buffer. `buffer.memory` exhaustion triggers a block up to `max.block.ms`.

Q: Partition count = parallelism ceiling?
A: Yes. Throughput ≤ `partitions × per-partition throughput`, and consumer parallelism in a group ≤ partition count.

Q: What is the `key` used for?
A: `hash(key) % partitions` determines the partition. Same key ⇒ same partition ⇒ ordering per key.

Q: Ordering guarantee scope?
A: Only within a partition, and only for a single producer instance. Two producers writing the same key can interleave.

Q: Null keys?
A: Go to the sticky/round-robin partitioner — effectively random distribution, so no ordering at all.

Q: Retention: `retention.ms` vs `retention.bytes` and segment rollover?
A: A segment is deleted when it is older than `retention.ms` **or** the log exceeds `retention.bytes`, checked at rollover (`log.roll.hours`). Compacted topics delete by key instead.

Q: Log compaction?
A: For keyed topics, keeps the latest value per key (`cleanup.policy=compact`). Great for state, wrong for an event history.

---

## Consumer configuration

Q: `max.poll.records`?
A: Max records returned per `poll()`. Bigger = more throughput per poll, but more time in processing.

Q: `max.poll.interval.ms`?
A: The maximum time between two `poll()` calls before the consumer is considered dead and kicked out. **This is the setting that causes rebalance storms.**

Q: `session.timeout.ms`?
A: Failure-detection time for heartbeats between polls. Must be well below `max.poll.interval.ms`.

Q: `group.instance.id` (static membership)?
A: Gives the consumer a stable identity so rebalances are avoided on restart/reconnect. Requires a rolling upgrade of group members and a broker version that supports it.

Q: Rebalance listener cost?
A: `onPartitionsRevoked` must **commit and drain** before partitions are reassigned, or the next consumer reprocesses. A slow revoke callback itself prolongs the rebalance.

Q: Symptom of a rebalance storm?
A: Lag grows, consumer CPU near zero, `consumer-group-rebalance` / "partitions revoked" logs repeating, processing effectively stopped.

Q: Pause-and-persist pattern?
A: `poll()` → `pause(partitions)` → process → commit → `resume()`. Prevents a long batch from being interrupted mid-flight.

Q: Manual assignment (`assign()`)?
A: Skips the group protocol entirely: no rebalances, no offsets in the group (you manage them), no horizontal scaling. Right for fixed, small consumer sets; wrong when you need dynamic scaling.

Q: Consumer group isolation?
A: Each group has its own offsets and its own partition assignment, so multiple groups can read the same topic independently. Logical isolation only — not I/O isolation.

Q: Quotas?
A: Producer/consumer quotas (`client.id`/user quotas) bound bandwidth per client, protecting the cluster from one tenant.

---

## Idempotency, transactions, outbox

Q: Dual-write problem?
A: DB commit and Kafka publish are two transactions with no shared atomicity — either the event is missing or the state is wrong.

Q: Outbox pattern?
A: Write the event to an `outbox` table **in the same transaction** as the state change; a relay polls and publishes. Guarantees at-least-once publication.

Q: Outbox relay variants?
A: Debounced poll of a status column, or CDC (Debezium) from the WAL. CDC is lower latency and does not poll, but adds operational machinery.

Q: Do outbox consumers still need idempotency?
A: Yes — the relay is at-least-once (it can publish then crash before marking sent), and consumer rebalances replay.

Q: Idempotency key options?
A: `(group, topic, partition, offset)` for exact replay protection, or a business key (e.g. `paymentId`) in a dedup table for cross-delivery protection. Business keys are what you need when the same logical event can arrive from more than one topic.

Q: Check-and-insert idempotency?
A: `INSERT INTO processed (event_id) VALUES (?) ON CONFLICT DO NOTHING` in the same transaction as the state change — one atomic unit.

Q: Kafka transactions (`transactional.id`)?
A: Give exactly-once *within Kafka*: consume-process-produce atomically, with offsets committed to the transaction. Requires `read_committed` on the consumer side, costs throughput, and does not extend to a database.

Q: Exactly-once across Kafka and Postgres?
A: Not with Kafka transactions. Options: (a) idempotent consumer + dedup table (at-least-once + dedup), (b) the outbox pattern, (c) XA/other distributed transactions (rarely worth it). Choose (a) or (b).

Q: Source of truth rule?
A: A state-changing consumer must not be the only writer of its state; either it is idempotent against the same source of truth, or it is a projection that can be rebuilt.

---

## Design patterns

Q: Saga pattern: why not a distributed transaction?
A: Because coordinating a two-phase commit across a database, a broker, and an HTTP boundary is unavailable-prone and slow. Sagas compensate explicitly instead.

Q: Choreographed vs orchestrated saga?
A: Choreographed: each service reacts to events, no central coordinator — simple, but the flow is hard to see. Orchestrated: a coordinator drives the steps and decides compensations — explicit and debuggable, at the cost of a new component.

Q: Compensating action vs rollback?
A: There is no true rollback across services; you publish a compensating event (`RefundIssued` vs `PaymentCaptured`) that semantically undoes the effect. It must itself be idempotent and may be visible to users in between.

Q: When is a synchronous call better than an event?
A: When the caller needs the answer now (validation, authorization, price), the user is waiting, and the dependency is reliable. Events are for decoupling and for work the caller does not need to wait for.

Q: Command vs event naming?
A: Commands are imperatives addressed to one handler (`CreateOrder`, `CancelOrder`); events are past-tense facts (`OrderCreated`, `OrderCancelled`) that any number of consumers may react to. Naming enforces the distinction.

Q: Who owns a topic?
A: Exactly one team owns the schema and the publish contract. Consumers subscribe without owning it; that ownership boundary is what prevents schema drift.

---

## Schema evolution

Q: Schema Registry purpose?
A: Enforce compatibility on write so a schema break cannot reach the topic, and let consumers resolve writer/reader versions at read time.

Q: Compatibility levels?
A: `BACKWARD` (new schema can read old data), `FORWARD` (old schema can read new data), `FULL` (both), `BACKWARD_TRANSITIVE`, `FULL_TRANSITIVE` (compare against *all* previous versions).

Q: Safe change?
A: Add a field **with a default**. Removing/renaming a field, changing a type, or removing a default breaks compatibility.

Q: Removing a field: which direction breaks?
A: Removing it breaks *forward* compatibility (new data has no such field for an old reader). Mark it with a default of null and deprecate, rather than deleting.

Q: Changing a field type int → string?
A: Breaking in both directions under `FULL`. Introduce a new field with a new name and deprecate the old one.

Q: `optional` → `required` on a new field?
A: Breaking (an old record may lack it). Ship as optional first, then tighten after consumers are upgraded.

Q: Enum: add a new symbol?
A: Backward-compatible for writers, forward-risky for readers that match exhaustively. Document that consumers must tolerate unknown symbols.

Q: `FULL_TRANSITIVE` vs `FULL`?
A: Transitive checks against all previous versions, not just the immediately preceding one. Safer, occasionally noisier.

Q: Schema on the message (self-describing) vs at the broker?
A: Schema Registry gives centralized enforcement and a compatibility gate; the message payload carries the schema id so consumers can resolve it. You still need a per-consumer override policy for intentional breaks.

---

## Operations

Q: Consumer lag — what to alert on?
A: Lag growth rate (messages/s) and oldest-unconsumed age vs retention. Absolute lag alone is a weak signal.

Q: Silent data loss signature?
A: `lag = 0` but `log_start_offset > consumer_offset`, or the consumer's position is behind `log_start_offset`: the data was expired before being read.

Q: DLT requirements?
A: Original payload, failure class, attempt count, original topic/partition/offset, timestamp, correlation id. Plus retention and an alert on depth.

Q: DLT depth alert?
A: Alert on both rate and depth — a DLT is a data-loss queue that nobody is draining.

Q: How many retry attempts before the DLT?
A: 3–5 with exponential backoff and jitter, then DLT. Infinite retries block the partition and stall all subsequent messages.

Q: Poison message vs transient failure?
A: Classify: validation/schema/consistency errors go straight to DLT (they will never succeed); timeouts and 5xx go to retry. Retrying a poison message forever is the mistake.

Q: Backpressure: why pull-based consumers are safe?
A: A slow consumer stops committing, so the broker retains the backlog — no loss. Capacity requirement: `retention` must exceed `max_tolerable_outage × production_rate`.

Q: Capacity rule of thumb?
A: Keep steady-state consumer throughput at ~50–60% of peak production so a spike or a consumer restart drains a backlog rather than falling further behind.

Q: Broker disk exhaustion?
A: Unrecoverable without painful surgery — it is the only Kafka failure that is genuinely destructive. Alert on disk usage and on `log.flush` / dirty ratio.

Q: Partition skew diagnosis?
A: Compare per-partition byte/produce-rate metrics; a single hot partition shows all traffic on one broker while the rest idle.

Q: Key observability for a consumer?
A: Lag, poll rate, poll latency, commit latency/failures, processing time per record, rebalance count, DLT depth, exception rate by class, records-per-partition.

---

## Numbers and defaults to memorize

Q: `session.timeout.ms` default?
A: 10 s (10,000 ms) in recent versions; historically 30 s. Verify for your client version.

Q: `max.poll.interval.ms` default?
A: 300,000 ms (5 min). Size it above your worst-case batch processing time.

Q: `max.poll.records` default?
A: 500. Raise it only with a matching `max.poll.interval.ms` increase.

Q: Safe producer settings?
A: `acks=all`, `enable.idempotence=true`, `retries=Integer.MAX`, `max.in.flight≤5`, `delivery.timeout.ms > linger.ms + request.timeout.ms`.

Q: Retention sizing rule?
A: `retention.ms ≥ max_tolerable_outage × production_rate × safety(2–3)`.

Q: DLT retry count?
A: 3–5, then DLT. Never infinite.

Q: Consumer throughput headroom?
A: ~2× peak production rate, so a restart drains a backlog.

Q: `linger.ms` typical?
A: 5–50 ms for throughput; `0` for lowest latency.

Q: `group.instance.id` effect?
A: Eliminates rebalances on restart/reconnect for up to `session.timeout.ms`.

Q: Outbox relay batch?
A: Batch (e.g. 100–1,000 rows) per poll, mark sent in the same transaction pattern; never publish twice from one row without a dedup key.
