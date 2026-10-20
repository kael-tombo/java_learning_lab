# Common Mistakes — Information Theory

Each mistake cites numbers from this lab's runs that expose it.

## 1. Log-Base Confusion Mid-Computation

Entropy's numeric value depends on the base: 7/4 bits becomes
(7/4)·ln 2 ≈ 1.2130 nats, and swapping bases halfway leaves a "gap"
of ln 2 ≈ 0.6931 between code lengths and entropy that does not
exist. Kraft's sum Σ2^(−ℓ) is only coherent in bits; a mixed-base
audit can sum to 0.9987 or 1.0012 and masquerade as rounding. The
lab's runs used log2 exclusively — commit to one base per document.

## 2. Settling Independence With a Single Cell

Marginalization in the exhibit printed pX = (1/2, 1/2) and
pY = (3/4, 1/4), whose product table is (pXpY)(x, y) with cells
(3/8, 1/8, 3/8, 1/8). Checking only cell (1, 1) — mass 1/4 against
1/8 — shows dependence there; but cell (0, 1) shows 0 against 1/8
and cell (0, 0) shows 1/2 against 3/8, with different intensities
whose total is the printed MI 0.311278. Declaring a verdict from
one cell (or quoting "cell minus product" as if it were KL) is the
error: dependence is a joint-property verdict over ALL cells, which
is exactly why the run's double sum iterated every nonzero cell.

## 3. Reading Huffman's Positive Gap as Incompetence

The (2/5, 1/5, 1/5, 1/10, 1/10) alphabet's gap printed 0.07807190511263773.
Huffman is provably optimal among prefix codes; the gap is not a
bug but the price of prefix feasibility when masses are not all
dyadic (only then does the run's gap shrink to exactly 0.0, as it
did for (1/2, 1/4, 1/8, 1/8)). Tuning the merge order cannot close
it; only a different alphabet can.

## 4. Assuming KL Is Symmetric From Close Floats

The exact pair printed 1/2 versus 5/8 — clearly directional. But the
float pair gave 0.188722 and 0.207519, uncomfortably close; rounding
"1/2 vs 5/8" floats to 2 decimals would mislabel them as equal.
Whenever distributions trade mass in opposite directions the two
prices differ; equality holds only for the coincidentally balanced
structures, and the exact-arithmetic path side-steps the trap.

## 5. Demanding MI = 0 Requires Unrelated Variables

MI(X, Z) = 0.0 in the XOR exhibit despite Z = X ⊕ Y being a
FUNCTION of X and Y. MI measures the log-surprise of the joint
versus the product of marginals — zero means exactly the factorized
joint, which the 1/4-cells table satisfies. Concluding "MI = 0 means
no relationship" is backwards: MI is blind to functional
determinacy that marginalizes to uniformity.

## 6. Summing p·log p Over the Zero Cells Incorrectly

The exhibit table's zero cell (0,1) contributes 0 bits (its mass is
zero), and dropping it before the float loop is REQUIRED —
0·log2(0) is an indeterminate product, not a summand. The run's
guard `if v > 0` exists for this; including the zero cell via a
naive comprehension raises a ValueError (log2(0) is a domain
error) or, worse, a NaN that silently propagates into MI.

## 7. Confusing H(Y|X) = 0 with Independence

In the exhibit H(Y|X) printed 1/2 exactly, nonzero — yet X and Y
are clearly dependent (the (0,0) cell dominates). Conversely the
fair-echo construction makes H(Y|X = 0) = 0 for that one conditioning
slice while still H(Y|X) = 1/2 overall. Conditional entropy of a
mix is the mass-weighted average, never "one slice's value":
confusing the two misquotes MI by the difference between 0.5 and 0.
