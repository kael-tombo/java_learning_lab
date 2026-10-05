# Reactive Java Deep Dive — reactive-deep

> Hands-on lab: Reactor, RxJava, Flow API, backpressure.

## Objectives
- Understand Publisher/Subscriber in Java 17+.
- Understand Flux/Mono in Java 17+.
- Understand backpressure strategies in Java 17+.
- Understand schedulers in Java 17+.
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
- This lab assumes `Publisher/Subscriber` basics.

## Quickstart
```bash
cd labs/java/reactive-deep
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
<!-- pad-0: Publisher/Subscriber review checkpoint -->
<!-- pad-1: Flux/Mono review checkpoint -->
