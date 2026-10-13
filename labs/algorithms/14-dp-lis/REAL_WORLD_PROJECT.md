# Real-World Project: Patience Analyzer for Sequences
> LIS length, reconstruction, and pile visualization for integer sequences.

## Problem
Given delivery-time or score sequences, find the longest improving run and show it.
The tool teaches both the O(n^2) DP and the O(n log n) patience method on the same data.
## Inputs
- sequences.txt with one space-separated integer sequence per line (length up to 5000).
- Mode flag: length-only, reconstruct, or piles (show patience piles).
- Fixture file with 6 sequences and expected lengths plus one expected reconstruction.
## Steps
1. Parse each line into an integer array, rejecting non-integer tokens with line numbers.
2. Compute LIS length with the O(n^2) DP as the reference implementation.
3. Compute LIS length with tails plus binary search as the fast implementation.
4. Assert both lengths agree on every input before printing anything.
5. Reconstruct one LIS with parent pointers from the O(n^2) table.
6. Print length, one LIS, and (in piles mode) the pile tops per element.
## Acceptance criteria
- All 6 fixtures report the expected lengths, including duplicates-heavy cases.
- Reference and fast lengths agree on 200 random fixed-seed sequences.
- Reconstruction output is strictly increasing and a subsequence of the input.
- Length-5000 decreasing input finishes both methods in under 3 seconds.
- Empty line input reports length 0 without errors.
## Failure modes
- Non-integer tokens fail with the exact line number, never a silent skip.
- Strictly-increasing semantics are documented and tested (equal values do not extend).
- Memory stays at two arrays; the full table is only built in reconstruct mode.
## Extensions
- Envelope-nesting mode: read (w,h) pairs and apply the sort-plus-LIS reduction.
- Count of distinct LIS values via DP extension (documented, tested on small inputs).
## How to demo
- Show piles mode on a 12-element sequence and explain each placement.
- Show the agreement check output on the random batch.
