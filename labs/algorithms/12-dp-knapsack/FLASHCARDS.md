# FLASHCARDS — 0/1 Knapsack (~60)
> Rapid recall: front → back. Cover recurrence, complexity, when-to-use.

| # | Front | Back |
|---|-------|------|
| 1 | 0/1 recurrence? | max(skip, take once) |
| 2 | Formula? | dp[i][w]=max(prev, prev[w-wi]+vi) |
| 3 | Bases? | dp[0][*]=0 |
| 4 | Answer cell? | dp[n][W] |
| 5 | Time? | O(nW) pseudo-poly |
| 6 | Space 2-D? | O(nW) |
| 7 | Space 1-D? | O(W) |
| 8 | 1-D direction? | descending |
| 9 | Ascending =? | unbounded (bug for 0/1) |
| 10 | 1-D invariant? | dp[w-wi] still prev-row |
| 11 | 2-D invariant? | first-i optimum |
| 12 | Reconstruct needs? | full table / take flags |
| 13 | Take condition? | dp[i][c]!=dp[i-1][c] |
| 14 | W=0? | 0 |
| 15 | Empty items? | 0 |
| 16 | wi>W? | skip |
| 17 | wi=0,vi>0? | always take (guard) |
| 18 | Example best? | 7 for (2,3)(3,4)(4,5) W5 |
| 19 | Chosen set? | items 0,1 |
| 20 | Fractional algo? | greedy ratio O(n log n) |
| 21 | Greedy 0/1? | fails (counter-exists) |
| 22 | Trap instance? | W50 ratio vs optimal gap |
| 23 | Unbounded loop? | ascending correct there |
| 24 | Pseudo means? | poly in W, exp in logW |
| 25 | NP-hard? | yes (no poly in n+logW) |
| 26 | Huge W? | meet-middle / FPTAS |
| 27 | Meet-middle n? | ≤34 |
| 28 | Small n? | brute 2ⁿ |
| 29 | Fractional proof? | exchange argument |
| 30 | 0/1 proof? | skip/take induction |
| 31 | Java table? | int[n+1][W+1] |
| 32 | Overflow? | guard near MAX |
| 33 | Validate? | Σw≤W, Σv==report |
| 34 | Brute check n? | ≤20 random |
| 35 | 1-D==2-D? | values equal |
| 36 | Ascending ≥? | over-count demo |
| 37 | Negative w? | invalid → throw |
| 38 | Negative W? | throw |
| 39 | Tie reconstruct? | either valid |
| 40 | Zero-weight loop? | handle before DP |
| 41 | Capacity units? | integers required |
| 42 | Real weights? | scale/discretize or FPTAS |
| 43 | Use case? | cargo / budget pack |
| 44 | When NOT? | W huge / fractional |
| 45 | Unbounded example? | coin change max |
| 46 | Fractional example? | gold dust |
| 47 | 2-D rows meaning? | prefix of items |
| 48 | Cols meaning? | capacities 0..W |
| 49 | Transition cost? | O(1) |
| 50 | States count? | n(W+1) |
| 51 | Recursion form? | dfs(i,rem) memo |
| 52 | Stack depth? | n |
| 53 | Iterative better? | large n/W |
| 54 | Parent table? | boolean take |
| 55 | Utilization metric? | Σw/W % |
| 56 | Test trio? | zero/skip/tie |
| 57 | Direction comment? | load-bearing line |
| 58 | One-line 2-D? | best of skip vs take |
| 59 | One-line 1-D? | reverse sweep reuses row |
| 60 | Summary? | exponential subsets → O(nW) table |
