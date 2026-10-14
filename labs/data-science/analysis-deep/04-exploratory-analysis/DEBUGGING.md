# Exploratory Analysis - Debugging Guide

## Symptom: pooled rate outside all stratum rates

Cause: arithmetic bug (wrong denominators) or mixing arms across strata -
a valid pooled rate always lies between its strata rates per arm (77.34 is
between 73.00 and 90.0 for treat). Fix: recompute from raw k/n and assert
containment per arm.

## Symptom: group n values do not sum to total

Cause: null keys silently grouped, or a filter applied after counting.
Fix: count before and after grouping, print the null-key bucket explicitly,
and assert 3+3 = 6 style reconciliation in tests.

## Symptom: correlation trio is inconsistent (signs clash with data)

Cause: misaligned arrays (age[i] paired with wrong spend[i]) after a sort
of one column. Fix: never sort parallel arrays independently; sort index
pairs, and verify one hand-computed cross-term (e.g. first pair
contribution) in tests.

## Symptom: reversal disappears on recheck

Cause: stratum key typo merging wards, or integer division (81/90 = 0 in
ints!) zeroing rates. Fix: keep keys exact, force double division
(100.0*k/n), and pin all six expected rates byte-for-byte.

## Symptom: shape signals disagree (bins say skew, mean/median say symmetric)

Cause: coarse bins manufacturing asymmetry, or a data transcription error
(the 15 typed as 1.5). Fix: re-bin at a second width and re-derive from raw
values; persistent-across-widths features are real.

## Symptom: overall mean outside group means

Cause: groups computed on different filters than the overall (missing
handling differs), or weighted-vs-unweighted confusion. Fix: single-pass
joint accumulation (as the snippet does) so overall and groups share one
denominator logic.

## Symptom: stakeholders quote your exploratory r as proof

Cause: record lacked the association-only caveat in writing. Fix: every
correlation line ships with n and "association, not causation" attached -
the snippet's own last line models the habit.
