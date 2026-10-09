# History: Probability Distributions

## The first named laws
**Jacob Bernoulli (1655–1705)** analyzed the binomial in *Ars Conjectandi* (1713) as a combinatorial counting problem. **Abraham de Moivre (1667–1754)** obtained the normal approximation to the binomial in *The Doctrine of Chances* (1718, definitive 3rd ed. 1756): C(n,k)2⁻ⁿ ≈ φ((k − n/2)/√(n/2))/√(n/2).

**Pierre-Simon Laplace (1749–1827)** generalized it to unequal p (the de Moivre–Laplace theorem, 1812) and, studying small errors in astronomy, derived the normal density exp(−x²/2σ²); Gauss used it for least-squares orbit fitting (*Theoria motus*, 1809), which is why it is still called the *Gaussian*.

**Siméon-Denis Poisson (1781–1840)** introduced the Poisson distribution in *Recherches sur la probabilité des jugements* (1837) as a limit of binomials for rare events. **Weldon's dice data** (1870s, communicated to Galton and Pearson) gave the first strong empirical fit to a χ²-type law, prompting **Karl Pearson (1857–1936)** to found *Biometrika* in 1901 and publish the χ² goodness-of-fit test (1900).

## The zoo expands
- **Student (W. S. Gosset, 1876–1937)** published the t distribution in *Biometrika* in 1908, deriving the sampling distribution of x̄/s for n = 5 under a normal model while working at Guinness.
- **R. A. Fisher (1890–1962)** systematized sampling distributions in *Statistical Methods for Research Workers* (1925) and, with F. Yates, *Statistical Tables for Biological, Agricultural and Medical Research* (1931) — the χ², t and F tables that made these laws usable without re-deriving them.
- **Rare-event families**: Bortkiewicz's *Das Gesetz der kleinen Zahlen* (1898) fitted Poisson laws to Prussian cavalry deaths per year; sums of exponentials produce the gamma, the waiting-time backbone of queueing theory (Erlang, 1917, for telephone exchanges).
- **Tails and extremes**: **Wilfred Pareto (1896)** fitted income to a power law; **R. A. Fisher and L. H. C. Tippett (1928)** identified the three types of limit laws for extremes; **E. J. Gumbel (1935)** fitted them to floods and wartime mortality, founding extreme-value theory.

## Limit theory closes the loop
**Paul Lévy (1886–1971)** characterized the stable laws (1925); **Gnedenko & Kolmogorov (1954)** proved the general stable limit theorems. At Los Alamos in the 1940s, **John von Neumann, Stanislaw Ulam and Nicholas Metropolis** used early computers to *sample* these densities to estimate neutron-criticality quantities — the Monte Carlo method — turning distribution evaluation into an algorithmic problem.

## Modern compendiums
**Johnson, Kotz & Balakrishnan**, *Continuous Univariate Distributions* (vols 1–2, 2nd ed. 1994) catalogues 100+ families with their histories; **Kotz, Balakrishnan & Johnson**, *Discrete Multivariate Distributions* (1997) does the same for discrete laws. The implementation references today are JDK 22+'s `java.util.random.Distribution` interfaces and Apache Commons Math's `NormalDistribution` / `PoissonDistribution`.

## Timeline: how the named distributions arrived

| Year | Distribution / result | Origin |
|---|---|---|
| 1713 | Binomial theorem applied to games | Jacob Bernoulli, *Ars Conjectandi* |
| 1733 | Normal curve (De Moivre–Laplace theorem) | De Moivre, *Approximatio*; extended by Laplace 1812 |
| 1846 | Poisson's law of small numbers | Poisson, *Recherches sur la probabilité des jugements* — arrivals rare enough that each is almost certainly the only one |
| 1889 | t-distribution | William Sealy Gosset, writing as "Student," *Biometrika* 1(2) — small-sample inference from n = 13 brewing trials at Guinness |
| 1900 | χ² distribution and goodness-of-fit test | Karl Pearson, *Phil. Trans. R. Soc. A* 195 |
| 1922 | Maximum likelihood + Fisher information | Fisher, "On the mathematical foundations of theoretical statistics," *Phil. Trans. R. Soc. A* 222 |
| 1924 | Central limit theorem, general case | Lindeberg; Lévy's independent proof 1935 |
| 1939 | Jeffreys, *Theory of Probability* (Oxford) | Bayesian computation with conjugate updating, including gamma–Poisson counting |
| 1953 | Good–Turing frequency estimation | I.J. Good, *Biometrika* 40 — estimating the probability of species you have not yet observed |

## Why "named" distributions survive

They are not a catalog for its own sake: each name is a *closure property*. Poisson is closed under superposition, gamma under addition, binomial under sums of Bernoullis, multinomial under marginalization. Naming a distribution is how applied work says "this model composes."
