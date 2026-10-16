# MLOps Orchestration - Lab README

Scheduling and connecting the steps that retrain, validate, and promote models.

## What you will learn
- DAG orchestration (tasks as a directed acyclic graph with dependencies), scheduling (cron for fixed cadence, event triggers for new-data or metric-based runs), artifact lineage (pointers to data version, code commit, and parameters for every run).
- Tasks retry with backoff and must be idempotent so a retry produces the same result as one run.
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
- CODE_DEEP_DIVE.md: three runnable programs (A07Backoff, B07Lineage, C07Gate).
- EXERCISES.md: seven hands-on tasks with expected outcomes.
- PERFORMANCE.md, SECURITY.md, DEBUGGING.md: operations, threats, fixes.
- INTERVIEW.md, FLASHCARDS.md: review material in Q&A form.

## Running the snippets
```sh
javac --release 21 -encoding UTF-8 A07Backoff.java B07Lineage.java C07Gate.java
java --class-path . A07Backoff
java --class-path . B07Lineage
java --class-path . C07Gate
```

## How to work this lab
1. Read THEORY.md, then run the three snippets and match outputs.
2. Read INTERNALS.md to connect each output number to its formula.
3. Do the EXERCISES.md tasks in order; each builds on the previous.
4. Finish with FLASHCARDS.md and the REFLECTION.md prompts.

## Where this fits
- Part of the ml-pipelines-deep track: features, training, evaluation, then serving, monitoring, orchestration, and the fraud-detection worked system.
