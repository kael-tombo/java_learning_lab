# FLASHCARDS — DP Deep Track
> ~60 rows. Track `dp-deep`.

| # | Front | Back |
|---|---|---|
| 1 | DP condition 1 | optimal substructure |
| 2 | DP condition 2 | overlapping subproblems |
| 3 | Knapsack 0/1 loop | backward c |
| 4 | Knapsack unbound loop | forward c |
| 5 | Knapsack bound | O(nW) pseudo-poly |
| 6 | LCS recurrence | match +1 else max |
| 7 | LCS time | O(mn) |
| 8 | LCS space opt | O(min(m,n)) |
| 9 | Edit ops | insert/delete/replace |
| 10 | LIS naive | O(n²) |
| 11 | LIS fast | tails + BS O(n log n) |
| 12 | lowerBound | first ≥ x |
| 13 | upperBound | first > x |
| 14 | Kadane | cur=max(x,cur+x) |
| 15 | Kadane all-neg | max element |
| 16 | Matrix chain | O(n³) intervals |
| 17 | Interval order | by length |
| 18 | Knuth needs | quad + monotonicity |
| 19 | Knuth bound | O(n²) |
| 20 | D&C opt | monotonic opt |
| 21 | CHT | lines min query |
| 22 | Li Chao | dynamic lines |
| 23 | Tree DP order | post-order |
| 24 | Reroot | two passes |
| 25 | Diameter trick | two BFS/DFS or DP |
| 26 | Digit states | pos/tight/sum |
| 27 | Tight=1 | bounded by prefix |
| 28 | Memo tight | only tight=0 |
| 29 | Leading zeros | flag/policy |
| 30 | Coin change ways | outer coins inner amt |
| 31 | Coin min coins | dp[0]=0, INF rest |
| 32 | Climb stairs | f(n)=f(n-1)+f(n-2) |
| 33 | LIS vs LCS | patience vs 2D |
| 34 | Reconstruction | parent table |
| 35 | Rolling rows | keep 2 rows |
| 36 | 1D vs 2D | order guards reuse |
| 37 | DAG DP | topo order = states |
| 38 | Bitmask DP | O(n²2^n) TSP |
| 39 | Profile DP | plug/tiling states |
| 40 | Aliens trick | Lagrangian param |
| 41 | Knuth opt range | opt[i][j-1]..opt[i+1][j] |
| 42 | Monge | quadrangle source |
| 43 | Convex cost | D&C eligible |
| 44 | Slope trick | convex piecewise |
| 45 | Master 2T(n/2)+n | Θ(n log n) |
| 46 | Master 7T(n/2)+n² | Θ(n^2.81) |
| 47 | Amortized push | O(1) |
| 48 | Φ method | real + ΔΦ |
| 49 | Overflow guard | long/addExact |
| 50 | INF choice | 1e18, no +overflow |
| 51 | Off-by-one | dp size n+1 |
| 52 | Empty base | dp[0]=identity |
| 53 | Fuzz oracle | brute n≤12 |
| 54 | Benchmark sizes | 1k→100k |
| 55 | Pitfall #1 | forward 0/1 reuse bug |
| 56 | Pitfall #2 | tight memo leak |
| 57 | Pitfall #3 | recursion depth |
| 58 | Pitfall #4 | int overflow totals |
| 59 | Pitfall #5 | wrong interval order |
| 60 | Interview line | invariant first, then code |
