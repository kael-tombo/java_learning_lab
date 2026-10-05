# JVM Internals

Understand the JVM from symptom to source: memory, JIT, GC,
synchronization, diagnostics. Six topic directories plus 10-layer
study files in this directory.

## File index (10-layer set)

| File | Purpose |
|------|---------|
| THEORY.md | Memory areas, JIT tiers, GC algorithms |
| CODE_DEEP_DIVE.md | HotSpot source-linked walkthroughs |
| EXERCISES.md | JOL, jstat, jcmd, GC-log drills |
| MATH_FOUNDATION.md | Queueing, Little's law, GC cost models |
| MINI_PROJECT.md | Custom synchronizer + benchmark |
| REAL_WORLD_PROJECT.md | 3 production incidents + capacity plan |
| QUIZ.md | Self-check questions |
| FLASHCARDS.md | Spaced-repetition cards |
| VISION.md | Mental models + career trajectory |
| INDEX.md | Topic-directory map (if present) |

## Prerequisites

- Solid Java + concurrency basics; comfort reading stack traces.
- JDK 17+ installed; ideally JDK 21 for generational ZGC + JFR pinning events.

## Tooling

- `jcmd` (histograms, JFR control, NMT), JFR + JMC (continuous profiling),
  async-profiler (CPU/alloc/lock flame graphs), `jstat`/`jhsdb` for logs.

## Safe usage notes

- Never run `jmap -dump` or heap histograms on latency-critical prod
  without a canary; prefer JFR (`JFR.start duration=...`) — near-zero overhead.
- Gate `async-profiler` wall-clock runs to 60–120 s; keep continuous JFR
  at default profile. Redact dumps before sharing.

## Sourced field notes (fetched Oct 2026 — verify before citing)

- https://docs.oracle.com/en/java/javase/21/docs/api/
- https://openjdk.org/jeps/444
- https://docs.spring.io/spring-boot/docs/current/reference/html/
