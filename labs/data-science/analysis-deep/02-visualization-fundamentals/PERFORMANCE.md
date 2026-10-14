# Visualization Fundamentals - Performance Notes

## Complexity of text charting (n values, b bins, c cells)

- Binning: O(n) time, O(b) counter memory. One pass, no sorting.
- Category counting: O(n) average with hashing, O(labels) memory.
- Binned means: O(n log c) with `TreeMap`, O(c) memory; a plain array of
  cells indexed like bins recovers O(n) when edges are uniform.
- Rendering: O(total count) characters; cap bar length (e.g. scale and label
  it) when counts reach thousands so output stays readable.

## Memory shape

Fixed bin arrays use O(b) regardless of n - the reason histograms scale to
streams: update counters per value, render at the end. Category maps grow
with distinct labels only. Raw values need not be retained after counting.

## JDK-specific guidance

- Primitive `int[]`/`double[]` counters beat boxed collections by a wide
  constant factor; no allocation per value.
- `StringBuilder` per line avoids quadratic string concatenation when bars
  are long.
- `TreeMap` pays log-factor per point; for uniform grids, index arithmetic
  into arrays is faster and simpler.
- Cap rendered bar width: beyond ~200 characters, print `count` plus a
  scaled bar and state the scale - terminals and logs both suffer otherwise.

## Scaling without libraries

Two-dimensional grids (x by y counters) extend the same pattern to dense
scatter data: O(n) time, O(cells) memory, densities printed as text. Exact
Anscombe-style shape checks on samples complement full-data grids.

## What is NOT claimed here

No frame rates or timings: text output speed depends on console and volume.
Size by the complexities above and measure on your own workload.

## Worked sizing example

One million values into 50 bins: one pass, 50 counters, trivial memory. The
same million as individually rendered points would need megabytes of output
and an unreadable blob - the binned version is both faster to draw and more
honest to read. That crossover (keep every point vs count into cells) sits
around a few thousand points for typical displays.
