# data-engineering-deep — Advanced Data Engineering

A deep, multi-layer treatment of production data engineering, sitting alongside
`labs/data-engineering/*`. Where the numbered labs each teach one technology,
this module teaches the *problems* that outlive any particular technology.

## Why this module exists

Technologies in this field turn over every 18 months. The problems do not:
idempotency, event time, back-pressure, schema evolution, cost, and
reconciliation look the same in Flink 1.14 and Flink 2.0. This module is
organised around those problems.

## The 10 layers

| File | What it covers |
|---|---|
| `README.md` | this file: scope, how to use it |
| `THEORY.md` | the mental models — time, state, delivery, cost |
| `MATH_FOUNDATION.md` | throughput, latency, cost, and probability you actually need |
| `CODE_DEEP_DIVE.md` | reading and writing the internals: shuffle, state, log |
| `EXERCISES.md` | 24 graded problems with solutions sketched |
| `QUIZ.md` | 15 questions testing judgement, not recall |
| `FLASHCARDS.md` | 60 cards for spaced repetition |
| `VISION.md` | the mastery path and milestones |
| `MINI_PROJECT.md` | one project: an end-to-end streaming warehouse |
| `REAL_WORLD_PROJECT.md` | a production redesign with real numbers |

## The 10 problem clusters

1. **Time** — event vs processing time, watermarks, lateness, corrections
2. **State** — bounded vs unbounded, backends, checkpointing, rescaling
3. **Delivery** — at-least-once, exactly-once, idempotency, dedup
4. **Schema** — evolution, compatibility, contracts, drift
5. **Scale** — partitioning, skew, back-pressure, parallelism
6. **Storage** — formats, partitioning, file health, lifecycle
7. **Correctness** — reconciliation, invariants, point-in-time joins
8. **Cost** — bytes scanned, shuffle, credits, cost per insight
9. **Reliability** — retries, SLOs, error budgets, backfill
10. **Governance** — classification, lineage, deletion, evidence

## How to use this module

1. Read `THEORY.md` end to end. It is ~100 lines and it is the spine.
2. Work `EXERCISES.md` in order; the later ones assume the earlier ones.
3. Use `FLASHCARDS.md` daily for 2 weeks, then weekly.
4. Take `QUIZ.md`. If you score under 12/15, revisit `THEORY.md` sections.
5. Build `MINI_PROJECT.md`. The crash-recovery step is not optional.
6. Design `REAL_WORLD_PROJECT.md` and defend it to a colleague.

## Prerequisites

Comfortable with Java 21, Maven, and basic SQL. You do not need prior
Flink/Spark/Kafka experience — the labs cover those, and this module assumes
you have met them at least once.

## Related

- `labs/data-engineering/01-data-pipelines` through `20-streaming-analytics`
- `labs/capstones/08-mini-spark`, `03-mini-kafka`
- `labs/production-engineering/17-data-architecture`
