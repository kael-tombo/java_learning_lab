# FLASHCARDS — DP Basics (~60)
> Rapid recall: front → back. Cover recurrence, complexity, when-to-use.

| # | Front | Back |
|---|-------|------|
| 1 | Fib recurrence? | F(n)=F(n-1)+F(n-2) |
| 2 | Bases fib? | 0,1 |
| 3 | ways recurrence? | W(n)=W(n-1)+W(n-2) |
| 4 | ways bases? | W(0)=1,W(1)=1 |
| 5 | Naive time? | exponential ~φⁿ |
| 6 | Naive recurrence? | T=T(n-1)+T(n-2)+O(1) |
| 7 | Memo time? | O(n) |
| 8 | Memo space? | O(n)+stack |
| 9 | Tab time? | O(n) |
| 10 | Tab space? | O(n) → O(1) opt |
| 11 | Memo invariant? | stored = final |
| 12 | Tab invariant? | dp[≤i] final after i |
| 13 | DAG order? | increasing i |
| 14 | ways(4)? | 5 |
| 15 | ways(n)=? | fib(n+1) |
| 16 | Top-down? | memo DFS |
| 17 | Bottom-up? | tabulation loop |
| 18 | Same big-O? | yes, both O(n) |
| 19 | Overlap needed? | yes else no gain |
| 20 | Optimal substructure? | deps optimal → optimum |
| 21 | Wrong base effect? | off-by-one everywhere |
| 22 | ways(0)=1 why? | empty way counts |
| 23 | fib(47) int? | overflows → long |
| 24 | Big n mod? | 1e9+7 per add |
| 25 | Depth risk? | StackOverflow; iterative |
| 26 | Sentinel? | -1 unknown (if valid ≥0) |
| 27 | Fast doubling? | O(log n) |
| 28 | Matrix fib? | O(log n) |
| 29 | Binet? | closed form, float issues |
| 30 | House robber same? | yes, linear DP skeleton |
| 31 | Min-cost stairs? | dp=min(prev two)+cost |
| 32 | Trace n=5 naive nodes? | 15 |
| 33 | Memo states n=5? | 6 |
| 34 | n=0 test? | base direct |
| 35 | n<0? | throw |
| 36 | Two-var update? | a,b=b,a+b |
| 37 | Mod placement? | per addition |
| 38 | BigInteger when? | exact huge fib |
| 39 | Use DP when? | overlap + DAG order |
| 40 | Skip DP when? | closed form / no overlap |
| 41 | Interview n≤25? | naive passes but DP better |
| 42 | Induction anchor? | bases |
| 43 | Step? | deps final → n final |
| 44 | Space lower? | Ω(1) order-2 |
| 45 | Reconstruct needs? | full table if path |
| 46 | Call DAG? | states as nodes |
| 47 | Saved work metric? | tree nodes − states |
| 48 | Java fill? | Arrays.fill(memo,-1) |
| 49 | long vs int? | long to n≈92 |
| 50 | n=10⁴ memo? | overflow stack |
| 51 | Iterative wins? | deep n |
| 52 | Test trio? | 0/1/large |
| 53 | Property memo==tab? | 0..30 |
| 54 | Identity test? | ways(n)==fib(n+1) |
| 55 | Counter-example? | ways(0)=0 shift bug |
| 56 | When-to-use DP? | repeated subproblems |
| 57 | Not DP? | divide-no-overlap |
| 58 | One-line memo? | compute once, reuse |
| 59 | One-line tab? | fill deps-first |
| 60 | Summary? | exponential → linear via caching |
