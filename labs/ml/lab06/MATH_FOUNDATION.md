# Naive Bayes Classifier - Mathematical Foundations

**Track:** ml  |  **Lab:** lab06  |  **Level:** Intermediate

> Companion notes to the runnable lab. Everything here is grounded in the source under `src/`, so a claim you cannot reproduce is a claim you do not ship.

| Doc | Read it when you want |
|---|---|
| `THEORY.md` | the mental model and the assumptions |
| `MATH_FOUNDATION.md` | the formulas, the derivations, the numerical traps |
| `CODE_DEEP_DIVE.md` | the Java implementation, line by line |
| `EXERCISES.md` | deliberate practice, one deliverable at a time |
| `QUIZ.md` | to find the gaps before an interview |
| `FLASHCARDS.md` | spaced repetition on the day before a review |
| `VISION.md` | the career-level context and the anti-patterns to avoid |
| `MINI_PROJECT.md` | a self-contained build you finish in one sitting |
| `REAL_WORLD_PROJECT.md` | the production system, on-call runbook included |

## Notation

| Symbol | Meaning |
|---|---|
| `P(y=c | x) ∝ P(y=c) · P(x | y=c)` | Bayes' rule (proportional) - drop the evidence constant for argmax |
| `P(x | y=c) = ∏ P(xᵢ | y=c)` | Naive independence - the assumption that costs accuracy |
| `P(xᵢ | y=c) = exp(−(xᵢ−μ_cᵢ)²/2σ_cᵢ²)/(σᵢc√2π)` | Gaussian likelihood - continuous features |
| `P(x | y=c) ∝ ∏ᵢ count(c, xᵢ)` | Multinomial likelihood - term counts per class |
| `P(xᵢ | y=c) = (count + α)/(N_c + α|V|)` | Laplace smoothing - keeps unseen values possible |
| `log P(c) + Σᵢ log P(xᵢ | c)` | Log-posterior score - argmax is identical, numerically safe |
| `confusion matrix metrics` | precision / recall / F1 - text classification is imbalanced in practice |

## Why the Math Matters

Naive Bayes is a complete generative model built on one approximation. That makes every term — prior, likelihood, smoothing, posterior — individually inspectable, which is why it remains a teaching vehicle long after better classifiers took over.


---

## 1. Bayes' theorem and dropping the evidence

```text
P(y|x) = P(x|y) P(y) / P(x)
argmax_c P(y=c|x) = argmax_c [ P(y=c) P(x|y=c) ]
P(x) = sum_c P(x|y=c) P(y=c) is constant in c
```

For classification the normaliser does not affect the argmax, so we never compute it. That also means the score is not a probability — it is a relative likelihood until you divide by the evidence.

**Worked example.** Two classes with prior-weighted likelihoods of 3.0 and 1.2: the argmax is class A. The actual posterior needs P(x) = 4.2, giving 0.714 — which is the only number you may publish.


---

## 2. Conditional independence

```text
P(x|y=c) = P(x_1|y=c) ... P(x_p|y=c)
true:      P(x_1, x_2|y=c) generally != product
log form: sum_i log P(x_i|y=c)
```

The independence assumption lets each feature's contribution be computed and cached separately, which is what makes training O(n · p) with tiny state and prediction O(support) rather than O(n ²).

**Worked example.** In spam data, P('free' and 'money' | spam) ≈ 0.08, while the independent product gives 0.10. A 25% relative error per pair compounds across tokens, which is why NB overconfident.


---

## 3. Gaussian NB parameters

```text
mu_cj = (1/N_c) sum_{i in c} x_ij
sigma^2_cj = (1/N_c) sum_{i in c} (x_ij - mu_cj)^2
log P(x_j|y=c) = -0.5 log(2 pi sigma^2_cj) - (x_j-mu_cj)^2 / (2 sigma^2_cj)
```

Each class gets a mean and a variance per feature. The quadratic term is a Mahalanobis-style distance, so Gaussian NB is effectively a diagonal Gaussian discriminant analysis.

**Worked example.** Class with x = 5, mu = 3, sigma = 2: -0.5 log(2 pi · 4) - 4/8 = -1.2655 - 0.5 = -1.7655. Class with sigma = 0.5: the same x becomes a much worse fit, which is why variance matters.


---

## 4. Multinomial NB with smoothing

```text
theta_cj = (count(c, token j) + alpha) / (sum_j' count(c, j') + alpha V)
log P(token|c) = log theta_cj
```

Smoothing keeps every token possible in every class. alpha interpolates between the MLE (alpha = 0) and a uniform prior (alpha → ∞); alpha = 1 is the classic Laplace choice.

**Worked example.** Class with 100 tokens and vocabulary 50,000: an unseen token has theta = 1/50100 with alpha = 1, not 0. Without smoothing the class loses forever.


---

## 5. Underflow and log-space scoring

```text
log score(c) = log P(y=c) + sum_j log P(token j | c)
log P(token|c) values around -9.5; 500 tokens
sum = -4750 -> P = e^-4750 = 0 in double
```

Double precision underflows around 1e-308, i.e. log p ≈ -709. Text documents exceed that within roughly 75 tokens at typical log-probabilities, so the failure is guaranteed, not possible.

**Worked example.** A 500-token document: probability-space product returns 0.0 for all classes. Log-space returns -4702.3 vs -4801.1 — a clear, correct difference.


---

## 6. Calibration error

```text
ECE = sum_b (n_b/N) | acc(b) - conf(b)|
for NB with correlated features the log-odds slope
shrinks far from 1, so |acc - conf| grows
```

NB is overconfident because independence makes the likelihood ratio too extreme. A one-parameter recalibration (Platt scaling) recovers most of it, which is usually cheaper than switching models.

**Worked example.** Bins with confidence 0.95 average accuracy 0.80: ECE ≈ 0.15. After Platt scaling the same bins sit near the diagonal with ECE ≈ 0.02.


---

## Cheat Sheet

- `P(y=c | x) ∝ P(y=c) · P(x | y=c)` - Bayes' rule (proportional)
- `P(x | y=c) = ∏ P(xᵢ | y=c)` - Naive independence
- `P(xᵢ | y=c) = exp(−(xᵢ−μ_cᵢ)²/2σ_cᵢ²)/(σᵢc√2π)` - Gaussian likelihood
- `P(x | y=c) ∝ ∏ᵢ count(c, xᵢ)` - Multinomial likelihood
- `P(xᵢ | y=c) = (count + α)/(N_c + α|V|)` - Laplace smoothing
- `log P(c) + Σᵢ log P(xᵢ | c)` - Log-posterior score
- `confusion matrix metrics` - precision / recall / F1

## Numerical Traps

- Computing P(c|x) as if it were P(x|c) — a classic and very quiet inversion.
- Dropping the evidence term and then publishing the score as a probability.
- Estimating variances with n−1 when the class is a population, which is standard for NB.
- Zero variance in a class making the Gaussian likelihood infinite — smooth the variance.
- Using counts for a Bernoulli model or indicators for a multinomial one.

## Self-Check Problems

1. For one document of 4 tokens, compute the multinomial NB score for two classes in probability space, then in log space; show the underflow.
2. Show that dropping P(x) does not change the argmax over any number of classes.
3. Compute Gaussian NB parameters for a 2-feature class and score a new point.
4. With alpha = 1, compute the smoothed probability of a token seen 0 times in a class with 100 tokens and |V| = 50,000.
5. Compute ECE for 3 bins with (n, conf, acc) = (500, 0.9, 0.95), (400, 0.6, 0.55), (100, 0.3, 0.2).
