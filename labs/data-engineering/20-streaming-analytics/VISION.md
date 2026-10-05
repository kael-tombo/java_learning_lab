# VISION — Streaming Analytics: Answers While the Event Is Happening
> Where this lab takes you: from "we could run that query" to sub-second
  dashboards that survive late data, back-pressure, and restarts.

## The Arc
1. **Sources** — events, partitions, throughput, delivery semantics.
2. **Time** — event time, processing time, watermarks, lateness policy.
3. **Aggregation** — windows, incremental aggregation, state growth.
4. **Serving** — materialised views, push vs pull, incremental updates.
5. **Operate** — lag, back-pressure, restarts, cost per insight.

## Milestones (checkable)
- [ ] M1: convert a processing-time job to a correct event-time job and show the delta.
- [ ] M2: implement incremental window aggregation with bounded state.
- [ ] M3: build a push-based serving path with < 1s end-to-end latency.
- [ ] M4: handle late data explicitly and quantify the correction cost.
- [ ] M5: answer "how expensive is this insight?" with a cost model.

## Anti-Goals
- A dashboard that is right on average and wrong at the edges.
- Unbounded state in a windowed aggregation.
- Treating "real time" as a latency target without a stated freshness budget.

## Interview Lens
- "Your live counter disagrees with the batch number. Why?"
- "How do you know how stale a number on the screen is?"
- "Late data arrives 40 minutes late. What do you do?"

## 30-Day Plan
- Wk1 THEORY + EXERCISES L1-L6. Wk2 MINI_PROJECT with a live dashboard.
- Wk3 add late-data correction and back-pressure. Wk4 REAL_WORLD_PROJECT.

## Done = You Can
- Build streaming analytics that is measurably correct, not just fast.
