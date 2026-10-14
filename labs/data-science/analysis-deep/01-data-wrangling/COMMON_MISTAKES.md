# Data Wrangling - Common Mistakes

## 1. Comparing doubles to NaN with ==

`v == Double.NaN` is always false, so missing cells slip into sums and NaN
poisons the total. Always branch on `Double.isNaN(v)`.

## 2. Zero-filling unknowns

Filling the lab column's NaN with 0 gives mean 4.8, not 6.0. Reserve zero
for measured zeros; keep unknowns as NaN until a modelled fill.

## 3. Imputing before deduplicating

The duplicated `c7|2026-01-05` row would tilt any fitted mean toward its
value. Dedup first, then fit the fill on unique rows.

## 4. Global mean under MAR

If missingness tracks age, one overall mean mixes bands dishonestly. Impute
within the observed driver (age bands) instead.

## 5. Silent coercion

`catch (Exception e) { continue; }` drops `"3x"`, `""`, `"N/A"` without a
trace: 7 inputs become 4 with no receipt. Log every reject with its reason
and reconcile parsed + rejected = inputs.

## 6. Auto-deleting fence flags

The 60.0 might be a typo - or the outage you were hired to find. Flags route
to review; deletion needs a proven collection error plus a log entry.

## 7. Unstable key separators

Joining key fields with `|` breaks if a field can contain `|`. Normalize
fields and pick a separator outside their alphabet, or hash a tuple.

## 8. Forgetting determinism

`HashMap` iteration order varies, so "kept" rows can shuffle between runs.
Use `LinkedHashMap` (or sort output) so the clean table is byte-stable.

## 9. Sorting NaN into quartiles

`Arrays.sort` on raw doubles parks NaN at the end; quartiles read off the
sorted array then sit in the wrong positions. Strip NaN (after counting it)
before any sort used for Q1/Q3/median.

## 10. Mean-filling a skewed column

On `{1, 2, NaN, 3, 100}` the mean-fill is 26.5 while the median-fill is 2.5.
Reaching for the mean by default lets one tail value set four cells' story;
check skew first, then choose.
