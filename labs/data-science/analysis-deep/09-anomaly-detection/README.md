# Lab 09 - Anomaly Detection

Anomalies are rare points that matter: fraud, outages, sensor failure.
This lab covers z-score/IQR baselines, the isolation intuition, the
precision/recall tradeoff across thresholds, the base-rate fallacy
with verified Bayes arithmetic, and the operational reality of alert
fatigue.

## Objectives

- Flag outliers with z-scores and the IQR rule on real numbers.
- Explain the isolation intuition: anomalies separate in few splits.
- Trace precision/recall across thresholds and pick one deliberately.
- Compute PPV from prevalence, sensitivity, and false-positive rate,
  and feel the base-rate fallacy quantitatively.
- Design alerts a human team can sustain without fatigue.

## Map of this lab

- THEORY.md / MATH_FOUNDATION.md - scores, rules, Bayes derivations.
- HOW_IT_WORKS.md / STEP_BY_STEP.md - detector workflow end to end.
- CODE_DEEP_DIVE.md - three runnable JDK-only Java programs.
- EXERCISES.md - hands-on tasks with inline datasets.
- HISTORY.md / REFERENCES.md - background and real books.
- ARCHITECTURE.md / INTERNALS.md / PERFORMANCE.md - implementation notes.
- DEBUGGING.md / COMMON_MISTAKES.md / INTERVIEW.md - pitfalls and Q&A.

## Conventions

- Java 21+, plain JDK only. Single-class, deterministic, ASCII output.
- All outputs in CODE_DEEP_DIVE.md are observed program output.
- Bayes numbers are computed by the BaseRate program, not asserted.

## Worked miniature

AnomBase centers eleven readings (mean 11.864, sd 5.739) with z and IQR
agreeing on index 7 (30.000). PrCurve sweeps t = 0.8/0.5/0.2 into P/R of
0.667/0.500, 0.600/0.750, 0.500/1.000. BaseRate lands PPV 0.0902: 99 true
vs 999 false per 100k. Reproduce all three before reading further.
