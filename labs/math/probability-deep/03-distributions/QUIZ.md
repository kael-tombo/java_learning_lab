# Distributions — Quiz (15 Questions with Worked Answers)

Named distributions, their moments, the central limit theorem and its
limitations, memorylessness, heavy tails, skew/kurtosis, and mixtures.

---

## Q1 — Poisson approximation to the binomial
**Q.** Binomial $B(1000,0.001)$. Mean, variance, and a Poisson approximation.

**A.** Mean $np=1$, variance $np(1-p)=0.999\approx1$ ⇒ Poisson($\lambda=1$).
Le Cam's inequality bounds the total variation error by $np^2=10^{-3}$ — an
extremely good approximation when $p$ is small and $n$ large, which is exactly
the regime of rare events (arrivals, failures, mutations). Note the variance is
$np(1-p)$, not $np$: the Poisson's variance equals its mean only in the limit.
This is the distribution behind "requests per second", "typos per page".

---

## Q2 — Exponential is memoryless; geometric too
**Q.** $T\sim\text{Exp}(\lambda)$: why is the residual life of $T-t$ still
exponential given survival past $t$?

**A.** $P(T-t>s\mid T>t)=\frac{e^{-\lambda(t+s)}}{e^{-\lambda t}}=e^{-\lambda s}$.
Discrete analogue: geometric with success probability $p$,
$P(G>k+1\mid G>k)=\frac{(1-p)^{k+1}}{(1-p)^k}=1-p$. Weibull with shape
$\ne1$ is **not** memoryless, and $\text{Poisson}(+\lambda)$ processes share the
property (increments are stationary). Practical consequence: for a Poisson
process, the next inter-arrival time is exponential and independent of the past —
this makes the process memoryless and lets you model it without tracking history.

---

## Q3 — Central limit theorem and its scope
**Q.** What exactly does CLT say, and what does it not?

**A.** If $X_i$ are i.i.d. with mean $\mu$ and finite variance $\sigma^2$, then
$(S_n-n\mu)/(\sigma\sqrt n)\Rightarrow N(0,1)$. Requirements: **independence**
and **finite variance** (satisfied for bounded variables; note CLT fails for
heavy-tailed $\alpha$-stable with $\alpha<2$). It does not say anything about a
single $n$, nor about skew (only asymptotically) nor about the *shape* of the
original distribution.
Practical caution: for skewed data you may need many more samples for the
normal approximation to hold at a usable error, and for very heavy tails (or
after outlier contamination) CLT is the wrong tool. Berry–Esseen bounds the
error by $C\rho/(\sigma^3\sqrt n)$ — the right way to know how large $n$ must be.

---

## Q4 — Beta and the inverse transform
**Q.** Why does the Beta distribution arise from order statistics?

**A.** If $U_{(k)}$ is the $k$-th order statistic of $n$ i.i.d. Uniform(0,1),
then $U_{(k)}\sim\text{Beta}(k,n+1-k)$: density $\frac{n!}{(k-1)!(n-k)!}u^{k-1}(1-u)^{n-k}$.
This is the universal building block for **Bayesian conjugacy**: a Beta
posterior arises whenever you update a Bernoulli likelihood with a Beta prior.
Uniformity matters: the Beta density is the normalizing constant times the
likelihood, and the normalizer is the beta function $B(k,n+1-k)$.

---

## Q5 — Gamma and its roles
**Q.** Three places the Gamma distribution shows up.

**A.** (i) Poisson processes: $T_n\sim\Gamma(n,\lambda)$ (Erlang);
(ii) conjugate prior for rate parameters with Poisson likelihood;
(iii) products and sums of exponentials, giving chi-square ($\Gamma(n/2, 1/2)$)
and $F$ distributions as ratios. Note the two-parameterization convention
trap: shape–rate $\mathrm{Gamma}(\alpha,\beta)$ has mean $\alpha\beta$, while
shape–scale $\mathrm{Gamma}(\alpha,\theta)$ has mean $\alpha\theta$. Mixing them
up is a common source of silently wrong numbers.

---

## Q6 — MGFs identify distributions
**Q.** Two variables have the same MGF near 0. Conclude?

**A.** They have the same distribution (existence and uniqueness theorem) —
**provided the MGF exists on a neighbourhood of 0**. Without that, moment
indeterminacy: Stieltjes' lognormal has moments matching $\text{Normal}(\mu,\sigma^2)$
but a different distribution. The MGF also only determines the distribution on
the convex hull of its support, so it cannot distinguish uniform(0,1) from
uniform(-1,1). Characteristic functions (always exist) fix both problems.
Practical relevance: is the exponential family "natural" (i.e. an existing MGF)
is what allows conjugate priors to work.

---

## Q7 — Skewness and the log transform
**Q.** Right-skewed positive data: what happens to skewness under $\log$?

**A.** Skewness decreases (typically towards zero), and $\log$ compresses the
long right tail. Skewness is the standardised third central moment
$g_1=\mathbb{E}[(X-\mu)^3]/\sigma^3$, which is **not** invariant under location
or scale (unlike the shape parameters $\gamma_1=\beta_2/\beta_2^2$ and
$\gamma_2=\beta_4/\beta_2^3$ in the Bowley/Pearson family — a useful
distinction). Rule of thumb: if skewness $>2$, log; if between $-2$ and 2,
probably fine; but always look at the histogram — skewness near 0 doesn't mean
symmetric (bimodal, uniform, and symmetric-but-heavy-tailed all have $g_1\approx0$).

---

## Q8 — Kurtosis is not "pointiness"
**Q.** Does high kurtosis mean a distribution is spiky?

**A.** Not necessarily: kurtosis measures tail weight relative to the normal,
$g_2=\frac{\mathbb{E}[(X-\mu)^4]}{\sigma^4}-3$ (excess kurtosis; 0 = normal).
The **Jensen-Shannon divergence to the normal** is the direct interpretable
measure of spikiness. A Laplace distribution has kurtosis $6-3=3$ (light tails
relative to normal) but is *not* spiky — it's flatter, a low "spikiness"
decreasing. The common conflation arises from visual intuition, not from the
math; report a proper divergence-to-normal if you want a spikiness measure.

---

## Q9 — Heavy tails and the mean
**Q.** Does $X$ with $\mathrm{Cauchy}(0,1)$ have a mean? SD?

**A.** Neither: $\mathbb{E}[X]$ doesn't exist (both tails diverge),
$\mathrm{Var}(X)=\infty$. The Cauchy is the canonical example: no CLT, no
mean-based summaries; use the median (0). Student-t with $\nu$ degrees of
freedom has finite moments only up to order $\nu$ — the mean exists only for
$\nu>1$. Central limit theorems don't apply to heavy-tailed data without
sub-exponential assumptions.

---

## Q10 — Truncated and censored data
**Q.** The difference between truncating and censoring?

**A.** **Truncation** removes out-of-range observations from the sample; the
data is missing at random w.r.t. the measurement range. **Censoring** (right)
keeps them, recording only "value exceeded threshold" — e.g. income above a
ceiling, survival times. Both bias naive estimates: truncating a heavy tail
*reduces* the apparent variance; naive analysis of censored data **under**estimates
the mean. The two are distinguishable only by knowing the censoring mechanism —
if it's not independent of the true value, there's no correction without extra
assumptions. This is why survival analysis exists (Kaplan–Meier, Cox).

---

## Q11 — Mixtures are not the same as anything simple
**Q.** If $0.5N(0,1)+0.5N(10,1)$, is it bimodal?

**A.** No: unimodal (mode around 5, though with a shoulder). Modes appear only
when components are separated by more than roughly $2\sigma$ (for equal weights,
roughly $2\sigma$; with $k$ components you need separation $\approx k^{1/k}\sigma$).
This is the empirical rule for mixture models: with $k$ components in $d$
dimensions, you need roughly $k^{1/d}$ points per dimension to resolve the modes.
Relevant when deciding how many mixture components the data can support, and a
warning about overfitting mixtures to small data.

---

## Q12 — Pareto and scale invariance
**Q.** Pareto with $x_m=1$, $\alpha=3$: mean, variance, median.

**A.** Mean $=x_m\frac{\alpha}{\alpha-1}=\frac32$, variance
$=\frac{\alpha x_m^2}{(\alpha-1)^2(\alpha-2)}=3$, median
$x_m2^{1/\alpha}=2^{1/3}\approx1.26$. Requires $\alpha>1$ for the mean and
$\alpha>2$ for the variance. Pareto is scale-invariant: if $X$ is Pareto then
$cX$ is Pareto with $x_m\mapsto cx_m$ — the basis of Zipf's law and of
rank-frequency analysis. Heavy tail ⇒ sample mean converges slowly and the
median/quantiles are the robust summaries.

---

## Q13 — The binomial exact vs normal approximation
**Q.** $B(100,0.5)$: when is the normal approximation acceptable?

**A.** Rule of thumb: $np\ge5$ and $n(1-p)\ge5$; here $np=50$ ✓, so
$Z=(X-50)/5\approx N(0,1)$ is fine. For $B(10,0.5)$ ($np=5$) use the exact
binomial or continuity correction ($+0.5$); for skewed cases
($np<5$ or $n(1-p)<5$) the normal is poor — use exact or Poisson when $p$ small.
Prefer the Wilson or Clopper–Pearson interval over the Wald interval: Wald
gives absurd bounds (like $>1$ probability) at small $n$.

---

## Q14 — The empirical distribution as a mixture
**Q.** ECDF vs PDF — which is the "distribution of my data"?

**A.** The empirical CDF $\hat F_n(x)=\frac1n\sum_i1_{x_i\le x}$ is always a
valid distribution (a mixture of point masses). It converges to $F$ uniformly
(Kolmogorov), with the finite-sample guarantee
$P(\sup_x|\hat F_n-F|>t)\le e^{-2nt^2}$ (Dvoretzky–Kiefer–Wolfowitz, two-sided).
The empirical PDF with binning introduces binning bias — a kernel density
estimate has its own bandwidth bias–variance trade-off. When is ECDF the right
tool? Quantile estimation, hypothesis tests that don't assume a form
(K-S), and any place where distribution *shape* isn't the question.

---

## Q15 — Which distribution to choose, and why it matters
**Q.** Fit the wrong family. What goes wrong concretely?

**A.** Three distinct harms:
(i) **Point estimates** — you plug in the wrong $\mathbb{E}[X]$ or $\sigma$.
(ii) **Uncertainty** — Gaussian intervals on heavy-tailed data have 95% coverage
that can be far below 95% (the true coverage of a normal-approximation
interval for heavy-tailed data tends to 0 as $\alpha\to2$); and for counts,
Poisson/normal intervals can produce negative lower bounds.
(iii) **Extrapolation and dependence** — a normal fit implies additive errors;
heavy-tailed errors break least-squares assumptions and produce the
"error-in-variables" and regression-to-the-mean traps. Always look at
QQ plots, not just summary statistics; a good fit on marginals still hides
dependence structure.

---

*Self-check: Q3, Q9 and Q15 are all "the theorem's hypotheses are violated"
cases. Q4, Q6 and Q11 test that you know *why* these distributions are named
and used, not just their densities.*