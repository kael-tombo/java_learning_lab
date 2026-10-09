# Interview: Generating Functions

## Conceptual Questions

**Q: What *is* a generating function, in one sentence?**
A: A way of writing a sequence (a₀, a₁, a₂, …) as the coefficient list of a formal power series a₀ + a₁x + a₂x² + …, so that operations on sequences (especially convolution) become algebraic operations on series (multiplication).

**Q: Why does multiplying two generating functions convolve their coefficients?**
A: Because [xⁿ](A·B) = Σ_{i+j=n} aᵢbⱼ — collecting all pairs whose indices sum to n is exactly the sum over ways to split n into two parts. Structurally: building a size-n object as (part of size i) + (part of size n−i) requires summing over every i, which is what the product does automatically.

**Q: Ordinary GF vs exponential GF — when do you use which?**
A: OGF for unlabeled/sequence-shaped structures (partitions, binary strings, coin change); EGF A(x) = Σ aₙxⁿ/n! for labeled structures (permutations, labeled graphs, mappings), where the n! divides out the ordering of labels. Mixing them gives answers correct only up to a factor of n!.

**Q: State the equivalence theorem and why it matters.**
A: A sequence has a rational GF P/Q (Q(0) ≠ 0) iff it satisfies a constant-coefficient linear recurrence given by Q: from Q = 1 − q₁x − … − qₖxᵏ, aₙ = q₁aₙ₋₁ + … + qₖaₙ₋ₖ. It matters because it makes recurrences and rational functions interchangeable — you can solve a recurrence by algebra, or generate a sequence by recurrence, whichever direction the problem hands you.

**Q: Solve aₙ = aₙ₋₁ + 2aₙ₋₂, a₀ = 1, a₁ = 3 via GFs.**
A: A(x) = (1 + 2x)/(1 − x − 2x²) = (1+2x)/((1−2x)(1+x)) = (4/3)/(1−2x) − (1/3)/(1+x), so aₙ = (4·2ⁿ − (−1)ⁿ)/3: 1, 3, 5, 11, 21, 43… Check a₂ = 3 + 2·1 = 5 ✓.

**Q: How many ways to make 50¢ with US coins? How do you get it?**
A: 50 ways (49 without using a half-dollar, plus the one 50¢ piece). From G(x) = 1/[(1−x)(1−x⁵)(1−x¹⁰)(1−x²⁵)(1−x⁵⁰)], extract [x⁵⁰] by folding one coin factor at a time: 1 → 11 → 36 → 49 → 50. Check at 25¢: 13 ways.

## Mechanical Questions

**Q: Partial fractions for (2x)/(1−x)(1−2x) and the coefficient formula.**
A: 2x = A(1−2x) + B(1−x). x = 0 → 0 = A + B; coefficient of x: 2 = −2A − B. Solving: A = −2, B = 2 → aₙ = −2·1ⁿ + 2·2ⁿ = 2^{n+1} − 2. Always do long division first if deg(numerator) ≥ deg(denominator).

**Q: GF for the number of binary strings with no two consecutive 0s.**
A: Recurrence aₙ = aₙ₋₁ + aₙ₋₂ (append 1, or append 10) with a₀ = 1, a₁ = 2 → A(x) = (1 + x)/(1 − x − x²) → aₙ = Fₙ₊₂: 1, 2, 3, 5, 8, 13. Same denominator as Fibonacci; the numerator holds the seeds.

**Q: Compute the 1000th Fibonacci number efficiently.**
A: Fast doubling, O(log n) multiplications: F₂ₖ = Fₖ(2Fₖ₊₁ − Fₖ), F₂ₖ₊₁ = Fₖ₊₁² + Fₖ², recursing on the bits of n — versus Θ(n) iterative additions. (Exact big-integer cost: O(M(log n)) with fast multiplication.) The GF view: 1/(1−x−x²) with root powers evaluated by squaring.

**Q: What is exp() used for in EGFs?**
A: "Sets of components": if C(x) is the EGF for connected labeled structures, then exp(C(x)) is the EGF for structures that are sets of them (e.g., exp(eˣ − 1) → set partitions/Bell numbers; exp of the tree EGF → forests). Exponentiation of an EGF encodes unordered, labeled union — the complement to 1/(1−C) for *sequences* of components.

## Applied Questions

**Q: Stream cipher keystream passes through an LFSR; what does the GF theory say?**
A: The keystream satisfies a linear recurrence of length L, so its GF is rational of degree L (Berlekamp–Massey: 2L output bits reveal the shortest such Q). An attacker then predicts the sequence — hence keystreams must be *nonlinear* combinations so no low-degree rational GF (short recurrence) describes them.

**Q: A client asks for "all valid schedules of length 20"; you must reject before computing. What do you do?**
A: Build the GF from the constraints, extract or bound the coefficient [x²⁰] cheaply (rational → Θ(k·20) recurrence loop; product of factors → DP over factors), compare against a response budget, and reject if over — never start generation and hope. This is the spec-then-extract split from lab 05's ARCHITECTURE.

**Q: How would you test a GF library?**
A: (1) Dual-path oracle: for every rational spec, compute coefficients by recurrence *and* by truncated multiplication, assert equal for n ≤ 200. (2) Known fixtures: Fibonacci, Catalan 1,1,2,5,14,42, coin change 13 at 25¢ / 50 at 50¢, Bell numbers 1,1,2,5,15,52 via exp(eˣ−1). (3) Truncation stability: degree-50 coefficients identical whether N = 50 or N = 100. (4) Ring laws: F·(1/F) = 1, commutativity, associativity on random rational pairs. (5) Overflow: `toLongExact` throws past Catalan n = 36 rather than wrapping.
