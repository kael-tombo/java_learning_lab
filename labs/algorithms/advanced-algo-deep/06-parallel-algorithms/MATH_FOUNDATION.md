# Math Foundation — Parallel Algorithms

Derivations, applicability, and counter-examples for the formulas this lab relies on.

---

## Brent's theorem

At each step either a node on the critical path executes, or all p processors are busy. There are at most T∞ critical-path steps and at most (T₁ - T∞)/p busy steps. Hence T_p ≤ T₁/p + T∞.

This is why greedy scheduling is within a factor 2 of optimal for any DAG.

## Scan of a linear recurrence

Any recurrence x_{i+1} = a_i·x_i + b_i can be written as 2×2 matrix product M_i = [[a_i, b_i],[0,1]]; composing them is associative, so a Θ(log n)-span tree combines them.

This is the associative-operator view that makes every linear scan parallelisable.

## Amdahl's law derivation

Serial fraction f takes f·T, the parallel part takes (1-f)T/p. Total T(p) = T(f + (1-f)/p), so speedup = 1/(f + (1-f)/p).

As p→∞ the speedup tends to 1/f — the serial fraction is the asymptotic ceiling.

## Work-span lower bounds

T_p ≥ T₁/p (work conserved) and T_p ≥ T∞ (critical path sequential). Hence T_p ≥ max(T₁/p, T∞).

A good algorithm makes T₁/p ≈ T∞ by raising parallelism T₁/T∞.

## Brent vs the lower bounds

Brent gives T_p ≤ T₁/p + T∞ ≤ 2·max(T₁/p, T∞) — within a factor 2 of the lower bound, so greedy scheduling is a 2-approximation.

This is why "just run the ready tasks" suffices in practice.
