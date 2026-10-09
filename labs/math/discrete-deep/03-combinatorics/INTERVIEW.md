# Interview: Combinatorics

## Counting Questions

**Q: How many bitstrings of length n have no two consecutive 0s?**
A: aₙ = aₙ₋₁ + aₙ₋₂ with a₁ = 2, a₂ = 3 (a₀ = 1), i.e., aₙ = Fₙ₊₂. Derivation: a valid string ends in 1 (append to any aₙ₋₁) or in 0 (must be preceded by 1, so append "10" to any aₙ₋₂). n = 5 → 13.

**Q: How many 5-card poker hands from a 52-card deck?**
A: C(52,5) = 2,598,960 — order doesn't matter, no repetition. If the deal order mattered it would be P(52,5) = 311,875,200, exactly 5! × more.

**Q: Probability that among 23 people two share a birthday?**
A: 1 − P(all distinct)/365²³ with distinct count 365·364·…·343 = 365!/(365−23)!. That ratio ≈ 0.4927, so the probability ≈ 50.7% — because the count of *pairs* is C(23,2) = 253, which already exceeds 365; √365 ≈ 19 gives the rough threshold.

**Q: Compute C(100, 50) without overflow.**
A: Multiplicative: Π_{i=1..50} (50+i)/i with `BigInteger`, dividing each step (exact at every prefix); or two-argument `BigInteger` factorial division. Never 100!/50!/50! in `long` — the intermediate 100! ≈ 9.3×10¹⁵⁷ is far past 2⁶³.

**Q: Explain inclusion–exclusion on "at least one of n properties."**
A: Σ_{k≥1} (−1)^{k+1} Σ_{|S|=k} N(P_S). Each element with r ≥ 1 properties is counted Σ_{j≥1} (−1)^{j+1}C(r,j) = 1 − (1−1)^r = 1 times; an element with none is counted 0 times (never appears in any term). The alternating signs make non-members cancel exactly.

## Structure and Recurrence Questions

**Q: Give the Catalan recurrence and one combinatorial interpretation.**
A: Cₙ = Σ_{i=0}^{n−1} CᵢCₙ₋₁₋ᵢ, C₀ = 1 → 1, 1, 2, 5, 14, 42. Interpretation: Dyck paths of semilength n split at the first return to height 0 into independent paths of sizes i−1 and n−i. Equivalent objects: triangulations of an (n+2)-gon, binary trees with n internal nodes, well-parenthesized products of n+1 factors.

**Q: Count derangements and give the recurrence.**
A: !n = (n−1)(!(n−1) + !(n−2)), !0 = 1, !1 = 0 → 0, 1, 2, 9, 44, 265. Element 1 occupies some position k; if k's owner takes position 1, the rest derange (n−2), else the rest is a restricted permutation of n−1 items. Asymptotically !n = round(n!/e), so P(no fixed point) → 1/e ≈ 0.368.

**Q: When does DP beat a closed form?**
A: DP wins when no closed form exists (obstacle grids, constrained paths) or when all table entries are needed: building Pascal's triangle is Θ(n²) but then every C(n,k) query is O(1), whereas the multiplicative formula is O(k) per query. For Catalan numbers the closed form C(2n,n)/(n+1) is O(n) versus the DP's Θ(n²) — use the closed form for a single large term.

## Applied Questions

**Q: A batch API generates all subsets of a user's 40 flags. Is that safe?**
A: No — 2⁴⁰ ≈ 1.1×10¹² subsets; output-bound work makes it a denial-of-service vector. Fix: compute the count cheaply (left-shift check against a budget) and reject before generating; also accept filters so callers request specific k (C(40,k)) rather than everything.

**Q: Why is a 64-bit random id unsafe for uniqueness checks?**
A: Birthday bound: with n ids in 2⁶⁴ space, collision probability ≈ n²/2⁶⁵. At n = 10⁹ that is ≈ 10¹⁸/3.7×10¹⁹ ≈ 2.7% — far higher than "1 in 2⁶⁴" suggests. Use 128-bit ids (collision negligible through 10¹² issuances) or an explicit uniqueness constraint.

**Q: How would you test a `binomial(n, k)` implementation?**
A: (1) Pascal's identity holds for all n ≤ 66; (2) symmetry C(n,k) = C(n,n−k); (3) row sums equal 2ⁿ; (4) cross-check against a brute-force subset enumerator for n ≤ 12; (5) `Math.addExact`/`multiplyExact` so overflow beyond C(66,33) raises instead of wrapping; (6) edge cases C(n,0) = 1, C(n,n) = 1, C(n,k) = 0 for k > n.
