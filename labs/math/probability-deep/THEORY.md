# Probability Theory

## 1. Probability Spaces and Axioms
A **probability space** (Ω, F, P) consists of:
- **Sample space Ω:** Set of all possible outcomes
- **σ-algebra F:** Collection of events (subsets of Ω)
- **Probability measure P:** F → [0, 1] satisfying:

**Kolmogorov Axioms:**
1. P(A) ≥ 0 for all A ∈ F
2. P(Ω) = 1
3. For disjoint A₁, A₂, ...: P(∪Aᵢ) = ΣP(Aᵢ)

**Consequences:**
- P(∅) = 0
- P(A') = 1 - P(A)
- P(A ∪ B) = P(A) + P(B) - P(A ∩ B)
- If A ⊆ B, then P(A) ≤ P(B)

**Conditional probability:** P(A|B) = P(A ∩ B) / P(B) for P(B) > 0

**Independence:** A and B are independent if P(A ∩ B) = P(A)·P(B)

**Bayes' Theorem:** P(A|B) = P(B|A)·P(A) / P(B)

**Law of Total Probability:** P(B) = Σ P(B|Aᵢ)·P(Aᵢ) for partition {Aᵢ}

## 2. Discrete Random Variables
A **random variable** X maps outcomes to real numbers.

**Probability mass function (PMF):** p(x) = P(X = x)

**Cumulative distribution function (CDF):** F(x) = P(X ≤ x)

**Key distributions:**
- **Bernoulli(p):** P(X=1) = p, P(X=0) = 1-p
- **Binomial(n,p):** P(X=k) = C(n,k)p^k(1-p)^(n-k)
- **Geometric(p):** P(X=k) = (1-p)^(k-1)p for k = 1, 2, ...
- **Poisson(λ):** P(X=k) = λ^k e^(-λ)/k!
- **Hypergeometric:** Sampling without replacement

**Expectation:** E[X] = Σ x·p(x)

**Variance:** Var(X) = E[(X - E[X])²] = E[X²] - (E[X])²

**Properties:**
- E[aX + b] = aE[X] + b
- Var(aX + b) = a²Var(X)
- For independent X, Y: Var(X + Y) = Var(X) + Var(Y)

## 3. Continuous Random Variables
A continuous RV has a **probability density function (PDF)** f(x) such that:
- f(x) ≥ 0
- ∫f(x)dx = 1
- P(a ≤ X ≤ b) = ∫[a,b] f(x)dx

**CDF:** F(x) = ∫[-∞,x] f(t)dt

**Key distributions:**
- **Uniform(a,b):** f(x) = 1/(b-a) for a ≤ x ≤ b
- **Exponential(λ):** f(x) = λe^(-λx) for x ≥ 0
- **Normal(μ,σ²):** f(x) = (1/√(2πσ²))e^(-(x-μ)²/(2σ²))
- **Gamma(α,β):** f(x) = (β^α/Γ(α))x^(α-1)e^(-βx)

**Expectation:** E[X] = ∫x·f(x)dx

**Properties:**
- E[g(X)] = ∫g(x)f(x)dx
- Memoryless property: P(X > s+t | X > s) = P(X > t) (Exponential)

## 4. Joint Distributions and Covariance
**Joint PMF/PDF:** Describes two random variables simultaneously.

**Marginals:** Sum/integrate out the other variable.

**Conditional distributions:** f(x|y) = f(x,y)/f_Y(y)

**Covariance:** Cov(X,Y) = E[(X-μ_X)(Y-μ_Y)] = E[XY] - E[X]E[Y]

**Correlation:** ρ = Cov(X,Y)/(σ_X·σ_Y); -1 ≤ ρ ≤ 1

**Independence:** X, Y independent ⟹ Cov(X,Y) = 0 (converse false)

**Conditional expectation:** E[X|Y] is a random variable; E[E[X|Y]] = E[X]

## 5. Moment Generating Functions
**MGF:** M_X(t) = E[e^(tX)]

**Properties:**
- M_X(0) = 1
- E[X^n] = M_X^(n)(0) (nth derivative at 0)
- M_{X+Y}(t) = M_X(t)·M_Y(t) for independent X, Y
- Uniqueness: MGF determines distribution (when it exists)

**Common MGFs:**
- Binomial: M(t) = (1-p+pe^t)^n
- Poisson: M(t) = e^(λ(e^t-1))
- Normal: M(t) = e^(μt + σ²t²/2)
- Exponential: M(t) = λ/(λ-t) for t < λ

## 6. Limit Theorems
**Law of Large Numbers (LLN):**
- **Weak:** (1/n)ΣXᵢ → μ in probability
- **Strong:** (1/n)ΣXᵢ → μ almost surely

**Central Limit Theorem (CLT):**
For i.i.d. Xᵢ with mean μ and variance σ²:
√n((1/n)ΣXᵢ - μ) → N(0, σ²) in distribution

Equivalently: (ΣXᵢ - nμ)/(σ√n) → N(0, 1)

**Applications:**
- Approximating binomial with normal (when np > 5, n(1-p) > 5)
- Confidence intervals
- Hypothesis testing
- Error bounds in estimation

**Berry-Esseen theorem:** Bounds CLT convergence rate: O(1/√n)

## 7. Markov Chains (Introduction)
A **Markov chain** is a sequence of random variables with:
P(X_{n+1} = j | X_n = i, X_{n-1}, ...) = P(X_{n+1} = j | X_n = i)

**Transition matrix P:** P_ij = P(X_{n+1} = j | X_n = i)

**Stationary distribution π:** π = πP (left eigenvector with eigenvalue 1)

**Key concepts:**
- Irreducible: every state reachable from every other
- Aperiodic: no periodic returns
- Ergodic: irreducible + aperiodic; converges to stationary distribution
- Absorption probabilities and expected hitting times
