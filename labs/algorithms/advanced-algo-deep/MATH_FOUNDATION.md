# MATH_FOUNDATION — Advanced Algorithms Deep Track
> Recurrences / Master theorem / amortized. Track `advanced-algo-deep`.

## 1. Recurrence toolkit
- Substitution, recursion tree, Master theorem, Akra-Bazzi.
- T(n) = a·T(n/b) + f(n); compare f vs n^{log_b a}.
- Strassen: T(n) = 7T(n/2) + O(n²) → O(n^{log2 7}) ≈ O(n^2.81).
- FFT: T(n) = 2T(n/2) + O(n) → O(n log n).
- Karger repetition: O(n² log n) trials × O(n²) contraction.

## 2. Master theorem cases
- Case 1: f(n) = O(n^{log_b a - ε}) → T = Θ(n^{log_b a}).
- Case 2: f(n) = Θ(n^{log_b a} log^k n) → T = Θ(n^{log_b a} log^{k+1} n).
- Case 3: f(n) = Ω(n^{log_b a + ε}) + regularity → T = Θ(f(n)).
- Example: mergesort 2T(n/2)+O(n) → case 2 → Θ(n log n).

## 3. Akra-Bazzi sketch
- T(n) = Σ a_i T(b_i n) + f(n); find p with Σ a_i b_i^p = 1.
- T = Θ(n^p (1 + ∫ f(u)/u^{p+1} du)).
- Handles uneven splits (e.g., hull recursion, quickselect variants).

## 4. Branching recurrences (exact exponential)
- T(n) ≤ Σ T(n - r_i) + poly(n); root of x^n = Σ x^{n-r_i}.
- Vertex cover branch (include/exclude): T(n) ≤ 2T(n-1) → O(2^n); bounded search improves base.
- Measure-and-conquer: non-uniform measure sharpens the base (e.g., 1.3^n).

## 5. Amortized analysis
- Aggregate: n ops total cost / n.
- Accounting: charge extra on cheap ops to pay for expensive ones.
- Potential: Φ(D_i) telescopes; amortized = real + ΔΦ.
- Union-find with path compression: O(α(n)) amortized.
- Dynamic array push: 3-credit accounting → O(1) amortized.
- Counter increment: bit-flip aggregate O(n) for n increments.

## 6. Randomized expectations
- Linearity of expectation over indicator variables.
- Karger: P(survive) ≥ 2/(n(n-1)) via product over contractions.
- Amplification: repeat k times → failure δ^k; set k = c·n² log n.
- Hashing: expected chain length = load factor α.

## 7. Approximation ratios
- Set cover greedy: H(d) via charging each pick to OPT.
- Vertex cover matching: |matching| ≤ OPT; output ≤ 2·OPT.
- Christofides: MST + matching ≤ 1.5·OPT (metric TSP).
- Knapsack FPTAS: scaling error ≤ ε·OPT with poly(n/ε) time.

## 8. Modular arithmetic facts
- Fermat: a^{p-1} ≡ 1 (mod p) for prime p.
- Euler: a^{φ(n)} ≡ 1 (mod n) when gcd(a,n)=1.
- CRT: unique solution mod Π m_i for coprime m_i.
- modMul overflow: use BigInteger or 128-bit guard.

## 9. Practice proofs (do on paper)
- Prove Strassen bound via Master case 1.
- Prove union-find amortized sketch via rank potential.
- Prove set-cover H(d) charging bound.
- Prove Karger survival product.

## Checklist
- [ ] State Master case in 30s. [ ] Sketch one amortized proof. [ ] Derive one ratio.
