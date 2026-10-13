# Theory: Longest Increasing Subsequence
> 1D DP over positions plus the patience-sorting speedup to O(n log n).

## Problem statement
- Input: array a[0..n-1] of comparable elements.
- Output: length of the longest strictly increasing subsequence, plus one such subsequence.
- Subsequence (order kept, contiguity not required) vs subarray (contiguous): different problems.
- Edge cases: empty gives 0; all-equal gives 1 under strict semantics.

## Recurrence (O(n^2) version)
- dp[i] = 1 + max dp[j] over j < i with a[j] < a[i]; dp[i] = 1 if no such j exists.
- Answer is max over i of dp[i], not dp[n-1]: the best subsequence can end anywhere.
- Parent[i] = argmax j gives reconstruction by walking back from the argmax i.
- Time O(n^2) from n states times O(n) transitions; space O(n).

## Tails method (O(n log n) version)
- Maintain tails[k] = smallest possible tail of an increasing subsequence of length k+1.
- For each x: binary-search the first tails entry >= x, replace it (or append if none).
- Replacement is safe: it only lowers a tail, which can never hurt future extensions.
- tails stays sorted because each entry is a minimal tail for its length class.

## Worked trace
- a = 3 1 2 8 6 7 4 5. tails evolves: [3], [1], [1,2], [1,2,8], [1,2,6], [1,2,6,7], [1,2,4,7], [1,2,4,5].
- Final length 4 (example LIS: 1 2 4 5); note tails itself is not the subsequence.
- Each step touches one binary search; total O(n log n) time, O(n) space.

## Correctness argument
- Invariant: after processing a prefix, tails[k] is minimal over that prefix - induction on steps.
- Binary search position pos means x extends length pos and beats the old tail there.
- Appending happens exactly when x extends the longest length seen so far.
- Strictness: first->= keeps equals from extending, matching strict LIS semantics.

## Complexity derivation
- O(n^2) version: n states, up to n transitions each, O(1) per transition.
- Tails version: n elements times Theta(log n) binary search = Theta(n log n).
- Reconstruction needs parent pointers (O(n) space); tails alone cannot rebuild the sequence.
- Sorting-based reductions (envelopes) add their O(n log n) sort on top.

## Variants
- Envelopes: sort width asc, height desc for ties, then LIS on heights.
- Non-decreasing variant: binary search first-> instead, with semantics stated up front.
- Counting distinct LIS: extra DP layer, valid only with duplicate handling.

## Pitfalls
- Returning tails content as the subsequence instead of its length.
- Ascending-tie sort in envelopes, letting equal widths nest illegally.
- Mixing strict and non-strict binary search across the two methods.
- Forgetting the answer is max dp[i], then returning dp[n-1].

## Interview signal
- Prove the tails invariant and the safety of replacement in two sentences.
- Explain the envelope tie rule from the nesting definition.
- State why reconstruction needs parents beyond tails.
