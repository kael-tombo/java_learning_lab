# VISION — Apache Flink: Stream Processing With Real State
> Where this lab takes you: from "Kafka plus a while loop" to an event-time,
> checkpointed, exactly-once stateful job that survives failure mid-window.

## The Arc
1. **Streams** — unbounded data, sources, operators, time.
2. **State** — keyed state, timers, windows, state backends.
3. **Time** — event time vs processing time, watermarks, lateness.
4. **Faults** — checkpoints, savepoints, exactly-once semantics.
5. **Scale** — key groups, rescaling, back-pressure, skew.

## Milestones (checkable)
- [ ] M1: convert a naive processing-time job into a correct event-time job.
- [ ] M2: implement a keyed tumbling window with a state backend you can inspect.
- [ ] M3: explain exactly-once end to end: checkpoint barrier, two-phase commit sink.
- [ ] M4: kill -9 a job mid-window and prove state recovers with no double count.
- [ ] M5: explain how rescaling moves key groups and what that costs.

## Anti-Goals
- Processing-time logic in a business correctness path.
- Unbounded state with no TTL; a leak you did not bound.
- Assuming a sink supports exactly-once because your source does.

## Interview Lens
- "The report is off by 3% after a restart. Why?"
- "Your job's state grew to 400GB. Where does it go?"
- "Watermark says 5 minutes behind. What do you do?"

## 30-Day Plan
- Wk1 THEORY + EXERCISES L1-L6. Wk2 MINI_PROJECT, then deliberately crash it.
- Wk3 add late-data handling and savepoint restore. Wk4 REAL_WORLD_PROJECT.

## Done = You Can
- Build, checkpoint, restore, and reason about a stateful streaming job.
