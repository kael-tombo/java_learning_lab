# Math Foundation: Amortized 2n and Map Accounting
> Aggregate pointer moves, O(1) window updates, fixed vs variable cost models.

## Definitions
- Window [l..r]; state: sum, frequency map, validity predicate.
- Expand: r++ with state add; shrink: l++ with state remove.
- Visit: pointer landing on an index; budget 2n total across both pointers.
- Shrinkable predicate: shrinking can restore validity (repeat-free, at-most-K).

## Counting argument
- l advances <= n times, r advances <= n times: <= 2n moves total.
- State updates O(1) amortized per move (hash ops, sum add/subtract).
- Total Theta(n) time; space O(1) for sums, O(alphabet) for frequency maps.
- Fixed windows: exactly n-k+1 slides at O(1): Theta(n) with no amortization needed.

## Recurrence
- Iterative, not recursive: progress measured by (l, r) lexicographic advance.
- Best-answer updates ride on expansion (longest) or valid shrinks (shortest).
- Last-seen map jumps l forward past repeats in O(1) per distinct char.
- Guard l = max(l, last+1) keeps monotonicity (the abba fix).

## Derivation of the bound
- Aggregate: every inner-shrink iteration advances l; l advances <= n times.
- Outer loop advances r <= n times: total iterations O(n) despite nesting.
- Map ops assumed O(1) average; worst-case hash pathologies noted, not analyzed here.
- Rescan-per-step variants would pay Theta(n^2): the incremental state is the difference.

## Worked mini-proofs
- Proof 1: aggregate 2n bound from monotone domains. (3 lines)
- Proof 2: window-sum correctness by induction on slides. (3 lines)
- Proof 3: repeat-free invariant maintenance with last-seen jumps. (4 lines)

## Exercises with answers
- 1. Moves bound for n = 10^6. Answer: at most 2 x 10^6 pointer moves.
- 2. Longest repeat-free length of abcabcbb. Answer: 3.
- 3. Fixed max-sum-k for [2,1,5,1,3,2], k = 3. Answer: 9 (windows 5+1+3).

## Pitfalls
- Backward l moves breaking the charging argument silently.
- Stale best values in shortest-window variants (update on the wrong side).
- Non-shrinkable predicates forced into the pattern anyway.

## Checklist
- Prove 2n by aggregate method without notes.
- State the guard that keeps l monotone and why it is needed.
