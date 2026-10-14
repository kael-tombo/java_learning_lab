# MINI_PROJECT — Dynamic Programming Track
> Core DP bench: LIS, LCS/edit distance, 0/1 knapsack, coin change, rod cutting, matrix chain, and DAG shortest paths with reconstruction.

## Inputs
- Fixed checks: LIS of [10,9,2,5,3,7,101,18] is 4; edit distance kitten->sitting is 3; knapsack (weights/values documented in code) verified against brute force at n <= 20.
- Random strings (len 50/200) and knapsack instances (n=30/100, W scaled) with fixed seeds for timing.

## Build steps
1. Implement LIS two ways (O(n^2) DP and O(n log n) patience) and assert agreement on 300 seeded arrays.
2. Implement LCS/edit-distance O(nm) with backpointer reconstruction; verify kitten->sitting = 3 with the alignment printed.
3. Implement 0/1 knapsack O(nW) plus brute-force oracle for n <= 20; verify agreement on 100 instances.
4. Implement coin change (min coins + count ways), rod cutting, matrix-chain O(n^3), and DAG shortest path O(V+E).
5. Record time and table sizes; note where the O(nW) knapsack is pseudo-polynomial in one paragraph.

## Acceptance criteria
1. LIS=4 and edit-distance=3 reproduce exactly with reconstructions shown.
2. Knapsack DP agrees with brute force on all 100 small instances.
3. Patience LIS agrees with O(n^2) LIS on all 300 arrays.
4. Matrix-chain prints the optimal parenthesization cost plus split table on the reference instance in code.
5. Timing table covers strings 50/200 and knapsack 30/100 from real runs with table sizes recorded.
6. Pseudo-polynomial paragraph correctly distinguishes n from W with a concrete bit-length example.

## Analysis prompts
1. Which DP table fills dominate runtime, and what does the shape say about cache behavior?
2. Where does reconstruction cost show up relative to value computation?
3. What breaks first if W grows 100x at fixed n (knapsack)?

## Non-goals
- Tree/digit/bitmask DP (dp-deep track), approximation schemes, and DP optimizations (Knuth/D&C) beyond naming.

## Reference values to reproduce
- LIS=4 with the subsequence named; edit-distance=3 with the alignment printed, not just the number.
- Knapsack DP must match brute force on all 100 small instances before the timing table counts.

## Stretch
- Add space-optimized edit distance (two rows) with reconstruction via divide-and-conquer (Hirschberg), verified on the 200-length pair.
- Add unbounded knapsack and document exactly which loop order changes and why.
