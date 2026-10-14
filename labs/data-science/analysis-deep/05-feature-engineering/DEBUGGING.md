# Feature Engineering - Debugging Guide

## Symptom: validation beats test by a wide margin

Cause: fold-impure fitting (scaler/target means saw held-out rows). Fix:
re-run with the row-id overlap checker; refit strictly inside folds; expect
the honest gap to shrink toward the true generalization error.

## Symptom: all-zeros row after encoding

Cause: unseen level mapped to zero vector (correct behavior) hitting a model
with no unknown handling - or a vocabulary typo ("Blue" vs "blue"). Fix:
normalize case/whitespace at fit and apply identically; add the unknown
column so "unseen" is a signal, not a void.

## Symptom: NaN column after log

Cause: zero/negative slipped past the guard. Fix: pre-count `x <= 0`,
apply the fitted shift, assert finite output per column, quarantine
offenders with counts.

## Symptom: one feature dominates coefficients

Cause: unscaled product (480) beside raw smalls (rooms 4). Fix: scale after
interacting; inspect coefficient x std (standardized effect) rather than raw
coefficients.

## Symptom: train/test skew in scaled means

Cause: apply used different constants than fit (recomputed "for
convenience"). Fix: single parameter object threaded from fit to apply;
test that apply output on train rows reproduces fit-time values exactly.

## Symptom: hashing collisions tank a key feature

Cause: width too small for identity-critical levels (billing ids merged at
random). Fix: reserve exact encoding for identities; hash only wide weak
signals, and widen until collision-rate estimates stop moving metrics.

## Symptom: target-encoded model perfect in train, flat in prod

Cause: full-label means memorized levels. Fix: rebuild with fold-nested
smoothed encoding; compare level-mean stability across folds - unstable
levels get heavier smoothing (larger m).
