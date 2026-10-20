# Explainable AI — Code Deep Dive

Two snippets: exact Shapley values for a 2-feature additive black box, and a grid-sampled
LIME surrogate. Deterministic; compile with `javac --release 21`, outputs quoted verbatim as observed.

## Snippet 1 — Shapley values by exact subset enumeration

Black box `f(x0, x1) = 1.5*x0 + 2.0*x1 + 0.5`; baseline `(0, 0)`; instance `(2, 3)`.

```java
public class ShapleyExact {
    public static void main(String[] args) {
        double f00 = f(0, 0), f10 = f(2, 0), f01 = f(0, 3), f11 = f(2, 3);
        System.out.printf("f([])=%.2f f({x0})=%.2f f({x1})=%.2f f({x0,x1})=%.2f%n", f00, f10, f01, f11);
        double phi0 = (f10 - f00) / 2 + (f11 - f01) / 2; // two orderings, averaged
        double phi1 = (f01 - f00) / 2 + (f11 - f10) / 2;
        System.out.printf("Shapley phi(x0) = %.2f (= w0*x0),  phi(x1) = %.2f (= w1*x1)%n", phi0, phi1);
        System.out.printf("additivity check: base + phi0 + phi1 = %.2f vs f(x) = %.2f%n", f00 + phi0 + phi1, f11);
    }
    static double f(double x0, double x1) { return 1.5 * x0 + 2.0 * x1 + 0.5; }
}
```

Observed output:

```
f([])=0.50 f({x0})=3.50 f({x1})=6.50 f({x0,x1})=9.50
Shapley phi(x0) = 3.00 (= w0*x0),  phi(x1) = 6.00 (= w1*x1)
additivity check: base + phi0 + phi1 = 9.50 vs f(x) = 9.50
```

Hand-check logic: for additive `f = b + w0 x0 + w1 x1` the pairwise margins telescope
exactly; efficiency holds numerically since `0.5 + 3 + 6 = 9.5`.

## Snippet 2 — LIME-style local surrogate, sampling-free grid

Four perturbation points on a fixed neighborhood: `(2,3), (3,3), (2,2), (1,3)`; ordinary
least squares over `[1, x0, x1]` (3x3 normal equations, Gaussian elimination in-class).

```java
public class LimeLocalFit {
    public static void main(String[] args) {
        double[][] xs = {{2, 3}, {3, 3}, {2, 2}, {1, 3}}; double[] ys = new double[4];
        for (int i = 0; i < 4; i++) ys[i] = blackBox(xs[i][0], xs[i][1]);
        // accumulate normal equations for columns [1, x0, x1]
        double s1 = 4, sx0 = 0, sx1 = 0, sxx0 = 0, sxx1 = 0, sx01 = 0, sy = 0, sx0y = 0, sx1y = 0;
        for (int i = 0; i < 4; i++) {
            sx0 += xs[i][0]; sx1 += xs[i][1]; sxx0 += xs[i][0] * xs[i][0]; sxx1 += xs[i][1] * xs[i][1];
            sx01 += xs[i][0] * xs[i][1]; sy += ys[i]; sx0y += xs[i][0] * ys[i]; sx1y += xs[i][1] * ys[i];
        }
        double[] c = solve3(new double[]{s1, sx0, sx1, sx0, sxx0, sx01, sx1, sx01, sxx1}, new double[]{sy, sx0y, sx1y});
        System.out.printf("surrogate: y = %.4f + %.4f*x0 + %.4f*x1%n", c[0], c[1], c[2]);
        System.out.printf("black box: y = 0.5 + 1.5*x0 + 2.0*x1  -> surrogate recovered it%n");
        for (int i = 0; i < 4; i++) { double fit = c[0] + c[1] * xs[i][0] + c[2] * xs[i][1];
            System.out.printf("point (%.0f,%.0f): truth=%.4f fit=%.4f residual=%.6f%n",
                xs[i][0], xs[i][1], ys[i], fit, fit - ys[i]); }
    }

    static double blackBox(double x0, double x1) { return 1.5 * x0 + 2.0 * x1 + 0.5; }
    static double[] solve3(double[] aIn, double[] bIn) { // solves a 3x3 system
        double[] a = aIn.clone(), b = bIn.clone(), x = new double[3];
        for (int col = 0; col < 3; col++) { // partial-pivot Gaussian elimination
            int piv = col;
            for (int r = col + 1; r < 3; r++) if (Math.abs(a[r * 3 + col]) > Math.abs(a[piv * 3 + col])) piv = r;
            swapRows(a, col, piv); double t1 = b[col]; b[col] = b[piv]; b[piv] = t1; double d = a[col * 3 + col];
            for (int r = col + 1; r < 3; r++) { double f1 = a[r * 3 + col] / d;
                for (int c2 = col; c2 < 3; c2++) a[r * 3 + c2] -= f1 * a[col * 3 + c2]; b[r] -= f1 * b[col]; }
        }
        for (int r = 2; r >= 0; r--) { double s2 = b[r]; // back substitution
            for (int c2 = r + 1; c2 < 3; c2++) s2 -= a[r * 3 + c2] * x[c2];
            x[r] = s2 / a[r * 3 + r];
        }
        return x;
    }
    static void swapRows(double[] a, int r1, int r2) {
        for (int c = 0; c < 3; c++) { double t = a[r1 * 3 + c]; a[r1 * 3 + c] = a[r2 * 3 + c]; a[r2 * 3 + c] = t; } }
}
```

Observed output:

```
surrogate: y = 0.5000 + 1.5000*x0 + 2.0000*x1
black box: y = 0.5 + 1.5*x0 + 2.0*x1  -> surrogate recovered it
point (2,3): truth=9.5000 fit=9.5000 residual=0.000000
point (3,3): truth=11.0000 fit=11.0000 residual=0.000000
point (2,2): truth=7.5000 fit=7.5000 residual=0.000000
point (1,3): truth=8.0000 fit=8.0000 residual=0.000000
```

Reading honestly: zero residuals happen only because the teacher really is linear and the
grid is square-ish; on a nonlinear black box the fit would compromise and show bigger
residuals — exactly when a local claim is implied and the proximity kernel matters.
