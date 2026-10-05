# Java IO / NIO Deep Lab

Hands-on deep dive: `java.io`, `java.nio`, channels, buffers, selectors, async IO.

## Prereqs
- JDK 17+ (`java -version`), Maven 3.9+
- Basic Java collections + concurrency
- OS concepts: file descriptors, page cache

## Contents
| File | Purpose |
|------|---------|
| THEORY.md | Concepts + mental models |
| EXERCISES.md | 10 hands-on labs |
| QUIZ.md | 20 self-check questions |
| FLASHCARDS.md | Rapid recall table |
| MATH_FOUNDATION.md | Throughput/latency math |
| CODE_DEEP_DIVE.md | Bytecode + HotSpot refs |
| VISION.md | Where IO is heading |
| MINI_PROJECT.md | File indexer mini project |
| REAL_WORLD_PROJECT.md | Log ingestor service |

## Usage
```bash
cd labs/java/java-io-nio-deep
# compile a sample
javac $(find . -name "*.java" | head -1)
# run with NIO flags
java -XX:+UseG1GC -Djdk.nio.maxCachedBufferSize=1048576 Main
```

## Learning Outcomes
- Choose classic IO vs NIO vs async correctly.
- Tune buffers, direct memory, and selectors.
- Diagnose `Too many open files` and direct-memory OOM.

## Next
See EXERCISES.md → MINI_PROJECT.md → REAL_WORLD_PROJECT.md.
