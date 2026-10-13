# Theory: Sliding Windows and Amortized Linearity
> Fixed and variable windows over arrays and strings with at-most-once pointer moves.

## Problem statement
- Fixed window: all subarrays of size k (max sum, averages).
- Variable window: longest/shortest subarray satisfying a content predicate (repeat-free, sum bound).
- Window [l..r] with incremental state (sum, frequency map) updated at both ends.
- Goal: O(n) total by moving each pointer at most n steps.

## Fixed windows
- Seed sum of a[0..k-1]; slide: add a[r+1], subtract a[l], advance both.
- Each step O(1); total O(n) time, O(1) space for n-k+1 windows.
- Correctness: the maintained sum always equals the current window by induction on slides.
- All-negative series work unchanged; the maximum is simply the least bad window.

## Variable windows (longest repeat-free substring)
- Expand r; while s[r] repeats inside, advance l past the previous occurrence.
- Last-seen map gives the shrink target in O(1); best bounds update on every expansion.
- Invariant: window is always repeat-free when the best update runs.
- "abba" trap: l = max(l, last+1) so l never moves backward.

## Amortized analysis
- l and r each advance at most n times over the run: at most 2n pointer moves.
- Inner shrink loops look nested but charge against l's forward progress (aggregate method).
- Total O(n) time with O(1) or O(alphabet) space depending on the state kept.
- Counters on visits verify the bound empirically.

## Shrinkable constraints
- Pattern needs a predicate where shrinking can restore validity (repeat-free, at-most-K).
- longest-with-property uses expand-then-shrink-while-invalid; shortest uses shrink-while-valid.
- Non-shrinkable predicates (median conditions, exact-once-everywhere) break the pattern.
- Naming the predicate and its shrink step is the design work of each new problem.

## Complexity derivation
- Fixed: n-k+1 windows times O(1) = Theta(n) time, Theta(1) space.
- Variable: 2n moves times O(1) updates = Theta(n) time, map space for frequencies.
- Rescanning the window per step would revert to Theta(n^2) - the incremental state prevents it.
- Alphabet-bounded maps (ASCII 128) keep space effectively constant.

## Variants
- At-most-K-distinct: same skeleton with a distinct-count validity predicate.
- Minimum window covering: shrink-while-valid with best tracking on the valid side.
- Deque-based sliding maximum: same window shape, stronger data structure.

## Pitfalls
- Letting l move backward via unguarded last-seen assignment.
- Recomputing window state from scratch each step (silent quadratic).
- Stale best bounds updated only on expansion in shortest-window problems.
- k = 0 or k > n handled as answers instead of errors.

## Interview signal
- Prove the 2n bound by counting pointer moves, not by gesturing at loops.
- State the window invariant and the shrink step for longest-unique.
- Classify a new problem as fixed vs variable window with reasons.
