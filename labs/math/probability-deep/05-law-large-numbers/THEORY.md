# Law of Large Numbers — Theory

## 1. Convergence in Probability — The Right Notion
X_n → X in probability means: for every ε > 0,
P(|X_n − X| >= ε) → 0 as n → ∞. Nothing says X_n = X for large n;
single samples remain wild. The laws of large numbers are theorems of
this kind for the sample mean X_n = (X1 + ... + Xn)/n of an i.i.d.
sample, and they are why averages are trustworthy instruments at all.

## 2. The Two Inequalities Everything Runs On
- Markov: for a NONNEGATIVE X and a > 0,
  P(X >= a) <= E[X]/a. Truncation algebra: E[X] >= a P(X >= a),
  since the expectation out-scales the tail indicator.
- Chebyshev: for any X with finite variance and t > 0,
  P(|X − E[X]| >= t) <= Var(X)/t^2. Apply Markov to the nonnegative
  variable (X − E[X])^2 with a = t^2 — a two-line proof, no extra
  hypotheses.

## 3. Weak Law of Large Numbers — Exact Statement
Let X1, X2, ... be i.i.d. with E[Xi] = μ and Var(Xi) = σ^2 < ∞. Set
X_n = (X1 + ... + Xn)/n. Then for every ε > 0:
  P(|X_n − μ| >= ε) → 0 as n → ∞.
Proof pattern in one breath: E[X_n] = μ exactly, Var(X_n) = σ^2/n by
the variance-algebra of independent summands, and Chebyshev with
t = ε gives P <= σ^2/(n ε^2) → 0. No independence relaxation is needed
for the variance step beyond pairwise uncorrelated sums.

## 4. Borel–Cantelli — The Statement Behind Almost Sure Claims
For events A1, A2, ...: if Σ_n P(A_n) < ∞, then P(A_n occurs
infinitely often) = 0. The lemma converts summable tail-probability
budgets into finitely-many-violations statements, which is exactly the
currency a strong law pays in.

## 5. Strong Law — Exact Statement
Kolmogorov's strong law: let X1, X2, ... be i.i.d. with
E|X1| < ∞ (integrability only, no variance assumed). Then
  X_n → μ = E[X1] with probability 1, i.e.,
  P(lim_n X_n = μ) = 1.
Probability 1 means: outside an exceptional event of total probability
zero, every realization settles — not just that violations become
unlikely, but that only finitely many occur along each sample path.

## 6. Weak vs Strong — Precisely What Differs
The weak law controls P(|X_n − μ| >= ε) AT each fixed n; the strong law
controls the total number of violations ALONG the realized sequence.
Strong implies weak, but the converse fails: sequences can violate at
densely spaced but sparse times while still failing to converge. The
strong law's hypothesis E|X| < ∞ is also the sharp one — means of
heavy-tailed variables (Cauchy-style) demonstrably refuse to settle.

## 7. Rate Note — What the CLT Adds
The central limit theorem, for i.i.d. summands with finite σ^2:
(a sum, centered and scaled) (S_n − nμ)/(σ√n) → Normal(0, 1) in
distribution. Numerically the typical fluctuation scale of X_n is
σ/√n — the 1/√n clock of the weak law upgraded from a bound to a
limit shape. Lab 06 reuses both facts for consistency of estimators.
