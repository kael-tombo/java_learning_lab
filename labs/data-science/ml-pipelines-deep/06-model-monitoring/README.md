# Model Monitoring - Lab README

Watching a deployed model and its data so regressions are caught after launch.

## What you will learn
- data drift (input distribution changes), concept drift (the input-output relationship changes), label delay (ground truth arrives late so true quality is unknowable at first).
- Drift is checked with distribution comparisons such as PSI (binned divergence between expected and actual shares) and the KS test (largest gap between two empirical CDFs) treated as concepts, not pass/fail numbers.
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
- CODE_DEEP_DIVE.md: three runnable programs (A06Psi, B06Ks, C06Alerts).
- EXERCISES.md: seven hands-on tasks with expected outcomes.
- PERFORMANCE.md, SECURITY.md, DEBUGGING.md: operations, threats, fixes.
- INTERVIEW.md, FLASHCARDS.md: review material in Q&A form.

## Running the snippets
```sh
javac --release 21 -encoding UTF-8 A06Psi.java B06Ks.java C06Alerts.java
java --class-path . A06Psi
java --class-path . B06Ks
java --class-path . C06Alerts
```

## How to work this lab
1. Read THEORY.md, then run the three snippets and match outputs.
2. Read INTERNALS.md to connect each output number to its formula.
3. Do the EXERCISES.md tasks in order; each builds on the previous.
4. Finish with FLASHCARDS.md and the REFLECTION.md prompts.

## Where this fits
- Part of the ml-pipelines-deep track: features, training, evaluation, then serving, monitoring, orchestration, and the fraud-detection worked system.
