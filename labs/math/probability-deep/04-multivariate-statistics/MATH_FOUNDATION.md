# Multivariate Statistics — Math Foundation

Executed arithmetic only (Python `fractions`, transcripts in
CODE_DEEP_DIVE.md). The joint table below is the lab's centerpiece.

## 1. A Four-Cell Joint PMF, Read Fully
Table on {0, 1} × {0, 1}:
P(0,0) = 1/8, P(0,1) = 3/8, P(1,0) = 3/8, P(1,1) = 1/8.
Run check: total mass 1. Marginals observed: P(X) = [1/2, 1/2] and
P(Y) = [1/2, 1/2]. Both variables are fair coins by their own axis;
dependence hides in the cell pairing, not the axes.

## 2. The Product Moment and Covariance, Exact
Observed: E[X] = 1/2, E[Y] = 1/2, E[XY] = 1/8 (the mass at (1,1) — the
only cell where the product is nonzero). Variances: Var(X) = Var(Y) =
1/4 (indicators: second moment equals mean). Covariance:
E[XY] − E[X] E[Y] = 1/8 − 1/4 = −1/8 exactly. Sign certified: the run
printed cov negative True.

## 3. Correlation Recovered in Closed Form
With σ_X σ_Y = 1/4 (square root of 1/16 in exact rational terrain):
ρ = (−1/8)/(1/4) = −1/2. Machine check of the normalization —
cov^2 == (1/4) · VarX · VarY printed True — confirms |ρ| = 1/2 <= 1
with equality nowhere attained. Negative association: X = 1 makes Y = 0
three times as likely as Y = 1 (cells 3/8 vs 1/8 after rescaling).

## 4. Conditional Rows of the Table
Condition on X = 1: preserve cells (1,0) = 3/8 and (1,1) = 1/8, divide
by P(X = 1) = 1/2 → conditional masses 3/4 and 1/4. Condition on X = 0
instead: 1/4 and 3/4. The row flip is the −1/2 correlation in table
form — conditioning visibly reverses Y's favorite value.

## 5. Var(aX + bY): Formula Directly Checked
Take a = 2, b = 3 on the four-cell table. Observed: direct variance of
W = 2X + 3Y from its own pushed-forward values equals 7/4; the formula
route 4·VarX + 9·VarY + 12·Cov = 1 + 9/4 − 3/2 = 7/4 matches, and the
run printed `match: True`. The cross term 2ab·Cov contributes −3/2,
which is the whole story of correlated sums.

## 6. Zero Covariance Without Independence — The Quadratic Trap
New variables: X uniform on {−1, 0, 1}, Y = X^2. Observed: E[X] = 0,
E[Y] = 2/3, E[XY] = E[X^3] = 0, hence Cov = 0 (executed). Dependence
certified in the same run: P(X = −1, Y = 1) = 1/3 against the
independence product P(X = −1) P(Y = 1) = 2/9 — a violated cell.
Covariance was blind to the cubic pattern; only asking about the cell
caught it.

## 7. Sum With a Curved Partner, Closed Form Strengthened
Same quadratic setting: W = X + X^2. Observed directly, from pushed
values on the three points: Var(W) = 8/9. The formula route —
( E[X^4] − (E[X])^2 ) + ( E[X^4] − (E[Y])^2 ) + 2·0 =
2/3 + 2/9 = 8/9 — printed equal to the direct value. Bilinear algebra
works on dependent partners too; it just cannot see their dependence.
