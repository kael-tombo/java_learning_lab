# Common Mistakes — Linear Algebra

Every item is anchored to a number that a run in this lab actually
produced or refuted.

## 1. Eliminating Along the Wrong Axis

Elimination acts on ROWS: row_j − m·row_i. A frequent slip is
subtracting multiples of row_i from COLUMN entries (i.e. operating
as if updating columns), which silently transposes the meaning of
the multipliers and produces a lower-triangular mess rather than an
upper-triangular system. The demo run collected multipliers
[−3/2, −1, 4] as row effects — an axis error there would have put
the −3/2 in a column and cascaded into nonsense pivots.

## 2. Row Swap Blindness

Dividing by zero is not modest — it is fatal. The exercise system
x + y + z = 6, 2x + 2y + z = 9, 2x + y + 2z = 10 left a zero in the
(2,2) slot, and without the printed row swap
(`zero pivot at column 2 -> swap rows 2 and 3`) the exact solve is
impossible to continue; float code "passes" instead by hiding
divisions near zero and returning garbage with plausible residuals.

## 3. Verifying Identities in Floats Instead of Exactly

The trace law trace(AB) = trace(BA) is an equality of rationals; a
float comparison "0.9999999 ≈ 1" can hide a coding bug (e.g. slicing
trace(BA) with only two of its three diagonal indices — exactly the
bug the first draft of this lab's program made, printing False).
Run over `Fraction`: here True/False are the whole story.

## 4. Treating Trace and Determinant as Interchangeable Summaries

For eigenvalues λ₁, λ₂ the trace reports λ₁ + λ₂ and det reports
λ₁λ₂ — different functions with different zeros. Taking "trace 4,
det 3" (the [[2, 1], [1, 2]] pair) and quoting det as λ₁ + λ₂ would
flip the eigenpair; the quadratic λ² − (trace)λ + det recovers
{1, 3} or the irrational {2 ± √2} for {4, 2}.

## 5. Certifying an Eigenvector in Reverse

For [[3, 1], [1, 1]] with λ = 2 ± √2 the vector (1, λ−3) is exact,
and the residual printed 0E−23 at 24 decimals. Reverse error is the
common mistake: taking two floating decimal places "close to λ"
(e.g. 0.58) and believing a moderate residual certifies the pair.
The exponential root of trust was λ² = 4λ − 2, exact; residuals
near zero only corroborate.

## 6. A Small Residual from an Ill-Conditioned Solve

For A = [[1, 2], [2, 4001/1000]] the exact solutions to
b₂ ∈ {6.001, 6.002, 6.004} were (1, 1), (−1, 2), (−5, 4): b changes
by 0.001 and the answer by 2. The inverse entries
[[4001, −2000], [−2000, 1000]] were verified to satisfy A·A⁻¹ = I,
and κ₁ = 36012001/1000 = 36012.001. Interpreting float solves here
as "residual tiny, therefore answer good" is bogus: the exact answer
itself swings wildly, so no residual can referee the input scale.

## 7. Applying the Multiplier to the Pivot Row

The update never touches the pivot row; only "slave" rows absorb
multiples. Applying the multiplier to row 1 (the pivot row) mutates
future multipliers — every m_ij would use the wrong denominators —
which pumps silently growing errors into otherwise identical code.
