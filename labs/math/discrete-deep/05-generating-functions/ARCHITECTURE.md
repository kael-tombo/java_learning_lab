# Architecture: Generating Function Code

## Separate Specification From Extraction

A GF library has three layers; collapsing them is what makes the code unreadable:

1. **Specification** — construct the series symbolically from structure: `Sequence.compose(coins)` → the product Π 1/(1−x^c); `recurrence(coeffs)` → 1/(1 − Σqᵢxⁱ); `exp(G)` for sets-of components. This layer outputs a *representation* (rational P/Q, product of factors, or explicit coefficient array), never a number.
2. **Extraction** — choose the algorithm by representation: rational → linear recurrence loop Θ(k·n); product of geometric factors → DP over factors Θ(Σ n/cᵢ); general series → truncated convolution Θ(n²) (or FFT Θ(n log n)).
3. **Read-out** — one function that converts internal coefficients to the caller's type (`long` with overflow check, or `BigInteger`), keeping EGF-vs-OGF conversion (the ×n! factor) at a single chokepoint.

The payoff: swapping extraction strategies never touches the specification, and every answer has a stated derivation path.

## Representation: Rational vs Truncated Series

```java
sealed interface Series {}
record Rational(BigInteger[] p, BigInteger[] q) implements Series {}   // P(x)/Q(x)
record Truncated(BigInteger[] c) implements Series {}                  // coefficients mod x^(N+1)
```

`Rational` is compact (2k+2 numbers regardless of n) and supports O(1)-per-term extraction; `Truncated` is explicit and supports multiplication/addition of non-rational GFs (coin products, exp/log). Convert Rational → Truncated by recurrence expansion; the reverse (fit a Truncated to a Rational) is Berlekamp–Massey — only do it deliberately, never silently.

## Overflow and Coefficient Type Policy

Counts overflow quickly (Catalan past `long` at n = 36, p(100) exceeds `int`). Policy: the library is `BigInteger` end-to-end; a checked adapter (`toLongExact`) throws `ArithmeticException` at the boundary. This costs performance only in the inner loop of Θ(n²) convolutions — and for the n where that matters, the numbers were too big for `long` anyway.

## Reuse Across the Course

- Lab 03 hands off recurrences (Fibonacci-like state machines) — those become `Rational` specs here.
- Lab 06 uses factorials and modular arithmetic; extracting coefficients mod p (Lucas/finite-field GFs) is the same read-out with a modulus policy attached.
- The security file's LFSR/linear-complexity work uses Berlekamp–Massey on `Truncated` — include it as a first-class algorithm, not a footnote, because its input/output contract (2L bits → shortest Q) is exactly the specification/extraction split.

## Testing Architecture

- **Oracle:** compute coefficients two independent ways — rational recurrence vs explicit truncated multiplication — and assert equality for n ≤ 200 on every rational spec (this caught the off-by-one seed errors listed in DEBUGGING).
- **Known sequences as fixtures:** Fibonacci (1,1,2,3,5), Catalan (1,1,2,5,14,42), coin change (25¢ → 13, 50¢ → 50), Bell via exp(eˣ−1) (1,1,2,5,15,52).
- **Stability property:** coefficients below degree d are unchanged when truncation N increases (N = 50 vs N = 100 must agree on the first 50) — this fails loudly on loop-bound bugs.
- **Ring-law property tests:** on random rational pairs, check F·G = G·F, F·(1/F) = 1, and (F·G)·H = F·(G·H) at degree 30 — algebraic laws are cheap to verify and catch indexing asymmetry immediately.
