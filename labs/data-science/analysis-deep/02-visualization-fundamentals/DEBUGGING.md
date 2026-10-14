# Visualization Fundamentals - Debugging Guide

## Symptom: counts do not sum to n

Cause: values falling outside [min, max) with no clamp, or NaN defeating the
index cast. Fix: clamp to end bins, filter NaN explicitly, and assert the
total equals input length in tests.

## Symptom: histogram changes shape between runs

Cause: bin edges derived from data min/max with unstable float formatting, or
a `HashMap`-ordered category axis. Fix: hard-code edges; use `TreeMap` for
numeric cells and `LinkedHashMap` for labels.

## Symptom: bar of value 9 renders in the wrong bin

Cause: edge-convention confusion (is 10.0 in bin 4 or bin 5?). Fix: document
left-closed/right-open with top-bin clamping, and unit-test exact edges
{0.0, 2.0, 10.0} expecting bins 0, 1, 4.

## Symptom: binned trend looks flat although scatter slopes

Cause: cells too wide (aggregation bias) or integer division truncating the
mean (`sum / n` with ints yields 4 instead of 4.5). Fix: narrow cells and
accumulate sums in double.

## Symptom: text bars misalign

Cause: proportional fonts or tab characters in the terminal. Fix: spaces
only, one `#` per unit, counts printed numerically so alignment is cosmetic
and exactness never depends on it.

## Symptom: category order shuffles

Cause: `HashMap` iteration for label counts. Fix: `LinkedHashMap` with
`merge`, preserving first-seen order (books, games, food).

## Symptom: reviewers dispute the finding

Cause: hidden defaults (unstated width, cropped axis). Fix: print edges,
width, baseline, and n in the chart itself - the lab's headers do exactly
this, making disputes checkable.

## Symptom: binned means disagree with hand arithmetic

Cause: accumulating into `int` sums (truncation) or pairing xs with the
wrong ys after a sort. Fix: keep parallel arrays unsorted (or sort index
pairs together), accumulate in double, and verify one cell by hand - e.g.
[2,4) holds y values 3,5,4,6 summing to 18, mean 4.5.
