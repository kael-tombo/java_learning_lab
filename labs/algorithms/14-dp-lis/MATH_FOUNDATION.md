# Math Foundation: LIS Bounds, Binary Search, Patience
> O(n^2) DP counting, the O(n log n) tails argument, binary search halving.

## Definitions
- dp[i]: LIS length ending exactly at position i (1 + best compatible predecessor).
- tails[k]: minimal possible tail of an increasing subsequence of length k+1.
- Binary search over tails: first index with value >= x (lower bound).
- Strict semantics: equals never extend; the search variant encodes this.

## Counting argument
- O(n^2) version: n states, each scanning up to n predecessors at O(1) each.
- Total Theta(n^2) worst case; sorted-ascending input attains it (all pairs compatible).
- Tails version: n placements, each one binary search over at most n piles.
- Total Theta(n log n); descending input still pays all n searches.

## Recurrence
- dp[i] = 1 + max{dp[j] : j < i, a[j] < a[i]}, or 1 if the set is empty.
- Answer max_i dp[i]; the recurrence is a DAG longest path (edges j -> i).
- Tails update: pos = lower_bound(tails, x); tails[pos] = x (or append).
- Binary search recurrence T(k) = T(k/2) + O(1) = Theta(log k).

## Derivation of the bound
- Halving argument: each step discards half the remaining pile range.
- After ceil(log2 n) + 1 steps one candidate remains: Theta(log n) per element.
- Tails sortedness invariant makes binary search applicable at every step.
- Replacement safety: lowering a tail preserves all future extensions (subset argument).

## Worked mini-proofs
- Proof 1: binary search takes Theta(log n) by the halving count. (3 lines)
- Proof 2: tails stays sorted by the minimal-tail definition per length. (4 lines)
- Proof 3: replacement never destroys extendability (old tail >= new tail). (4 lines)

## Exercises with answers
- 1. LIS length of 3 1 2 8 6 7 4 5. Answer: 4.
- 2. Tails after processing 3 1 2. Answer: [1, 2].
- 3. Why does tails length equal LIS length? Answer: appends happen exactly on extensions.

## Pitfalls
- Binary search variant (first->= vs first->) mismatched with strictness.
- Reading the subsequence from tails instead of parent pointers.
- Quoting O(n log n) while actually coding the O(n^2) predecessor scan.

## Checklist
- Derive both bounds from states-times-transitions and search-per-element.
- State the tails invariant and prove replacement safety.
