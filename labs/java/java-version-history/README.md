# Java Features from 1.2 to 25 — java-version-history

> Hands-on lab: the actual feature lineage of the Java platform, version by version, and the design pressure behind each change.

## Why this lab exists

Java's API surface looks arbitrary until you know the history. Why is
`java.util.function` (8) separate from `java.util.stream` (8) but both feel
older? Why did `Optional` land in 2014 and not 2004? Why is `var` a compile-time
feature (10) while `record` is a semantic one (16)?

Because each version responded to pressure that already existed:
performance (the JVM's early reputation), generics safety (post-2004 ecosystem
maturity), functional-programming revival, cloud concurrency, and — from 17
onward — the module system's need to close the JDK over its own internals.

Reading the timeline backwards explains modern Java far faster than reading
the JLS forwards.

## Objectives

- Reconstruct the feature lineage of the platform from 1.2 through 25.
- Explain *why* each major version arrived, tied to ecosystem pressure.
- Distinguish language features from library features from JVM features.
- Identify which version introduced each feature you use daily.
- Judge which historical decisions still constrain the platform today.

## Layout

| File | Purpose |
|---|---|
| `VISION.md` | Why history matters, mental models, learning path |
| `THEORY.md` | The full 1.2 → 25 feature timeline |
| `EXERCISES.md` | 10 hands-on "compile it on each version" labs |
| `QUIZ.md` | 20 questions with answers |
| `FLASHCARDS.md` | 235 version-attribution cards, incl. a "common misattributions" table |
| `MATH_FOUNDATION.md` | Amdahl's law, JMM cost models, version economics |
| `CODE_DEEP_DIVE.md` | Annotated evolution of single features across versions |
| `MINI_PROJECT.md` | Build a version-compatibility analyzer |
| `REAL_WORLD_PROJECT.md` | Produce a migration impact report for a real estate |

## Prerequisites

- JDK 21 and JDK 25 available (`java -version`).
- Comfortable with basic Java syntax.
- Reading `labs/java/java-migration/THEORY.md` afterwards is the natural next step.

## Quickstart

```bash
cd labs/java/java-version-history

# Compile the same source against several targets
javac --release 8   -d out8  src/main/java
javac --release 17  -d out17 src/main/java
javac --release 21  -d out21 src/main/java

# Inspect what the current runtime actually adds
java --describe-module java.base | head -40

# Release notes are the authoritative per-version source
# https://openjdk.org/projects/jdk/
```

## How to use

1. Read `THEORY.md` end to end — the timeline is the point of this lab.
2. Do Exercises 1–6 (the version compilation matrix).
3. Do Exercises 7–10 (design-pressure analysis).
4. Take `QUIZ.md` (aim 16/20).
5. Attempt `MINI_PROJECT.md`.

## Done when

- You can name the version and JEP for any feature you use weekly.
- You can explain why `Optional` was rejected for 10 years and then adopted.
- You can articulate the trade-off behind at least five historical decisions
  that still shape the platform.