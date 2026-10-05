# MINI_PROJECT — Linear Searching: Scan Bench + Visualize
> Implement + benchmark + visualize. ~2 hours.

## Goal
Compare linear scan vs sentinel vs parallel-stream on unsorted arrays; visualize probe
positions; find the n where sorting-once + binary search breaks even for q queries.

## Build Steps
1. `ScanBench.java`: loop, sentinel, `IntStream` variants with probe counters.
2. Datasets: n=10³..10⁶ random; key positions 0/mid/end/absent.
3. Visualize: probe tape `*` marks, e.g. `[. . * .]` hit at 2 after 3 probes.
4. Benchmark: best-of-5 per cell; plot probes vs n (linear fit).
5. Break-even: `sortCost + q·log n` vs `q·n/2` → solve q* for n=10⁵.

## Benchmark Table (fill)
| n | hit-0 ms | hit-mid ms | absent ms | probes-absent |
|---|----------|------------|-----------|---------------|
| 1k | | | | 1000 |
| 10k | | | | 10000 |
| 100k | | | | 100000 |

## Visualize
```
a=[5,2,9,2] k=2 probes: i=0(×) i=1(✓) → 1
```

## Acceptance
- [ ] Absent-probes == n (exact). [ ] Best/avg/worst ordering holds in timings.
- [ ] q* break-even computed + stated (e.g., q*>~17 for n=10⁵).

## Extensions
- Branch-miss note: sorted-vs-random key order timing.
- Bloom prefilter sketch for absent-heavy workload.
