# Streams & Optional Lab

Declarative data pipelines: streams, collectors, Optionals, parallel pitfalls.

## Prereqs
- JDK 17+, lambdas + generics
- Collections basics

## Contents
| File | Purpose |
|------|---------|
| THEORY.md | Concepts |
| EXERCISES.md | 10 hands-on |
| QUIZ.md | 20 Q |
| FLASHCARDS.md | Recall |
| MATH_FOUNDATION.md | Cost math |
| CODE_DEEP_DIVE.md | Bytecode/HotSpot |
| VISION.md | Roadmap |
| MINI_PROJECT.md | CSV analytics |
| REAL_WORLD_PROJECT.md | ETL pipeline service |

## Usage
```bash
cd labs/java/java-streams-optional
javac Main.java && java -Xmx1g -XX:+UseG1GC Main
```

## Outcomes
- Build lazy, short-circuiting pipelines.
- Use collectors/grouping correctly.
- Handle Optional without isPresent-get.

## Next
EXERCISES.md → MINI_PROJECT.md → REAL_WORLD_PROJECT.md.
