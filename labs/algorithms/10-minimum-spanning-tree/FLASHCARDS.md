# FLASHCARDS — Minimum Spanning Tree (~60)
> Rapid recall: front → back. Cover recurrence, complexity, when-to-use.

| # | Front | Back |
|---|-------|------|
| 1 | Goal? | min total connecting all V |
| 2 | Kruskal step? | sort edges, union if separated |
| 3 | Kruskal invariant? | taken ⊆ some MST |
| 4 | Kruskal time? | O(E log E) |
| 5 | Prim step? | add min fringe crossing edge |
| 6 | Prim invariant? | tree ⊆ some MST |
| 7 | Prim+PQ time? | O(E log V) |
| 8 | Prim naive time? | O(V²) |
| 9 | Cut property? | lightest crossing in some MST |
| 10 | Cycle property? | heaviest on cycle never needed |
| 11 | DSU ops? | find + union |
| 12 | DSU amortized? | ~α(V) ≈ const |
| 13 | DSU tricks? | path compression + rank |
| 14 | Stop condition? | V-1 edges |
| 15 | Disconnected? | MSF |
| 16 | Negatives ok? | yes |
| 17 | Directed? | no (arborescence instead) |
| 18 | Unique iff? | distinct weights |
| 19 | Triangle 1,2,3 total? | 3 |
| 20 | Square ties total? | 3 (any 3) |
| 21 | Sort dominates? | yes for Kruskal |
| 22 | Stale Prim edge? | skip (both in tree) |
| 23 | key[v] means? | min edge tree→v |
| 24 | Borůvka? | parallel rounds O(E log V) |
| 25 | Second-best? | max-edge-on-path swap |
| 26 | Use case? | network / wiring design |
| 27 | Shortest ≠ MST? | different objectives |
| 28 | Steiner? | NP-hard; MST is relaxation |
| 29 | Overflow guard? | long total |
| 30 | Java sort? | Arrays.sort comparingInt |
| 31 | Java PQ? | fringe min edge |
| 32 | inTree[]? | Prim membership |
| 33 | parent/rank arrays? | DSU state |
| 34 | find iterative? | avoid recursion |
| 35 | Skip-edge meaning? | cycle edge |
| 36 | Taken edge cut? | component cut lightest |
| 37 | Dense choice? | Prim O(V²) may win |
| 38 | Sparse choice? | Kruskal or Prim+PQ |
| 39 | Recurrence? | sorting recurrence, not DP |
| 40 | Union by? | rank/size |
| 41 | Path compression? | flatten on find |
| 42 | MST edges count? | V-1 (connected) |
| 43 | MSF edges? | V-components |
| 44 | Validate MST? | acyclic + V-1 + min (brute small) |
| 45 | Random test? | Kruskal==Prim weight |
| 46 | Brute n≤7? | enumerate trees |
| 47 | When NOT? | directed/shortest/constrained |
| 48 | Dynamic weights? | dynamic MST needed |
| 49 | Space? | O(V+E) |
| 50 | Kruskal needs? | edge list |
| 51 | Prim needs? | adj + PQ |
| 52 | Tie policy? | document (any valid) |
| 53 | Zero weights? | fine, taken early |
| 54 | Equal sort stable? | any order valid |
| 55 | Exchange argument? | swap proof for safety |
| 56 | Cut example? | {A}\|{B,C} → AB |
| 57 | Cycle example? | skip AC weight 3 |
| 58 | Test trio? | forest/tie/overflow |
| 59 | One-line Kruskal? | lightest acyclic edge repeatedly |
| 60 | One-line Prim? | cheapest connection to growing tree |
