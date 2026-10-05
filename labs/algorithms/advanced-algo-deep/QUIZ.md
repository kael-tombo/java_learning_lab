# QUIZ — Advanced Algorithms Deep Track
> 15 questions with answers. Track `advanced-algo-deep`.

1. Bit DP TSP complexity? → O(n²·2^n) time, O(n·2^n) space.
2. Why does Miller-Rabin use several bases? → Each base cuts error ≤ 1/4; repetition drives it exponentially down.
3. Pollard Rho expected time? → O(n^{1/4}) heuristically via birthday paradox.
4. Aho-Corasick search bound? → O(n + m + z): build trie+fail once, linear scan.
5. Monotone chain hull complexity? → O(n log n) dominated by sort.
6. Left-turn test formula? → cross(o,a,b) = (a-o)×(b-o); pop if ≤ 0 (for lower hull excluding collinear).
7. Work vs span? → Work = total ops; span = longest dependency chain.
8. Brent's scheduling bound? → Tp ≤ W/P + S on P processors.
9. Las Vegas vs Monte Carlo? → Las Vegas always correct, random time; Monte Carlo bounded time, small error.
10. Karger success probability? → ≥ 2/(n(n-1)); repeat O(n² log n) times to amplify.
11. Set-cover greedy ratio? → H(d) ≤ ln d + 1 where d = max set size.
12. When is Strassen worth it? → Above crossover n0 (~64-128) given constants and memory cost.
13. CRT requirement? → Moduli pairwise coprime; combine via Garner/construction.
14. Skip list expected height? → O(log n) via geometric coin flips.
15. LP rounding for vertex cover? → 2-approximation via rounding x_i ≥ 1/2.

## Scoring
- 13-15: expert. 10-12: practitioner. < 10: revisit THEORY + flashcards.

## Follow-ups
- Prove one bound on paper; implement one variant from memory.
