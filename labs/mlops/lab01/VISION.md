# ML Pipeline Orchestration - Vision & Where This Is Going

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

## 1. The Future State

Orchestration converges on declarative, data-centric pipelines where the trigger is a data event rather than a clock, lineage is automatic, and the DAG definition, the environment and the data snapshot are all content-hashed. The remaining human job is deciding what must fail loudly.

The test of that future state is boring: a new engineer ships a change to ml pipeline orchestration on day two without asking anyone where the magic lives.

## 2. What "Good" Looks Like in Practice

- Every run records commit, data version, params and image.
- Freshness is alerted on alongside failures.
- Backfill is a supported path with documented ordering and dedupe.
- Concurrency is capped per pool and reviewed when a queue grows.

## 3. Capability Ladder

| Level | Capability | You can... |
|---|---|---|
| L1 | Model it | Draw a DAG for a real pipeline and find the critical path. |
| L2 | Make it safe | Idempotent tasks, bounded retries, dead-letter path. |
| L3 | Make it reproducible | Versioned inputs, fingerprint per run, backfill tested. |
| L4 | Make it observable | Freshness SLO, lineage queries, cost per node. |

## 4. Behaviours to Build

Assume every task will run twice. Alert on staleness, not just failure. Repair gaps rather than pretending they did not happen.

## 5. Anti-Vision (the failure mode we are avoiding)

- A linear shell script with comments instead of a real DAG.
- Retries with no cap because 'the scheduler handles it'.
- Backfill that only fixes the newest window.
- Green dashboards hiding a week-old dataset.

## 6. Technology Shifts That Change the Work

1. Data-quality-triggered runs replacing pure schedule-based triggers.
1. Automatic lineage from query plans and feature definitions.
1. Lakehouse-native orchestration with declarative transformations.
1. Cost-aware scheduling that defers low-value retrains automatically.

## 7. Your 30/60/90 Commitment

- **30 days.** Model a real pipeline as a DAG; compute and print the critical path.
- **60 days.** Make every task idempotent with bounded retries and a dead-letter path.
- **90 days.** Add freshness alerting, lineage queries and a tested backfill for a known gap.

## 8. How To Tell You Are Actually Getting Better

- I can draw any pipeline's dependency graph from memory.
- Running a task twice is a no-op.
- I can answer 'why did this number change' from the ledger.
- My pipeline pages on staleness, not only on failures.

## 9. Principles That Should Not Change

- **Model a pipeline as a DAG** Model a pipeline as a DAG and reason about its topological order
- **Distinguish task, operator, schedule, run** Distinguish task, operator, schedule, run and dataset in an orchestrator
- **Implement retries, timeouts** Implement retries, timeouts and idempotency so a failed run can resume

> Orchestration is where reliability becomes a property of the definition rather than of the operator's memory.
