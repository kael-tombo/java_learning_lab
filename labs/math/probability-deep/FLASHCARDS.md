# Probability Flashcards

## Fundamentals
| Front | Back |
|-------|------|
| Sample space Ω | Set of all possible outcomes |
| Event | Subset of sample space |
| P(A) ≥ 0 | Non-negativity axiom |
| P(Ω) = 1 | Normalization axiom |
| P(A') | 1 - P(A) |
| P(A ∪ B) | P(A) + P(B) - P(A∩B) |
| Conditional probability P(A|B) | P(A∩B)/P(B) |
| Independence | P(A∩B) = P(A)P(B) |
| Bayes' Theorem | P(A|B) = P(B|A)P(A)/P(B) |
| Law of total probability | P(B) = ΣP(B|Aᵢ)P(Aᵢ) |

## Discrete Distributions
| Front | Back |
|-------|------|
| Bernoulli(p) | Single trial: P(1)=p, P(0)=1-p |
| Binomial(n,p) | C(n,k)p^k(1-p)^(n-k) |
| Geometric(p) | (1-p)^(k-1)p; trials until first success |
| Poisson(λ) | λ^k e^(-λ)/k!; rare events |
| Hypergeometric | Sampling without replacement |
| E[X] for Binomial | np |
| Var(X) for Binomial | np(1-p) |
| E[X] for Poisson | λ |
| Var(X) for Poisson | λ |
| E[X] for Geometric | 1/p |

## Continuous Distributions
| Front | Back |
|-------|------|
| Uniform(a,b) | f(x) = 1/(b-a); E[X] = (a+b)/2 |
| Exponential(λ) | f(x) = λe^(-λx); memoryless |
| Normal(μ,σ²) | Bell curve; 68-95-99.7 rule |
| Gamma(α,β) | Generalizes exponential |
| E[X] for Exponential | 1/λ |
| Var(X) for Exponential | 1/λ² |
| E[X] for Uniform | (a+b)/2 |
| Memoryless property | P(X>s+t\|X>s) = P(X>t) |

## Expectation and Variance
| Front | Back |
|-------|------|
| E[X] | Σx·p(x) or ∫x·f(x)dx |
| E[aX+b] | aE[X] + b |
| E[g(X)] | Σg(x)p(x) or ∫g(x)f(x)dx |
| Var(X) | E[(X-μ)²] = E[X²] - (E[X])² |
| Var(aX+b) | a²Var(X) |
| Cov(X,Y) | E[XY] - E[X]E[Y] |
| Correlation ρ | Cov(X,Y)/(σ_X·σ_Y) |
| Independent ⟹ | Cov(X,Y) = 0 |
| Var(X+Y) independent | Var(X) + Var(Y) |

## Limit Theorems & Markov Chains
| Front | Back |
|-------|------|
| Law of Large Numbers | Sample mean → population mean |
| Central Limit Theorem | (X̄-μ)/(σ/√n) → N(0,1) |
| CLT applicability | n ≥ 30 for approx. normality |
| MGF M_X(t) | E[e^(tX)] |
| MGF property | M_{X+Y} = M_X·M_Y if independent |
| Markov property | Future depends only on present |
| Transition matrix P | P_ij = P(X_{n+1}=j \| X_n=i) |
| Stationary distribution π | π = πP |
| Ergodic chain | Irreducible + aperiodic |
| Absorption probability | Probability of reaching absorbing state |
