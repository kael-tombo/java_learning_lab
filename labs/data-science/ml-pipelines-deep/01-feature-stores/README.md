# Lab 01 — Feature Stores

## Goal
Understand why ML teams put features behind a store instead of ad-hoc
SQL, and how the store prevents training/serving mismatch.

## Core ideas
- Offline store: point-in-time-correct training rows built with as-of joins.
- Online store: low-latency key-value serving of the latest feature vector.
- Feature versioning: v1/v2 of a definition coexist so old models keep working.
- Serving skew: training used one transform, serving uses another; metrics rot.
- Backfill discipline: recompute history with the versioned transform, never patch by hand.
- TTL/retention: stale rows expire so serving never reads ancient values.

## What you do here
1. Read THEORY.md for as-of join semantics and skew mechanics.
2. Study CODE_DEEP_DIVE.md: three runnable JDK-only programs.
3. Work EXERCISES.md with small inline datasets.
4. Use FLASHCARDS.md and INTERVIEW.md to check recall.

## Prerequisites
Java 21+, comfort with lists/maps, basic ML vocabulary (features, labels).

## File map
22 notes: THEORY, HOW_IT_WORKS, ARCHITECTURE, INTERNALS, STEP_BY_STEP,
VISUAL_GUIDE, CODE_DEEP_DIVE, EXERCISES, MATH_FOUNDATION, HISTORY,
MENTAL_MODELS, WHY_IT_EXISTS, WHY_IT_MATTERS, PERFORMANCE, SECURITY,
DEBUGGING, COMMON_MISTAKES, INTERVIEW, REFLECTION, REFERENCES,
FLASHCARDS, README (this file).

## Rule for this lab
Every numeric claim is either a standard textbook fact or the observed
output of a snippet compiled with `javac --release 21` and run.

## How to verify your work
Compile the three CODE_DEEP_DIVE.md programs and match outputs
exactly: as-of values 2.0/3.0/NO_FEATURE with bias 1.0, maxdiffs 0.0
and 1.0, TTL kept=2 dropped=2 coverage=0.5. Any deviation means the
code was altered — diff before proceeding, since later labs assume
these semantics hold.
