# VISION — Apache Spark: Distributed Compute That Hides From You
> Where this lab takes you: from `map/reduce` anxiety to reading a Spark
> physical plan, fixing skew, and tuning shuffle in production.

## The Arc
1. **Model** — RDDs, DataFrames, Datasets, Catalyst, Tungsten.
2. **Execute** — stages, tasks, shuffles, the DAG scheduler.
3. **Optimize** — partitioning, broadcast joins, AQE, predicate pushdown.
4. **Operate** — executors, memory tiers, dynamic allocation, failures.
5. **Stream** — Structured Streaming, watermarks, checkpointing.

## Milestones (checkable)
- [ ] M1: explain a shuffle end to end, including where the bytes physically go.
- [ ] M2: read a `physical_plan` output and name each operator's cost.
- [ ] M3: fix a 20x skew in a groupBy with salting and show the stage time drop.
- [ ] M4: convert a slow join into a broadcast hash join deliberately and measure.
- [ ] M5: size executors for a known dataset and justify cores:memory:offheap ratios.

## Anti-Goals
- Collecting UDFs for logic Catalyst can already do in SQL.
- `cache()` without a measured reuse count.
- Believing `repartition` is free; it is a full shuffle you are choosing to pay.

## Interview Lens
- "Why is my groupBy slow only on Tuesdays?" (answer: a hot key lands on a holiday)
- "Task failed 3 times with `FetchFailedException` — what happened?"
- "How would you process 60TB with 200 executors?"

## 30-Day Plan
- Wk1 THEORY + EXERCISES L1-L6. Wk2 MINI_PROJECT with a plan-reading habit.
- Wk3 tune one real skew + one join. Wk4 REAL_WORLD_PROJECT with a cost story.

## Done = You Can
- Profile, tune, and reason about a Spark job line by line of the plan.
