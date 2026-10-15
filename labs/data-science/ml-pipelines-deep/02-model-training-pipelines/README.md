# Lab 02 — Model Training Pipelines

## Goal
Learn how training is organized as a repeatable staged pipeline rather
than a notebook run: ordered DAG stages, validation gates that stop bad
data, deterministic retraining, and registries that track exactly what
produced each model.

## Core ideas
- DAG stages: ingest, validate, transform, train, evaluate, register,
  each with declared inputs and outputs.
- Data validation: schema checks plus null-rate and range monitors that
  flag drift before training starts.
- Deterministic retraining: fixed seeds and pinned code/data versions
  so reruns reproduce results.
- Artifact registry: versioned storage of datasets, models, and metrics.
- Experiment tracking: every run records params, metrics, code hash,
  and data hash.

## What you do here
1. Read THEORY.md for stage contracts and gate semantics.
2. Study CODE_DEEP_DIVE.md: three runnable JDK-only programs.
3. Work EXERCISES.md against small inline datasets.
4. Use FLASHCARDS.md and INTERVIEW.md to check recall.

## Prerequisites
Java 21+, basic statistics vocabulary (mean, null rate), familiarity
with lab 01 concepts (versions, lineage).

## File map
22 notes: THEORY, HOW_IT_WORKS, ARCHITECTURE, INTERNALS, STEP_BY_STEP,
VISUAL_GUIDE, CODE_DEEP_DIVE, EXERCISES, MATH_FOUNDATION, HISTORY,
MENTAL_MODELS, WHY_IT_EXISTS, WHY_IT_MATTERS, PERFORMANCE, SECURITY,
DEBUGGING, COMMON_MISTAKES, INTERVIEW, REFLECTION, REFERENCES,
FLASHCARDS, README (this file).

## Rule for this lab
Every numeric claim is either a standard textbook fact or the observed
output of a snippet compiled with `javac --release 21` and run.
