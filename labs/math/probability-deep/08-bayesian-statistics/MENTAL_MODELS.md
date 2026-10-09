# Mental Models: Bayesian Statistics

## 1. Bayes Is a Reweighting Machine
You hold a distribution over hypotheses; data arrive with a likelihood per hypothesis; the posterior is the prior *reweighted* by those likelihoods. Nothing is created: hypotheses the data find implausible shrink, plausible ones grow, all relative to each other. Prior odds × likelihood ratio = posterior odds — three numbers, one line.

## 2. The Prior Is a Regulatory Constraint, Not a Guess You're Lying About
With 10 flips, the prior contributes pseudo-observations: Beta(2,2) = "2 heads, 2 tails" before seeing data. Posterior mean is the weighted average of prior mean (weight 4) and data mean (weight 10). As n grows the prior's weight vanishes ~ 4/(n+4) — that decay rate *is* the sensitivity analysis.

## 3. Conjugacy Is Closure
When the likelihood's functional form matches the prior's (Binomial × Beta, Poisson × Gamma, Normal × Normal), updating is arithmetic on parameters: (α, β) → (α + k, β + n − k). No integration, O(1) per observation — which is why conjugate models run in microseconds while MCMC runs in minutes.

## 4. Credible vs Confidence: Different Questions
Credible interval: "given model + prior + data, 95% of my posterior mass is here." Confidence interval: "if I repeated this experiment forever, 95% of my intervals would cover θ." One is about this θ (posterior), the other about the procedure (coverage). Both say "95%" — neither can be translated into the other's sentence.

## 5. The Marginal Likelihood Is What You Pay for a Model
P(D | M) = ∫ P(D | θ, M) π(θ | M) dθ — the average likelihood over the prior. Complex models get penalized automatically (mass spread over poorly-fitting θ), which is the Bayesian Occam's razor and the denominator everyone forgets when reporting "posterior ∝ likelihood × prior."

## 6. MCMC Is a Correlated Tourist, Not a Viewer
A Metropolis or HMC chain walks the posterior: each step depends on the last, so draws are autocorrelated and ESS = N/(1 + 2Σρₖ) ≪ N. Diagnostics (split-R̂ across chains, ESS, trace plots) are not bureaucracy — they are the checks that the tourist actually visited every mode of the posterior.

## 7. The Likelihood Ratio Is the Only Currency
Prior odds × LR = posterior odds. Spam scores, A/B posteriors, Enigma key updates — every deployed Bayesian system is this single line in different clothing. The prior sets the exchange rate, data supply LRs, and the posterior is the running balance; "my prior was weak" just means "I walked in with a small balance."

## 8. Evidence Is an Average, Not a Maximum
BF = ∫L(θ)π(θ)dθ averages the likelihood over the model's whole territory, while the MLE only visits the peak. A model with prior width 2 over a likelihood that fits only within 0.1 keeps about 0.1/2 = 5% of its own prior mass near the fit — that ratio is the complexity penalty, paid automatically. Optimization asks for the best θ; evidence asks how much of the model you were forced to use.

## 9. Decisions Are Posterior Expectations, Not Verdicts
Under squared loss the Bayes action is E[θ|D]; under asymmetric loss it is a posterior quantile; under 0-1 loss against a threshold it is whichever side of c the posterior mass sits. "Significant / not significant" is a loss function in disguise — once the loss is named, the rule falls out of the posterior instead of being negotiated after the data arrive.

## 10. Shrinkage Is What Pooling Looks Like From Inside
A group with n = 3 estimates nothing alone; its posterior mean slides toward the population mean by (group precision)/(group + population precision). That slide is lab 06's bias-variance tradeoff expressed as a prior: you buy bias to drop variance, and the hierarchy computes the exchange rate per group from τ instead of a tuning knob picked by hand.
