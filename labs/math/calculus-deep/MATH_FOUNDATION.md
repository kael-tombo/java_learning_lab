# Calculus Mathematical Foundation

## 1. The Real Number System
Calculus operates on ℝ, the complete ordered field. Completeness means every nonempty set bounded above has a least upper bound (supremum). This property distinguishes ℝ from ℚ and underpins all limit arguments.

**Archimedean Property:** For any x ∈ ℝ, there exists n ∈ ℕ with n > x.

**Density of ℚ:** Between any two reals lies a rational number.

## 2. Formal Limit Definition
**Definition:** lim(x→a) f(x) = L iff ∀ε > 0, ∃δ > 0 such that
0 < |x - a| < δ ⟹ |f(x) - L| < ε.

**Negation (non-existence):** ∃ε > 0 such that ∀δ > 0, ∃x with
0 < |x - a| < δ but |f(x) - L| ≥ ε.

**Sequential criterion:** lim(x→a) f(x) = L iff for every sequence x_n → a (x_n ≠ a), f(x_n) → L.

## 3. Continuity
**Definition:** f is continuous at a if lim(x→a) f(x) f(a).

**Theorem (Extreme Value):** A continuous function on [a,b] attains its maximum and minimum.

**Theorem (Intermediate Value):** If f is continuous on [a,b] and k lies between f(a) and f(b), then ∃c ∈ (a,b) with f(c) = k.

## 4. Differentiability
**Definition:** f is differentiable at a if lim(h→0) [f(a+h) - f(a)]/h exists.

**Theorem:** Differentiability implies continuity (converse is false: |x| at 0).

**Mean Value Theorem:** If f is continuous on [a,b] and differentiable on (a,b), then ∃c ∈ (a,b) with f'(c) = (f(b) - f(a))/(b - a).

**Rolle's Theorem:** Special case where f(a) = f(b); guarantees f'(c) = 0.

## 5. The Riemann Integral
**Definition:** ∫[a,b] f(x)dx = lim(n→∞) Σ f(x_i*)Δx_i where Δx = (b-a)/n.

**Integrability:** Continuous functions on [a,b] are Riemann integrable. Bounded functions with finitely many discontinuities are also integrable.

**Fundamental Theorem of Calculus:**
- Part 1: d/dx ∫[a,x] f(t)dt = f(x)
- Part 2: ∫[a,b] f(x)dx = F(b) - F(a) where F' = f

## 6. Series Convergence
**Definition:** Σa_n converges iff the sequence of partial sums S_N = Σ(n=1 to N) a_n converges.

**Cauchy criterion:** Σa_n converges iff ∀ε > 0, ∃N such that |Σ(n=m to p) a_n| < ε for all p ≥ m ≥ N.

**Absolute convergence:** Σ|a_n| converges implies Σa_n converges.

**Rearrangement theorem:** Absolutely convergent series can be rearranged freely; conditionally convergent series can be rearranged to any value (Riemann).

## 7. Taylor's Theorem
**Statement:** If f has n+1 derivatives near a, then
f(x) = Σ(k=0 to n) f^(k)(a)/k! ·(x-a)^k + R_n(x)
where R_n(x) = f^(n+1)(ξ)/(n+1)! ·(x-a)^(n+1) for some ξ between a and x (Lagrange remainder).

## 8. Key Proofs
**Product rule proof:** Add and subtract f(x+h)g(x) in the difference quotient, split, and take limits.

**Chain rule proof:** Define Δu = g(x+h) - g(x); write [f(g(x+h)) - f(g(x))]/h = [f(u+Δu) - f(u)]/Δu · Δu/h.

**Fundamental theorem proof:** Use the Mean Value Theorem on F(x) = ∫[a,x] f(t)dt to show F'(x) = f(x).
