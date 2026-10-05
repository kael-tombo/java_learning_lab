# VISION — Feature Stores: Training and Serving From One Definition
> Where this lab takes you: from "the SQL query is copy-pasted into the serving
  code" to a feature store where definitions, freshness, and skew are managed.

## The Arc
1. **Why** — training/serving skew, the historical feature problem.
2. **Offline** — batch materialization, point-in-time correctness, backfills.
3. **Online** — low-latency store, keys, TTLs, partial updates.
4. **Consistency** — offline/online parity, freshness SLOs, feature drift.
5. **Operate** — registry, ownership, cost, deprecation.

## Milestones (checkable)
- [ ] M1: implement a point-in-time-correct join and prove it with a leak test.
- [ ] M2: materialize a feature table and a matching online store from one definition.
- [ ] M3: write a parity test comparing offline and online values for the same event.
- [ ] M4: detect and alert on offline/online skew beyond a threshold.
- [ ] M5: deprecate a feature version without breaking any consumer.

## Anti-Goals
- Computing features at serving time from raw tables.
- A feature whose definition lives in a notebook.
- Online stores with no TTL, growing forever.

## Interview Lens
- "How do you avoid training/serving skew?"
- "Your model accuracy dropped after a data change. Feature or model?"
- "How do you backfill a feature definition change?"

## 30-Day Plan
- Wk1 THEORY + EXERCISES L1-L6. Wk2 MINI_PROJECT with a leak test.
- Wk3 add online store + parity. Wk4 REAL_WORLD_PROJECT with a skew incident story.

## Done = You Can
- Ship features that are reproducible, consistent, and safe to change.
