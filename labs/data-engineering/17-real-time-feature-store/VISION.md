# VISION — Real-Time Feature Store: Serving Features in Milliseconds
> Where this lab takes you: from a Redis cache of a few flags to a feature
  serving layer with freshness contracts, partial updates, and fallbacks.

## The Arc
1. **Why** — the online path, latency budgets, why the batch store cannot serve.
2. **Keys** — entity keys, composite keys, cardinality, hot keys.
3. **Freshness** — per-feature TTL, staleness budgets, behavioural vs static.
4. **Correctness** — offline/online parity, update ordering, partial writes.
5. **Operate** — latency, hit rate, backpressure, degradation.

## Milestones (checkable)
- [ ] M1: design a key schema for a 90M-entity store and compute the memory footprint.
- [ ] M2: implement a partial-update path and prove a failed update leaves a consistent row.
- [ ] M3: build a staleness-aware serving response the model can reason about.
- [ ] M4: write a fallback chain and demonstrate a graceful degradation under outage.
- [ ] M5: hit a p99 budget with a measured load test and a written capacity model.

## Anti-Goals
- Features without per-feature TTLs.
- Falling back silently to a default that the model was never trained on.
- One giant hash per entity containing every feature ever defined.

## Interview Lens
- "Your feature store p99 is 40ms. Where is the time?"
- "What does your model do when a feature is missing?"
- "How do you roll back a bad feature computation without downtime?"

## 30-Day Plan
- Wk1 THEORY + EXERCISES L1-L6. Wk2 MINI_PROJECT with a load test.
- Wk3 add staleness policy and a fallback chain. Wk4 REAL_WORLD_PROJECT.

## Done = You Can
- Serve features at a stated budget and degrade predictably when inputs fail.
