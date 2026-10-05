# Java Performance Engineering — performance-deep

> Hands-on lab: JMH, JIT, profiling, GC latency.

## Objectives
- Understand JMH benchmarks in Java 17+.
- Understand JIT C1/C2 & inlining in Java 17+.
- Understand escape analysis in Java 17+.
- Understand allocation profiling in Java 17+.
- Run, measure, and explain every example.

## Layout
- `THEORY.md` — concepts (exists).
- `EXERCISES.md` — 8–10 hands-on labs.
- `QUIZ.md` — 20 self-check questions.
- `CODE_DEEP_DIVE.md` — annotated snippets.
- `MINI_PROJECT.md` / `REAL_WORLD_PROJECT.md` — builds.

## Prerequisites
- JDK 17+ (`java -version`), Maven 3.9+.
- IDE with debugger; JFR/JMC optional.
- This lab assumes `JMH benchmarks` basics.

## Quickstart
```bash
cd labs/java/performance-deep
mvn -q test
```

## How to use
1. Read THEORY.md.
2. Do EXERCISES 1–4.
3. Attempt MINI_PROJECT.
4. Take QUIZ (aim 16/20).

## Done when
- You can whiteboard the core flow without notes.
- All tests green; one benchmark or metric captured.
<!-- pad-0: JMH benchmarks review checkpoint -->
<!-- pad-1: JIT C1/C2 & inlining review checkpoint -->
