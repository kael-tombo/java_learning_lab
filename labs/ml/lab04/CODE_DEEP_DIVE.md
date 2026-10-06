# Support Vector Machines - Code Deep Dive

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

## 1. Module Map

```text
src/com/ml/lab04/
  Main.java                 driver: 2D separable + noisy datasets
  Svm.java                  primal view: fit via dual, predict, supportVectors()
  Kernel.java               @FunctionalInterface: double of(double[] a, double[] b)
  Kernels.java              linear, polynomial, rbf implementations
  Smo.java                  two-variable coordinate ascent on alpha
  SvmC.java                 C and gamma sweep over a validation grid
```

Kernel evaluation dominates runtime, so Kernels is the only place that knows about distance. Caching the kernel matrix is correct only while the data is fixed — the moment you add rows, the cache is a correctness bug.

## 2. Core Types

| Type | Responsibility |
|---|---|
| `Svm` | alpha[], b, supportVectorIndices; fit/predict/decisionFunction |
| `Kernel` | a functional interface so kernels are swappable and unit-testable |
| `Smo` | coordinate ascent: pick two alphas, solve the 2x2 subproblem in closed form |
| `SvmC` | grid sweep over C and gamma, returning validation curves |

---

## 3.1 Kernel functions and the squared-distance shortcut

Kernels are lambdas. The RBF expands the squared distance so the inner product never has to be recomputed per pair.

```java
@FunctionalInterface
public interface Kernel {
    double of(double[] a, double[] b);
    default String name() { return "custom"; }
}

public final class Kernels {
    public static Kernel linear() {
        return (a, b) -> {                       // K(x,z) = x.z
            double s = 0;
            for (int i = 0; i < a.length; i++) s += a[i] * b[i];
            return s;
        };
    }
    public static Kernel rbf(double gamma) {
        return new Kernel() {
            @Override public String name() { return "rbf(" + gamma + ")"; }
            @Override public double of(double[] a, double[] b) {
                double d2 = 0;                   // ||a-b||^2 without cancellation
                for (int i = 0; i < a.length; i++) {
                    double d = a[i] - b[i];
                    d2 += d * d;
                }
                return Math.exp(-gamma * d2);
            }
        };
    }
    public static Kernel poly(double r, int degree) {
        return (a, b) -> {
            double dot = 0;
            for (int i = 0; i < a.length; i++) dot += a[i] * b[i];
            return Math.pow(dot + r, degree);
        };
    }
}
```


---

## 3.2 SMO update for two alphas with clipping

The 2x2 subproblem has a closed form; the eta = K11 + K22 - 2K12 guard catches the degenerate case where the two points are identical.

```java
static void updatePair(int i, int j, double[] a, int[] y, double[][] K,
                         double C, double b) {
    if (a[i] < EPS || a[j] < EPS || a[i] >= C - EPS || a[j] >= C - EPS) return;
    double eta = K[i][i] + K[j][j] - 2 * K[i][j];            // >= 0 for a PSD kernel
    if (eta < 1e-12) return;                                   // identical points
    double oldI = a[i], oldJ = a[j];
    double ei = decision(i, a, y, K, b) - y[i];
    double ej = decision(j, a, y, K, b) - y[j];
    a[j] = clamp(a[j] - y[j] * (ei - ej) / eta, 0, C);         // equality constraint
    double lo = Math.max(0, a[j] - a[i]);
    double hi = Math.min(C, C + C - a[j] - a[i]);
    a[j] = Math.min(hi, Math.max(lo, a[j]));
    a[i] = clamp(a[i] + y[i] * y[j] * (oldJ - a[j]), 0, C);    // keep sum a_i y_i fixed
}

static double decision(int k, double[] a, int[] y, double[][] K, double b) {
    double f = b;
    for (int m = 0; m < a.length; m++) if (a[m] > EPS) f += a[m] * y[m] * K[m][k];
    return f;
}
```


---

## 4. Cost Model

| Operation | Complexity | Notes |
|---|---|---|
| Kernel matrix construction | `O(n²p)` | memory 8n² bytes is usually the binding limit |
| One SMO sweep over all pairs | `O(n²)` | in practice far fewer pairs thanks to the violation heuristic |
| Training to tolerance | `O(pass · n²)` | typically 5–30 passes with a shrinking eta |
| Prediction per point | `O(s · d)` | s = number of support vectors, d = kernel dimension |

## 5. Correctness and Numerics

- Standardise before computing any kernel; add a test that fails without it.
- Use an epsilon when deciding whether an alpha is at a bound.
- Recompute b as the mean over support vectors strictly inside the margin.
- Track the KKT violation and stop on it, not on a fixed iteration count.
- Report the support-vector fraction; above ~0.8 the model is memorising.

## 6. Test Strategy

- SVC on two well-separated points recovers w with ||w|| within 5% of the analytic value.
- Scaling one feature by 1000 changes predictions — proving scaling is active, not decorative.
- A linear kernel on linearly separable data yields zero training error.
- The linear kernel on a linear model reproduces a plain logistic/perceptron solution up to the loss used.
- SMO's final KKT violation is below 1e-4 for every interior alpha.
- Two identical rows produce eta <= 0 and are skipped without NaN.

## 7. Extension Points

- Add Platt scaling and show the sigmoid probabilities are calibrated on held-out data.
- Implement a linear kernel with sparse data so n can exceed 10^6.
- Report a learning curve against n to show where the margin stops helping.

## 8. Review Checklist

- [ ] Kernel is a swappable functional interface, not a boolean flag
- [ ] Scaling happens before the kernel, in the estimator
- [ ] Alpha bounds and the equality constraint are enforced on every update
- [ ] Training stops on KKT violation with a tolerance
- [ ] gamma and C are parameters with a sweep, not constants
- [ ] Support-vector fraction is logged every run
