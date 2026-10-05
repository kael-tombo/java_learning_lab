# MINI_PROJECT — Searching Overview: Retrieval Shootout
> Implement + benchmark + visualize. ~3 hours.

## Goal
Shootout: linear vs binary vs `HashSet` on 3 workloads (one-shot, repeated-query,
mutating); visualize interval-halving; recommend per workload with numbers.

## Build Steps
1. One codebase, three adapters + `Collections.binarySearch` parity.
2. Workloads: A) 1 query/unsorted B) 10⁴ queries/sorted C) 50% inserts + queries.
3. Visualize: binary interval trace `[lo,hi) mid=v` per probe (n=15 demo).
4. Benchmark table + workload-winner matrix.
5. Mutation test: sorted-array insert cost vs `TreeSet`/`HashSet`.

## Benchmark Table (fill)
| workload | linear | binary (+sort amort) | hash | winner |
|----------|--------|----------------------|------|--------|
| A one-shot | | — | | linear |
| B 10k queries | | | | binary/hash |
| C mutating | | | | hash/tree |

## Visualize
```
[0,15) mid=7=43 <k → [8,15) mid=11=78 >k → [8,11) …
```

## Acceptance
- [ ] Interval trace shrinks every probe (assert). [ ] Winner differs by workload.
- [ ] Sort-amortization math shown for B (sort/q).

## Extensions
- Interpolation on uniform data; Bloom + binary fallback.
