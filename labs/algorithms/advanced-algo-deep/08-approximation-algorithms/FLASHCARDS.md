# Flashcards — Approximation Algorithms

Format: **Q → A**.

---

| # | Question | Answer |
|---|----------|--------|
| 1 | α-approximation (min) | ALG ≤ α·OPT, α ≥ 1 |
| 2 | α-approximation (max) | ALG ≥ α·OPT, α ≤ 1 |
| 3 | PTAS | 1+ε for any ε>0, runtime depends on ε |
| 4 | FPTAS | PTAS polynomial in n and 1/ε |
| 5 | Greedy set cover | Θ(log n)-approximation |
| 6 | Set cover lower bound | no (1-o(1))·ln n unless P=NP |
| 7 | Vertex cover via matching | 2-approximation |
| 8 | Matching lower bound on cover | |M| ≤ OPT |
| 9 | Metric TSP via MST | 2-approximation |
| 10 | Christofides | 3/2 for metric TSP |
| 11 | General TSP hardness | no constant-factor poly approximation |
| 12 | Metric hypothesis | triangle inequality on edge weights |
| 13 | Knapsack FPTAS | Θ(n²/ε) |
| 14 | Knapsack greedy failure | small high-ratio item blocks big value item |
| 15 | Knapsack exact DP | Θ(n·W), pseudo-polynomial |
| 16 | Pseudo-polynomial | polynomial in the value, not the bit-length |
| 17 | Strongly NP-hard | no FPTAS unless P=NP |
| 18 | Metric TSP shortcutting | triangle inequality makes it non-increasing |
| 19 | MST doubling cost | 2·MST |
| 20 | Euler tour of doubled MST | visits every edge twice |
| 21 | Shortcut repeated vertices | removes duplicates, keeps cost ≤ tour |
| 22 | Vertex cover vs matching duality | any cover ≥ any matching |
| 23 | Greedy set cover choice | set covering the most uncovered elements |
| 24 | Set cover element charge | 1/(newly covered by this set) |
| 25 | Total charge bound | H_n·OPT |
| 26 | Knapsack DP state | value — scaled for the FPTAS |
| 27 | Scaling δ | ε·max_value/n |
| 28 | Rounded knapsack guarantee | value ≥ (1-ε)·OPT |
| 29 | When FPTAS impossible | strongly NP-hard problems |
| 30 | Bin packing | strongly NP-hard — no FPTAS |
| 31 | Vertex cover best known | 2-approximation |
| 32 | Metric TSP best known | 1.5 (Christofides) |
| 33 | General TSP vs metric TSP | general has no constant approximation |
| 34 | Approx ratio is | a worst-case bound over all inputs |
| 35 | Approximate does not mean | close on every instance — it is a worst-case ratio |
| 36 | Maximal matching is | edge-maximal — cannot add an edge |
| 37 | Maximal vs maximum matching | maximal ⊇ at least half the optimum size |
| 38 | Set cover universe n | H_n ≈ ln n + γ factor |
| 39 | Knapsack FPTAS input | (n, W, values, weights) |
| 40 | Knapsack FPTAS output | (1-ε)-approximation |
| 41 | MST lower bound on TSP | MST ≤ OPT (optimal tour minus an edge) |
| 42 | Euler circuit cost | 2·MST |
| 43 | Shortcut cost | ≤ Euler tour cost, by triangle inequality |
| 44 | Approx scheme meaning | trade time for the error ε |
| 45 | PTAS example | Euclidean TSP has a PTAS (Arora/Mitchell) |
| 46 | FPTAS for Euclidean TSP | no — geometric TSP is not strongly NP-hard but the FPTAS is open/limited; it has a PTAS |
| 47 | Vertex cover integrality LP | the 2-approximation matches the LP half-integrality |
| 48 | Half-integral LP optimum | ≤ 2·OPT for vertex cover |
| 49 | Greedy maximal matching | Θ(E) time |
| 50 | Matching endpoints cover all edges | yes, by maximality of M |
| 51 | Why greedy maximal matching covers | any uncovered edge could be added to M, contradicting maximality |
| 52 | Set cover greedy tight example | classic log n gap construction |
| 53 | Approx ratio is worst-case | over all inputs — many instances do better |
| 54 | Approx ratio of Christofides | 3/2 |
| 55 | Christofides components | MST + min perfect matching on odd-degree vertices |
| 56 | Odd-degree vertices count | even, by handshaking |
| 57 | Why perfect matching on odd-degree vertices | to make all degrees even so an Eulerian circuit exists |
| 58 | Approx in practice | the ratio is worst-case; many instances do far better |
| 59 | FPTAS rounding correctness | each item's value rounds down by < δ, total loss < n·δ ≤ ε·max_value ≤ ε·OPT |
