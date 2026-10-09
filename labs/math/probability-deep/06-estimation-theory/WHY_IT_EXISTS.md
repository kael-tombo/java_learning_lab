# Why It Exists: Estimation Theory

## The problem: "guess the parameter" had no rules
Gauss's least squares (1809) worked, but *why* it worked depended on an assumed normal error model, and nothing said what to do with a different model. Pearson's method of moments (1894) fit any parameter by equating sample and population moments — convenient, but with no optimality claim, so two people could produce two estimates with no principled way to choose.

## What Fisher's 1922 paper supplied
A framework where every guess has a *property list*:
1. **Consistency** — θ̂ → θ as n → ∞.
2. **Bias** — E[θ̂] − θ, and the acknowledgment that zero bias is not the goal (MSE is).
3. **Efficiency** — variance relative to the Cramér–Rao bound 1/(n·I(θ)); MLE attains it asymptotically in regular families.
4. **Sufficiency** — a guarantee that no data were discarded along the way.

With those, "which estimator?" became a question with answers instead of opinions.

## Why the Cramér–Rao bound matters even when unattainable
It is a *floor*: if your best candidate's variance is 4× the bound, either the bound's assumptions fail (say so) or a better estimator exists (Rao–Blackwellize, use the MLE, or go Bayesian). It converts vague unease about precision into a number.

## Why an entire subfield beyond MLE
- **Small n**: MLE of σ² is biased; unbiasedness and UMVU (Neyman 1937, Lehmann–Scheffé 1950) fix small samples.
- **Dependent/misspecified data**: MLE's information-based SE is wrong; White's sandwich (1980) restores validity.
- **Computation**: some likelihoods have no closed form — Wald's decision theory (1950) gives a criterion to optimize numerically, and the bootstrap (Efron 1979) gives error bars without a formula.
- **Many parameters**: p near n makes MLE erratic; shrinkage (James–Stein 1961) and regularization beat it *everywhere* in p ≥ 3 — the first rigorous proof that "biased but tighter" can dominate.

## The honest boundary
Estimation theory assumes the model family is right. If the data are lognormal and you estimate a normal's μ, every optimality theorem is about the wrong target — which is why diagnostics (lab 07) and model checks precede estimation in any serious workflow.

## The alternative, and why it failed

**"Pick the estimate that looks most reasonable."** Pre-Fisher practice: Gauss's normality assumption justified least squares for *one* model, and nothing else; Pearson's moments fit anything but ranked nothing. Two 1930s concrete failures forced criteria: (1) moments estimators for the negative binomial can fall outside the parameter space (no admissible value), so a "reasonable" procedure can be undefined; (2) with two competing estimates of a star's position there was no way to say which would be wrong *less often* — Neyman (1937) and Wald (1950) fixed this by making the loss function (bias² + variance, or explicit decision loss) part of the question rather than an afterthought.

**"Just report the estimate and move on."** The 1940s–60s regulatory and scientific record shows why not: without a variance, a point estimate cannot be compared, pooled, or falsified. Cramér–Rao gave the reference point (if your SE is 4× the bound, either assumptions fail or a better estimator exists), Rao–Blackwell and Lehmann–Scheffé gave exact optimizers for the unbiased class, and the sandwich (White 1980) gave a variance you can still trust when the model is wrong — each theorem answers a question "just report it" cannot even ask.

## Two questions worth re-answering after this lab

1. *Why not always the MLE?* Because optimality is asymptotic and conditional: at small n the MLE of σ² is biased (n−1)/n, at boundaries it converges at rate n not √n (Uniform's max), under dependence its SE is wrong, and in p ≥ 3 it is *inadmissible* under squared error (James–Stein 1961 — shrinkage beats it at every θ). The MLE is the default, not the theorem.
2. *What does an SE actually promise?* That across repeated samples at your actual n, the interval built from it covers ~95% of the time — a property of the *procedure* (model 5). Everything this lab adds (sandwich, BCa, profile LR) exists because one of the ingredients of that promise — correct family, independence, symmetric likelihood — was quietly false, and the promise had to be repaired rather than dropped.
