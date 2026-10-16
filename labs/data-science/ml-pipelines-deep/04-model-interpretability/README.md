# Lab 04 — Model Interpretability

## Goal
Explain model behavior honestly: separate global from local questions,
measure permutation importance, read partial dependence, fit local
surrogates in the LIME spirit, attribute credit with Shapley values,
and state the stability caveats every explanation carries.

## Core ideas
- Global vs local explanations (whole-model behavior vs one prediction).
- Permutation importance: accuracy drop when a feature is shuffled.
- PDP concept: model output vs one feature with others fixed/averaged.
- LIME concept (Ribeiro 2016): local interpretable surrogate near x0.
- SHAP concept (Lundberg/Lee 2017): Shapley values with efficiency,
  symmetry, dummy, additivity axioms.
- Interpretability-vs-accuracy framing and explanation stability limits.

## What you do here
1. Read THEORY.md for the axioms and method mechanics.
2. Study CODE_DEEP_DIVE.md: three runnable JDK-only programs.
3. Work EXERCISES.md with hand recomputation first.
4. Use FLASHCARDS.md and INTERVIEW.md to check recall.

## Prerequisites
Java 21+, weighted averages and basic game-theory intuition (sharing a
payout), familiarity with train/test vocabulary.

## File map
22 notes: THEORY, HOW_IT_WORKS, ARCHITECTURE, INTERNALS, STEP_BY_STEP,
VISUAL_GUIDE, CODE_DEEP_DIVE, EXERCISES, MATH_FOUNDATION, HISTORY,
MENTAL_MODELS, WHY_IT_EXISTS, WHY_IT_MATTERS, PERFORMANCE, SECURITY,
DEBUGGING, COMMON_MISTAKES, INTERVIEW, REFLECTION, REFERENCES,
FLASHCARDS, README (this file).

## Rule for this lab
Every numeric claim is either a standard textbook fact or the observed
output of a snippet compiled with `javac --release 21` and run.
