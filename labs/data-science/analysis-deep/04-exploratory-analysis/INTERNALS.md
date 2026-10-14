# Exploratory Analysis - Internals (JDK Mechanics)

## Group accumulation pattern

`computeIfAbsent(key, k -> new double[2])` fetches or creates the (sum, n)
cell in one hash lookup; amortized O(1) per row. `LinkedHashMap` preserves
first-seen group order (north before south), so reports read naturally and
rerun identically. Overall mean accumulates in the same loop - one pass,
three outputs, no second traversal to drift out of sync.

## Rate arithmetic in doubles

`100.0 * k / n` forces floating-point division; `100 * k / n` with ints
would truncate to whole percent before the decimal point exists. Raw counts
(81/90) stay in the printout next to percents so readers can re-divide -
the audit habit that makes the paradox checkable rather than asserted.

## Shared correlation routine

One `corr` method serves all three pairs: dual mean accumulation, then a
joint deviation loop for s_xy, s_xx, s_yy, then the ratio. Reuse guarantees
the trio is comparable (same formula, same rounding); separate inline
implementations per pair would invite subtle divergence.

## Sorted-copy discipline

Shape displays sort clones, never live columns: `s = right.clone();
Arrays.sort(s)`. Median reads index n/2 (odd n = 9 gives the 5th value,
3.0). Binning loops pin out-of-range values to end bins with explicit
bounds rather than silently extending the scale.

## Determinism notes

Fixed arrays, ordered maps, no randomness, no locale formatting. The paradox
percentages print full double precision (86.66666666666667), which looks
verbose but pins exact verification - round only in prose, never in the
verified output.

## Percent formatting choice

Rates print full double precision (86.66666666666667) rather than rounded
percent strings: exactness first, readability in prose. A display layer may
round to one decimal (86.7%) only after the exact value is logged - rounding
early would make the 3.33-point ward-A gap unverifiable from output.
