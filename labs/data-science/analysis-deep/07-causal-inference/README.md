# Lab 07 - Causal Inference

Correlation is not causation. This lab covers what causation means,
why randomized trials are the benchmark, how confounding (including
Simpson's paradox) misleads, and what quasi-experimental designs -
matching, difference-in-differences, discontinuity, instruments - can
and cannot claim. Every causal claim here is stated with its
assumptions, never as magic.

## Objectives

- Separate correlation from causation with concrete numerical examples.
- Explain why randomization (RCTs) is the gold standard.
- Define confounding and demonstrate Simpson's paradox with real numbers.
- Describe propensity-score matching as a concept with its key assumption.
- Write the difference-in-differences structure and its parallel-trends
  assumption.
- Sketch regression discontinuity and instrumental variables, including
  the relevance and exclusion requirements for instruments.

## Map of this lab

- THEORY.md / MATH_FOUNDATION.md - potential outcomes, confounding math.
- HOW_IT_WORKS.md / STEP_BY_STEP.md - how each design is reasoned about.
- CODE_DEEP_DIVE.md - three runnable JDK-only Java programs.
- EXERCISES.md - hands-on arithmetic on small inline datasets.
- HISTORY.md / REFERENCES.md - Fisher/RCT lineage and real books.
- ARCHITECTURE.md / INTERNALS.md / PERFORMANCE.md - implementation notes.
- DEBUGGING.md / COMMON_MISTAKES.md / INTERVIEW.md - pitfalls and Q&A.

## Caution flag

Causal conclusions always rest on untestable assumptions (no unmeasured
confounding, parallel trends, exclusion). This lab names the assumption
every time a method is used. Any sentence that hides one is a bug.

## Conventions

- Java 21+, plain JDK only. Single-class, deterministic, ASCII output.
- Numeric claims in CODE_DEEP_DIVE.md are observed program output.
