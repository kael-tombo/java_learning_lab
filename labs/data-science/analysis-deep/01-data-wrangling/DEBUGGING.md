# Data Wrangling - Debugging Guide

## Symptom: column mean is NaN after cleaning

Cause: a NaN slipped through the sum loop. Fix: filter with `Double.isNaN`
before aggregating, then assert zero NaN remain (or an explicit accepted
count). Add a post-fill scan that fails on unexpected NaN.

## Symptom: unique-key count exceeds row count

Cause: key includes a varying column (timestamp with millis, UUID) so every
row looks unique. Fix: drop non-identifying fields from the key and
normalize (trim, case-fold, truncate timestamps to the event grain).

## Symptom: coercion rejects spike after a release

Cause: upstream format drift - new sentinel, thousands separators, encoding
change. Fix: histogram reject reasons, diff against the known set
(`"3x"`-style, blank, sentinel), and confirm with the feed owner before
touching the grammar.

## Symptom: IQR flags everything / nothing

Cause: wrong quartile method on tiny n, or fences computed on uncleaned
data (NaN included, duplicates included). Fix: clean first (coerce, dedup,
drop NaN), then compute type-7 quartiles on the analysis column.

## Symptom: z-screen misses an obvious giant

Cause: masking - the giant inflates the sd (14.73 here absorbs part of the
60.0). Fix: lead with the IQR rule for detection; use z-scores descriptively
after handling the flag.

## Symptom: reruns shuffle row order

Cause: `HashMap`-based dedup iteration. Fix: `LinkedHashMap` or an explicit
sort of the output; diff reruns byte-wise in tests.

## Symptom: downstream mean shifted after a "no-op" clean

Cause: an implicit choice (zero-fill, key change) moved the estimand.
Fix: diff before/after summaries per column and require the receipts
(counts at each stage) in every cleaning report.

## Symptom: median disagrees with a hand calculation

Cause: even-n averaging forgotten (median of four values needs the middle
pair's mean), or NaN/duplicates left in the sorted array. Fix: assert the
array is NaN-free and deduped before sorting, and unit-test median on both
odd- and even-length inputs with known answers (7 values median 9.0 here).
