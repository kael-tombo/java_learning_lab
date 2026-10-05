# FLASHCARDS — Searching Track
> ~60 rows. Track `searching`.

| # | Front | Back |
|---|---|---|
| 1 | Binary bound | O(log n) |
| 2 | Safe mid | (lo+hi)>>>1 |
| 3 | Interval | [lo,hi) half-open |
| 4 | lowerBound | first ≥ x |
| 5 | upperBound | first > x |
| 6 | Exact hit | lb if a[lb]==x |
| 7 | Count of x | ub - lb |
| 8 | Empty done | lo==hi |
| 9 | Progress | hi-lo shrinks |
| 10 | Rotated insight | one half sorted |
| 11 | Rotated dupes | O(n) worst |
| 12 | Peak move | toward higher |
| 13 | Peak edge | ends valid |
| 14 | Answer-search | monotonic predicate |
| 15 | Ship lo/hi | max .. sum |
| 16 | Koko predicate | hours ≤ H |
| 17 | Interpolation avg | O(log log n) |
| 18 | Interp worst | O(n) skewed |
| 19 | Exponential | O(log pos) |
| 20 | T(n)=T(n/2)+1 | Θ(log n) |
| 21 | Master a=1 | case 2 |
| 22 | Info lower bound | ⌈log₂(n+1)⌉ |
| 23 | Linear scan | O(n) unsorted |
| 24 | Sentinel | reduce branches |
| 25 | Arrays.binarySearch | (-(ip)-1) if absent |
| 26 | Collections.BS | same contract |
| 27 | Comparator BS | order + equals consistent |
| 28 | NaN caution | unordered doubles |
| 29 | Bisect left | lowerBound |
| 30 | Bisect right | upperBound |
| 31 | First true | predicate LB |
| 32 | Last false | lb - 1 |
| 33 | Fixed-point | a[i]==i search |
| 34 | Missing positive | variant scan |
| 35 | 2D sorted matrix | staircase O(m+n) |
| 36 | Bitonic max | peak variant |
| 37 | Sqrt(x) int | answer-search |
| 38 | long sums | overflow guard |
| 39 | Recursion space | O(log n) frames |
| 40 | Iterative | O(1) space |
| 41 | Fuzz n | ≤ 12 brute |
| 42 | Benchmark | 1k→10M |
| 43 | Branchless | cmov mid select |
| 44 | Cache | binary jumps miss |
| 45 | Eytzinger | cache-friendly layout |
| 46 | Gallop | exponential runs |
| 47 | Skip ahead | interpolation runs |
| 48 | Pitfall #1 | (lo+hi)/2 overflow |
| 49 | Pitfall #2 | closed-interval ±1 |
| 50 | Pitfall #3 | infinite loop mid=lo |
| 51 | Pitfall #4 | unsorted input |
| 52 | Pitfall #5 | dupes rotated |
| 53 | Pitfall #6 | predicate flip |
| 54 | Amortized batch | sort once O(n log n) |
| 55 | q queries | q log n vs sort+q |
| 56 | Uniform pick | interpolation |
| 57 | Adversarial | skewed kills interp |
| 58 | Trace table | lo/hi/mid each step |
| 59 | Done proof | measure hi-lo → 0 |
| 60 | Interview line | invariant first |
