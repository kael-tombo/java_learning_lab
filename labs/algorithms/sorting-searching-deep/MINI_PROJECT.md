# MINI_PROJECT — Sorting and Searching Deep Track
> Advanced selection and integer-key structures: worst-case-linear select, suffix-array doubling, k-way external merge, and van Emde Boas on bounded universes.

## Inputs
- Adversarial arrays for quickselect (organ-pipe + crafted pivots), random texts to 100k chars for suffix work, and integer sets in universe U = 2^16 for vEB.
- External-merge spill files: 4 sorted runs of 250k ints each on disk.

## Build steps
1. Implement median-of-medians select (groups of 5) and verify against sorting on 500 seeded arrays including adversarial ones.
2. Implement suffix-array doubling (O(n log n)) and verify banana -> [5,3,1,0,4,2] plus agreement with naive sorting on random strings.
3. Implement 4-way external merge over the spill files with a heap; verify byte-equality with in-memory sort.
4. Implement a small van Emde Boas layout over U = 2^16 (or a documented y-fast-trie-style simplification, labeled as such) and verify member/successor against TreeSet.
5. Record time and comparison/op counts per method with machine/JDK noted.

## Acceptance criteria
1. Median-of-medians agrees with sorting on all 500 arrays; adversarial quickselect-killer input included in the set.
2. Doubling suffix array matches naive order on all random-string tests including banana.
3. External merge output is byte-identical to in-memory sort of the concatenated runs.
4. vEB successor queries match TreeSet on 10k seeded operations (or the labeled simplification documents its exact deviation).
5. Results table states measured time plus operation counts; no bound quoted without its measurement beside it.
6. Write-up states select Omega(n) (must read all input) vs the O(n) worst-case median-of-medians guarantee.

## Analysis prompts
1. How large is the median-of-medians constant vs sorting at n = 10k on your runs?
2. Which doubling round dominates suffix-array time, and why?
3. At what run size does external merge beat in-memory sort on your machine (or why never, if RAM suffices)?

## Non-goals
- Full y-fast tries, fusion trees, and cache-oblivious sorting (named with papers-level pointers, not built).

## Oracle agreements to reproduce
- Banana must reproduce sa [5,3,1,0,4,2] through the doubling implementation, not just the naive one.
- Median-of-medians must survive the quickselect-killer input with linear scaling while plain quickselect degrades.

## Stretch
- Implement SA-IS or prefix-doubling with radix phases and compare build time against plain doubling.
- Add a cache-miss counter (perf-based, documented as machine-specific) for the select methods.
