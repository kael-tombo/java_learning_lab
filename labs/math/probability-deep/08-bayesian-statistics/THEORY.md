# Bayesian Statistics — Theory

## 1. The Engine, Rebuilt From Lab 01
Bayes' theorem prices hypotheses by their data likelihoods weighted by
priors. In this lab's register:
  posterior ∝ likelihood × prior,
with the proportionality constant exact-known as the evidence — the
probability of the observed data under the prior-marginalized model.
Every Bayesian computation is a bookkeeping triple: prior (what you
knew), likelihood (what the data endorse), posterior (what remains).

## 2. Beta–Binomial Conjugacy — Exact Statement
Let p ~ Beta(a, b) as prior and observe s successes, f failures in n
Bernoulli trials (f = n − s). Then the posterior is EXACTLY
  Beta(a + s, b + f).
No integration ever confronts the analyst; the updating law simply
adds successes to the first parameter, failures to the second. This
is why the pair is called conjugate: prior and posterior stay inside
the same family.

## 3. Posterior Summaries — Closed Forms
For Beta(a + s, b + f) (write A = a + s, B = b + f):
- Posterior mean: A/(A + B) — the parameter-weighted lawful average.
- Posterior mode (the MAP for this family): (A − 1)/(A + B − 2),
  valid when A, B > 1.
- Normalization: ∫ x^{A−1}(1−x)^{B−1} dx = B(A,B) =
  Γ(A)Γ(B)/Γ(A+B); on integer parameters this is factorial
  arithmetic — the lab checks B(9,5) = 1/6435 from 8!·4!/13!.

## 4. The Posterior Predictive — Statement
Probability of the NEXT trial being a success, integrating over the
posterior rather than plugging in a point estimate:
  P(next head) = E[p | data] = (a + s)/(a + b + n).
This adds the prior mass back into the denominator, which is why the
predictive differs from the plug-in ratio s/n — with exact tracking in
MATH_FOUNDATION.md (9/14 vs 7/10 for the worked dataset).

## 5. Sequential Equals Batch
Updating with evidence one observation at a time produces the same
posterior as absorbing the whole batch at once — the two parameters
just add in either order. The lab verifies this as a machine equality
(Beta(9, 5) both ways), which is the Bayesian version of sufficient
statistics doing their job (Lab 06's factorization, repurposed).

## 6. Normal–Normal Conjugacy — Statement
With known variance σ^2 and prior μ ~ Normal(μ0, τ^2), observations
x1..xn give a Normal posterior with
  precision: 1/τ^2 + n/σ^2 (precisions ADD),
  mean: posterior mean = (μ0/τ^2 + Σx_i/σ^2)/(1/τ^2 + n/σ^2).
Data shrinkage toward data grows linearly in n; the framework is the
continuous twin of Beta–Binomial counting (statement level here; the
executed lab is the Bayesian coin).

## 7. MAP vs Posterior Mean vs Credible Intervals
Three different Bayesian points/intervals: the MAP maximizes the
posterior density (mode), the posterior mean integrates it, and a
central credible interval brackets a stated posterior probability
(e.g., 95%). None of these is a frequentist confidence interval: a
credible interval makes a direct probability claim about the given
interval under the posterior law, no long-run replication semantics
attached. Priors are choices — the lab shows their fingerprints
(1/5 vs 7/10 on nearly the same data).
