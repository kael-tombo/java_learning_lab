# Advanced Mathematics Foundation

## 1. Group Theory Axioms and Theorems

**Theorem (Unique Identity):** In a group G, the identity element is unique.
*Proof:* If e and e' are both identities, then e = e ∗ e' = e'.

**Theorem (Unique Inverses):** Each element has a unique inverse.
*Proof:* If b and c are inverses of a, then b = b ∗ e = b ∗ (a ∗ c) = (b ∗ a) ∗ c = e ∗ c = c.

**Lagrange's Theorem:** For finite group G and subgroup H, |H| divides |G|.
*Proof:* Define cosets gH = {gh : h ∈ H}. Cosets partition G, each has size |H|. Thus |G| = [G:H]·|H|.

**First Isomorphism Theorem:** For homomorphism φ: G → H, G/ker(φ) ≅ im(φ).

## 2. Ring Theory Foundations

**Theorem:** ℤ/nℤ is a field iff n is prime.
*Proof:* If n = ab is composite, then ā·b̄ = 0̄ with ā, b̄ ≠ 0̄, so zero divisors exist — not a field. If n = p prime, every non-zero a has gcd(a,p) = 1, so ∃x,y: ax + py = 1, thus x̄ is the inverse of ā.

**Theorem (First Isomorphism for Rings):** For ring homomorphism φ: R → S, R/ker(φ) ≅ im(φ).

**Theorem:** Every maximal ideal is prime. In a PID, every non-zero prime ideal is maximal.

## 3. Metric Space Theorems

**Theorem:** A convergent sequence is Cauchy.
*Proof:* If x_n → x, then for ε/2 > 0, ∃N with d(x_n, x) < ε/2 for n ≥ N. For m, n ≥ N: d(x_m, x_n) ≤ d(x_m, x) + d(x, x_n) < ε.

**Theorem:** ℝ is complete.
*Proof:* A Cauchy sequence in ℝ is bounded, so by Bolzano-Weierstrass has a convergent subsequence. The full sequence converges to the same limit.

**Theorem:** A continuous function on a compact metric space is uniformly continuous.
*Proof:* For ε > 0, each x has δ_x with d(x,y) < δ_x ⟹ d(f(x),f(y)) < ε/2. Balls B(x, δ_x/2) cover the space; compactness gives finite subcover. Take δ = min δ_x_i/2.

## 4. Topology Theorems

**Theorem (Heine-Borel):** A subset of ℝ^n is compact iff it is closed and bounded.
*Proof (sketch):* Compact ⟹ closed (complement is open via finite subcover argument) and bounded (cover by balls of radius k). Closed and bounded ⟹ compact via sequential compactness and Bolzano-Weierstrass.

**Theorem:** The continuous image of a compact set is compact.
*Proof:* Let f: X → Y continuous, X compact. For an open cover of f(X), preimages cover X. Finite subcover of X maps to finite subcover of f(X).

**Theorem:** The continuous image of a connected set is connected.
*Proof:* If f(X) = U ∪ V (disjoint open), then X = f⁻¹(U) ∪ f⁻¹(V) would disconnect X.

## 5. Analysis Theorems

**Theorem (Bolzano-Weierstrass):** Every bounded sequence in ℝ^n has a convergent subsequence.
*Proof:* Bisect the bounding box; one half contains infinitely many terms. Repeat to get nested boxes with diameters → 0. Pick one term from each; the limit is in the intersection.

**Theorem (Uniform Limit):** The uniform limit of continuous functions is continuous.
*Proof:* For ε > 0, choose N with |f_N(x) - f(x)| < ε/3. By continuity of f_N at x₀, ∃δ with |x - x₀| < δ ⟹ |f_N(x) - f_N(x₀)| < ε/3. Then |f(x) - f(x₀)| ≤ |f(x) - f_N(x)| + |f_N(x) - f_N(x₀)| + |f_N(x₀) - f(x₀)| < ε.

## 6. Measure Theory Foundations

**Theorem (Monotone Convergence):** If 0 ≤ f_n ↑ f pointwise, then ∫f_n ↑ ∫f.

**Theorem (Dominated Convergence):** If f_n → f pointwise and |f_n| ≤ g with ∫g < ∞, then ∫f_n → ∫f.

**Theorem:** The Dirichlet function (1 on ℚ, 0 elsewhere) is Lebesgue integrable with integral 0, but not Riemann integrable.
*Proof:* ℚ has measure zero, so the function equals 0 almost everywhere. Riemann integrability requires continuity almost everywhere, which fails.
