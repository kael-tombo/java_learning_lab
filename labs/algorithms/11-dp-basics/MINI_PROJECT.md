# MINI_PROJECT — DP Basics: Three-Forms Lab + Cliff Demo
> Implement + benchmark + visualize. ~2 hours.

## Goal
Ship naive/memo/tab/mod in one file, print dp tables, and demo the exponential cliff +
overflow + depth lessons with numbers.

## Build Steps
1. `Forms.java`: all four + call/state counters.
2. Visualize: call tree excerpt (n=5) + `dp=[1,1,2,3,5,8]` row print.
3. Benchmark: n=10..45 table (naive to timeout vs memo/tab instant).
4. Overflow: fib(47) int vs long vs mod(100) exact values asserted.
5. Depth: memo at 10⁴ (overflow expected) vs tab pass — record.

## Benchmark Table (fill)
| n | naive ms/calls | memo ms | tab ms | mod ms |
|---|----------------|---------|--------|--------|
| 20 | / | | | |
| 30 | / | | | |
| 40 | / | | | |

## Visualize
```
naive tree(5): 15 nodes  vs  memo states: 6  (saved=9)
```

## Acceptance
- [ ] Cliff table + depth evidence included.
- [ ] Mod value for fib(100) asserted (354224848).

## Extensions
- Fast-doubling at 10⁶ (mod) one-liner comparison.
