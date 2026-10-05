# Reflection & Annotations Lab

Runtime metaprogramming: Class/Method/Field, proxies, annotation processing.

## Prereqs
- JDK 17+, OOP + generics
- Basic classpath/module reads

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
| MINI_PROJECT.md | Mini DI container |
| REAL_WORLD_PROJECT.md | Plugin/validation framework |

## Usage
```bash
cd labs/java/java-reflection-annotations
javac Main.java && java -Xmx512m --add-opens java.base/java.lang=ALL-UNNAMED Main
```

## Outcomes
- Use reflection safely with setAccessible + opens.
- Build/consume runtime + compile-time annotations.
- Prefer MethodHandles over raw reflection on hot paths.

## Next
EXERCISES.md → MINI_PROJECT.md → REAL_WORLD_PROJECT.md.
