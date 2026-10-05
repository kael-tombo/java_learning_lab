# MINI_PROJECT — Recursion: Call-Tree Visualizer + Depth Lab
> Implement + benchmark + visualize. ~3 hours.

## Goal
Visualize naive-fib call tree vs memo DAG, measure the 40× cliff, and prove depth
limits with a countdown-to-overflow experiment + iterative fallback.

## Build Steps
1. `TreeViz.java`: instrumented fib (call ids, depth) emitting ASCII tree for n=5.
2. Counters: naive calls vs memo states; assert memo states == n+1-ish.
3. Benchmark: n=10..45 naive vs memo/tab timings (log-scale table).
4. Depth: countdown 10³..10⁶, catch StackOverflowError, record max depth.
5. Fallback: iterative versions pass at 10⁶ (mod) where recursion dies.

## Benchmark Table (fill)
| n | naive ms/calls | memo ms/states | tab ms |
|---|----------------|----------------|--------|
| 20 | | | |
| 30 | | | |
| 40 | | | |

## Visualize
```
fib(4)─┬fib(3)─┬fib(2)…
       └fib(2)* (memo: * = reused, no subtree)
```

## Acceptance
- [ ] Tree vs DAG diagrams included. [ ] Overflow depth recorded.
- [ ] Iterative passes where recursive fails (evidence).

## Extensions
- Fast-doubling O(log n) at n=10⁶ (mod) comparison.
