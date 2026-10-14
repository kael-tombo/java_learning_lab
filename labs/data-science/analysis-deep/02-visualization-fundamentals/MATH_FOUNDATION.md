# Visualization Fundamentals - Math Foundation

## Histogram bin index

For edges min + k x width, value v falls in bin
k = floor((v - min) / width). With min 0, width 2: v = 5 gives
floor(2.5) = 2, the [4,6) bin. The Java cast `(int)` matches floor for
non-negative offsets; clamping pins out-of-range values to end bins.

## Bin width trade-off (bias vs variance)

Narrow bins: low bias (detail preserved), high variance (counts bounce with
sampling noise). Wide bins: smooth but biased (the 9 merges into the bulk).
No formula picks width universally; comparing two widths (as the exercises
ask) shows which features persist and are therefore real.

## Mean vs median as shape signal

Right skew pulls the mean above the median: here 3.6 > 3.0 with the lone 9.
The gap's sign diagnoses skew direction; its size relative to spread says
whether the tail matters. Symmetric data keeps them together.

## Binned means as conditional expectation

Cell mean = E[y | x in cell], estimated by the cell average. With cells
[0,2) through [6,8), the estimates 3.0, 4.5, 6.5, 8.0 trace the underlying
trend the way a regressogram does. Standard error per cell is s/sqrt(n), so
the n = 2 end cells are noisier than the n = 4 middle ones.

## Sample sd formula behind the trio

Sample sd = sqrt(sum (x - mean)^2 / (n - 1)). Series b: deviations
-4,-2,0,2,4, squares sum 40, /4 = 10, sqrt = 3.1622776601683795. Series c:
deviations -8,0,0,0,8, squares sum 128, /4 = 32, sqrt = 5.656854249492381.
Same mean 6.0, sds 0 / 3.16 / 5.66: spread hints at shape but never resolves
it - that needs the plot.

## Proportion arithmetic

books 3/8 = 0.375, games 3/8 = 0.375, food 2/8 = 0.25; fractions sum to 1.
Report counts with fractions so sampling uncertainty (n = 8 total) stays
visible beside the point estimate.
