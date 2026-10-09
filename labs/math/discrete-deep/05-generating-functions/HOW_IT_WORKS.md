# How It Works: Solving a Recurrence With Its Generating Function

Worked problem: aₙ = aₙ₋₁ + 2aₙ₋₂ for n ≥ 2, with a₀ = 1, a₁ = 3. Find a closed form for aₙ.

## 1. Attach the GF

Define A(x) = Σ_{n≥0} aₙxⁿ. The sequence is the object; A(x) is its name tag. Goal: find a closed-form expression for A(x), then read off coefficients.

## 2. Multiply the Recurrence by xⁿ and Sum

Sum over n ≥ 2:

Σ_{n≥2} aₙxⁿ = Σ_{n≥2} aₙ₋₁xⁿ + 2·Σ_{n≥2} aₙ₋₂xⁿ

Each side in terms of A(x):

- Left: A(x) − a₀ − a₁x = A(x) − 1 − 3x
- First right term: x·Σ_{n≥2} aₙ₋₁x^{n−1} = x(A(x) − a₀) = x(A(x) − 1)
- Second right term: 2x²·Σ_{n≥2} aₙ₋₂x^{n−2} = 2x²A(x)

The index shift is the whole technique: multiplying by xⁿ and re-indexing turns "lag by k" into "multiply by xᵏ."

## 3. Solve the Algebraic Equation for A(x)

```
A − 1 − 3x = x(A − 1) + 2x²A
A − 1 − 3x = xA − x + 2x²A
A(1 − x − 2x²) = 1 − x + 3x ... careful: bring constants right:
A(1 − x − 2x²) = 1 + 3x − x = 1 + 2x
A(x) = (1 + 2x) / (1 − x − 2x²)
```

The denominator Q(x) = 1 − x − 2x² encodes the recurrence; the numerator P(x) = 1 + 2x encodes the seeds a₀ = 1, a₁ = 3. (Sanity: [x⁰]P/Q = 1 ✓ since Q(0) = 1.)

## 4. Factor and Split (Partial Fractions)

1 − x − 2x² = (1 − 2x)(1 + x). So

A(x) = (1 + 2x)/[(1 − 2x)(1 + x)] = c₁/(1 − 2x) + c₂/(1 + x)

Solve 1 + 2x = c₁(1 + x) + c₂(1 − 2x): constants → c₁ + c₂ = 1; x-coefficients → c₁ − 2c₂ = 2. Subtract: 3c₂ = −1 → c₂ = −1/3, c₁ = 4/3.

## 5. Expand Each Piece as a Geometric Series

- 4/3 · 1/(1 − 2x) = (4/3)·Σ 2ⁿxⁿ
- −1/3 · 1/(1 + x) = −(1/3)·Σ (−1)ⁿxⁿ

Therefore **aₙ = (4·2ⁿ − (−1)ⁿ)/3**.

## 6. Verify Against the Recurrence (by Hand)

- a₀ = (4·1 − 1)/3 = 1 ✓
- a₁ = (4·2 − (−1))/3 = 9/3 = 3 ✓
- a₂ = (4·4 − 1)/3 = 15/3 = 5. Recurrence: a₂ = a₁ + 2a₀ = 3 + 2 = 5 ✓
- a₃ = (4·8 + 1)/3 = 33/3 = 11. Recurrence: 5 + 2·3 = 11 ✓
- a₄ = (4·16 − 1)/3 = 63/3 = 21. Recurrence: 11 + 2·5 = 21 ✓

Also read A(x) directly as a series: P/Q with Q = 1 − x − 2x² gives the recurrence aₙ = aₙ₋₁ + 2aₙ₋₂ from the denominator — confirming the round trip recurrence → GF → partial fractions → closed form → recurrence.

## 7. Why This Beats Unrolling

Unrolling the recurrence gives aₙ in terms of aₙ₋₂ (parity cases, doubling at each step → Θ(n) arithmetic with growing integers). The closed form evaluates one term with exponentiation by squaring: 2ⁿ in O(log n) multiplications, plus one division by 3 — Θ(log n) work for a single large n. The GF method also *discovered* the roots (2 and −1) as the recurrence's eigenmodes, which is exactly the characteristic-equation method in disguise: denominator 1 − x − 2x² ↔ characteristic r² − r − 2 = 0 with roots 2, −1.
