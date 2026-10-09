# History: Random Variables

## Expectation enters through gambling
**Christiaan Huygens (1629–1695)** published *De Ratiociniis in Ludo Aleae* (1657), the first definition of mathematical expectation: the value a fair game should have. **Jacob Bernoulli (1655–1705)** extended it in *Ars Conjectandi* (1713), computing expectations of compound bets. **Abraham de Moivre (1667–1754)**, in *The Doctrine of Chances* (1st ed. 1718, 3rd ed. 1756), showed the binomial approaches the bell curve — the first normal approximation and the first appearance of a *continuous* sampling distribution.

## Moments and their inequalities
**Pierre-Simon Laplace (1749–1827)** systematized the moment generating function and used moments to fit distributions to astronomical data. **Siméon-Denis Poisson (1781–1840)** named the Poisson distribution in 1837 while studying criminal verdicts. **Pafnuty Chebyshev (1821–1894)** proved in 1867 that P(|X − μ| ≥ kσ) ≤ 1/k² using only the first two moments — the first limit theorem proved by moment bounds. **Andrey Markov (1856–1922)** generalized the inequality to arbitrary moments (1906).

The word **variance** itself is **Ronald A. Fisher (1890–1962)**'s, introduced in his 1918 paper on the correlation between relatives — a statistician's term that only later became the fundamental quantity of probability.

## Making "random variable" a function
**Émile Borel (1871–1956)** constructed the σ-algebra of measurable sets (1909); **Henri Lebesgue (1875–1941)** supplied the integral (1902). **Thomas Joannes Stieltjes (1856–1894)** introduced the integral ∫ f dF (1894), letting a CDF F play the role of density for discrete, continuous and mixed distributions at once. **Andrey Kolmogorov (1903–1987)** defined a random variable as a measurable function X: Ω → ℝ in *Grundbegriffe* (1933).

## Limit theory for variables
**Paul Lévy (1886–1971)** proved the CLT with finite variance (1901) and classified stable laws (1925); **Boris Gnedenko and Kolmogorov** consolidated the general limit theorems in *Limit Distributions for Sums of Independent Random Variables* (1954). **Harald Cramér (1893–1987)** and **Harald Wold (1903–1989)** gave the Cramér–Wold device (1936): the joint law of (X₁,…,X_p) is fixed by all one-dimensional projections t₁X₁ + … + t_pX_p — reducing multivariate questions to single variables.

## Timeline with the people involved

| Year | Event | Why it mattered for random variables |
|---|---|---|
| 1654 | Pascal–Fermat correspondence on the points problem | Established that uncertain outcomes can be scored by their *expectation*, the first random variable calculation |
| 1713 | Jacob Bernoulli, *Ars Conjectandi* (published posthumously) | Law of large numbers: the sample average of an i.i.d. variable converges to its expectation |
| 1733 | De Moivre, *Approximatio ad Summam Terminorum Binomii* | Normal curve derived from the binomial, tying a discrete variable to a continuous limit |
| 1900 | Karl Pearson, χ² goodness-of-fit test | First systematic test of whether observed frequencies match a theoretical distribution |
| 1933 | Kolmogorov, *Grundbegriffe der Wahrscheinlichkeitsrechnung* | Measure-theoretic foundation: a random variable is a measurable function into ℝ |
| 1935 | R.A. Fisher, *Design of Experiments* + χ² and t tables | Sampling distributions become practical tools for working scientists |
| 1946 | Ulam, von Neumann, Metropolis at Los Alamos | Monte Carlo: random variables simulated on ENIAC to solve transport problems |
| 1951 | Neyman–Pearson lemma published (work from 1930s) | Formalizes most powerful tests; connects distributions to decision rules |
| 1969 | Khan, Srinivasan, packet-switching studies (ARPANET era) | Discrete distributions (Poisson, geometric) become load models for networks |

## Branches and later developments

- **Characteristic functions** (Lévy, 1920s–30s): the Fourier transform of a distribution uniquely determines it, and convolutions become multiplications — the clean route to the CLT.
- **Stable and infinitely divisible distributions** (Lévy, 1924): identified as the only possible non-Gaussian limits of the CLT — later found to model financial returns.
- **Rao–Blackwell theorem** (1947): conditioning a statistic reduces variance without changing its mean — a free improvement to any estimator.
