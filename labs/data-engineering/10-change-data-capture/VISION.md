# VISION — Change Data Capture: Databases as Event Sources
> Where this lab takes you: from nightly table dumps to a log-based CDC stream
> with ordering, schema evolution, and exactly-once propagation.

## The Arc
1. **Why** — incremental vs CDC vs polling, latency and load trade-offs.
2. **Mechanics** — WAL/binlog parsing, LSN, GTID, snapshot-then-stream.
3. **Semantics** — insert/update/delete, ordering, transaction boundaries.
4. **Schema** — evolution events, compatibility, tombstone handling.
5. **Deliver** — exactly-once into a lakehouse, deduplication keys.

## Milestones (checkable)
- [ ] M1: explain snapshot + stream CDC and why the snapshot must be consistent.
- [ ] M2: implement ordering logic so events for one key stay in commit order.
- [ ] M3: handle a schema change (add column, rename, drop) without breaking consumers.
- [ ] M4: deliver CDC into a table with an idempotent upsert key and prove no duplicates.
- [ ] M5: quantify the load CDC puts on the source and defend the connector choice.

## Anti-Goals
- Polling a table every 5 seconds and calling it CDC.
- Emitting rows without their transaction context and losing ordering.
- Assuming a connector can be paused without a slot being retained forever.

## Interview Lens
- "How do you know your CDC didn't miss a transaction?"
- "Source lag is 400k events. What are the possible causes?"
- "Why did a rename break three downstream jobs?"

## 30-Day Plan
- Wk1 THEORY + EXERCISES L1-L6. Wk2 MINI_PROJECT with a real binlog stream.
- Wk3 add schema evolution and dedup. Wk4 REAL_WORLD_PROJECT with an SLO.

## Done = You Can
- Stand up a CDC pipeline that is ordered, evolvable, and exactly-once end to end.
