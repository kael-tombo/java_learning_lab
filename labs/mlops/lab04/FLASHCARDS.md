# Feature Store Architecture - Flashcards (60 cards)

**Track:** mlops  |  **Lab:** lab04  |  **Level:** Intermediate

> Companion notes to the runnable lab. Everything here is grounded in the source under `src/`, so a claim you cannot reproduce is a claim you do not ship.

| Doc | Read it when you want |
|---|---|
| `THEORY.md` | the mental model and the assumptions |
| `MATH_FOUNDATION.md` | the formulas, the derivations, the numerical traps |
| `CODE_DEEP_DIVE.md` | the Java implementation, line by line |
| `EXERCISES.md` | deliberate practice, one deliverable at a time |
| `QUIZ.md` | to find the gaps before an interview |
| `FLASHCARDS.md` | spaced repetition on the day before a review |
| `VISION.md` | the career-level context and the anti-patterns to avoid |
| `MINI_PROJECT.md` | a self-contained build you finish in one sitting |
| `REAL_WORLD_PROJECT.md` | the production system, on-call runbook included |

**Format.** Question (front) -> answer (back). Use for spaced repetition: day 0, day 1, day 3, day 7, day 21. Do not read the answer first.

| # | Front | Back |
|---|---|---|
| 1 | Why a feature store needs two stores? | Offline for training history and reproducibility; online for low-latency serving of the latest value. |
| 2 | What is training-serving skew? | Training and serving computing the same feature differently, so the model sees inputs it was never trained on. |
| 3 | What is point-in-time correctness? | Joining training rows only to feature values that existed at the label's timestamp. |
| 4 | What should you alert on for a feature store? | Staleness or freshness lag per feature, not just pipeline success. |
| 5 | Push versus pull materialisation? | Pull recomputes on a schedule (reproducible, cheap); push updates on write (fresher, costlier, harder to reproduce). |
| 6 | Why does a feature need an owner? | Ownership prevents forks: two teams shipping different formulas for the same feature name. |
| 7 | What is a feature view? | A versioned definition of features over an entity and a source, materialised into both stores. |
| 8 | What is the parity test? | Reading the same entity from online and offline and asserting the values match. |
| 9 | What is Two stores, one definition? | The offline store holds history in Parquet for training; the online store holds the latest values in Redis or DynamoDB for serving. |
| 10 | What is Training-serving skew is the enemy? | Skew appears when training reads a feature computed one way and serving computes it another: different rounding, different null handling, different time zone. |
| 11 | What is Freshness is a feature-store property? | A feature that is a week stale at serving time is a different feature than the one you trained on. |
| 12 | What is Ownership and reuse? | A feature without an owner becomes a fork. |
| 13 | What is Push versus pull materialisation? | Pull (batch) recomputes on a schedule: simple and reproducible. |
| 14 | In this lab, what does `online[entity][feature] = f(batch(source))` mean? | Materialisation: one definition, two projections |
| 15 | In this lab, what does `lookback = f(t_event, t_window)` mean? | Point-in-time join: no future values in training |
| 16 | In this lab, what does `freshness = now - max(event_ts) per feature` mean? | Freshness: the property to alert on |
| 17 | In this lab, what does `staleness_pct = P(freshness > threshold)` mean? | Staleness rate: share of reads served stale |
| 18 | In this lab, what does `materialisation_lag = write_ts - event_ts` mean? | Lag: seconds between event and availability |
| 19 | In this lab, what does `reuse_ratio = features reused / features defined` mean? | Platform value: the argument for a store |
| 20 | You see 'Model accuracy drops after a successful migration' in production. What is the cause and the fix? | training-serving skew from a reimplemented transformation Fix: one definition materialised into both stores; add a parity test |
| 21 | You see 'Offline metrics are far better than live results' in production. What is the cause and the fix? | point-in-time leakage in the training join Fix: join on event time with an explicit lookback window |
| 22 | You see 'A feature silently became a month old' in production. What is the cause and the fix? | no freshness metric published Fix: alert on freshness per feature, not just pipeline success |
| 23 | You see 'Two teams have a 'lifetime value' feature with different formulas' in production. What is the cause and the fix? | no ownership or naming discipline Fix: named owners, documented semantics, deprecation workflow |
| 24 | You see 'Online reads time out under peak load' in production. What is the cause and the fix? | no batching, one round trip per feature Fix: batch feature reads into one request per entity |
| 25 | You see 'A feature change broke training silently' in production. What is the cause and the fix? | no versioning on feature views Fix: version the view; a new definition is a new view |
| 26 | Which Java API is the backbone of: the versioned definition | `record FeatureView(String name, int version, String entity, Map<String, String> semantics)` |
| 27 | Which Java API is the backbone of: the difference between a usable and an unusable online path | `Batch feature reads into one call` |
| 28 | Which Java API is the backbone of: staleness tolerance is per feature, not global | `Duration TTL per feature` |
| 29 | Which Java API is the backbone of: the timestamp that makes point-in-time joins possible | `record FeatureValue(Object v, Instant eventTs)` |
| 30 | Which Java API is the backbone of: an in-memory online store that makes parity testable | `AtomicReference<Map<String,Object>> per entity` |
| 31 | Why does Two stores, one definition matter operationally? | The offline store holds history in Parquet for training; the online store holds the latest values in Redis or DynamoDB for serving. |
| 32 | Why does Training-serving skew is the enemy matter operationally? | Skew appears when training reads a feature computed one way and serving computes it another: different rounding, different null handling, different time zone. |
| 33 | Why does Point-in-time correctness matter operationally? | Training rows must see only the feature values that existed at the label timestamp. |
| 34 | Why does Freshness is a feature-store property matter operationally? | A feature that is a week stale at serving time is a different feature than the one you trained on. |
| 35 | Why does Ownership and reuse matter operationally? | A feature without an owner becomes a fork. |
| 36 | Why does Push versus pull materialisation matter operationally? | Pull (batch) recomputes on a schedule: simple and reproducible. |
| 37 | In the Feature Store Architecture pipeline, what happens next? Define the entity key, the feature semantics and the owner b... | Define the entity key, the feature semantics and the owner before writing code. |
| 38 | In the Feature Store Architecture pipeline, what happens next? Write one transformation that produces the value; it feeds b... | Write one transformation that produces the value; it feeds both stores. |
| 39 | In the Feature Store Architecture pipeline, what happens next? Materialise to the offline store with the event timestamp pr... | Materialise to the offline store with the event timestamp preserved for point-in-time joins. |
| 40 | In the Feature Store Architecture pipeline, what happens next? Materialise to the online store with a TTL matching the feat... | Materialise to the online store with a TTL matching the feature's staleness tolerance. |
| 41 | In the Feature Store Architecture pipeline, what happens next? Test parity: read the same entity from both stores and asser... | Test parity: read the same entity from both stores and assert the values agree. |
| 42 | In the Feature Store Architecture pipeline, what happens next? Publish freshness and reuse metrics; alert on the staleness ... | Publish freshness and reuse metrics; alert on the staleness rate. |
| 43 | Exercise focus: Design the feature view contract | Get the semantics right before the code. |
| 44 | Exercise focus: One transform, two stores, verified | The anti-skew property, demonstrated. |
| 45 | Exercise focus: Point-in-time joins done correctly | Prove the leak and fix it. |
| 46 | Exercise focus: Freshness monitoring | Catch stale features before users do. |
| 47 | Exercise focus: Online read batching and latency | Make the serving path fast enough. |
| 48 | Exercise focus: Materialisation lag attribution | Know which stage to fix. |
| 49 | State the Point-in-time join correctness result for Feature Store Architecture. | Purchase at t=10:00 with a 'lifetime value' feature that includes the purchase. A naive latest-value join gives 0 leakage visible in CV; a correct join excludes it and accuracy drops to honest levels. |
| 50 | State the Staleness distribution result for Feature Store Architecture. | tau = 1h, hourly materialisation: normal freshness is 0-60min, so S is near 0. A broken upstream job pushes freshness to 26h and S goes to 1.0 within one cycle. |
| 51 | State the Materialisation lag budget result for Feature Store Architecture. | Budget 15min: ingest 2min, compute 8min, write 1min = 11min typical, so S is high. Moving compute to a bigger pool takes it to 5min and the SLO holds. |
| 52 | State the Online read cost and batching result for Feature Store Architecture. | 6 features read individually: 6 round trips at 0.5ms each = 3ms. Batched into one call: 0.6ms, a 5x p99 improvement for one code change. |
| 53 | How do you prevent skew structurally? | One transformation feeding both stores, so there is no second implementation to drift. |
| 54 | What breaks if you drop event timestamps? | Point-in-time joins become impossible, so training silently leaks the future. |
| 55 | How should online reads be batched? | One request per entity containing all required features, not one call per feature. |
| 56 | When do you need push materialisation? | For real-time counters and behaviours where hourly freshness is not good enough. |
| 57 | Assumption / invariant to defend: A feature has exactly one definition, versioned in code... | A feature has exactly one definition, versioned in code |
| 58 | Assumption / invariant to defend: Entity keys are stable and shared between online and offline stores... | Entity keys are stable and shared between online and offline stores |
| 59 | Assumption / invariant to defend: Event timestamps are preserved end to end for point-in-time correctnes... | Event timestamps are preserved end to end for point-in-time correctness |
| 60 | Assumption / invariant to defend: Online TTLs reflect each feature's staleness tolerance, not a global d... | Online TTLs reflect each feature's staleness tolerance, not a global default |

## Deck Notes

- Rows are generated from this lab's own concepts, equations, failure modes and Java APIs - if you disagree with a card, fix the card.
- The last block of cards is deliberately operational: they are the questions a staff engineer gets asked in a design review.
