# Lab 08 - Experimentation (A/B Testing)

An A/B test randomizes users (or another unit) into control and
treatment, then compares goal metrics while guardrail metrics stand
watch. This lab covers test anatomy, power reasoning, peeking dangers,
sample-ratio checks, and novelty effects - with every number verified
by a runnable JDK-only program.

## Objectives

- Name the parts: hypothesis, randomization unit, control, goal vs
  guardrail metrics.
- Explain power qualitatively (bigger effect needs smaller n) and the
  standard-error scaling 1/sqrt(n).
- Show why peeking inflates false positives; use fixed horizons or
  sequential methods.
- Run an SRM chi-square check on allocation counts.
- Recognize novelty/primacy effects and plan past them.

## Map of this lab

- THEORY.md / MATH_FOUNDATION.md - tests, CIs, power math, SRM math.
- HOW_IT_WORKS.md / STEP_BY_STEP.md - running a test end to end.
- CODE_DEEP_DIVE.md - three runnable JDK-only Java programs.
- EXERCISES.md - hands-on tasks with inline numbers.
- HISTORY.md / REFERENCES.md - background and real books (Kohavi et al).
- ARCHITECTURE.md / INTERNALS.md / PERFORMANCE.md - implementation notes.
- DEBUGGING.md / COMMON_MISTAKES.md / INTERVIEW.md - pitfalls and Q&A.

## Conventions

- Java 21+, plain JDK only. Single-class, deterministic, ASCII output.
- Significance 0.05 and power 0.8 appear as stated conventions, not laws.
- All outputs in CODE_DEEP_DIVE.md are observed program output.

## Worked miniature

AbTest reads 1200/10000 vs 1320/10000 as diff 0.01200, z 2.55739,
p 0.01055, CI [0.00280, 0.02120]. SampleSize shows MDE halving per 4x
traffic (0.0376 at n = 1000 down to 0.0047 at n = 64000). Srm clears
5050/4950 (p 0.3173) and flags 5400/4600. Reproduce all three first.
