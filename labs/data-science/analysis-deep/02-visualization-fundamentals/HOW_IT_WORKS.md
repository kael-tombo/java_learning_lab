# Visualization Fundamentals - How It Works

## From values to text bars

1. **Fix the scale first.** Choose min, max, and bin width before counting.
   The lab histogram uses min 0, width 2, five bins: [0,2) [2,4) [4,6)
   [6,8) [8,10). Values on an edge fall in the higher bin by the cast rule.
2. **Assign each value to a bin.** Index = (int)((v - min) / width), clamped
   to the ends. Count per bin in O(n).
3. **Render counts as bars.** One `#` per observation, plus the numeric count
   beside it so the chart stays exact, not decorative.
4. **Read shape, not decoration.** Peak location, spread, gaps, and isolated
   bars (the lone 9 in [8,10)) are the findings; everything else is ink.

## How binned means work

For dense (x, y) data, group x into cells and report each cell's n and mean
y. The lab's twelve points give cell means 3.0, 4.5, 6.5, 8.0 across cells
[0,2) [2,4) [4,6) [6,8) - a rising trend summarized in four numbers. This is
the one-dimensional version of the regression smooth any plotting package
draws.

## How the Anscombe check works

Compute group means and sds, then compare against a plot (here, reasoning
about the three series). Series a (flat sixes, sd 0), b (2..10 slope, sd
3.16), and c (outlier pair, sd 5.66) share mean 6.0 exactly. Statistics
agree; shapes disagree; the plot is the tiebreaker that statistics cannot be.

## How bar proportions work

Count per label, divide by the total (3/8, 3/8, 2/8), and draw bars alongside
the fractions. Keeping counts next to proportions prevents the classic error
of comparing percentages with different denominators.

## Failure preview

Skip the scale step and two analysts bin the same data differently, then
argue about "findings" that are really binning artifacts. Hide the empty
[6,8) bin and the gap vanishes from every downstream slide. Average the
three mean-6.0 series together and flat, trend, and outlier-pair become one
fictional "typical" series. Each pipeline step exists to prevent one of
these specific, common failures.
