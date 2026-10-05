# FLASHCARDS — Advanced Algorithms Deep Track
> ~60 rows. Track `advanced-algo-deep`.

| # | Front | Back |
|---|---|---|
| 1 | Bit DP TSP bound | O(n²·2^n) time |
| 2 | Held-Karp base | dp[1][0] = 0 |
| 3 | Subset iteration idiom | sub = (sub-1) & mask |
| 4 | Lowest set bit | x & -x |
| 5 | Popcount | Integer.bitCount |
| 6 | Miller-Rabin error/base | ≤ 1/4 per round |
| 7 | Deterministic bases <2^64 | {2,3,5,7,11,13} subset |
| 8 | Fermat trap | Carmichael numbers (561) |
| 9 | Pollard Rho idea | Floyd cycle on f(x)=x²+c |
| 10 | Rho expected | O(n^{1/4}) |
| 11 | CRT needs | coprime moduli |
| 12 | modPow | binary exponentiation |
| 13 | Aho goto | trie edges |
| 14 | Aho fail | longest proper suffix link |
| 15 | Aho output | dict suffix links |
| 16 | KMP pi | longest prefix-function |
| 17 | Z-box | [l,r] match window |
| 18 | SA construction | prefix-doubling O(n log n) |
| 19 | Kasai | O(n) LCP |
| 20 | Cross product sign | left turn iff > 0 |
| 21 | Hull sort key | x then y |
| 22 | Collinear policy | pop ≤ 0 (strict hull) |
| 23 | Sweep status | balanced BST |
| 24 | Closest pair | O(n log n) strip check ≤7 |
| 25 | Permutation count | n! |
| 26 | Inclusion-exclusion | Σ(-1)^k unions |
| 27 | Meet-in-middle | split n/2, hash join |
| 28 | Branching vector | T(n) ≤ ΣT(n-r_i) |
| 29 | Work W | total operations |
| 30 | Span S | critical path |
| 31 | Speedup bound | ≤ W/S (parallelism) |
| 32 | Brent | Tp ≤ W/P + S |
| 33 | Prefix span | O(log n) |
| 34 | ForkJoin threshold | tune ~1k-10k |
| 35 | Race fix | join before read |
| 36 | Las Vegas | correct, random time |
| 37 | Monte Carlo | bounded time, error δ |
| 38 | Amplify | repeat k: δ^k |
| 39 | Karger step | random edge contract |
| 40 | Karger success | ≥ 2/n(n-1) |
| 41 | Hashing expected | O(1) with load control |
| 42 | Skip list height | O(log n) w.h.p. |
| 43 | Set-cover ratio | H(d) ≤ ln d+1 |
| 44 | Vertex-cover 2-apx | maximal matching |
| 45 | TSP metric 1.5 | Christofides |
| 46 | Knapsack FPTAS | scale + round profits |
| 47 | LP rounding | x≥1/2 → 2-apx VC |
| 48 | Dual bound | weak duality ALG/OPT |
| 49 | Strassen | 7 mults, O(n^2.81) |
| 50 | Crossover | naive below n0 |
| 51 | FFT bound | O(n log n) |
| 52 | Bit-reversal | iterative FFT order |
| 53 | Master case 1 | f < n^{log_b a} |
| 54 | Master case 2 | f = Θ(n^{log_b a}) |
| 55 | Master case 3 | f larger + regularity |
| 56 | Amortized accounting | charge ops to objects |
| 57 | Potential method | Φ diff telescopes |
| 58 | Union-find α | inverse Ackermann |
| 59 | Pitfall #1 | overflow in modMul |
| 60 | Pitfall #2 | forgetting fail-link BFS order |
