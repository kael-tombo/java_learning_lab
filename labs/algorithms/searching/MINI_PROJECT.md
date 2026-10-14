# MINI_PROJECT — Searching Track
> Search-method shootout on sorted arrays, hash tables, and BSTs: binary, exponential, interpolation, hash lookup, and tree search with hit/miss splits.

## Inputs
- Sorted int arrays (n = 10k/100k/1M, fixed seeds) plus 50/50 present/absent query batches of 10k keys.
- Uniform vs skewed (zipf-like) query distributions to stress interpolation search honestly.
- Hash table at load factors 0.5/0.75/0.95 with open addressing; BST built by random insertions.

## Build steps
1. Implement binary search (half-open intervals), exponential search (range-find then binary), and interpolation search with a division-by-zero guard.
2. Build the hash table with documented probe counting and the BST with height tracking.
3. Time 10k-query batches split into hit Avg and miss Avg per (method, n, distribution); record comparisons/probes alongside ms.
4. Demonstrate interpolation collapse on skewed keys (report the measured probe inflation, whatever it is).
5. Document the load-factor effect: probe counts at 0.5 vs 0.95 from real runs.

## Acceptance criteria
1. All methods return identical hit/miss answers to Arrays.binarySearch on the same batches (or document the deliberate semantic difference).
2. Results table has hit and miss columns separately; no blended averages hiding miss cost.
3. Interpolation guard test (constant-slope segment) passes without division errors.
4. Load-factor table shows probe growth from real runs at all three factors.
5. BST height recorded per n beside the measured search time (no height claim without the number).
6. Write-up states binary O(log n), interpolation expected O(log log n) under uniformity, hash expected O(1), BST O(h).

## Analysis prompts
1. Where does exponential search beat plain binary, in cache terms?
2. How far does skew push interpolation from its uniform-case bound?
3. At what load factor does open addressing stop being worth it on your runs?

## Non-goals
- Full-text and fuzzy search, learned indexes, and concurrent hash tables (each named with its trigger).

## Hit/miss numbers to reproduce
- Binary search on 1M ints must land near 20 comparisons per query; record yours beside the theory.
- Expected qualitative results: interpolation shines on uniform and inflates on skew; open addressing degrades past 0.9 load.

## Stretch
- Add jump search (block size sqrt(n)) and place its measured comparisons between linear and binary.
- Add a Bloom prefilter in front of the miss batch and measure skipped probes vs filter cost.
