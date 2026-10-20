# Generating Functions — Theory

## 1. What an Ordinary Generating Function Says

A sequence a₀, a₁, a₂, ... becomes A(x) = Σ aₖxᵏ. The point is not
convergence: x is a formal placeholder, and multiplication in the
polynomial ring carries every counting rule. [xⁿ]A(x) — the coefficient
operator — reads off the number of weight-n objects. The lab runs exact
integer multiplication, so every coefficient below is an observed
integer, never a floating-point artifact.

## 2. The Product Rule, With Its Semantics Made Exact

If A(x) counts objects of type 1 and B(x) objects of type 2, then
A(x)·B(x) counts PAIRS with total weight n, because the term
aᵢxⁱ · bⱼxʲ lands at xⁿ exactly when i + j = n. Run-exhibited instance
of the sum-form: Σ coeff of (1+x)(1+x+x²) = 2·3 = 6 (printed both
sides). Setting x = 1 evaluates "all weights at once", which is why
coefficient sums multiply: (1+x)⁴ has coefficient sum 16 = 2⁴, not the
cube's 27 = 3³ obtained for (1+x+x²)³ — three choices three times.

## 3. Expansion Instances, Fully Extracted

(1+x)⁴: coefficients 1, 4, 6, 4, 1 (run printed the array; the sum 16
certifies 2⁴ outcomes). (1+x+x²)³: 1, 3, 6, 7, 6, 3, 1 — the central
coefficient [x³] = 7 counts triples from {0,1,2} summing to 3: the six
permutations of (0,1,2) plus (1,1,1), exactly 3 + 3 + 1 = 7. Sum of
all seven coefficients: 27 = 3³, printed against the literal power.
The engine multiplies; it does not approximate.

## 4. Dice as a Cross-Referenced Product

One fair die has GF D(x) = x + x² + ... + x⁶; two dice give D(x)² with
coefficients (totals 2..12): 1, 2, 3, 4, 5, 6, 5, 4, 3, 2, 1 — the run
printed the row and certified the sum 36. The apex [x⁷] = 6 counts the
six ordered pairs (1,6),(2,5),(3,4),(4,3),(5,2),(6,1); the extremes at
2 and 12 hold exactly one pair each. This row is the textbook picture
of convolution as multiplication.

## 5. Coefficients of 1/∏(1−xᵏ): Integer Partitions

The recurrence p(n) = Σ p(n−k) over k ≤ n, seeded p(0) = 1, IS the
coefficient rule of 1/∏_{k≥1}(1−xᵏ) — each factor contributes "zero or
more parts of size k". Run output, n = 0..12: 1, 1, 2, 3, 5, 7, 11,
15, 22, 30, 42, 56, 77, with p(10) = 42 confirmed by independent
brute-force partition enumeration (both printed 42; p(12) = 77
likewise). No closed form is needed at this scale — the GF is the
algorithm.

## 6. Euler's Distinct = Odd Theorem, Verified on Data

The two GFs ∏(1+xᵏ) and ∏ 1/(1−x^{2k−1}) multiply to the same series
because (1+xᵏ) = (1−x^{2k})/(1−xᵏ) and the even factors telescope.
Run check n = 6..10: distinct-part counts 4, 5, 6, 8, 10 equal
odd-part counts at every n (equal True on all five rows). This is an
identity-proving power the naive census cannot supply — one inequality
chain collapses both collections.

## 7. Making Change and the Program Plan

Coin system {1, 2, 5} up to amount 10: ways run 1, 1, 2, 2, 3, 4, 5,
6, 7, 8, 10, i.e. [x¹⁰] = 10, which the brute triple list substantiates:
(0,0,2), (0,5,0), (1,2,1), (2,4,0), (3,1,1), (4,3,0), (5,0,1),
(6,2,0), (8,1,0), (10,0,0). The lab's two programs: exact polynomial
multiplication with the x = 1 ledger, then the dice/coin/partition
battery with brute and Euler cross-checks.
