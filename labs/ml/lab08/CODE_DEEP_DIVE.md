# Principal Component Analysis - Code Deep Dive

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

## 1. Module Map

```text
src/com/ml/lab08/
  Main.java                driver: 4D data reduced to 2D, variance report
  Pca.java                 fit via covariance eigendecomposition, transform, inverseTransform
  SvdPca.java              same results via SVD of the centred matrix
  Eigen.java               Jacobi eigenvalue solver for real symmetric matrices
  VarianceReport.java      explained ratios, cumulative curve, reconstruction error
```

Eigen.java is a symmetric-matrix solver, not a general eigensolver. Keeping it symmetric-specialised removes an entire class of bugs and is stable for the small p where this route is appropriate.

## 2. Core Types

| Type | Responsibility |
|---|---|
| `Pca` | mean, components, eigenvalues; fit/transform/inverseTransform |
| `SvdPca` | the numerically preferred path; cross-checked against Pca in tests |
| `Eigen` | Jacobi iteration returning eigenvalues and eigenvectors for a symmetric matrix |
| `VarianceReport` | explained ratios, cumulative curve, reconstruction error per k |

---

## 3.1 Fit as a complete, serialisable transform

Scaling, centring and the component matrix travel together. A PCA that ships as a bare matrix is a bug waiting for a unit mismatch.

```java
public record PcaModel(double[] featureMean, double[] featureScale,
                         double[][] components, double[] eigenvalues,
                         boolean standardised) {

    public double[][] transform(double[][] x) {
        int n = x.length, k = components.length;
        double[][] z = new double[n][k];
        for (int i = 0; i < n; i++) {
            for (int c = 0; c < k; c++) {
                double s = 0;
                for (int j = 0; j < components[c].length; j++) {
                    double v = standardised ? (x[i][j] - featureMean[j]) / featureScale[j]
                                             : (x[i][j] - featureMean[j]);
                    s += v * components[c][j];
                }
                z[i][c] = s;
            }
        }
        return z;
    }
}
```


---

## 3.2 Eigen-decomposition via the Jacobi method

Jacobi rotations iteratively zero off-diagonal entries of a symmetric matrix, converging to eigenvalues on the diagonal and eigenvectors as columns of the rotation product.

```java
static Eigen decompose(double[][] a) {
    int n = a.length;
    double[][] m = deepCopy(a);              // working copy: never mutate the input
    double[][] v = identity(n);              // accumulates rotations into eigenvectors
    for (int sweep = 0; sweep < 50; sweep++) {
        double off = 0;
        for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) off += m[i][j] * m[i][j];
        if (off < 1e-20) break;              // converged: off-diagonal mass ~ 0
        for (int p = 0; p < n - 1; p++) {
            for (int q = p + 1; q < n; q++) {
                if (Math.abs(m[p][q]) < 1e-18) continue;
                double theta = (m[q][q] - m[p][p]) / (2 * m[p][q]);
                double t = Math.signum(theta) / (Math.abs(theta) + Math.sqrt(theta * theta + 1));
                double c = 1 / Math.sqrt(t * t + 1), s = t * c;   // stable rotation
                rotate(m, v, p, q, c, s);
            }
        }
    }
    double[] values = new double[n];
    for (int i = 0; i < n; i++) values[i] = m[i][i];            // eigenvalues
    sortDescendingKeepingColumns(values, v);                    // eigenvalues AND vectors
    fixSignConvention(v);                                       // reproducible sign
    return new Eigen(values, v);
}
```


---

## 4. Cost Model

| Operation | Complexity | Notes |
|---|---|---|
| Covariance construction | `O(np²)` | fine to p ≈ 1000 |
| Jacobi eigenvalue sweeps | `O(sweeps · p³)` | typically 5–10 sweeps for a symmetric matrix |
| Transformation of new data | `O(n·p·k)` | k = retained components |
| Truncated SVD instead | `O(np·k)` | the route to use when p is large |

## 5. Correctness and Numerics

- Always centre; make it part of fit so callers cannot forget.
- Sort eigenvalues and permute eigenvector columns together — a classic silent bug.
- Fix the sign convention so two runs produce byte-identical models.
- Use (n−1) in the covariance, and never form XᵀX when p is large.
- Assert the explained ratios sum to 1 within 1e-9; it catches most implementation errors.

## 6. Test Strategy

- Explained variance ratios sum to 1 ± 1e-9.
- Pca and SvdPca agree on components up to sign within 1e-8.
- Two runs produce byte-identical component matrices (sign convention holds).
- Transform then inverseTransform reconstructs to within 1e-8 when k = p.
- Truncating to k components gives a reconstruction error matching 1 - cumulative_k.
- A dataset with one dominant axis puts PC1 on that axis when not standardised.

## 7. Extension Points

- Implement truncated SVD on a sparse matrix and compare with covariance PCA.
- Add whitening and show the effect on k-means cluster shapes.
- Implement incremental PCA (online updating) for streaming features.

## 8. Review Checklist

- [ ] Centring is inside fit, not the caller's responsibility
- [ ] Standardisation is an explicit, recorded flag
- [ ] Eigenvalue/vector pairs are permuted together
- [ ] Sign convention fixed and asserted in a test
- [ ] Mean, scale and components serialised as one unit
- [ ] k chosen with downstream validation, not only cumulative variance
