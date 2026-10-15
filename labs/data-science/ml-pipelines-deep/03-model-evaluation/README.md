# Lab 03 — Model Evaluation

## Goal
Evaluate classifiers honestly: read a confusion matrix, compute
precision/recall/F1 correctly, know when ROC-AUC misleads on imbalanced
data, use proper scoring rules for probabilities, and split data so
results mean what they claim.

## Core ideas
- Confusion matrix (TP/FP/TN/FN) as the source of all rate metrics.
- Precision, recall, F1 (harmonic mean of the two).
- ROC-AUC concept and PR curves for class imbalance.
- Log-loss and Brier score as proper scoring rules (concept level).
- Calibration: predicted probabilities matching observed frequencies.
- Stratified K-fold: preserve class ratios across folds.
- Train/val/test discipline and leakage via preprocessing.

## What you do here
1. Read THEORY.md for definitions and formulas.
2. Study CODE_DEEP_DIVE.md: three runnable JDK-only programs.
3. Work EXERCISES.md with hand recomputation first.
4. Use FLASHCARDS.md and INTERVIEW.md to check recall.

## Prerequisites
Java 21+, fractions and logarithms at high-school level, familiarity
with train/test vocabulary.

## File map
22 notes: THEORY, HOW_IT_WORKS, ARCHITECTURE, INTERNALS, STEP_BY_STEP,
VISUAL_GUIDE, CODE_DEEP_DIVE, EXERCISES, MATH_FOUNDATION, HISTORY,
MENTAL_MODELS, WHY_IT_EXISTS, WHY_IT_MATTERS, PERFORMANCE, SECURITY,
DEBUGGING, COMMON_MISTAKES, INTERVIEW, REFLECTION, REFERENCES,
FLASHCARDS, README (this file).

## Rule for this lab
Every numeric claim is either a standard textbook fact or the observed
output of a snippet compiled with `javac --release 21` and run.
