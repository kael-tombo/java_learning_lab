# MINI_PROJECT — DFS: Structure Explorer (Cycles/Orders/Components)
> Implement + benchmark + visualize. ~3 hours.

## Goal
Build a DFS explorer printing discovery/finish times, parenthesis nesting, cycle verdict,
and topo order on DAGs; compare DFS vs BFS on deep maze.

## Build Steps
1. `Explore.java`: recursive + iterative DFS, 3-color cycle check, times.
2. Visualize: ASCII stack per step (`[1→2→3]`) + interval diagram `1:[1,6] 2:[2,5]`.
3. Topo: reverse-postorder on course DAG; Kahn cross-check validity.
4. Benchmark: deep chain 10⁵ (recursive overflows vs iterative passes) + timings.
5. Fuzz: random digraphs, cycle verdict agrees with Kahn-leftover.

## Benchmark Table (fill)
| graph | recursive | iterative | cycle agree? |
|-------|-----------|-----------|--------------|
| chain 10⁵ | OVERFLOW | ms= | — |
| random 10³ | | | 100% |

## Visualize
```
push 1 [1] push 2 [1,2] pop 2 [1] … postorder: 3,2,1
```

## Acceptance
- [ ] Interval nesting holds (assert no partial overlap).
- [ ] Directed vs undirected cycle suites correct.
- [ ] Overflow evidence + iterative fix recorded.

## Extensions
- Kosaraju SCC count on top (preview).
