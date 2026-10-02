# Probability: Random Variables, Distributions, and Bayes' Theorem

## 1. Probability Fundamentals

### 1.1 Sample Space
Set of all possible outcomes: S

### 1.2 Events
Subset of sample space: E ⊆ S

### 1.3 Probability Axioms
- P(S) = 1
- 0 ≤ P(E) ≤ 1
- P(E ∪ F) = P(E) + P(F) - P(E ∩ F)

## 2. Random Variables

### 2.1 Discrete Random Variables
- Takes countable values
- X: S → {x₁, x₂, ...}

### 2.2 Continuous Random Variables
- Takes uncountable values
- Described by probability density function (PDF)

## 3. Expected Value and Variance

### 3.1 Expected Value
- Discrete: E[X] = Σ x·P(X=x)
- Continuous: E[X] = ∫ x·f(x)dx

### 3.2 Variance
- Var(X) = E[(X - E[X])²] = E[X²] - (E[X])²

## 4. Common Distributions

### 4.1 Discrete
- Uniform: P(X=k) = 1/n
- Bernoulli: P(X=1) = p, P(X=0) = 1-p
- Binomial: P(X=k) = C(n,k)p^k(1-p)^(n-k)
- Poisson: P(X=k) = λ^k e^(-λ) / k!

### 4.2 Continuous
- Uniform: f(x) = 1/(b-a)
- Exponential: f(x) = λe^(-λx)
- Normal: f(x) = (1/√(2πσ²))e^(-(x-μ)²/2σ²)

## 5. Bayes' Theorem

P(A|B) = P(B|A)·P(A) / P(B)

### 5.1 Prior Probability
P(A) before evidence

### 5.2 Posterior Probability
P(A|B) after evidence

### 5.3 Likelihood
P(B|A)

## 6. Central Limit Theorem

For large n, sum/average of i.i.d. variables approximates normal distribution regardless of original distribution.

## 7. Law of Large Numbers

As n → ∞, sample mean → expected value

## Sourced field notes (fetched Oct 2026 — verify before citing)

- Seeing Theory Ch. 1: Basic Probability — Chance Events, Expectation, Variance (Brown University, Daniel Kunin et al.) — https://seeing-theory.brown.edu — interactive expectation/variance visualizations map onto lab §2–3 (random variables, E[X], Var(X)); run the Expectation tile before coding discrete vs. continuous expected-value drills.
- Seeing Theory Ch. 2: Compound Probability — Set Theory, Counting, Conditional Probability — https://seeing-theory.brown.edu — complements lab §1 (sample space, events, axioms) and §5 (Bayes); use the Conditional Probability tile to sanity-check prior/posterior/likelihood exercises.
- Seeing Theory Ch. 3: Probability Distributions — Random Variables, Discrete and Continuous, Central Limit Theorem — https://seeing-theory.brown.edu/probability-distributions/index.html — directly supports lab §4 (Bernoulli/Binomial/Poisson/Normal) and §6 (CLT); compare the CLT sampler against the lab's i.i.d.-average normality claim.
- Seeing Theory Ch. 5: Bayesian Inference — Bayes' Theorem, Likelihood, Prior to Posterior — https://seeing-theory.brown.edu/bayesian-inference/index.html — use the disease-test example and prior-to-posterior slider to verify lab §5 Bayes-rule calculations (P(A|B) = P(B|A)P(A)/P(B)).