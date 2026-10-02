# Kafka Streams Theory

## Stream-Table Duality
- **KStream**: Append-only log of facts
- **KTable**: Changelog representing current state
- Either can be derived from the other

## Processing Guarantees
- At-most-once: No retries
- At-least-once: Retry with duplicates
- Exactly-once: Kafka transactions + idempotent writes

## State Stores
- RocksDB: Embedded KV store (default)
- InMemory: Pure in-memory

## Sourced field notes (fetched Oct 2026 — verify before citing)
- "Exactly-Once Semantics Are Possible: Here's How Kafka Does It" (Confluent blog by Neha Narkhede, Guozhang Wang et al., Jun 30 2017, updated Mar 2025 — accessed Oct 2026) — https://www.confluent.io/blog/exactly-once-semantics-are-possible-heres-how-apache-kafka-does-it/ — Takeaway tied to lab processing-guarantees exercise: map at-least-once (producer retry duplicates) vs at-most-once (no retry, possible loss) vs exactly-once onto the lab's read-process-write loop and reproduce the retry-duplicate case first.
- "Exactly-Once Semantics Are Possible: Here's How Kafka Does It" (Confluent blog by Neha Narkhede, Guozhang Wang et al., Jun 30 2017, updated Mar 2025 — accessed Oct 2026) — https://www.confluent.io/blog/exactly-once-semantics-are-possible-heres-how-apache-kafka-does-it/ — Takeaway tied to lab idempotence config: set `enable.idempotence=true` for per-partition no-duplicate in-order writes (sequence-number dedupe in the log) before attempting full transactions.
- "Exactly-Once Semantics Are Possible: Here's How Kafka Does It" (Confluent blog by Neha Narkhede, Guozhang Wang et al., Jun 30 2017, updated Mar 2025 — accessed Oct 2026) — https://www.confluent.io/blog/exactly-once-semantics-are-possible-heres-how-apache-kafka-does-it/ — Takeaway tied to lab Kafka Streams config: set `processing.guarantee=exactly_once`, pair with consumer `isolation.level=read_committed` and producer `transactional.id` so state-store updates + output writes + offset commits land atomically.
- "Exactly-Once Semantics Are Possible: Here's How Kafka Does It" (Confluent blog by Neha Narkhede, Guozhang Wang et al., Jun 30 2017, updated Mar 2025 — accessed Oct 2026) — https://www.confluent.io/blog/exactly-once-semantics-are-possible-heres-how-apache-kafka-does-it/ — Takeaway tied to lab tuning exercise: adjust `commit.interval.ms` to trade throughput vs end-to-end latency under exactly-once (short ~100 ms interval costs 15–30% per the post's benchmarks; larger intervals amortize transaction overhead).
