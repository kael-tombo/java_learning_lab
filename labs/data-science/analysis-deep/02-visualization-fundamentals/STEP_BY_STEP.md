# Visualization Fundamentals - Worked Example

## Histogram of {1, 2, 2, 3, 3, 3, 4, 4, 5, 9}, width 2 from 0

Assign each value: 1 -> [0,2); 2,2,3,3,3 -> [2,4); 4,4,5 -> [4,6);
nothing -> [6,8); 9 -> [8,10). Counts: 1, 5, 3, 0, 1; total 10, reconciled.
The empty [6,8) bin is drawn (as `0` with no bar) because hiding empty bins
lies about the gap between the bulk and the 9.

## Reading the shape

Peak at [2,4), right tail via the isolated 9. Mean of the ten values is 3.6;
the median is 3.0. Mean above median plus a far right bar says right skew -
the same mean/median comparison used for shape reading in later labs.

## Binned means on the twelve (x, y) points

Cells: [0,2) holds (1,2),(1,4): mean 3.0. [2,4) holds four points: mean 4.5.
[4,6) holds four points: mean 6.5. [6,8) holds two points: mean 8.0.
Monotone rise 3.0 -> 4.5 -> 6.5 -> 8.0: the trend survives aggregation, and
each cell reports its n so no cell hides behind a mean of two points.

## Same-mean trio

Series means are all exactly 6.0 (a: five 6s; b: 2+4+6+8+10=30; c:
-2+6+6+6+14=30). Sample sds: 0.0, 3.1622776601683795, 5.656854249492381.
Write the three one-line "plots" (flat, slope, outlier pair) and confirm no
summary table distinguishes what the drawing makes obvious.

## Category bars

books 3/8, games 3/8, food 2/8. Bars `###`, `###`, `##` keep the count
visible next to the fraction, so a reader sees both the proportion and the
n = 8 behind it.

## Sanity checks to run

- Histogram counts sum to 10; any other total means a value escaped the
  scale (check clamping) or NaN entered the index cast.
- Binned cell n values sum to 12; cell means times n must reconstruct each
  cell's y-sum (e.g. 4 x 4.5 = 18 = 3+5+4+6 for the raw points 3,5,4,6).
- Category fractions sum to 1: 3/8 + 3/8 + 2/8 = 8/8. A shortfall means a
  label was filtered before counting.
