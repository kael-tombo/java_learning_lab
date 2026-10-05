# FLASHCARDS — Dynamic Programming Track
> ~60 rows. Track `dynamic-programming`.

| # | Front | Back |
|---|---|---|
| 1 | DP cond 1 | optimal substructure |
| 2 | DP cond 2 | overlapping subproblems |
| 3 | fib memo | O(n) |
| 4 | fib naive | Θ(φ^n) |
| 5 | Memo key | all varying params |
| 6 | Base first | before recursion |
| 7 | Grid recurrence | up + left |
| 8 | Obstacle cell | 0 ways |
| 9 | Coin min base | dp[0]=0, INF rest |
| 10 | Ways order | coins outer |
| 11 | 0/1 loop | backward |
| 12 | Unbounded loop | forward |
| 13 | Bound rule | states × trans cost |
| 14 | Tabulation | bottom-up order |
| 15 | Compression | keep lookback rows |
| 16 | Rolling | 2 rows for grids |
| 17 | Reconstruction | parent table |
| 18 | Depth risk | StackOverflow chain |
| 19 | Iterative fix | explicit table |
| 20 | long counts | avoid overflow |
| 21 | INF pick | 1e18, safe add |
| 22 | addExact | overflow trap |
| 23 | computeIfAbsent | memo idiom |
| 24 | -1 sentinel | unknown memo |
| 25 | Reachable only | memo sparsity win |
| 26 | Full table | tabulation cost |
| 27 | Stairs | f(n-1)+f(n-2) |
| 28 | Robber | max(prev,pp+x) |
| 29 | LCS mini | match+1 else max |
| 30 | LIS mini | tails + BS |
| 31 | Kadane mini | cur=max(x,cur+x) |
| 32 | DAG DP | topo = state order |
| 33 | Tree DP | post-order |
| 34 | Digit states | pos/tight/sum |
| 35 | Interval order | by length |
| 36 | Matrix chain | O(n³) |
| 37 | Knapsack | O(nW) |
| 38 | Master 2T+T | n log n |
| 39 | Aggregate | total/n |
| 40 | Accounting | credits pay future |
| 41 | Potential | real + ΔΦ |
| 42 | DSU α | near const |
| 43 | Array push | O(1) amortized |
| 44 | Counter | bit-flip O(1) |
| 45 | Fuzz small | brute n≤12 |
| 46 | Benchmark | 1k→100k |
| 47 | Trace columns | state/decision/OK |
| 48 | Off-by-one | size n+1 |
| 49 | Empty input | identity base |
| 50 | Unreachable | INF/-1 sentinel |
| 51 | Tie policy | any valid + test |
| 52 | Stack→heap | table conversion |
| 53 | Cache locality | row-major loops |
| 54 | Boxed hot loop | avoid Integer |
| 55 | Pitfall #1 | incomplete memo key |
| 56 | Pitfall #2 | missing base |
| 57 | Pitfall #3 | int overflow |
| 58 | Pitfall #4 | forward 0/1 bug |
| 59 | Pitfall #5 | recursion depth |
| 60 | Interview line | invariant first |
