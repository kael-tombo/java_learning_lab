# Flashcards — Randomized Algorithms

Format: **Q → A**.

---

| # | Question | Answer |
|---|----------|--------|
| 1 | Las Vegas | always correct, expected time bounded |
| 2 | Monte Carlo | bounded time, correct with high probability |
| 3 | Randomised quicksort expected | Θ(n log n) |
| 4 | Randomised quicksort worst | Θ(n²), probability 2^{-Θ(n)} |
| 5 | Quickselect expected | Θ(n) |
| 6 | Median-of-medians | deterministic O(n) selection |
| 7 | Miller–Rabin error | ≤ 4⁻ᵏ for k rounds |
| 8 | Reservoir sampling | uniform k-sample in one pass |
| 9 | Reservoir rule for i > k | include with probability k/i |
| 10 | Reservoir space | Θ(k) |
| 11 | Expected hash lookup | Θ(1) |
| 12 | Load factor α | n/m — expected chain length |
| 13 | Universal hashing | random hash family defeats fixed worst-case keys |
| 14 | Freivalds' | Monte Carlo matrix-product check |
| 15 | Boosting MC | independent repetitions multiply success |
| 16 | LV worst case | improbable, not eliminated |
| 17 | LV correctness | always — coins affect only time |
| 18 | MC correctness | with high probability — coins can fool it |
| 19 | Adversary vs random pivots | cannot force the bad path |
| 20 | Randomised quicksort recurrence | E[T(n)] = Θ(n) + (2/n)Σ E[T(k)] |
| 21 | Quickselect recurrence | E[T(n)] ≤ E[T(3n/4)] + Θ(n) |
| 22 | Why quickselect is LV | the k-th smallest is found correctly regardless of pivots |
| 23 | Why quicksort is LV | the output is always sorted; pivots affect only time |
| 24 | Reservoir final probability | k/n for every item |
| 25 | Randomised hash table worst case | Θ(n) chain — but improbable under universal hashing |
| 26 | MC error amplification | k rounds: δᵏ |
| 27 | 4⁻¹⁰ | ≈ 10⁻⁶ |
| 28 | 40 MR rounds | error ≤ 4⁻⁴⁰ — cryptographically negligible |
| 29 | LV example beyond quicksort | randomised quickselect |
| 30 | MC example beyond MR | Freivalds' |
| 31 | Expected chain length | α = n/m |
| 32 | Universal hash family | P(h(x)=h(y)) ≤ 1/m |
| 33 | Why seeds must be unpredictable | a predictable seed lets the adversary rebuild the worst case |
| 34 | Time-based seed | predictable — insecure for hash randomisation |
| 35 | Randomised quicksort pivot choice | uniform over the current subarray |
| 36 | E[T(n)] for randomised quicksort proof sketch | E[T(n)] = Θ(n) + (2/n)ΣE[T(k)] |
| 37 | Linearity of expectation in QS proof | no independence needed across subproblems |
| 38 | Freivalds' trick | multiply by a random vector r and check A(Br) = Cr |
| 39 | Freivalds' error | ≤ 1/2 per random r |
| 40 | Reservoir eviction | uniform over the k items |
| 41 | One pass streaming sample | reservoir sampling |
| 42 | Randomised selection vs deterministic | LV O(n) vs median-of-medians O(n) with a big constant |
| 43 | Quickselect degrades to | Θ(n²) on always-median pivots — but random pivots avoid that in expectation |
| 44 | Monte Carlo primality vs Fermat | Fermat fails on Carmichael numbers; MR does not |
| 45 | Randomised algorithms in production | quicksort, quickselect, hash tables, sampling |
| 46 | E[T] vs worst T | expected can be Θ(n log n) while worst is Θ(n²) |
