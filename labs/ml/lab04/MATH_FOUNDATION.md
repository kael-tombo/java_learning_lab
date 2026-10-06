# Support Vector Machines - Mathematical Foundations

**Track:** ml  |  **Lab:** lab04  |  **Level:** Advanced

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
| `min 0.5||w||² s.t. yᵢ(wᵀxᵢ + b) ≥ 1` | Hard-margin primal - maximum-margin separator |
| `min 0.5||w||² + CΣξᵢ s.t. yᵢf(xᵢ) ≥ 1 − ξᵢ` | Soft-margin primal - slack variables priced by C |
| `f(x) = Σ αᵢyᵢK(xᵢ,x) + b` | Decision function - prediction depends only on support vectors |
| `K(x,z) = exp(−γ||x−z||²)` | RBF kernel - infinite-dimensional feature map |
| `margin width = 2/||w||` | Geometric margin - objective minimises ||w|| to widen it |
| `αᵢ ∈ [0, C], Σαᵢyᵢ = 0` | Dual constraints - 0 < α identifies support vectors |
| `K(x,z) = (xᵀz + r)^d` | Polynomial kernel - finite-degree expansion |
| `gamma = 1/(2σ²)` | RBF bandwidth - set from feature variance when not tuned |

## Why the Math Matters

The SVM is where optimisation theory becomes geometry. The dual derivation shows why only a few points matter, and the kernel trick shows that a model in an infinite space can still be trained and evaluated with only pairwise inner products.


---

## 1. Primal to dual

```text
min 0.5||w||^2 + C sum xi   s.t. y_i(w.x_i + b) >= 1 - xi, xi >= 0
dual: max sum a_i - 0.5 || sum a_i y_i x_i ||^2  s.t. 0 <= a_i <= C, sum a_i y_i = 0
```

Lagrangian duality is exact for this convex problem: the dual optimum equals the primal optimum. That is why training can be expressed purely in terms of pairwise similarities.

**Worked example.** For a 3-point linearly separable set, the dual has a unique solution with two non-zero α (the support vectors); the third point's α is exactly 0 and it can be deleted without moving the boundary.


---

## 2. The margin and its geometric meaning

```text
distance from a point to the boundary = |w.x + b| / ||w||
correct side requires >= 1/||w||, so margin width = 2/||w||
minimising 0.5||w||^2 maximises the margin
```

This is why hard-margin SVMs are robust: a point deep inside a class region has zero influence. Robustness to noise comes from the *loss on the margin*, not from counting points.

**Worked example.** ||w|| = 2 gives a margin of 1.0; ||w|| = 10 gives 0.2. A support vector moved 0.01 along the normal cannot change ||w|| much, but a point that leaves the margin band enters as a new α and can.


---

## 3. Kernel expansion

```text
linear:   K(x,z) = x.z
polynomial: K(x,z) = (x.z + r)^d
RBF:      K(x,z) = exp(-gamma ||x-z||^2)
||x-z||^2 = ||x||^2 - 2x.z + ||z||^2
```

Every training and prediction step only ever needs K(xᵢ,xⱼ). Expanding the polynomial as a feature map gives degree-d terms with binomial coefficients; the RBF expansion is an infinite sum over the feature map.

**Worked example.** Polynomial with d=3, r=1, x.z=2: K = 27, and the expansion is 8x₁³ + 12x₁²x₂ + 6x₁x₂² + x₂³ + 6x₁² + 12x₁x₂ + 6x₂ + 3x₁ + 3x₂ + 1.


---

## 4. KKT conditions and SMO convergence

```text
stationarity: w = sum a_i y_i x_i
complementary slackness: a_i (margin violation) = 0
0 <= a_i <= C, sum a_i y_i = 0
violation = |y_i f(x_i) - 1| when 0 < a_i < C
```

A point with a strictly interior α must sit exactly on the margin; a point at α = 0 must be correctly classified outside it; a point at α = C is inside the margin. SMO sweeps α until no interior point is violated.

**Worked example.** Two interior points violating by 0.01 and -0.02: SMO picks both, solves the 2x2 quadratic exactly, and the total KKT violation drops by ~0.03 in a single update.


---

## 5. Soft margin C and the classification error trade-off

```text
training error ~ C (large C)
generalisation gap = train err - test err grows with C
for separable data, large C drives ||w|| -> infinity
```

There is no closed-form error curve; the only honest way to pick C is a validation sweep. Separable data plus large C is numerically the worst case, not the best.

**Worked example.** Separable data with C = 1e6: train error 0, support-vector fraction 0.98, test error 0.19. Dropping C to 0.1 gives 0.94 support vectors and test error 0.04.


---

## 6. Scalability, and the practical ceiling

```text
kernel matrix: n^2 doubles = 8n^2 bytes
time per SMO pass: O(n^2)
heuristic bound in use: n < 5 x 10^4
```

Memory, not time, is the binding constraint. Above that, use a linear kernel (sparse representation), an approximate kernel, or switch algorithms entirely.

**Worked example.** n = 10,000 needs 800 MB for the matrix; n = 40,000 needs 12.8 GB and likely OOMs on a 16 GB pod. n = 1,000,000 is unthinkable for a kernel SVM.


---

## Cheat Sheet

- `min 0.5||w||² s.t. yᵢ(wᵀxᵢ + b) ≥ 1` - Hard-margin primal
- `min 0.5||w||² + CΣξᵢ s.t. yᵢf(xᵢ) ≥ 1 − ξᵢ` - Soft-margin primal
- `f(x) = Σ αᵢyᵢK(xᵢ,x) + b` - Decision function
- `K(x,z) = exp(−γ||x−z||²)` - RBF kernel
- `margin width = 2/||w||` - Geometric margin
- `αᵢ ∈ [0, C], Σαᵢyᵢ = 0` - Dual constraints
- `K(x,z) = (xᵀz + r)^d` - Polynomial kernel
- `gamma = 1/(2σ²)` - RBF bandwidth

## Numerical Traps

- Using RBF without standardising — gamma then describes a different geometry than you think.
- Assuming ||w|| from the dual equals the primal objective; they differ by the slack contribution.
- Reading the decision value as a probability and calibrating a threshold on it.
- Precomputing a kernel matrix for n above the memory budget instead of switching to a linear kernel.
- Sweeping C on the test set; the optimal margin is chosen, not measured.

## Self-Check Problems

1. For two points x=(-1,-1) and z=(1,1) with labels -1 and +1, find the hard-margin solution by hand.
2. Expand (xᵀz + 1)² and identify every monomial term with its coefficient.
3. Show that the RBF kernel matrix for n points is always positive semi-definite by construction.
4. Compute the kernel matrix for three 2D points under linear, polynomial(d=2) and RBF(gamma=0.5).
5. Given a trained SVM with α = [0.4, 0.0, 0.7] and y = [1, -1, 1], state which points are support vectors and why.
