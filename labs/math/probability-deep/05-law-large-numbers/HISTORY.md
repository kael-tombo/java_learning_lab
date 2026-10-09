# History: Law of Large Numbers and CLT

## The first limit theorem and its flaw
**Jacob Bernoulli (1655–1705)** proved the weak law of large numbers in *Ars Conjectandi* (posthumously, 1713): for i.i.d. trials the relative frequency converges to p. His proof bounded the deviation by sums of binomial terms evaluated at the worst point — valid but so slow that the figure usually quoted from his hand computation is 25 550 throws to guarantee staying within 1/1000 of p with probability 1000/1001. **Abraham de Moivre (1667–1754)** found the limiting shape first: the normal approximation to the binomial (*The Doctrine of Chances*, 1718), a special case of the CLT 130 years early.

**Daniel Bernoulli (1700–1782)** presented the St. Petersburg paradox to the St. Petersburg Academy in 1738: a game with payoff 2ᵏ at probability 2⁻ᵏ has infinite expectation, so *no* law of large numbers applies to it — the first explicit boundary of the theory, and his fix (expected utility, logarithmic in wealth) started decision theory.

## Laplace to Chebyshev
**Pierre-Simon Laplace (1749–1827)** extended the CLT to non-identical summands and arbitrary p in *Théorie analytique des probabilités* (1812, with Fourier methods). **Siméon-Denis Poisson (1781–1840)** used "loi des grands nombres" in 1837 loosely — Gauss criticized his over-application. **Pafnuty Chebyshev (1821–1894)** gave the first rigorous proof for i.i.d. variables with finite variance (1867) using his moment inequality P(|X − μ| ≥ kσ) ≤ 1/k²; **Andrey Markov (1856–1922)** extended it to higher moments (1898–1900).

## Rigor and generalization
**Aleksandr Lyapunov (1857–1918)** proved the CLT via characteristic functions with a finite third absolute moment (1901) — the first fully rigorous proof. **Jarl Waldemar Lindeberg (1881–1969)** stated the condition (1922) that carries the CLT for non-identical summands; **William Feller (1906–1970)** and **Paul Lévy (1886–1971)** completed the general picture: **Lévy (1925)** classified the stable laws, showing Gaussian is just one stable limit — with α ≤ 2 and no finite variance, sums converge to non-Gaussian stable laws.

**Andrey Kolmogorov (1903–1987)** proved the strong law for i.i.d. with finite mean (1930) and the 0–1 law (1929); **Hartman & Wintner (1941)** showed the SLLN holds for i.i.d. *iff* E|X| < ∞. **Alexander Lyapunov's** approach and **Esseen's** Berry–Esseen bound (1945, constant later improved to ≤ 0.4748 by Shevtsova, 2011) quantify *how fast* the CLT approaches normality.

## Who relaxed which assumption — the line of descent

Each row is a step where one person removed a restriction the previous proof needed:

| Years | Person | Result | Assumption removed or added |
|---|---|---|---|
| 1713 | Jacob Bernoulli | WLLN for the binomial | baseline: bounded summands only |
| 1733/1756 | de Moivre | normal approximation to the binomial | fixed p, n → ∞ (special case of CLT) |
| 1738 | D. Bernoulli | St. Petersburg paradox | showed a *finite mean is required* — counterexample, not theorem |
| 1812 | Laplace | CLT for non-identical summands | relaxed identical distribution (though with informal rigor) |
| 1867 | Chebyshev | WLLN via moment inequality | first proof needing only finite variance |
| 1898–1900 | Markov | higher-moment method | supplied the inequality toolkit (Markov's inequality, 1884) |
| 1901 | Lyapunov | CLT via characteristic functions | first rigorous CLT: finite third absolute moment |
| 1922 | Lindeberg | Lindeberg condition | rigorously non-identical summands, no single dominant term |
| 1925 | Lévy | stable laws | described what happens *when* variance is infinite |
| 1929 | Khinchin | WLLN for E&#124;X&#124; < ∞ | removed finite variance from the weak law |
| 1929–30 | Kolmogorov | 0–1 law; SLLN for finite mean | almost-sure mode of convergence |
| 1941 | Hartman & Wintner | SLLN holds iff E&#124;X&#124; < ∞ | closed the exact boundary for the strong law |
| 1945 | Esseen | Berry–Esseen bound | first *quantitative* rate of CLT convergence |
| 2011 | Shevtsova | C ≤ 0.4748 | current best universal constant in that bound |

Reading the table in order is reading the lab's own structure: weak law → rigor → non-identical case → failure case → exact boundary → speed.
