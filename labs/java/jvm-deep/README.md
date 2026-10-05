# JVM Deep Lab

Bytecode, classloading, JIT, GC, tuning — from source to safepoint.

## Prereqs
- JDK 21+, `javap/jcmd/jfr` comfort
- Concurrency + memory basics

## Contents
| File | Purpose |
|------|---------|
| THEORY.md | Concepts |
| EXERCISES.md | 10 hands-on |
| QUIZ.md | 20 Q |
| FLASHCARDS.md | Recall |
| MATH_FOUNDATION.md | Heap/pause math |
| CODE_DEEP_DIVE.md | Bytecode/HotSpot |
| VISION.md | Roadmap |
| MINI_PROJECT.md | Alloc profiler |
| REAL_WORLD_PROJECT.md | Tuning + incident drill |

## Usage
```bash
cd labs/java/jvm-deep
javac Main.java && java -Xmx1g -Xlog:gc* -XX:+UseG1GC Main
jcmd <pid> JFR.start duration=30s filename=app.jfr
```

## Outcomes
- Read bytecode + JIT logs.
- Diagnose GC/heap/metaspan issues.
- Tune flags with evidence.

## Next
EXERCISES.md → MINI_PROJECT.md → REAL_WORLD_PROJECT.md.
