# VISION — Apache Flink (Advanced): CEP, Table API, and Production Scale
> Where this lab takes you: from DataStream fundamentals to Flink SQL, the
> Table API, complex event processing, and running stateful jobs at scale.

## The Arc
1. **Unified** — DataStream vs Table API, when each is right.
2. **Declarative** — Flink SQL, windows in SQL, time attributes.
3. **Patterns** — CEP: patterns, contiguity, timeouts, after-match skip.
4. **Connectors** — Kafka, JDBC, Iceberg/Delta sinks, exactly-once sinks.
5. **Scale** — parallelism, key groups, RocksDB tuning, HA patterns.

## Milestones (checkable)
- [ ] M1: write a fraud pattern in both CEP and Table API and compare readability.
- [ ] M2: explain `TIME_ATTRIBUTE` and how watermarks flow through a SQL window.
- [ ] M3: build a CDC-to-lakehouse pipeline with a two-phase-commit sink.
- [ ] M4: size state, tune RocksDB, and demonstrate sub-second checkpoint intervals.
- [ ] M5: rescale a job from p=32 to p=128 via savepoint and measure recovery.

## Anti-Goals
- Mixing DataStream and Table APIs in one job without a reason.
- CEP patterns that match everything, generating an unmanageable output rate.
- Assuming `FOR SYSTEM_TIME AS OF` is free; it is a real read.

## Interview Lens
- "Why does your Flink SQL join to a dimension table not work?"
- "How do you detect 'A then B within 30s, but not if C intervenes'?"
- "Your checkpoints take 40s. What are the options?"

## 30-Day Plan
- Wk1 THEORY + EXERCISES L1-L7. Wk2 MINI_PROJECT in Table API + CEP.
- Wk3 add a lakehouse sink, then tune state. Wk4 REAL_WORLD_PROJECT.

## Done = You Can
- Choose the right Flink API for a job and operate it at production scale.
