# Lab 10 - Data Pipelines

Data must move from sources to decisions reliably: ingested, validated,
transformed, and served, again every day. This lab covers batch vs
streaming, idempotency, delivery semantics, schema evolution, replay
discipline, quality checks, and DAG orchestration - with runnable
JDK-only programs for the core mechanics.

## Objectives

- Contrast batch vs streaming and pick by latency need, honestly priced.
- Define idempotency and show a replay-safe sink in code.
- Explain at-least-once vs exactly-once as concepts, carefully stated.
- Judge schema changes as additive-compatible vs breaking.
- Practice backfill/replay discipline and data-quality checks (counts,
  null rates, drift).
- Sketch an orchestration DAG without vendor lock-in claims.

## Map of this lab

- THEORY.md / MATH_FOUNDATION.md - semantics, compat rules, check math.
- HOW_IT_WORKS.md / STEP_BY_STEP.md - pipeline lifecycle end to end.
- CODE_DEEP_DIVE.md - three runnable JDK-only Java programs.
- EXERCISES.md - hands-on tasks with inline data.
- HISTORY.md / REFERENCES.md - background and real books (Kleppmann).
- ARCHITECTURE.md / INTERNALS.md / PERFORMANCE.md - implementation notes.
- DEBUGGING.md / COMMON_MISTAKES.md / INTERVIEW.md - pitfalls and Q&A.

## Careful-statements rule

No vendor version numbers, no throughput claims, no invented specs. Queues
are described by their widely documented default semantics (at-least-once
delivery is the common default, which permits duplicates) and nothing more.

## Conventions

- Java 21+, plain JDK only. Single-class, deterministic, ASCII output.
- All outputs in CODE_DEEP_DIVE.md are observed program output.

## Worked miniature

PipeIdem merges two batches with a replay into {o1=9.5, o2=4.0, o3=7.25},
rows = 3, unchanged by the repeat. PipeQuality reports rows 6, nulls 2,
nullRate 0.333, drift 0.375 vs ref 9.0. PipeSchema rules currency
COMPATIBLE and the double-to-string retype BREAKING. Reproduce all three.
