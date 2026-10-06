# MINI_PROJECT — Nightly Retraining DAG with Lineage

**Track:** mlops  |  **Lab:** lab01  |  **Level:** Intermediate

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

**Brief.** Build a real DAG that validates data, trains, evaluates, and promotes only on passing gates — with retries, freshness and lineage.

**Timebox.** 4 hours

## 1. Why This Project Exists

Every ML system needs this exact pipeline. Doing it once by hand makes the promotion gate and the freshness alarm obvious later.

## 2. Requirements

- Six nodes: ingest, validate, featurise, train, evaluate, register.
- Idempotent writes keyed by run id; demonstrate double execution is a no-op.
- Bounded retries with exponential backoff plus a dead-letter path.
- Concurrency caps for the expensive train node; show the effect of removing them.
- Freshness SLO with an alert; reproduce a green-but-stale pipeline.
- Lineage ledger that answers 'why did accuracy change' from commit, data version and params.
- A promotion gate that refuses to register a failing model.

## 3. Build Order

| Step | Time | What you do | Done when |
|---|---|---|---|
| 1 | 25m | Declare the DAG; implement topological execution and cycle detection | A printed order and critical path |
| 2 | 30m | Make each node idempotent and keyed by run id | A double-run no-op test |
| 3 | 30m | Add retries, timeouts and a dead-letter table | A simulated failure path |
| 4 | 30m | Add pool caps; benchmark with and without them | A queue-time comparison |
| 5 | 25m | Add freshness SLO and reproduce a stale-but-green run | A firing freshness alert |
| 6 | 30m | Add lineage ledger and answer a metric-change question | A lineage lookup |
| 7 | 30m | Wire the promotion gate; prove it blocks a failing model | A blocked promotion you can show |

## 4. Architecture Sketch

```text
 ingest --> validate --> featurise --> train --> evaluate --> register
    |          |            |            |          |            |
  pool:dw    pool:dw      pool:spark   pool:gpu   pool:cpu    pool:reg
    |          |            |            |          |            |
    +----------+------------+------------+----------+------------+
                                  |
                        RunLedger: fingerprint, timings,
                        freshness, cost, dead letters
                                  |
                   alert on failure OR on staleness
```

## 5. Implementation Notes

- Make the train node deliberately slow so the concurrency comparison is visible.
- The freshness scenario is the one people forget: a green DAG with a week-old table.
- Dead letters need an owner and a replay command, or they are a graveyard.
- The promotion gate is the point of the whole pipeline; test it by trying to promote a bad model.

## 6. Deliverables

1. Runnable DAG executor with a printed critical path.
1. Idempotency test proving double execution is a no-op.
1. Concurrency comparison with and without pool caps.
1. Lineage query answering a metric-change question, plus a runbook.

## 7. Grading Rubric

| Dimension | Weight | What earns full marks |
|---|---|---|
| Correctness | 30% | Topological execution, idempotency, cycles detected |
| Reliability | 25% | Bounded retries, dead letters, timeouts, pool caps |
| Observability | 25% | Freshness alert, lineage ledger, cost per node |
| Governance | 20% | Promotion gate demonstrably blocks a failing model |

## 8. Stretch Goals

- Add dynamic task mapping for per-partition work.
- Implement a backfill command and repair a simulated 3-day gap.
- Add cost-aware scheduling that defers low-value retrains.

## 9. Definition of Done

You are finished when every box below is checked, not when the code compiles.

- [ ] Six nodes: ingest, validate, featurise, train, evaluate, register.
- [ ] Idempotent writes keyed by run id; demonstrate double execution is a no-op.
- [ ] Bounded retries with exponential backoff plus a dead-letter path.
- [ ] Concurrency caps for the expensive train node; show the effect of removing them.
- [ ] Freshness SLO with an alert; reproduce a green-but-stale pipeline.
- [ ] Lineage ledger that answers 'why did accuracy change' from commit, data version and params.
- [ ] A stranger can reproduce the reported numbers with one command
- [ ] The limitations section says what this cannot do
- [ ] At least one number is alerted on in production

## 10. Retrospective Template

- What worked:
- What surprised me:
- The one number I would alert on in production:
- What I would delete before shipping this to real users:
