# Java Foreign Function & Memory Lab (Panama)

Safe off-heap + native interop: MemorySegment, Arena, Linker, MethodHandles.

## Prereqs
- JDK 22+ (stable FFM API), `java -version`
- C basics: pointers, structs, `strlen`/`qsort`
- Modules: `java.base` includes `java.lang.foreign`

## Contents
| File | Purpose |
|------|---------|
| THEORY.md | FFM mental models |
| EXERCISES.md | 9 hands-on labs |
| QUIZ.md | 20 questions |
| FLASHCARDS.md | Recall table |
| MATH_FOUNDATION.md | Address math |
| CODE_DEEP_DIVE.md | HotSpot/panama refs |
| VISION.md | Roadmap |
| MINI_PROJECT.md | Native grep via arena |
| REAL_WORLD_PROJECT.md | Image/native codec service |

## Usage
```bash
cd labs/java/java-module-foreign
javac --enable-native-access=ALL-UNNAMED Main.java
java --enable-native-access=ALL-UNNAMED -Xmx512m Main
```

## Outcomes
- Allocate/manage arenas without leaks.
- Bind native funcs with Linker safely.
- Avoid use-after-free across threads.

## Next
EXERCISES.md → MINI_PROJECT.md → REAL_WORLD_PROJECT.md.
