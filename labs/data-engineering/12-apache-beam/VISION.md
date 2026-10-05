# VISION — Apache Beam: One API, Batch and Streaming
> Where this lab takes you: from "which engine?" to writing a pipeline once in
  a model that runs on multiple runners, and knowing when not to.

## The Arc
1. **Model** — PCollection, DoFn, Pipeline, transforms, Coder.
2. **Windows** — fixed/sliding/streaming windows, triggers, accumulators.
3. **Execution** — runners (Direct, Flink, Spark), portability, fusion.
4. **Semantics** — at-least-once, exactly-once, idempotency, checkpointing.
5. **Compose** — schema, state/timers, side inputs, dynamic work rebalancing.

## Milestones (checkable)
- [ ] M1: write a pipeline in the Beam model and run it on Direct and Flink.
- [ ] M2: explain the model-vs-runner boundary and what a runner may optimize.
- [ ] M3: implement a custom `DoFn` with state and timers.
- [ ] M4: make one pipeline run unchanged on Direct, Flink, and Spark.
- [ ] M5: measure the portability cost of an engine-specific transform.

## Anti-Goals
- Falling back to engine-specific APIs in "portable" pipelines.
- Assuming a Coder will be inferred for a custom type and then blowing up at scale.
- Treating unbounded input as a loop over a list.

## Interview Lens
- "Why Beam and not just Flink SQL?"
- "Your pipeline runs on Direct but not Spark. Why?"
- "How do you dedupe a Beam pipeline with at-least-once delivery?"

## 30-Day Plan
- Wk1 THEORY + EXERCISES L1-L6. Wk2 MINI_PROJECT running on 2 runners.
- Wk3 add state/timers and a side input. Wk4 REAL_WORLD_PROJECT.

## Done = You Can
- Write once, reason about semantics precisely, and pick the right runner.
