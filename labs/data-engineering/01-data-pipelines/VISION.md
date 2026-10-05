# VISION — Data Pipelines: From Batches to Events
> Where this lab takes you: from "copy a file every night" to running a
> fault-tolerant, back-pressured, replayable production pipeline.

## The Arc
1. **Shape** — batch vs streaming, push vs pull, ETL vs ELT.
2. **Flow** — extract, transform, load as composable stages.
3. **Contracts** — schemas, idempotency, exactly-once illusion.
4. **Failure** — retries, backfill, poison pills, late data.
5. **Scale** — partitioning, skew, cost of recomputation.

## Milestones (checkable)
- [ ] M1: draw a pipeline for "1M orders/day -> daily revenue table" and label every hop.
- [ ] M2: write an idempotent loader and prove it by running it twice.
- [ ] M3: implement a bounded, parallel batch transform with a bounded queue.
- [ ] M4: build a checkpointed streaming job that survives a process kill mid-window.
- [ ] M5: explain late-arriving events and choose watermark vs allowed-lateness.

## Anti-Goals
- Pipelines with no schema, no metrics, and no way to tell if they ran.
- In-memory state in batch jobs that makes a re-run non-deterministic.
- Pretending exactly-once is free; it is a price you pay for state.

## Interview Lens
- "Your pipeline processed 40% of yesterday's rows. Debug it."
- "How do you backfill 90 days without double counting?"
- "Batch or streaming for a fraud rules engine — justify."

## 30-Day Plan
- Wk1 THEORY + EXERCISES L1-L5. Wk2 build MINI_PROJECT, measure throughput.
- Wk3 force a crash, replay, prove idempotency. Wk4 REAL_WORLD_PROJECT war story.

## Done = You Can
- Design, operate, and backfill a pipeline you would be paged for.
