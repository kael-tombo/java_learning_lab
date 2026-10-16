# Fraud Detection System - Lab README

A worked system combining rules and a model to flag rare abusive transactions under tight latency.

## What you will learn
- class imbalance (fraud is an order of magnitude rarer than legitimate traffic, far below 1% in typical settings), operating-point choice (threshold picked on precision/recall, not accuracy), cost asymmetry (a missed fraud generally costs more than one manual review, stated qualitatively).
- Feature latency budgets split cheap inline features (amount, velocity counters) from slow ones (graph or aggregate lookups) that must stay out of the request path.
- How to compute the key quantities in plain Java 21+ with no libraries.
- How the pieces fail in production and which signals warn you first.

## Prerequisites
- Java 21+ installed; `javac --release 21` must succeed.
- Comfort with means, medians, and basic probability; no ML library needed.
- Familiarity with running single-class programs from the command line.

## File map
- THEORY.md: concepts, vocabulary, and standard formulas for this lab.
- MATH_FOUNDATION.md: derivations and worked numeric examples.
- HOW_IT_WORKS.md: end-to-end behavior of the running system.
- ARCHITECTURE.md: components and data flow between them.
- INTERNALS.md: mechanics behind each snippet result.
- CODE_DEEP_DIVE.md: three runnable programs (A08Metrics, B08Cost, C08Lag).
- EXERCISES.md: seven hands-on tasks with expected outcomes.
- PERFORMANCE.md, SECURITY.md, DEBUGGING.md: operations, threats, fixes.
- INTERVIEW.md, FLASHCARDS.md: review material in Q&A form.

## Running the snippets
```sh
javac --release 21 -encoding UTF-8 A08Metrics.java B08Cost.java C08Lag.java
java --class-path . A08Metrics
java --class-path . B08Cost
java --class-path . C08Lag
```

## How to work this lab
1. Read THEORY.md, then run the three snippets and match outputs.
2. Read INTERNALS.md to connect each output number to its formula.
3. Do the EXERCISES.md tasks in order; each builds on the previous.
4. Finish with FLASHCARDS.md and the REFLECTION.md prompts.

## Where this fits
- Part of the ml-pipelines-deep track: features, training, evaluation, then serving, monitoring, orchestration, and the fraud-detection worked system.
