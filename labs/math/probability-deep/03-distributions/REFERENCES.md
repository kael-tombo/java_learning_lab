# References: Probability Distributions

## Primary sources
- **J. Bernoulli**, *Ars Conjectandi*, Basel, 1713 — binomial calculus.
- **A. de Moivre**, *The Doctrine of Chances*, 3rd ed., London, 1756 — normal approximation to the binomial.
- **S.-D. Poisson**, *Recherches sur la probabilité des jugements en matière criminelle et en matière civile*, Bachelier, 1837 — the Poisson distribution and "loi des grands nombres."
- **W. S. Gosset ("Student")**, "The probable error of a mean", *Biometrika* 6(1):1–25, 1908 — the t distribution.
- **K. Pearson**, "On the criterion... goodness of fit", *Phil. Mag.* 50:157–175, 1900 — the χ² test that made distributions checkable.
- **R. A. Fisher**, *Statistical Methods for Research Workers*, Oliver & Boyd, Edinburgh, 1925 — χ², t, F tables for practitioners.

## Compedia of families
- **N. L. Johnson, S. Kotz & N. Balakrishnan**, *Continuous Univariate Distributions*, 2nd ed., vols 1–2, Wiley, 1994 — the standard encyclopedia: 100+ families with derivations, relations and history.
- **S. Kotz, N. Balakrishnan & N. L. Johnson**, *Discrete Multivariate Distributions*, Wiley, 1997 — multinomial, negative multinomial and their kin.
- **E. J. Gumbel**, *Statistics of Extremes*, Columbia UP, 1958 (1st ed. 1958; orig. 1935 German) — extreme-value families for floods, loads and maxima.

## Theory
- **W. Feller**, *An Introduction to Probability Theory and Its Applications*, vol. 1, 2nd ed. 1968; vol. 2, 1971, Wiley — binomial/Poisson limits, stable laws, renewal theory.
- **B. V. Gnedenko & A. N. Kolmogorov**, *Limit Distributions for Sums of Independent Random Variables*, Addison-Wesley, 1954 — stable domains of attraction.
- **S. Kotz, N. Balakrishnan & N. L. Johnson**, *Continuous Multivariate Distributions*, 2nd ed., Wiley, 2000 — multivariate normal, Dirichlet, multinomial (see lab 04).
- **P. Billingsley**, *Probability and Measure*, 3rd ed., Wiley, 1995 — the measure-theoretic underpinning of density/cdf equivalence.

## Applied and computational
- **N. L. Johnson & S. Kotz**, *Urn Models and Their Application*, Wiley, 1977 — the discrete constructions behind hypergeometric/negative binomial.
- **W. H. Press et al.**, *Numerical Recipes*, 3rd ed., Cambridge UP, 2007 — ch. 6: special functions, sampling algorithms (ziggurat, PTRS), statistical tests.
- **Apache Commons Math javadoc** (`NormalDistribution`, `PoissonDistribution`, `Distribution`) — the reference implementation this lab's contract mirrors.
- **L. Wasserman**, *All of Statistics*, Springer, 2004, ch. 3–5 — concise distribution theory aimed at inference.
- **C. McElreath**, *Statistical Rethinking*, 2nd ed., CRC, 2020, ch. 2–4 — distributions as model-building blocks.

## Bibliography entries (formatted)

- Johnson, N.L., Kotz, S. & Balakrishnan, N. (1994). *Continuous Univariate Distributions*, 2nd ed., Vol. 1. Wiley. ISBN 978-0-471-58495-7. The definitive reference for parameterizations and moments of the gamma, normal, exponential, beta families.
- Johnson, N.L. & Kotz, S. (1969). *Discrete Distributions*. Houghton Mifflin. Binomial, Poisson, geometric, negative binomial — including the derivation of each from a physical counting process.
- Ross, S.M. (2019). *A First Course in Probability*, 10th ed. Pearson. ISBN 978-0-13-518816-3. Chapters 4–6: moment-generating functions and the named distributions in one consistent notation.
- devroye, L. (1986). *Non-Uniform Random Variate Generation*. Springer. ISBN 978-0-387-96305-1. Free from the author's page; the source for the sampling algorithms in PERFORMANCE.md.

**Primary sources:** Student (1908), "The probable error of a mean," *Biometrika* 6(1), 1–25 — the t-distribution; Poisson (1837), *Recherches sur la probabilité des jugements*.

**Verification practice:** every formula in this lab was checked against `scipy.stats` (`stats.poisson.pmf(k, 4)`, `stats.gamma.mean(a=2, scale=3)`). Re-run those calls before trusting a transcription.
