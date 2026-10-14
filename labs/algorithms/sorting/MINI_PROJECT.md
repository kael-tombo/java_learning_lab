# MINI_PROJECT — Sorting Track
> Benchmark suite across six sorting methods plus quickselect, on random, sorted, reverse, and heavy-dupe inputs to n=1M.

## Inputs
- Generators with fixed seeds: uniform random, sorted, reverse, organ-pipe, and 3-value dupes; sizes 10k/100k/1M.
- Methods: insertion, mergesort (stable), heapsort, quicksort (median-of-3 + insertion cutoff), 3-way quicksort, JDK Arrays.sort, quickselect for k=n/2.

## Build steps
1. Implement each method over int[] with a shared swap/compare counter harness.
2. Verify every output against Arrays.sort on 200 seeded small arrays (correctness gate before timing).
3. Time median-of-3 runs per (method, distribution, size); record ms and comparison counts in results.csv.
4. Plot ASCII bars per distribution showing where quicksort degrades and where 3-way wins on dupes.
5. Document stability (mergesort stable; heapsort/quicksort not) with a paired-key test proving it.

## Acceptance criteria
1. Correctness gate passes 200/200 before any timing row is recorded.
2. results.csv has the header method,dist,n,ms,comparisons with all 7x5x3 combinations filled from real runs.
3. Heavy-dupes column shows 3-way quicksort beating plain quicksort (state the measured factor, whatever it is).
4. Sorted-input column shows insertion sort near-linear behavior with the comparison count to prove it.
5. Stability test demonstrates mergesort keeping paired-key order while heapsort does not (or documents the observed outcome).
6. Write-up states the Omega(n log n) comparison lower bound and which methods meet it in expectation.

## Analysis prompts
1. Which distribution most punishes median-of-3 quicksort, and what does the comparison count show?
2. At what n does insertion sort lose to mergesort on random input on your machine?
3. Why does 3-way partitioning collapse the dupe case to near-linear?

## Non-goals
- External sorting, parallel sorts, and string/radix sorts (named as follow-ups with trigger sizes).

## Reference behavior to reproduce
- Correctness gate first: 200/200 seeded arrays identical to Arrays.sort before any timing cell counts.
- Expected qualitative results: 3-way wins heavy-dupes, insertion wins tiny/sorted, quicksort median-of-3 needs the adversarial test to justify its cutoff.

## Stretch
- Add dual-pivot quicksort (JDK-style) and place it in the results table from real runs.
- Add a comparison-count ceiling test that fails any method exceeding 2x its expected count on random input.
