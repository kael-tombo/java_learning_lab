# Records, Sealed & Pattern Matching Lab

Modern data modeling: records, sealed hierarchies, switch patterns, deconstruction.

## Prereqs
- JDK 21+ (patterns + record patterns stable)
- Generics + collections basics

## Contents
| File | Purpose |
|------|---------|
| THEORY.md | Concepts |
| EXERCISES.md | 10 hands-on |
| QUIZ.md | 20 Q |
| FLASHCARDS.md | Recall |
| MATH_FOUNDATION.md | Exhaustiveness math |
| CODE_DEEP_DIVE.md | Bytecode/refs |
| VISION.md | Roadmap |
| MINI_PROJECT.md | Expression evaluator |
| REAL_WORLD_PROJECT.md | Rules/pricing engine |

## Usage
```bash
cd labs/java/java-records-sealed-patterns
javac --enable-preview --release 21 Main.java  # if preview needed
java -XX:+UseG1GC Main
```

## Outcomes
- Model DTOs as records; hierarchies as sealed.
- Write exhaustive switches without default.
- Use record patterns + guards correctly.

## Next
EXERCISES.md → MINI_PROJECT.md → REAL_WORLD_PROJECT.md.
