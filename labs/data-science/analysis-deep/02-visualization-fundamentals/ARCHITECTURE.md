# Visualization Fundamentals - Architecture

## Text-chart pipeline

```text
values --> SCALE (min, width, bins) --> BIN (index per value)
   --> COUNT (per-bin totals) --> RENDER (count + '#' bar per bin)
```

## Component responsibilities

- **Scale:** owns edges. Declares min, width, bin count, and the edge rule
  (left-closed, right-open; top bin closed on both ends). No counting logic.
- **Binner:** pure index function `(int)((v - min) / width)` with clamping.
  Out-of-range values pin to the end bins and are reported, never dropped.
- **Counter:** integer array accumulation, O(n). Totals must reconcile with
  input length.
- **Renderer:** prints `edge-range: count + bar`. Bar length equals count
  exactly (scale 1 char = 1 observation); no normalization without a label.
- **Binned-mean reducer:** `TreeMap` from cell index to (sum, n), emitting
  cells in x order with both n and mean shown.

## JDK mapping

- Counts: `int[]` arrays indexed by bin - no boxing, no maps needed.
- Category counts: `LinkedHashMap` with `merge` for stable label order.
- Ordered cells: `TreeMap<Integer, double[]>` so output follows the x-axis.
- Bars: `StringBuilder` loops; deterministic across runs and locales.

## Invariants

1. The scale is declared before any value is examined for shape.
2. Every input value appears in exactly one bin; counts sum to n.
3. Empty bins render explicitly - absence of bar is data.
4. Any aggregated number (cell mean, proportion) is printed beside its n.

## Worked trace through the pipeline

Input 5.0 with scale (min 0, width 2): index floor(2.5) = 2, counter[2]++.
After all ten values, counters read [1,5,3,0,1]; renderer prints each with
its edge range. Change width to 5 and the same values give [9,1]: identical
input, coarser lens. The architecture isolates that lens choice in Scale so
reviews can challenge it without rereading counting code.
