# Java Module System Lab (JPMS)

Strong encapsulation, module-info, jlink images, layers.

## Prereqs
- JDK 17+, Maven/Gradle basics
- Packages vs classpath pain (jar hell)

## Contents
| File | Purpose |
|------|---------|
| THEORY.md | JPMS concepts |
| EXERCISES.md | 9 hands-on |
| QUIZ.md | 20 Q |
| FLASHCARDS.md | Recall |
| MATH_FOUNDATION.md | Graph/size math |
| CODE_DEEP_DIVE.md | Bytecode/refs |
| VISION.md | Roadmap |
| MINI_PROJECT.md | Modular CLI |
| REAL_WORLD_PROJECT.md | Modular microservice image |

## Usage
```bash
cd labs/java/java-module-system
javac -d mods --module-source-path src $(find src -name module-info.java)
java --module-path mods -m com.app/com.app.Main
jlink --module-path mods:$JAVA_HOME/jmods --add-modules com.app --output img
```

## Outcomes
- Write exports/opens/requires correctly.
- Build minimal jlink runtime.
- Debug split-package + service wiring.

## Next
EXERCISES.md → MINI_PROJECT.md → REAL_WORLD_PROJECT.md.
