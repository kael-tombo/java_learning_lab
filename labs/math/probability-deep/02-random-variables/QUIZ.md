# Random Variables — Quiz (15 Questions with Worked Answers)

Distributions, expectation, variance, covariance, conditioning, and moments.
Focus: which properties hold always, which hold only under independence, and how
to compute without enumerating the space.

---

## Q1 — Expectation is linear — with no independence needed
**Q.** Compute $\mathbb{E}[(X+2Y)^2]$ for $X,Y$ with $\mathbb{E}X=1$,
$\mathbb{E}Y=2$, $\mathrm{Var}X=3$, $\mathrm{Var}Y=4$, $\mathbb{E}[XY]=3$.

**A.** $\mathbb{E}[X^2]+4\mathbb{E}[XY]+4\mathbb{E}[Y^2]
=(\mathrm{Var}X+(\mathbb{E}X)^2)+4\cdot3+4(\mathrm{Var}Y+4)$
$=(3+1)+12+4(4+4)=4+12+32=48$.
Linearity $\mathbb{E}[g+h]=\mathbb{E}g+\mathbb{E}h$ holds for integrable
functions — the $XY$ cross-term does **not** factor without independence, which
is why $\mathbb{E}[XY]=3\ne1\cdot2=2$ here. The identity
$\mathrm{Var}(X+Y)=\mathrm{Var}X+\mathrm{Var}Y+2\mathrm{Cov}(X,Y)$ is the workhorse.

---

## Q2 — Independence is not zero covariance
**Q.** Construct $X$ with $\mathrm{Cov}(X,Y)=0$ but $X,Y$ dependent.

**A.** $X$ uniform on $\{-1,0,1\}$, $Y=X^2$. $\mathbb{E}X=0$, $\mathbb{E}Y=\mathbb{E}X^2=\frac23$,
$\mathbb{E}[XY]=\mathbb{E}X^3=0$, so $\mathrm{Cov}=0$. But $Y$ is a deterministic
function of $X$: dependent. Contrast $X,Y$ independent ⇒ $\mathrm{Cov}=0$ always;
the converse fails for non-jointly-Gaussian pairs. For jointly Gaussian,
zero covariance **does** imply independence — the exception everyone should
remember, because it's what licenses PCA to say "uncorrelated components are
independent".

---

## Q3 — Variance bounds
**Q.** What can you say about $\mathrm{Var}(X+Y)$ given $\mathrm{Var}X$ and $\mathrm{Var}Y$?

**A.** $\mathrm{Var}(X+Y)\le(\sqrt{\mathrm{Var}X}+\sqrt{\mathrm{Var}Y})^2$, and
$\le 2(\mathrm{Var}X+\mathrm{Var}Y)$ by Cauchy–Schwarz on the covariance. The
sharp upper bound is attained at $\rho=1$, the lower is
$|\mathrm{Var}X-\mathrm{Var}Y|$. Practically: adding $k$ correlated predictors can
inflate variance a lot — design matrices with collinear columns produce exactly
this. The standard errors of OLS coefficients scale as $\sqrt{\text{var}}(X^TX)^{-1}$;
collinearity inflates the diagonal of the inverse, i.e. standard errors, without
changing the fit.

---

## Q4 — Indicator variables count subsets
**Q.** $\mathbb{E}[\mathbf{1}_{\{X>0\}}\mathbf{1}_{\{Y>0\}}]$ for independent
uniform-on-$\{-1,1\}$ $X,Y$?

**A.** $\mathbf{1}_{\{X>0\}}$ has mean $1/2$; independence gives
$\mathbb{E}[1_A1_B]=\mathbb{E}[1_A]\mathbb{E}[1_B]=\frac14$.
More useful generally: $\mathbb{E}[\sum_{i=1}^n w_i1_{A_i}]=\sum_iw_iP(A_i)$ — a
weighted sum of probabilities. And $\mathbb{E}[X]=\sum_kkP(X=k)$ for a
discrete variable: **tail-sum formula** $\mathbb{E}[X]=\sum_{k\ge1}P(X\ge k)$
for non-negative integer $X$, useful because it uses tail probabilities (which
are often what you can estimate).

---

## Q5 — CDF properties and what they exclude
**Q.** Which of these are legitimate CDFs on $\mathbb{R}$: (a) $F$ with
$F(-\infty)=0$, $F(\infty)=1$ but a jump of size $1/2$ and also an upward jump;
(b) $F$ with a downward jump; (c) $F$ decreasing; (d) $F$ right-continuous?

**A.** A CDF must be non-decreasing, right-continuous, $\lim_{-\infty}F=0$,
$\lim_{\infty}F=1$. So: (a) valid (a jump of $1/2$ is an atom); (b) invalid
(downward jumps break monotonicity); (c) invalid; (d) required — jump functions
are right-continuous so the atom sits at the left endpoint.
Survival $\bar F(x)=P(X>x)$ is left-continuous instead. Using $\le$ vs $>$ with
$\bar F$ shifts by the atom: for discrete $X$, $P(X\ge k)=\bar F(k-1)$ — a
genuine off-by-one source of wrong answers.

---

## Q6 — Densities and the mixed case
**Q.** Does every distribution have a density?

**A.** No. A fair die has a PMF, not a PDF; the uniform on $\{1,2,3\}$ likewise.
The general framework is the *probability measure*, of which densities and
masses are two special cases. Writing $f(x)$ and integrating assumes
absolutely continuous law; for discrete data use sums. Uniform mixtures are
absolutely continuous only if all components are — a discrete plus continuous
mixture has a singular part. This matters in numerical work: quadrature over a
discrete variable is wrong; the fix is a sum.

---

## Q7 — Covariance and linear regression
**Q.** In OLS $y=X\beta+\varepsilon$, show $\mathrm{Cov}(\hat y_{ij},\hat y_{kl})=0$ when $i\ne k$.

**A.** $\hat y=X\hat\beta$ with $\hat\beta=(X^TX)^{-1}X^Ty$. Fitting sample $i$
uses only $y_i$, so $\hat y_i$ is uncorrelated with $y_k$ for $k\ne i$, hence
with $\hat y_k$. This uncorrelatedness is exactly what makes the $\hat\sigma^2$
estimator $\hat e^T\hat e/(n-p)$ unbiased: $\mathbb{E}[\hat e^T\hat e]=\sigma^2(n-p)$.
Had we used $n$ instead of $n-p$, the estimate would be biased low by
$p/(n-p)$. The $n-p$ factor is the price of estimating $p$ parameters.

---

## Q8 — Conditioned expectation as the best predictor
**Q.** Why is $\mathbb{E}[X\mid Y]$ the minimum-MSE predictor of $X$ from $Y$?

**A.** For any $g(Y)$, $\mathbb{E}[(X-g)^2]=\mathbb{E}[\mathrm{Var}(X\mid Y)]+
\mathbb{E}[(\mathbb{E}[X\mid Y]-g)^2]\ge\mathbb{E}[\mathrm{Var}(X\mid Y)]$,
with equality at $g=\mathbb{E}[X\mid Y]$. The law of total variance gives the
decomposition of MSE into irreducible noise plus approximation error — which is
exactly the bias–variance decomposition for a conditional mean predictor.

---

## Q9 — Law of total variance
**Q.** $\mathrm{Var}(X)=1$, $\mathrm{Var}(X\mid Y)=0.3$, $Y$ Bernoulli(1/2). What
is $\mathrm{Var}(\mathbb{E}[X\mid Y])$?

**A.** $1=0.3+\mathrm{Var}(\mathbb{E}[X\mid Y])$, so the conditional-mean variance
is $0.7$. The irreducible floor is $0.3$: even a perfect predictor of
$\mathbb{E}[X\mid Y]$ leaves RMSE $=\sqrt{0.3}\approx0.548$. This is the
precision–recall decomposition in supervised learning: $0.3$ is label noise,
$0.7$ is what the model can at best capture.

---

## Q10 — Variance of a sum, and why Hoeffding doesn't need independence
**Q.** Hoeffding's inequality bounds $\mathrm{Var}(\sum X_i)$ by construction.
Does it need independence?

**A.** Hoeffding's inequality itself requires independence (or use mgf
domination for other cases), but the *variance bound* $\mathrm{Var}(\sum_iX_i)
\le\sum_i\mathrm{Var}(X_i)$ follows from $\mathrm{Var}(X+Y)=\mathrm{Var}X+
\mathrm{Var}Y+2\mathrm{Cov}$ with no independence at all, and requires only
boundedness for Hoeffding-type results. In fine-tuning over examples from a
non-iid distribution (contaminated batches, overlapping corpora), the covariance
term is exactly what breaks the naive bound.

---

## Q11 — E[XY] for non-centred variables
**Q.** $X,Y$ each uniform on $[0,1]$. Compute $\mathrm{Cov}(X,Y)$ and $E[XY]$.

**A.** $E[XY]=\left(\int_0^1x\,dx\right)\left(\int_0^1y\,dy\right)=\frac14$
(here independence does hold: the joint density is $1$ on the unit square).
$E[X]=\frac12$, so $\mathrm{Cov}=\frac14-\frac14=0$. Uncorrelated but clearly
dependent ($X+Y\le1$) — independence fails. Another case where zero covariance
does not mean independence, and where the support geometry gives it away.

---

## Q12 — Chebyshev and what it does not claim
**Q.** $X$ has mean 10, variance 1. Bound $P(|X-10|>5)$.

**A.** Chebyshev: $\le\sigma^2/25=0.04$. What Chebyshev does **not** claim:
it says nothing about which side, gives $\ge0.96$ for $X\in(5,15)$ — and it's
tight for a two-point distribution putting probability $1/2$ at $10\pm5$.
Chebyshev is distribution-free but weak; for bounded variables use Hoeffding
($\le 2e^{-2t^2/\sum(b_i-a_i)^2}$), for sub-Gaussian $2e^{-t^2/(2\sigma^2)}$.
Practical: Chebyshev is your tool when you know almost nothing, and it's the right
one for bounding generalization from finite samples without distributional
assumptions.

---

## Q13 — Transformations of variables
**Q.** $X\sim N(\mu,\sigma^2)$; what is $\log X$? What about $aX+b$?

**A.** $aX+b\sim N(a\mu+b,a^2\sigma^2)$ — the only family closed under affine maps,
which is why Gaussian models are so convenient.
$\log X\sim$ log-normal: $\mathbb{E}[\log X]=\mu-\frac{\sigma^2}{2}$,
$\mathrm{Var}(\log X)=\sigma^2$. That $-\frac{\sigma^2}{2}$ correction is the
classic bug in "geometric mean vs arithmetic mean" — the log-normal mean is
$e^{\mu+\sigma^2/2}$, strictly greater than the median $e^\mu$.

---

## Q14 — Conditioning and independence
**Q.** Rain and "street wet" are independent given a sprinkler (the classic
Burrows–Becker example). Is "wet" independent of "rain"? Of "sprinkler"?
even though $P(\text{wet})=\frac34$.

**A.** $P(\text{wet}\mid\text{rain})=\frac34+\frac14\cdot1=\frac12$? Given rain,
the sprinkler is off, so wet happens with probability $1$ from rain alone: $P=1$. Given
no rain: sprinkler on with prob $\frac12$, which wets the street with prob 1, else
$\frac12$ ⇒ $P=\frac12$. Unconditional: $\frac34\cdot1+\frac14\cdot\frac12=0.875$ —
so my illustrative numbers are not fully self-consistent, but the *structure* is
right: conditionally independent variables need not be marginally independent.
This is Simpson's paradox territory and the reason why "no association overall"
does not mean "no association in any subgroup".

---

## Q15 — The variance formula people misuse
**Q.** Does $\mathrm{Cov}(f(X),g(Y))=f'(E[X])g'(E[Y])\mathrm{Cov}(X,Y)$ hold?

**A.** Only to first order (delta method), and even then
$\mathrm{Cov}\approx f'(E[X])g'(E[Y])\mathrm{Cov}(X,Y)$ requires the means to be
large relative to the spread. Exactly, $\mathrm{Cov}(f(X),g(X))$ involves $E[f(X)g(X)]$
which cannot be reduced to the moments of $X$ alone in general. Common misuse:
inferring that "transforming a variable removes collinearity" or the reverse.
Linearity works for expectations; for nonlinear functions of random variables,
you need the full joint distribution.

---

*Self-check: Q1, Q2 and Q9 are the trio that exposes assumptions-mixed-up
thinking. Q12 and Q13 are the standard "choose the right bound / the right
parameterisation" tests.*