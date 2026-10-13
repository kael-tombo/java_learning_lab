# Vision: Longest Increasing Subsequence
> 1D DP over sequences plus the patience-sorting speedup to O(n log n).

## Where this leads
- Envelope nesting, box stacking, and patience-sorting applications.
- The tails-array technique: maintaining candidate endings with binary search.
- Reading a problem as longest-something-subsequence, a recurring interview shape.
## What mastering it unlocks
- Write the O(n^2) recurrence dp[i] = 1 + max dp[j] over j < i with a[i] > a[j].
- Maintain the tails array and explain why each entry is the smallest possible ending.
- Reconstruct one LIS with parent pointers, and explain why tails alone cannot do it.
- Reduce envelope nesting to LIS by sorting correctly, including the tie rule.
- Argue the O(n log n) bound from binary search per element.
## What it does not cover
- Longest common subsequence (two strings, not one) - that is the 13-dp-lcs lab.
- Longest increasing contiguous subarray, which is a different and easier problem.
- Counting all distinct LIS instances, which needs extra care with duplicates.
## Core questions you will answer
- Why is tails[k] the smallest possible tail of an increasing subsequence of length k+1?
- Why must equal widths sort height descending in the envelope reduction?
- Why does replacing tails[pos] never destroy a future extension?
- When is the O(n^2) version preferable to the O(n log n) one?
## How to judge progress
- Code both versions from memory and cross-check them on random small inputs.
- Explain the tie rule in the envelope reduction without hand-waving.
- Reconstruct an LIS, not just its length, on a 10-element example.
## Common misuse
- Returning tails.length as the answer while believing tails holds the subsequence.
- Using strictly-less binary search variants inconsistently for equal elements.
## After this lab
- 13-dp-lcs for the two-sequence counterpart of this lab.
- 12-dp-knapsack for DP over capacities instead of positions.
One-line self-test: Explain in one paragraph why tails stays sorted throughout the scan.
