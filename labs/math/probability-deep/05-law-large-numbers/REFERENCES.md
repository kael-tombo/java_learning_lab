# References: Law of Large Numbers and CLT

## Primary sources
- **J. Bernoulli**, *Ars Conjectandi*, Basel, 1713, part IV — first weak law of large numbers (and his hand-computed trial counts).
- **D. Bernoulli**, "Specimen theoriae novae de mensura sortis", *Comment. Acad. Sci. Imp. Petropolit.* 5:175–192, 1738 (read 1731) — St. Petersburg paradox; the case where expectation, hence the LLN, does not exist.
- **A. de Moivre**, *The Doctrine of Chances*, 3rd ed., London, 1756 — normal approximation to the binomial.
- **P.-S. Laplace**, *Théorie analytique des probabilités*, Courcier, 1812 — CLT for non-identical summands, Fourier methods.
- **P. L. Chebyshev**, "Sur une généralisation du théorème de Laplace", *C. R. Acad. Sci. Paris* 61:355–359, 1865 / his 1867 papers — moment inequality and the first rigorous LLN proof.
- **A. A. Markov**, *Calculation of Probabilities*, St. Petersburg, 1897 (Russian) — extension to higher moments.
- **A. M. Lyapunov**, *Sur une proposition de la théorie des probabilités*, Bull. Acad. Sci. St. Pétersbourg, 1901 — first rigorous CLT via characteristic functions.
- **J. W. Lindeberg**, "Eine neue Methode... ", *Math. Z.* 15:215–225, 1922 — the Lindeberg condition.
- **A. N. Kolmogorov**, "Über das Gesetz der großen Zahlen", *Math. Ann.* 101:1–11, 1929, and "Über die Kollokation..." (SLLN, 1930) — the strong law for i.i.d. finite-mean variables.
- **P. Hartman & A. Wintner**, "On the law of large numbers", *Amer. J. Math.* 63:351–360, 1941 — SLLN holds iff E|X| < ∞.
- **P. Lévy**, *Théorie de l'addition des variables aléatoires*, Gauthier-Villars, Paris, 1937 (collecting his 1925–1937 papers) — stable laws as the true limit theory; the Gaussian is only the α = 2 case.

## Textbooks
- **W. Feller**, *An Introduction to Probability Theory and Its Applications*, vol. 1, 2nd ed., Wiley, 1968 — ch. VIII–X: LLN, CLT, geometric interpretation; vol. 2 (1971) for stable laws and renewal theory.
- **B. V. Gnedenko & A. N. Kolmogorov**, *Limit Distributions for Sums of Independent Random Variables*, Addison-Wesley, 1954 — the definitive stable-limit reference.
- **R. Durrett**, *Probability: Theory and Examples*, 5th ed., Cambridge UP, 2019 — ch. 4: SLLN, CLT, moment bounds, with clean proofs.
- **P. Billingsley**, *Probability and Measure*, 3rd ed., Wiley, 1995 — convergence in distribution/probability/a.s. and their relationships.
- **P. Petrov**, *Sums of Independent Random Variables*, Springer, 1975 — Berry–Esseen bounds with explicit constants.
- **R. B. Ash**, *Basic Probability Theory*, Wiley, 1970 — excellent treatment of the three convergence modes.

## Heavy tails and practice
- **S. I. Resnick**, *Heavy-Tail Phenomena: Probabilistic and Statistical Modeling*, Springer, 2007 — when the CLT fails: stable laws, regular variation, why averages of financial/telecom data misbehave.
- **D. Siegmund**, *Sequential Analysis: Tests and Confidence Intervals*, Springer, 1985 — what changes when n is a stopping time.
- **L. Wasserman**, *All of Statistics*, Springer, 2004, ch. 5 — CLT and its use in confidence intervals.

## Formatted entries for the papers cited above

- Kolmogorov, A. N. (1929). Über das Gesetz der großen Zahlen. *Mathematische Annalen*, 101, 1–11. — the 0–1 law and the modern formulation of the LLNs.
- Hartman, P., & Wintner, A. (1941). On the law of large numbers. *American Journal of Mathematics*, 63(2), 351–360. — SLLN holds if and only if E|X| < ∞.
- Esseen, C.-G. (1945). On the distribution function of sums of independent random variables. *Acta Mathematica*, 77, 1–9. — the Berry–Esseen theorem; the constant C lives here.
- Shevtsova, I. G. (2011). On the absolute constant in the Berry–Esseen inequality. *Theory of Probability and Its Applications*, 56(1), 162–164. — the current C ≤ 0.4748.
- Khinchin, A. (1929). Sur la loi des grands nombres. *Comptes Rendus de l'Académie des Sciences de Paris*, 189, 477–479. — WLLN under E|X| < ∞ alone.

**Which to open first:** Esseen 1945 if you care about rates (it is where the ρ/σ³ ratio enters), Hartman–Wintner 1941 if you care about the exact boundary of the SLLN, Feller vol. 1 ch. VIII–X for everything as a worked textbook treatment. The Shevtsova constant matters only if you quote C numerically — otherwise state "some universal C" and you are never wrong.
