# FLASHCARDS — Two Pointers Technique
> ~60 rows. Front | Back. Lab `17-two-pointers`.

| # | Front | Back |
|---|---|---|
| 1 | Define Two Pointers Technique | converging / sliding pointer pairs on ordered data |
| 2 | Core formula/object | left/right move by predicate; monotonicity of feasibility |
| 3 | Key invariant | loop invariant: all discarded positions cannot be in solution |
| 4 | Headline complexity | O(n) time after sort, O(1) extra space |
| 5 | Production example | pair-sum, dedup, container-with-most-water |
| 6 | Base case | Empty/singleton trivial solution; null rejected |
| 7 | Aux structure | Table/heap/map summarizing processed prefix |
| 8 | Progress measure | Strictly monotonic potential toward termination |
| 9 | Correctness lemmas | Safety (invariant) + progress + termination |
| 10 | Master theorem case 1 | f(n)=O(n^{log_b a - e}) => T=O(n^{log_b a}) |
| 11 | Master theorem case 2 | f(n)=Theta(n^{log_b a}) => T=O(n^{log_b a} log n) |
| 12 | Master theorem case 3 | f(n)=Omega(...) + regularity => T=Theta(f(n)) |
| 13 | Amortized: aggregate | Total cost / n over sequence |
| 14 | Amortized: accounting | Prepay credits on cheap ops for expensive ones |
| 15 | Amortized: potential | Phi maps state to saved energy; a_i = c_i + ΔPhi |
| 16 | P vs NP relevance | Exact exponential vs poly approximation tradeoff |
| 17 | Top-down vs bottom-up | Memo recursion vs tabulation order |
| 18 | Reconstruction trick | Parent pointers + backtrack from optimum |
| 19 | Overflow guard | long accumulators; Math.addExact/multiplyExact |
| 20 | Off-by-one guard | Half-open [l,r) + unit tests on boundaries |
| 21 | Fuzz oracle | Small-n brute force comparison, 200 seeds |
| 22 | Benchmark sizes | 1k/10k/100k/1M with warmup, report median |
| 23 | Cache effect | Table layout row-major; blocking for locality |
| 24 | Parallel span | Critical path length; Brent T_p <= T1/p + T_inf |
| 25 | Randomized amplification | Repeat k times; error drops exponentially |
| 26 | Hash rolling update | Drop high digit, shift, add new: O(1) per slide |
| 27 | KMP pi meaning | Longest proper prefix which is also suffix |
| 28 | DP order | Topological order of DAG; loops respect dependencies |
| 29 | Greedy proof tool | Exchange argument / matroid / stays-ahead |
| 30 | When to sort first? | When monotonicity/order enables linear scan |
| 31 | Space optimization | Keep only prev row / rolling arrays when transitions local |
| 32 | Sentinel value | Define for empty: 0 / empty list / Optional |
| 33 | Tie-breaking rule | Fix deterministic order; document it |
| 34 | Worst-case family | Adversarial input forcing max work (sorted/reverse/collisions) |
| 35 | Lower bound idea | Decision-tree / counting argument |
| 36 | Numerical stability | Prefer long/double with epsilon; avoid catastrophic cancellation |
| 37 | Concurrency hazard | Shared aux mutation; use thread-local or fork-join |
| 38 | API design | Pure solve() + reconstruct(); no I/O inside |
| 39 | Test pyramid | Unit edges + property fuzz + benchmark regression |
| 40 | Interview pitch (30s) | Two Pointers Technique: converging / sliding pointer pairs on ordered data keeping loop invariant: all discarded positions cannot be in solution achieving O(n) time after sort, O(1) extra space |
| 41 | Misconception #1 | Average != worst case |
| 42 | Misconception #2 | Value-only DP forgets reconstruction |
| 43 | Pitfall: recursion depth | n>10k overflows stack; go iterative |
| 44 | Pitfall: hash collisions | Use double mod or verify candidates |
| 45 | Pitfall: comparator bug | Inconsistent compareTo breaks sort/heap |
| 46 | Visual cue | Draw state DAG / window / residual graph for n=4 |
| 47 | Neighbor lab link | See INDEX.md for adjacent technique comparison |
| 48 | One-line decision rule | Use when invariant holds and n justifies overhead |
| 49 | Exit criterion | Input exhausted or target reached + invariant => done |
| 50 | Recall #50 for Two Pointers Technique | loop invariant: all discarded positions cannot be in solution |
| 51 | Recall #51 for Two Pointers Technique | loop invariant: all discarded positions cannot be in solution |
| 52 | Recall #52 for Two Pointers Technique | loop invariant: all discarded positions cannot be in solution |
| 53 | Recall #53 for Two Pointers Technique | loop invariant: all discarded positions cannot be in solution |
| 54 | Recall #54 for Two Pointers Technique | loop invariant: all discarded positions cannot be in solution |
| 55 | Recall #55 for Two Pointers Technique | loop invariant: all discarded positions cannot be in solution |
| 56 | Recall #56 for Two Pointers Technique | loop invariant: all discarded positions cannot be in solution |
| 57 | Recall #57 for Two Pointers Technique | loop invariant: all discarded positions cannot be in solution |
| 58 | Recall #58 for Two Pointers Technique | loop invariant: all discarded positions cannot be in solution |
| 59 | Recall #59 for Two Pointers Technique | loop invariant: all discarded positions cannot be in solution |
| 60 | Recall #60 for Two Pointers Technique | loop invariant: all discarded positions cannot be in solution |

## How to use
- Shuffle; 80%+ first-try = pass. Bury solved cards (Anki-style).
