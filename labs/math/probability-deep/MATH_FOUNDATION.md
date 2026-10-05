# Probability Mathematical Foundation

## 1. Measure-Theoretic Probability
A probability space (Ω, F, P) where:
- Ω is the sample space
- F ⊆ 2^Ω is a σ-algebra (closed under complement and countable unions)
- P: F → [0,1] is a measure with P(Ω) = 1

**Kolmogorov's axioms** formalize probability as measure theory. This foundation handles both discrete and continuous cases uniformly.

## 2. Key Theorems

**Theorem (Inclusion-Exclusion):**
P(∪Aᵢ) = ΣP(Aᵢ) - ΣP(Aᵢ∩Aⱼ) + ΣP(Aᵢ∩Aⱼ∩Aₖ) - ...

*Proof by induction:* Base case n=2 is the addition rule. Inductive step applies the base case to (∪_{i=1}^n A_i) ∪ A_{n+1}.

**Theorem (Monotone Convergence):**
If A₁ ⊆ A₂ ⊆ ... then P(∪Aₙ) = lim P(Aₙ).

*Proof:* Write ∪Aₙ = ⊔(Aₙ \ A_{n-1}) as disjoint union; countable additivity gives P(∪Aₙ) = ΣP(Aₙ \ A_{n-1}) = lim Σ_{k=1}^n P(A_k \ A_{k-1}) = lim P(A_n).

## 3. Expectation Theorems

**Theorem (Linearity):** E[aX + bY] = aE[X] + bE[Y].
*Proof (discrete):* E[aX + bY] = Σ(ax + by)p(x,y) = aΣx·p(x,y) + bΣy·p(x,y) = aE[X] + bE[Y].

**Theorem (Independence):** If X, Y independent, E[XY] = E[X]E[Y].
*Proof:* E[XY] = ΣΣxy·p(x,y) = ΣΣxy·p_X(x)p_Y(y) = (Σx·p_X(x))(Σy·p_Y(y)) = E[X]E[Y].

**Theorem (Variance):** Var(X) = E[X²] - (E[X])².
*Proof:* Var(X) = E[(X-μ)²] = E[X² - 2μX + μ²] = E[X²] - 2μE[X] + μ² = E[X²] - μ².

## 4. Bayes' Theorem Proof
P(A|B) = P(A∩B)/P(B) = P(B|A)P(A)/P(B) by definition of conditional probability and symmetry of intersection.

**General form:** P(Aᵢ|B) = P(B|Aᵢ)P(Aᵢ) / ΣⱼP(B|Aⱼ)P(Aⱼ) via law of total probability.

## 5. Central Limit Theorem (Lindeberg-Lévy)
**Theorem:** For i.i.d. X₁, ..., Xₙ with mean μ and finite variance σ²:
Z_n = (ΣXᵢ - nμ)/(σ√n) → N(0,1) in distribution.

*Proof sketch via MGFs:*
- M_{Z_n}(t) = [M_X(t/(σ√n))]^n · e^(-μt√n/σ)
- Taylor expand M_X: M_X(s) = 1 + μs + (μ²+σ²)s²/2 + o(s²)
- Substitute s = t/(σ√n): log M_{Z_n}(t) = n·log(1 + μt/(σ√n) + t²/(2n) + o(1/n)) - μt√n/σ
- As n → ∞: log M_{Z_n}(t) → t²/2
- Thus M_{Z_n}(t) → e^(t²/2) = M_{N(0,1)}(t); uniqueness of MGFs gives convergence.

## 6. Law of Large Numbers
**Weak LLN (Khinchine):** For i.i.d. Xᵢ with finite mean μ, (1/n)ΣXᵢ → μ in probability.

*Proof via Chebyshev:* P(|X̄_n - μ| ≥ ε) ≤ Var(X̄_n)/ε² = σ²/(nε²) → 0.

**Strong LLN:** Almost surely (Kolmogorov); requires more advanced tools (Borel-Cantelli).

## 7. Markov Chain Theorems

**Theorem:** An irreducible, aperiodic Markov chain has a unique stationary distribution π.

*Proof:* Perron-Frobenius: P has eigenvalue 1 with unique positive left eigenvector (normalized to sum 1). Convergence follows from spectral gap.

**Ergodic Theorem:** For ergodic chain, (1/n)Σ 1_{X_k=i} → π_i almost surely. Time averages equal ensemble averages.
