# Flashcards — Law of Large Numbers

## Theorem-Statement Cards

### Card 1
**Front**: State the weak law of large numbers with full hypotheses.
**Back**: If X1, X2, ... are i.i.d. with E[Xi] = μ and
Var(Xi) = σ^2 < ∞, then the sample mean X_n satisfies
P(|X_n − μ| >= ε) → 0 for every ε > 0.

### Card 2
**Front**: State Kolmogorov's strong law exactly.
**Back**: If X1, X2, ... are i.i.d. with E|X1| < ∞, then X_n → μ =
E[X1] with probability 1: P(lim_n X_n = μ) = 1 — no variance needed,
integrability is sharp.

### Card 3
**Front**: State Chebyshev's inequality.
**Back**: For any X with finite variance and t > 0:
P(|X − E[X]| >= t) <= Var(X) / t^2.

### Card 4
**Front**: State Markov's inequality and its required hypothesis.
**Back**: For a NONNEGATIVE X and a > 0: P(X >= a) <= E[X]/a; the
nonnegativity is essential, since truncation math needs the lower cut.

### Card 5
**Front**: State the first Borel–Cantelli lemma.
**Back**: If Σ_n P(A_n) < ∞, then P(A_n occurs infinitely often) = 0 —
summable tail budgets buy finitely many violations per sample path.

### Card 6
**Front**: State the central limit theorem (finite variance case).
**Back**: For i.i.d. summands with mean μ and σ^2 < ∞:
(S_n − nμ)/(σ√n) → Normal(0, 1) in distribution; typical fluctuation
scale of the mean is σ/√n.

## Concept Cards

### Card 7
**Front**: Weak vs strong law — what EXACTLY differs?
**Back**: Weak controls P(|X_n − μ| >= ε) at each fixed n; strong
controls violations along each realization (finitely many, almost
surely). Strong implies weak, not conversely.

### Card 8
**Front**: Variance of the sample mean of i.i.d. summands?
**Back**: Var(X_n) = σ^2/n exactly; for Bernoulli(1/2) that is 1/(4n)
— the 1/n clock (executed: 1/4 at n = 1, 1/1024 at n = 256).

### Card 9
**Front**: Why is E|X| < ∞ (not just finite E[X]) the strong-law
hypothesis?
**Back**: Interchange between mean and limit requires absolute
summability; Cauchy-type means fail to settle without it, matching the
heavy-tail crawl observed over 200000 draws.

## Judge-the-Number Cards

### Card 10
**Front**: n = 4, c = 1/2: Chebyshev bound vs exact probability?
**Back**: 1/4 vs 1/8 — envelope holds with a factor two to spare.

### Card 11
**Front**: Exponential(1): exact P(X >= 3)?
**Back**: e^{−3} = 0.049787068367863944 — below the Markov 1/3 and
Chebyshev 1/4 envelopes, both honest.
