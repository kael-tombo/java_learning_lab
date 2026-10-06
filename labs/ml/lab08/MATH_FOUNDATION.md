# Principal Component Analysis - Mathematical Foundations

**Track:** ml  |  **Lab:** lab08  |  **Level:** Intermediate

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
| `Σ = (1/(n−1)) XᵀX (centred X)` | Sample covariance - the matrix whose eigenvectors we want |
| `Σvᵢ = λᵢvᵢ` | Eigenproblem - directions and their variance |
| `EV ratio = λᵢ / Σᵢλᵢ` | Explained variance ratio - share of variance per component |
| `zᵢ = (xᵢ − μ) Wₖ` | Projection - score in the new basis |
| `x̂ = μ + z Wₖᵀ` | Reconstruction - rank-k approximation of X |
| `λᵢ = sᵢ² / (n−1)` | Singular-value link - why SVD avoids forming Σ |
| `total variance = Σᵢ var(xᵢ)` | Trace relation - explained ratios must sum to 1 |

## Why the Math Matters

PCA is one Lagrange multiplier and a symmetric eigenproblem. Once you see that maximising projection variance under a unit-norm constraint gives the eigenvectors of the covariance matrix, everything — reconstruction, explained variance, the SVD equivalence — follows.


---

## 1. Variance maximisation as an eigenproblem

```text
max_w Var(w'x) = w' S w  s.t.  w'w = 1
Lagrangian: S w - lambda w = 0
=> w = eigenvector of S with the largest eigenvalue
```

One constraint turns a quadratic optimisation into an eigenproblem. The optimum is a unit vector because the objective is homogeneous of degree two, so without the constraint it is unbounded.

**Worked example.** A 2D dataset with S = [[3, 2], [2, 3]] has eigenvalues 5 and 1 with eigenvectors (1,1)/√2 and (1,−1)/√2. PC1 keeps 5/6 = 83% of variance.


---

## 2. Explained variance and the cumulative curve

```text
explained_i = lambda_i / trace(S)
trace(S) = sum_j var(x_j)
cumulative_k = sum_{i<=k} lambda_i / trace(S)
```

The trace is total variance, so the ratios must sum to 1. A steep drop followed by a flat tail is the natural place to cut; the 95% convention is a starting point, not a decision.

**Worked example.** Eigenvalues 5.0, 1.0, 0.5, 0.3, 0.2 total 7.0. k = 2 keeps 85.7%, k = 3 keeps 92.9%, k = 4 keeps 97.1%.


---

## 3. Eigen-decomposition versus SVD

```text
X_c = X - 1 mu'  (centred)
S = X_c' X_c / (n-1)
SVD: X_c = U S V'  =>  lambda_i = s_i^2 / (n-1)
components W = V
```

SVD avoids forming the p×p covariance matrix, so the conditioning cost of squaring is not paid. The eigenvalues of the covariance are the squared singular values, scaled.

**Worked example.** p = 50,000 features: forming XᵀX needs 20 GB and squares the condition number. Truncated SVD on X_c needs O(p·k) and never forms it.


---

## 4. Reconstruction error from the spectrum

```text
||X_c - Z_k W_k'||_F^2 = sum_{i>k} s_i^2
relative error = 1 - cumulative_k
```

Because the components are orthogonal, the discarded variance is exactly the sum of the dropped eigenvalues. That makes k selection a pure trade-off curve with no fitting required.

**Worked example.** Dropping a component with eigenvalue 0.5 out of 7.0 total adds a relative error of 7.1% — visible, but often harmless if that direction is noise.


---

## 5. Whitening and why it changes distance geometry

```text
whitened = Z_k / s_i  (each component scaled to unit variance)
eigenvalues of Cov(whitened) = I
```

Whitening removes all residual variance differences between components, so euclidean distance no longer favours high-variance directions. Useful for k-means and k-NN after PCA; usually harmful if you want to keep the importance structure.

**Worked example.** Components with s = 10 and s = 1 contribute 100:1 to unwhitened distance and 1:1 after whitening — a large change in which points look close.


---

## 6. Choosing k by downstream performance

```text
for k in 1..p_max:
  Z_k = X_c W_k
  score_k = cross_val_score(model, Z_k)
choose argmax_k score_k - lambda * k
```

Retained variance is not usefulness. The right k is the one that maximises held-out performance of the model you actually care about, which can be far below the variance threshold.

**Worked example.** For a text classifier, k = 50 keeps 40% of variance but often beats k = 300 which keeps 95%, because the extra dimensions are noise.


---

## Cheat Sheet

- `Σ = (1/(n−1)) XᵀX (centred X)` - Sample covariance
- `Σvᵢ = λᵢvᵢ` - Eigenproblem
- `EV ratio = λᵢ / Σᵢλᵢ` - Explained variance ratio
- `zᵢ = (xᵢ − μ) Wₖ` - Projection
- `x̂ = μ + z Wₖᵀ` - Reconstruction
- `λᵢ = sᵢ² / (n−1)` - Singular-value link
- `total variance = Σᵢ var(xᵢ)` - Trace relation

## Numerical Traps

- Forgetting to centre, which makes PC1 point at the mean vector.
- Sorting eigenvalues without permuting the eigenvectors with them.
- Assuming the eigenvector sign is meaningful.
- Dividing by n rather than n−1 in the covariance, biasing eigenvalues low.
- Treating cumulative explained variance as a decision rule rather than a diagnostic.

## Self-Check Problems

1. Compute the covariance matrix and both eigenvalues by hand for the 2D example [[3,2],[2,3]].
2. Derive the eigenvectors of the same matrix and verify S w = lambda w.
3. Show that the reconstruction error equals the sum of dropped eigenvalues.
4. Given eigenvalues 5.0, 1.0, 0.5, 0.3, 0.2, find k for 85%, 93% and 97% cumulative variance.
5. Demonstrate that PCA on unscaled data collapses to the highest-variance axis for a 2D case.
