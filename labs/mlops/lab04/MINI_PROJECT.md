# MINI_PROJECT — Point-in-Time Correct Feature Store

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

**Brief.** Build a feature store with one definition feeding offline and online stores, point-in-time joins, and freshness monitoring.

**Timebox.** 4 hours

## 1. Why This Project Exists

Skew and leakage are invisible by construction; this project makes both fail loudly in a test.

## 2. Requirements

- Define a feature view: entity, 4+ features, owners, TTLs, units and null semantics.
- One transformation materialising to an offline store (event timestamps preserved) and an online store.
- Parity test comparing both stores over a sample of entities.
- Point-in-time join for training rows with an explicit lookback window; show the leak it prevents.
- Freshness monitor with a staleness rate and an alert; break an upstream to prove it fires.
- Batched online reads with a measured latency budget.
- Version the view and show a deprecation path.

## 3. Build Order

| Step | Time | What you do | Done when |
|---|---|---|---|
| 1 | 30m | Feature view contract: entities, semantics, owners, TTLs, lookbacks | A documented contract |
| 2 | 40m | One transform into offline and online stores | Two stores from one definition |
| 3 | 25m | Parity test over sampled entities | A passing parity test |
| 4 | 40m | Point-in-time join; quantify the leak avoided | A measured optimism number |
| 5 | 30m | Freshness monitor and staleness alert; break an upstream | An alert that fires |
| 6 | 25m | Batched online reads with a latency budget | A before/after latency table |
| 7 | 25m | Versioning plus deprecation; runbook | A working deprecation |

## 4. Architecture Sketch

```text
 source events (event_ts preserved)
            |
     FeatureView.transform()  <-- ONE definition
            |
   +--------+---------+
   |                  |
offline store     online store (TTL per feature)
(history)        (latest value, batched reads)
   |                  |
point-in-time     serving path (p99 budget)
join (lookback)        |
   |             parity test (sample entities)
   |                  |
training rows    freshness monitor -> staleness rate -> alert
```

## 5. Implementation Notes

- Put a feature in the source that includes future information; the leak must be visible.
- Assert the point-in-time join in a test, not in a comment.
- TTL should come from each feature's staleness tolerance, argued in the contract.
- Parity is the cheapest skew detector you will ever write.

## 6. Deliverables

1. Feature view contract plus a registry that enforces owners and semantics.
1. Parity test plus a point-in-time join test.
1. Freshness report with a demonstrated alert.
1. Latency table for unbatched versus batched reads, plus a runbook.

## 7. Grading Rubric

| Dimension | Weight | What earns full marks |
|---|---|---|
| Correctness | 30% | One definition, parity passing, point-in-time joins proven |
| Leak prevention | 20% | Quantified optimism removed by the lookback join |
| Operations | 25% | Freshness alerts, TTLs, latency budget met |
| Governance | 15% | Versioning, deprecation, owners enforced |
| Communication | 10% | Contract and runbook a teammate could use |

## 8. Stretch Goals

- Add push materialisation for a real-time counter alongside pull for aggregates.
- Track reuse across two teams and consolidate a duplicated feature.
- Add a deprecation notice period with consumer tracking.

## 9. Definition of Done

You are finished when every box below is checked, not when the code compiles.

- [ ] Define a feature view: entity, 4+ features, owners, TTLs, units and null semantics.
- [ ] One transformation materialising to an offline store (event timestamps preserved) and an online store.
- [ ] Parity test comparing both stores over a sample of entities.
- [ ] Point-in-time join for training rows with an explicit lookback window; show the leak it prevents.
- [ ] Freshness monitor with a staleness rate and an alert; break an upstream to prove it fires.
- [ ] Batched online reads with a measured latency budget.
- [ ] A stranger can reproduce the reported numbers with one command
- [ ] The limitations section says what this cannot do
- [ ] At least one number is alerted on in production

## 10. Retrospective Template

- What worked:
- What surprised me:
- The one number I would alert on in production:
- What I would delete before shipping this to real users:
