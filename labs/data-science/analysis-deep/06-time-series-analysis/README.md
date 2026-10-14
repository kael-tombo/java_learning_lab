# Lab 06 - Time Series Analysis

Ordered observations y_1 ... y_T where the index is time. This lab
covers stationarity, autocorrelation structure, ARIMA-style models,
temporal validation, decomposition, baselines, and error metrics.

## Objectives

- Explain stationarity and why most classical models assume it.
- Read ACF/PACF plots to suggest AR vs MA structure.
- Write down AR/MA/ARIMA(p,d,q) equations and difference a trend.
- Split series temporally (never shuffle) and avoid lookahead leakage.
- Decompose trend/seasonal/residual and beat naive baselines honestly.
- Compute MAE/RMSE/MAPE and state MAPE's zero-division trap.

## Map of this lab

- THEORY.md / MATH_FOUNDATION.md - definitions, ARIMA equations, ACF math.
- HOW_IT_WORKS.md / STEP_BY_STEP.md - end-to-end forecasting workflow.
- CODE_DEEP_DIVE.md - three runnable JDK-only Java programs.
- EXERCISES.md - hands-on tasks on small inline datasets.
- HISTORY.md / REFERENCES.md - Box-Jenkins lineage and real books.
- ARCHITECTURE.md / INTERNALS.md / PERFORMANCE.md - implementation notes.
- DEBUGGING.md / COMMON_MISTAKES.md / INTERVIEW.md - pitfalls and Q&A.

## Conventions

- Java 21+, plain JDK only (java.util, java.lang.Math, streams).
- All snippets are single-class, deterministic, ASCII output.
- Every numeric claim in CODE_DEEP_DIVE.md is observed program output.

## Prerequisites

Basic statistics (mean, variance, correlation) and comfort reading
a for-loop. No external libraries are used anywhere in this lab.

## Worked miniature

TsDiff takes {4, 6, 9, 13, 18, 24} to diffs {2, 3, 4, 5, 6} with variance
falling from 48.2222 to 2.0000. TsErrors scores MAE 1.4000, RMSE 1.4832,
MAPE 9.4940% with one zero skipped. TsAcf reads lag-2 0.4722 against
lag-1 0.1250 on zigzag data. Reproduce all three before reading further.

## How to verify

Every snippet compiles under `javac --release 21 -encoding UTF-8` and
runs with `java -cp . <Class>`. If your output differs by any digit,
the bug is in transcription - the checked-in outputs are observed.
