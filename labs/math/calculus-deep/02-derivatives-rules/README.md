# Derivatives and Rules

## Overview

The derivative as a limit of difference quotients, then the working
rules: power, product, quotient, chain, plus exponentials, logs, and
trig. Closes with Rolle and the Mean Value Theorem with hypotheses
stated exactly, and why differentiability implies continuity.

## Contents

- THEORY.md: difference-quotient definition, proof sketch that
  differentiability implies continuity, five rules, standard
  derivatives, Rolle/MVT with the |x| counterexample.
- MATH_FOUNDATION.md: four rule applications evaluated at points
  (product 59.1124487914452, chain 0.8, quotient 3, trig-chain
  0.4233600241796016), each confirmed by central differences,
  plus an MVT equality case (c = 2 on [1,3]).
- CODE_DEEP_DIVE.md: central-difference harness verifying each closed
  form to 8+ figures; tangent-line and MVT scans.

## Prerequisites

Limit laws and continuity (lab 01); algebra through rational functions.

## How to work this lab
Apply each rule by hand first, then run the central-difference harness
against your answer — agreement to 8 figures is the pass criterion, and
disagreement means your algebra (not the code) is wrong. Pay special
attention to the chain-rule nesting order: most errors come from
differentiating outside-in in the wrong sequence.
