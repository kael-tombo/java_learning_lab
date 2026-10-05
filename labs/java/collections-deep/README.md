# Deep Collections Engineering — collections-deep

> Hands-on lab: hashing, trees, concurrent maps, custom structures.

## Objectives
- Understand hash spreading & bins in Java 17+.
- Understand red-black trees in Java 17+.
- Understand ConcurrentHashMap in Java 17+.
- Understand CopyOnWriteArrayList in Java 17+.
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
- This lab assumes `hash spreading & bins` basics.

## Quickstart
```bash
cd labs/java/collections-deep
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
<!-- pad-0: hash spreading & bins review checkpoint -->
<!-- pad-1: red-black trees review checkpoint -->
