# Data Wrangling - Internals (JDK Mechanics)

## NaN handling

`Double.NaN` is unordered: `NaN == NaN` is false and every comparison with
NaN is false. The only reliable test is `Double.isNaN(v)`. Summation loops
must branch on it explicitly, because adding NaN poisons the total to NaN.
Sorting with `Arrays.sort` moves NaN to the end; the snippets avoid this by
filtering NaN before any sort.

## Insertion-ordered dedup

`LinkedHashMap.putIfAbsent(key, row)` keeps the first row per key and
ignores later ones in O(1) amortized time. Iteration order equals first-seen
order, so output is deterministic across runs - a plain `HashMap` would not
guarantee that. The composite key joins normalized fields with a separator
that cannot appear in the fields themselves.

## Quantile interpolation (type-7)

For sorted `s` of length n and probability p, position
`h = 1 + (n - 1) * p` (1-based). Let lo = floor(h), hi = ceil(h),
frac = h - lo. The quantile is `s[lo] + frac * (s[hi] - s[lo])`.
With n = 10, p = 0.25: h = 3.25, so Q1 sits a quarter of the way from the
3rd to the 4th value - which is exactly how 13.0 arises in the example.

## Parsing internals

`Double.parseDouble` accepts leading/trailing whitespace itself, but the
snippet trims first so blank strings can be labelled `"blank"` and sentinels
like `"N/A"` get their own reason. Catching `NumberFormatException` per
element keeps one bad cell from aborting the column.

## Mean vs median cost

Mean is one O(n) pass. Median needs a sort: O(n log n) time and an O(n)
copy if the input must not be mutated. Mode is one hashmap pass, O(n)
average time. For wide tables the sort dominates, which is why streaming
sketches exist - but on small data, sort-and-pick is exact and simple.

## Determinism notes

No randomness, no wall-clock reads, no locale-dependent formatting appear in
the lab snippets. `Arrays.toString` on doubles prints shortest round-trip
representations, so outputs are byte-identical on any JDK 21+ runtime.
