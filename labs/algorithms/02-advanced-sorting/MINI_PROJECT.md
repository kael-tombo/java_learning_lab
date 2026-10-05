# MINI_PROJECT — Advanced Sorting: Engine + Benchmark + Visualize
> Implement + benchmark + visualize. ~4 hours.

## Goal
Build `SortEngine` (quick-shuffle + 3-way + merge + heap) with counters, ASCII partition
diagram, and a benchmark proving `n log n` scaling + quick-worst avoidance.

## Build Steps
1. Implement quick (shuffle, Lomuto + 3-way), merge (buffer-once), heap.
2. Counters: comparisons, swaps/copies, max depth.
3. Visualize: print pivot + `L|p|G` split per partition on n=16.
4. Benchmark: n=10k..160k doubling; distributions random/sorted/duplicates.
5. Worst demo: quick-no-shuffle on sorted 20k (timeout/4× vs shuffle) — record.

## Benchmark Table (fill)
| n | quick ms | 3-way-dup ms | merge ms | heap ms | ratio |
|---|----------|--------------|----------|---------|-------|
| 10000 | | | | | — |
| 20000 | | | | | ~2.1 |
| 40000 | | | | | ~2.1 |
| 80000 | | | | | ~2.1 |

## Visualize
```
pivot=5 L=[2,1,3] p[5] G=[9,7,8] depth=2
```

## Acceptance
- [ ] Ratios ~2.1 (linearithmic), not 4×.
- [ ] Sorted-input disaster demoed + fixed by shuffle (numbers).
- [ ] 3-way wins all-duplicates ≥5× vs Lomuto.

## Extensions
- Insertion cutoff sweep (8/16/32) — best cutoff reported.
- `Arrays.sort` parity check on 10⁵ random.
