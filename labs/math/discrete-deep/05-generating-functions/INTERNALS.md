# Internals: How Generating Functions Are Computed

## Coefficient Arrays: Truncated Formal Series

The computational object is `BigInteger[] c` with `c[i] = [xⁱ]F(x)`, truncated at degree N. All arithmetic is done in the ring ℤ[[x]]/xᴺ⁺¹:

- **Add/subtract:** element-wise, Θ(N).
- **Multiply:** Θ(N²) schoolbook convolution (`c[k] = Σ a[i]b[k−i]`), or Θ(N log N) via NTT/FFT when N is large and coefficients fit the modulus (or via Kronecker substitution for big integers).
- **Divide** (A/B where B[0] ≠ 0): recursive/iterative inversion — b⁻¹[0] = 1/b[0], then b⁻¹[k] = −(1/b[0])·Σ_{i=1..k} b[i]·b⁻¹[k−i], giving A·B⁻¹ in Θ(N²). **B[0] = 0 means not invertible** (division by x isn't allowed in this ring) — the error to check first when a "closed form" explodes.
- **Composition** F(G(x)) with G[0] = 0: Horner-style, Θ(N²) or better with Newton iteration.

## Exponentiation and the Exp/Log Map

`exp(A)` for A[0] = 0 solves F′ = A′·F by Newton iteration: O(M(N) log N) with fast multiplication, Θ(N²) naively. `log(A) = ∫ A′/A` similarly. This is what makes "sets of connected structures = exp(structures)" computable to degree N: EGF of set partitions = exp(eˣ − 1) truncated at N gives Bell numbers B₀..B_N in roughly Θ(N²) with naive multiply — versus B₅₀ ≈ 4.9×10⁶⁴ needing big integers regardless.

## Reading Off Coefficients of Rational Functions

For A(x) = P(x)/Q(x) with Q(0) = 1, the **linear recurrence** from the denominator is the cheapest extraction: if Q(x) = 1 − q₁x − … − qₖxᵏ then aₙ = q₁aₙ₋₁ + … + qₖaₙ₋ₖ. Extraction is Θ(k·N) with O(k) memory — no series multiplication at all. Example: 1/(1−x−x²) → Fibonacci; (1+x)/(1−x−x²) → shifted Fibonacci. A rational-coefficient library should *detect* denominator degree k and switch to the recurrence automatically.

## Partial Fractions (Root-Based Closed Forms)

Distinct roots λᵢ of Q: A = Σ cᵢ/(1 − x/λᵢ) gives aₙ = Σ cᵢ·λᵢⁿ. Repeated roots add polynomial factors (n^j·λᵢⁿ). Finding roots numerically is unstable for high degree — libraries either require factored input or fall back to the linear recurrence. This is where complex arithmetic enters: the roots of the denominator may be complex, and conjugate pairs recombine into real terms (n^j·rⁿ·cos/sin patterns), which is why a "simple" recurrence can have oscillating closed forms.

## Multivariate Series

Coefficient extraction in two variables uses the same convolution in 2D: Θ(N⁴) naive for N×N grids (Σ_{i₁+i₂=n, j₁+j₂=m}), reducible with FFT techniques. Partitions with restrictions (distinct parts, bounds) become products Π (1 + x^k) truncated — each factor a two-term series, so the whole product is Θ(k·N) accumulation.

## Complexity Summary (exact, no benchmarks)

| Operation on degree-N truncations | Cost |
|---|---|
| add / scalar mult | Θ(N) |
| multiply (schoolbook) | Θ(N²) |
| multiply (FFT/NTT) | Θ(N log N) |
| invert / divide | Θ(N²) naive, O(M(N) log N) Newton |
| exp / log | Θ(N²) naive, O(M(N) log N) Newton |
| rational → recurrence read-off | Θ(k·N), O(k) memory |
| nth term of linear recurrence | Θ(k·N) iteratively, O(M(log n)) via fast doubling for constant-coefficient order-k companions |

Memory for all naive methods: Θ(N) coefficients (plus their integer bit-widths, which for counts like p(n) grow as Θ(√n) digits by the Hardy–Ramanujan formula).
