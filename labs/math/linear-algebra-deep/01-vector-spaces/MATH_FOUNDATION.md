# Vector Spaces — Math Foundation

All computations below were executed in exact rational arithmetic
(Python `fractions`) and the stated values are the observed outputs,
not hand derivations.

## 1. Span Membership Is a Linear System

Question: is (1,0,2) in span{(1,1,0),(0,1,1)}?

Set a(1,1,0) + b(0,1,1) = (1,0,2) and read coordinate-wise:

- First coordinate: a = 1.
- Second: a + b = 0, so b = −1.
- Third: b = −1 against required 2. Contradiction.

**Not in the span.** Contrast (1,2,1): a = 1, b = 1, third coordinate
1 = 1. **In the span.** One sign flip in the target decides membership —
span questions are solved systems, never inspections.

## 2. Determinant Test for Independence

{(1,2,3), (4,5,6), (7,8,10)}: determinant = **−3** (exact), hence
independent. Compare the textbook triple {(1,2,3),(4,5,6),(7,8,9)}:
determinant = **0**, dependent (third row = 2·second − first: check
2(4,5,6) − (1,2,3) = (7,8,9)). A single entry (9 → 10) moves the
determinant off zero — dependence in R³ is a knife-edge condition,
det = 0, and this pair shows both sides of it.

## 3. Rank–Nullity With Exhibited Bases

T: R⁴ → R³, rows (1,0,2,−1), (0,1,1,3), (2,1,5,1).

- Row dependence: 2·(1,0,2,−1) + (0,1,1,3) = (2,1,5,1) exactly → the
  third row adds nothing → rank = 2.
- Null space: free x₃, x₄. Setting (x₃,x₄) = (1,0) gives (−2,−1,1,0);
  (0,1) gives (1,−3,0,1). Dot products against both rows are 0,0 and
  0,0 respectively (verified) → nullity = 2.
- 2 + 2 = 4 = dim R⁴. ∎

## 4. Coordinates in a Nonstandard Basis

v = (3,7), basis {(1,1),(1,−1)}: solve c₁ + c₂ = 3, c₁ − c₂ = 7 →
c₁ = 5, c₂ = −2. Check: 5(1,1) − 2(1,−1) = (5−2, 5+2) = (3,7). ∎
Coordinates are solutions, and the solution here is integral — a
property of this basis (determinant −2 divides evenly), not a general
promise.
