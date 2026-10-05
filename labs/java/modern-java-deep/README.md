# Modern Java Deep Dive

Master Java 17–21+: records, sealed classes, pattern matching, virtual
threads, structured concurrency. Five atomic micro-labs plus 10-layer
study files in this directory.

## File index (10-layer set)

| File | Purpose |
|------|---------|
| THEORY.md | Feature reference with code (records → ZGC) |
| CODE_DEEP_DIVE.md | Annotated internals walkthroughs |
| EXERCISES.md | Hands-on drills per feature |
| MATH_FOUNDATION.md | Cost models (threads, pinning, Amdahl) |
| MINI_PROJECT.md | Small scoped build (ADT + service) |
| REAL_WORLD_PROJECT.md | Virtual-threads FinTech migration |
| QUIZ.md | Self-check questions |
| FLASHCARDS.md | Spaced-repetition cards |
| MODULE_INTERVIEW_GUIDE.md | Interview Q&A per feature |
| VISION.md | Data-oriented thesis + migration strategy |
| INDEX.md | Micro-lab (01–05) directory map |

## Prerequisites

- Java 17+ fluency; JDK 21 for virtual threads, pattern switch,
  record patterns, sequenced collections.
- Maven or Gradle; JUnit 5 basics.

## How to use

1. Read VISION.md, then THEORY.md end to end.
2. Work micro-labs 01 → 05 sequentially (each is self-contained).
3. Do EXERCISES.md + MINI_PROJECT.md, then the migration in
   REAL_WORLD_PROJECT.md.

## JDK 21 + preview flags

```bash
java --enable-preview --release 21 Main.java
mvn -Dmaven.compiler.release=21 -DcompilerArgs="--enable-preview" test
```

String templates and structured concurrency need `--enable-preview`
on JDK 21. Never ship preview flags to production without a rollout plan.

## Sourced field notes (fetched Oct 2026 — verify before citing)

- https://openjdk.org/jeps/444
- https://openjdk.org/jeps/462
- https://docs.oracle.com/en/java/javase/21/docs/api/
