# History: Estimation Theory

## Least squares before statistics
**Carl Friedrich Gauss (1777–1855)** claimed he used the method of least squares from 1795 and published it in *Theoria Motus Corporum Coelestium* (1809); **Adrien-Marie Legendre (1752–1833)** published it independently in 1805. Gauss argued the estimator is optimal *if* errors are normal — the first time an estimator was derived from an explicit distributional assumption. **Pierre-Simon Laplace** supplied the method of least deviations as a robust alternative (1810s).

## Moments and maximum likelihood
**Karl Pearson (1857–1936)** introduced the method of moments (1894) and fitted curves by matching sample moments — dominant until 1912. **Ronald A. Fisher (1890–1962)**, in a 1912 Cambridge paper, showed maximum likelihood beats moments in efficiency, then defined consistency, sufficiency and efficiency in *Philosophical Transactions* (1922, "On the mathematical foundations of theoretical statistics"). In that paper he also introduced the **score** and **Fisher information**, obtained the asymptotic variance 1/(n·I(θ)), and named the log-likelihood. Fisher's *Statistical Methods for Research Workers* (1925) put estimation into practice.

## Unbiasedness, bounds, decision
**Jerzy Neyman (1894–1981)** made unbiasedness the criterion in "On the best unbiased estimators of the parameter" (*Bull. AMS*, 1937) — and, with Egon Pearson, hypothesis testing (lab 07). **Harald Cramér (1893–1987)** (*Mathematical Methods of Statistics*, 1946) and **C. R. Rao (1920–2023)** (*Bull. Calcutta Stat. Assoc.*, 1945) proved the lower bound Var(θ̂) ≥ 1/(n·I(θ)) for unbiased estimators — the **Cramér–Rao bound**.

**C. R. Rao (1945)** and **David Blackwell (1919–2011)** (1947) showed conditioning a statistic on a sufficient statistic cannot increase variance — Rao–Blackwellization; **Erich Lehmann (1917–2009)** and **Herman Scheffé (1910–1996)** characterized the unique UMVU estimators (Lehmann–Scheffé theorem, 1950).

## Computation turns estimation into an algorithm
**Abraham Wald (1902–1950)** reframed estimation as decision theory with risk and admissibility (*Statistical Decision Functions*, 1950). **Maurice Quenouille (1949)** and **John Tukey (1915–2000)** devised the jackknife; **Bradley Efron (1938–)** introduced the bootstrap in 1979 (*Annals of Statistics* — "Bootstrap methods: another look at the jackknife"), which made sampling-distribution questions answerable by simulation. Efron's later work on one-step estimators and boosting (1986) carried estimation into machine learning.

## Timeline: estimation theory in dates

| Year | Advance | One-line significance |
|---|---|---|
| 1805 | Legendre publishes least squares | The first estimator, before the word existed |
| 1809 | Gauss, *Theoria Motus* | Least squares derived from an explicit normal-error model |
| 1894 | Pearson's method of moments | Fitting by equating moments — no optimality claim attached |
| 1912 | Fisher's Cambridge note on likelihood | The paper that started the moments-vs-likelihood argument |
| 1922 | Fisher, *Phil. Trans.* 222 | Consistency, sufficiency, efficiency, score, information |
| 1937 | Neyman, *Bull. AMS* 43 | Unbiasedness as a criterion worth optimizing |
| 1945/1946 | Rao; Cramér | The lower bound every SE is measured against |
| 1949/1950 | Rao–Blackwell; Lehmann–Scheffé; Wald | Conditioning improves; UMVU characterized; estimation = decision |
| 1956/1961 | Stein; James–Stein | The sample mean is inadmissible in p ≥ 3 — biased estimators win |
| 1979 | Efron, *Ann. Statist.* 7 | The bootstrap: error bars without a formula |
| 1980 | White, *Econometrica* 48 | Sandwich variance — SEs survive dependence and misspecification |

## The two schools and how they merged

Pearson's moment school dominated 1894–1930 because moments need no optimization — every estimator is a closed form. Fisher's likelihood school won because efficiency is checkable (relative to 1/(n·I)) while "reasonable" is not, and because computers made maximizing a function cheaper than deriving a moment match. The modern default (MLE first, moments as starting values or sanity checks) is that argument's verdict; the methods of moments survive exactly where the likelihood is intractable (GMM in econometrics) — a boundary worth knowing.

## What got invented for computation

Wald's decision theory (1950) reframed estimation as minimizing risk — which made numerical optimization legitimate rather than a fallback. Then Efron (1979) showed the computer can *replace* theory: resampling gives a sampling distribution when no formula exists. The bootstrap's ancestor is Tukey's jackknife (Quenouille 1949, Tukey 1958): estimating bias by deleting observations, O(n) refits, before machines were cheap enough for O(B·n) resampling.
