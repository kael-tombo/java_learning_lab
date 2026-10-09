# Performance: Generating Function Algorithms

## Extraction Strategies and Their Exact Costs

For the n-th term of a sequence with GF A(x) = P/Q, deg Q = k:

| Strategy | Time | Memory | When |
|---|---|---|---|
| Linear recurrence loop from Q | Θ(k·n) | O(k) | any n, rational GF |
| Fast doubling / matrix power | O(k³·M(log n)) with matrix mult, O(M(log n)) for constant k | O(k²) | huge n (10⁹+) |
| Truncated series to degree n | Θ(n²) schoolbook multiply | O(n) | many small n, or non-rational GF |
| Series via FFT | Θ(n log n) per multiply | O(n) | very large truncations |
| Closed form Σcᵢλᵢⁿ | O(#distinct roots) per term | O(1) | roots known, needs exact arithmetic |

Key rule: **once you have Q, never multiply series again** — the recurrence read-off is Θ(k·n) and beats Θ(n²) convolutions by a factor of n/k.

## When a Closed Form Beats DP (Concrete)

- Fibonacci/Fib-like aₙ = aₙ₋₁ + 2aₙ₋₂: iterative DP Θ(n) time, O(1) memory. Binet/fractional-power form computes one term in O(log n) via exponentiation by squaring (exactly, using fast doubling: F₂ₙ = Fₙ(2Fₙ₊₁ − Fₙ), F₂ₙ₊₁ = Fₙ₊₁² + Fₙ²). For n = 10⁹ the loop does 10⁹ additions; fast doubling does ~60 doublings.
- Catalan: DP Θ(n²) additions vs closed form C(2n,n)/(n+1) = Θ(n) multiplications — a factor-of-n win (see lab 03).
- Coin change for arbitrary n with fixed coin set: DP Θ(K·n) (K coin types) has **no** comparable closed form; that is a case where the GF *is* the answer's representation, and the DP is the extraction.

## Cost of Algebra Itself

- Truncated product of two degree-N series: Θ(N²) (schoolbook) — building Π 1/(1−x^cᵢ) for K coin types by K successive products is Θ(K·N²).
- Inverting (dividing by) a series: Θ(N²) naive, O(M(N) log N) with Newton iteration — for GF(2) or modular coefficient rings with fast multiplication this becomes near-linear.
- exp/log of a series: Θ(N²) naive, O(M(N) log N) Newton — needed for the exp(G) constructions (set-of components).
- Partial fractions with degree-N denominator: root-finding is numerically unstable beyond modest degree; symbolic factorization cost dominates and is the reason libraries prefer the recurrence path.

## Coefficient Size Is a Hidden Cost

The truncation degree N is not the storage: counts grow. p(100) ≈ 7.9×10¹¹ (12 digits, exceeds `int`), p(1000) ≈ 2.4×10³¹ (32 digits), and by the Hardy–Ramanujan asymptotic p(n) ~ e^(π√(2n/3))/(4n√3) the digit count is Θ(√n) — so storing degree-N coefficient lists costs Θ(N·√N) digits ≈ Θ(N^1.5) word operations for the big-integer multiplications, not Θ(N²) word ops. Any performance claim for series libraries must state the coefficient ring (fixed-width mod p vs exact integers).

## Composition (F(G(x))) Is the Expensive One

Formal composition costs Θ(N²) with Horner (evaluating N nested polynomials each of degree ≤ N). Compared with multiplication (also Θ(N²) but with a much smaller constant and vectorizable), composition dominates when a formula requires nested substitutions — prefer the structural route (functional equation → kernel method → linear solve) over raw composition.

## Practical Summary

- Need one term, n up to 10⁷, rational GF: recurrence loop, Θ(k·n), O(k) memory.
- Need one term, n = 10¹⁸: fast doubling O(log n).
- Need 10,000 terms of a non-rational GF: series truncation once, Θ(N²) or Θ(N log N), then O(1) lookups — precomputation is the point.
- Never build a degree-10⁶ series with schoolbook convolution (10¹² operations); switch to FFT or to recurrence extraction.
