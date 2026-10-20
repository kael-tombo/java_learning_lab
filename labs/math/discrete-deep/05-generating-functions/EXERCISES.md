# Exercises — Generating Functions

Five problems with worked solutions; numbers quoted from the captured
runs in CODE_DEEP_DIVE.md.

## Problem 1. Extract by Hand, Then Trust the Engine

State all coefficients of (1+x)⁴ and their sum; state [x³] of
(1+x+x²)³ and characterize its witnesses.

**Solution**: Run array: 1, 4, 6, 4, 1, summing to 16 = 2⁴ — the
C(4,k) row. [x³] of the trinomial cube printed 7: the choices are the
six permutations of (0,1,2) plus the (1,1,1) entry, i.e. 3 + 3 + 1.
Full row: 1, 3, 6, 7, 6, 3, 1 with coefficient sum 27 = 3³ (printed
equal both ways).

## Problem 2. The x = 1 Evaluation Homomorphism

Why does the sum of coefficients multiply? Verify on
(1+x)(1+x+x²).

**Solution**: Substituting x = 1 turns Σ aₖ into A(1), and
(A·B)(1) = A(1)·B(1) is just multiplication respecting evaluation.
Run printed both: sum 6 for the product, and 2·3 = 6 for the factors.
Any missed cross-term would break this ledger instantly.

## Problem 3. Dice Totals as Coefficients

Give the two-dice count of each total and the total-accounting line.

**Solution**: Printed row 2..12: 1, 2, 3, 4, 5, 6, 5, 4, 3, 2, 1,
summing to 36. [x⁷] = 6 counts ordered pairs (1,6),(2,5),(3,4),(4,3),
(5,2),(6,1); [x²] and [x¹²] are 1 apiece; [x¹] = 0 cannot arise from
two positive dice.

## Problem 4. Change for 10 Under {1, 2, 5}

Count ways and enumerate them against the GF table.

**Solution**: The DP run printed ways for amounts 0..10 as
1, 1, 2, 2, 3, 4, 5, 6, 7, 8, 10, so exactly 10 ways for ten. The
brute triple scan substantiates each: (0,0,2), (0,5,0), (1,2,1),
(2,4,0), (3,1,1), (4,3,0), (5,0,1), (6,2,0), (8,1,0), (10,0,0) — the
coefficient of x¹⁰ in the product of the three unary parts is 10.

## Problem 5. Partitions and Euler's Collapse

Report p(10) and p(12) by the GF, verify by brute force, and exhibit
the distinct = odd identity at n = 9.

**Solution**: GF row (run-printed): 1, 1, 2, 3, 5, 7, 11, 15, 22, 30,
42, 56, 77 for n = 0..12, so p(10) = 42 and p(12) = 77; the brute
partitions counter printed 42 and 77 in the same columns. At n = 9:
distinct-part count 8 equals odd-part count 8 (run equal True, on all
five displayed rows 4, 5, 6, 8, 10) — the telescoping (1+xᵏ) =
(1−x²ᵏ)/(1−xᵏ) does in one algebra move what enumeration does in
seven.
