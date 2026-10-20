# Generating Functions — Flashcards (Verified Numbers)

Each number below appeared in an executed run captured in CODE_DEEP_DIVE.md.

### Card 1
**Front**: What does [xⁿ] of an ordinary GF denote?
**Back**: The exact count of weight-n objects. Extraction is integer
arithmetic in this lab: (1+x)⁴ printed 1, 4, 6, 4, 1, sum 16 = 2⁴.

### Card 2
**Front**: The product rule, semantically?
**Back**: [xⁿ](A·B) counts pairs (object of type A, object of type B)
with weights summing to n; the cross-terms aᵢxⁱ · bⱼxʲ land at n iff
i + j = n.

### Card 3
**Front**: Sum of coefficients of a product?
**Back**: Multiplies: A(1)·B(1). Run pair: (1+x)(1+x+x²) printed sum 6
against factors 2 · 3 = 6.

### Card 4
**Front**: Expand (1+x+x²)³?
**Back**: 1, 3, 6, 7, 6, 3, 1 — [x³] = 7 is six perms of (0,1,2) plus
(1,1,1); coefficient sum 27 = 3³ printed against the literal power.

### Card 5
**Front**: Two-dice totals as a coefficient row?
**Back**: 1, 2, 3, 4, 5, 6, 5, 4, 3, 2, 1 for totals 2..12, sum 36 =
6²; [x⁷] = 6 ordered pairs; [x¹] = 0.

### Card 6
**Front**: Which single coefficient is the dice apex and why?
**Back**: [x⁷] = 6, the maximum, from (1,6),(2,5),(3,4),(4,3),(5,2),
(6,1) — six distinct diagonals, each diagonal contributing its length.

### Card 7
**Front**: GF of the partition numbers?
**Back**: 1/∏_{k≥1}(1−xᵏ); the recurrence p(n) = Σ p(n−k), p(0) = 1,
printed 1, 1, 2, 3, 5, 7, 11, 15, 22, 30, 42, 56, 77 for n = 0..12.

### Card 8
**Front**: p(10) and its cross-check?
**Back**: 42 by the GF and 42 by independent brute-force partition
enumeration — both printed. p(12) = 77 likewise confirmed.

### Card 9
**Front**: Euler's distinct = odd identity, run-numbers?
**Back**: n = 6..10: distinct 4, 5, 6, 8, 10 = odd-parts 4, 5, 6, 8,
10, all five rows equal True. Cause: ∏(1+xᵏ) = ∏(1−x²ᵏ)/(1−xᵏ)
telescoping the even factors.

### Card 10
**Front**: The DP that animates 1/∏(1−xᵏ)?
**Back**: For k = 1..N, for i = k..N add p[i−k] to p[i] — each factor
"any number of parts of size k" is the inner forward pass (the
distinct-parts version just runs i downward).

### Card 11
**Front**: Ways to pay 10 with coins {1, 2, 5}?
**Back**: 10 ways, printed in the table 0..10 as
1, 1, 2, 2, 3, 4, 5, 6, 7, 8, 10, with the brute triple list showing
all ten (x₁, x₂, x₅) witnesses.

### Card 12
**Front**: What does convergence NOT matter for here?
**Back**: Everything is a formal coefficient: the engine multiplies
polynomial arrays; x is a bookkeeping symbol and [xⁿ] an exact integer
operator — no floating point anywhere in the two programs.
