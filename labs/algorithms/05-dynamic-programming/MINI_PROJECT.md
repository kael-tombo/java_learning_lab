# MINI_PROJECT — DP Overview: State-Design Studio
> Implement + benchmark + visualize. ~4 hours.

## Goal
Solve 3 DPs (Fib, LIS, 0/1-knapsack-lite) with memo+tab, state tables printed,
and a scaling wall demo (W-blowup) with alternative named.

## Build Steps
1. `Studio.java`: fib (3 forms), LIS O(n log n), knapsack 1-D + 2-D value.
2. Visualize: print dp rows for ways(6) + knapsack 4×6 table (circle takes).
3. Benchmark: fib 40 cliff; LIS n=10³ (O(n²) vs O(n log n)); knapsack W sweep.
4. Wall: W=10³→10⁷ at fixed n (time/memory curve); declare infeasible point.
5. Cross-check: memo==tab values on 50 random instances per problem.

## Benchmark Table (fill)
| task | naive/O(n²) | optimized | states | verdict |
|------|-------------|-----------|--------|---------|
| fib40 | | | | memo/tab win |
| LIS 10⁴ | | | | n log n wins |
| knap W sweep | | | | wall at W≈… |

## Visualize
```
dp ways: [1,1,2,3,5,8,13]
knap row i=2: [0,0,3,4,4,7]
```

## Acceptance
- [ ] Tables printed + direction comments. [ ] Wall point stated with alternative.
- [ ] 150/150 cross-checks green.

## Extensions
- Reconstruction for LIS (parent pointers) + FPTAS note.
