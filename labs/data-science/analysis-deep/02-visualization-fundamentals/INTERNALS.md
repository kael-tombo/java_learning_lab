# Visualization Fundamentals - Internals (JDK Mechanics)

## Bin index arithmetic

`(int)((v - min) / width)` truncates toward zero, which for non-negative
offsets equals floor. Negative offsets would truncate upward, so the clamp
`if (b < 0) b = 0` doubles as the guard. Exact edge hits (v = 4.0, width 2)
yield index 2, i.e. left-closed/right-open intervals. Floating-point
fuzz at edges (e.g. 0.1 + 0.2 style sums) can misbin by one ulp; the lab's
whole-number data avoids it, and production code should nudge by a tiny
epsilon or use `BigDecimal` edges.

## Integer counting, exact rendering

`int[] counts` accumulates without boxing; `StringBuilder` appends one `#`
per unit so bar length is the count, verifiable by eye. No locale-sensitive
formatting is used: doubles print via string concatenation of whole-valued
doubles (`[0.0,2.0)`), identical on any JDK 21+.

## Ordered maps for ordered axes

`TreeMap` iterates keys ascending, so binned-mean rows print left to right
along x with no explicit sort. `LinkedHashMap` keeps first-seen label order
for categories (books, games, food), which reads naturally and stays stable
across runs - `HashMap` would scramble it.

## Mean accumulation precision

Sums accumulate in `double` in input order; for the lab's magnitudes the
error is zero. Cell means divide sum by cell n once, after the loop - never
incrementally, which would compound rounding.

## Determinism notes

No randomness, no time reads, no locale formatting. Given the same arrays,
every snippet prints byte-identical output on any conforming runtime, which
is what makes text charts testable with plain string comparison.

## Edge-case arithmetic worth knowing

`(int)(9.0 / 2)` = 4 selects the last bin [8,10) - the top edge belongs to
the final bin by clamping, not by a sixth bin. `(int)(0.0 / 2)` = 0 starts
the first bin. A value of exactly 10.0 also clamps to bin 4, which the edge
audit in EXERCISES.md task 7 verifies directly.
