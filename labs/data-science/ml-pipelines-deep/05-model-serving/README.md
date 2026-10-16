# Model Serving - Lab README

Putting a trained model behind an interface that returns predictions for new inputs.

## What you will learn
- batch (offline, scheduled scoring of stored data), online (request/response per input), streaming (continuous scoring of an event flow).
- Latency budgets split by use case: interactive paths care about p50/p99 per request, background paths care about throughput per hour.
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
- CODE_DEEP_DIVE.md: three runnable programs (A05Latency, B05Batching, C05Canary).
- EXERCISES.md: seven hands-on tasks with expected outcomes.
- PERFORMANCE.md, SECURITY.md, DEBUGGING.md: operations, threats, fixes.
- INTERVIEW.md, FLASHCARDS.md: review material in Q&A form.

## Running the snippets
```sh
javac --release 21 -encoding UTF-8 A05Latency.java B05Batching.java C05Canary.java
java --class-path . A05Latency
java --class-path . B05Batching
java --class-path . C05Canary
```

## How to work this lab
1. Read THEORY.md, then run the three snippets and match outputs.
2. Read INTERNALS.md to connect each output number to its formula.
3. Do the EXERCISES.md tasks in order; each builds on the previous.
4. Finish with FLASHCARDS.md and the REFLECTION.md prompts.

## Where this fits
- Part of the ml-pipelines-deep track: features, training, evaluation, then serving, monitoring, orchestration, and the fraud-detection worked system.
