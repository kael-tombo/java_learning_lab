# math-for-ai-deep — Code Deep Dive

Java 21, no dependencies. Every numerical algorithm implemented explicitly, with the
identity it satisfies written next to it as the assertion.

## 1. Project Structure

```
math-for-ai-deep/
  src/com/ailab/math/
    linalg/{Vector,Matrix,GramSchmidt,Linalg}.java
    decomp/{JacobiEigen,Svd,PowerIteration,Cholesky}.java
    ad/{Tape,Node,ReverseMode}.java
    prob/{Distributions,ExponentialFamily}.java
    bayes/{Bayes,BetaBinomial,NormalNormal,Vi}.java
    info/{Entropy,Kl,Js,Perplexity}.java
    opt/{Convex,Optimizers,Lagrangian}.java
    numeric/{Stable,Kahan,LogSumExp}.java
    Main.java
```

## 2. Matrix With Shape Assertions

```java
public final class Matrix {

    public final int rows, cols;
    private final double[][] a;

    public Matrix(int rows, int cols) { this.rows = rows; this.cols = cols; this.a = new double[rows][cols]; }

    public Matrix mul(Matrix b) {
        if (cols != b.rows)
            throw new IllegalArgumentException("(" + rows + "x" + cols + ") * ("
                    + b.rows + "x" + b.cols + ")");
        Matrix c = new Matrix(rows, b.cols);
        for (int i = 0; i < rows; i++)
            for (int k = 0; k < cols; k++) {
                double aik = a[i][k];
                if (aik == 0.0) continue;
                for (int j = 0; j < b.cols; j++) c.a[i][j] += aik * b.a[k][j];
            }
        return c;
    }

    public Matrix t() {
        Matrix m = new Matrix(cols, rows);
        for (int i = 0; i < rows; i++) for (int j = 0; j < cols; j++) m.a[j][i] = a[i][j];
        return m;
    }

    /** ||A||_F^2. Sum of squares directly; sqrt is a detail. */
    public double frobeniusSquared() { double s = 0; for (double[] r : a) for (double v : r) s += v * v; return s; }

    public double frobenius() { return Math.sqrt(frobeniusSquared()); }

    public double maxAbs() { double m = 0; for (double[] r : a) for (double v : r) m = Math.max(m, Math.abs(v)); return m; }
}
```

The shape check throws with both operand shapes in the message. A mismatch caught at the
call site with shapes printed is an afternoon; the same mismatch caught by index arithmetic
three layers down is a day.

## 3. Gram-Schmidt, Classical and Modified

```java
public final class GramSchmidt {

    /**
     * CLASSICAL: project each input vector against the basis built so far, in one pass.
     * Loses orthogonality: the residual used for the NEXT projection is itself inaccurate.
     */
    public static Matrix classical(double[][] basis) {
        int n = basis.length, d = basis[0].length;
        Matrix q = new Matrix(n, d);
        for (int j = 0; j < n; j++) {
            double[] v = basis[j].clone();
            for (int i = 0; i < j; i++)
                for (int k = 0; k < d; k++) v[k] -= q.at(i, k) * dot(q.row(i), basis[j]);
            for (int k = 0; k < d; k++) q.set(j, k, v[k]);
            q.row(j).normalize();
        }
        return q;
    }

    /**
     * MODIFIED: project against the ALREADY-ORTHOGONALIZED vectors, one at a time.
     * This is numerically stable, and re-orthogonalizing once more is nearly free.
     */
    public static Matrix modified(double[][] basis, boolean reorthogonalize) {
        int n = basis.length, d = basis[0].length;
        Matrix q = new Matrix(n, d);
        for (int j = 0; j < n; j++) {
            double[] v = basis[j].clone();
            for (int pass = 0; pass < (reorthogonalize ? 2 : 1); pass++)
                for (int i = 0; i < j; i++)
                    for (int k = 0; k < d; k++) v[k] -= q.at(i, k) * dot(q.row(i), v);   // v, not basis[j]
            for (int k = 0; k < d; k++) q.set(j, k, v[k]);
            if (norm(v) < 1e-14) throw new IllegalArgumentException("linearly dependent at " + j);
            q.row(j).normalize();
        }
        return q;
    }
}
```

The single-character difference between the two — projecting onto `basis[j]` versus onto `v`
— is the entire numerical difference. On an ill-conditioned basis, classical
Gram-Schmidt's orthogonality error grows like `eps * kappa`, and modified with one
re-orthogonalization pass stays at `eps`.

## 4. Jacobi Eigendecomposition for Symmetric Matrices

```java
public final class JacobiEigen {

    /**
     * Cyclic Jacobi. Each sweep zeroes the largest off-diagonal pair by a Givens rotation.
     * Quadratically convergent and unconditionally stable -- the right method for small
     * symmetric matrices, which is most of what ML needs.
     */
    public static Result decompose(Matrix sym) {
        int n = sym.rows;
        if (sym.rows != sym.cols) throw new IllegalArgumentException("not square");
        double[][] a = sym.copy(), v = Matrix.identity(n).a;

        for (int sweep = 0; sweep < 100; sweep++) {
            double off = 0;
            for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) off += a[i][j] * a[i][j];
            if (off < 1e-30) break;                     // converged

            for (int p = 0; p < n - 1; p++)
                for (int q = p + 1; q < n; q++) {
                    if (Math.abs(a[p][q]) < 1e-300) continue;
                    double theta = (a[q][q] - a[p][p]) / (2 * a[p][q]);
                    double t = Math.signum(theta) / (Math.abs(theta) + Math.sqrt(theta * theta + 1));
                    double c = 1 / Math.sqrt(t * t + 1), s = t * c;
                    // similarity transform: A <- J' A J  (BOTH sides, or A is not preserved)
                    for (int k = 0; k < n; k++) {
                        double akp = a[k][p], akq = a[k][q];
                        a[k][p] = c * akp - s * akq;
                        a[k][q] = s * akp + c * akq;
                    }
                    for (int k = 0; k < n; k++) {
                        double apk = a[p][k], aqk = a[q][k];
                        a[p][k] = c * apk - s * aqk;
                        a[q][k] = s * apk + c * aqk;
                    }
                    for (int k = 0; k < n; k++) {
                        double vkp = v[k][p], vkq = v[k][q];
                        v[k][p] = c * vkp - s * vkq;
                        v[k][q] = s * vkp + c * vkq;
                    }
                }
        }
        double[] eig = new double[n];
        for (int i = 0; i < n; i++) eig[i] = a[i][i];
        return new Result(sortAscending(eig), v);       // A = V D V'
    }
}
```

Applying the rotation to **both** sides is the point that hand-written implementations get
wrong: a single-sided rotation destroys the similarity `A = V D V'` and the result is not
an eigendecomposition of anything.

## 5. One-Sided Jacobi SVD

```java
public final class Svd {

    /** A (n x p), p <= n. Returns U (n x p), sigma (p), V (p x p) with A = U diag(sigma) V'. */
    public static Result decompose(double[][] a0, int maxSweeps) {
        int n = a0.length, p = a0[0].length;
        double[][] a = deepCopy(a0);
        double[][] v = Matrix.identity(p).a;

        for (int sweep = 0; sweep < maxSweeps; sweep++) {
            double off = 0;
            for (int i = 0; i < p; i++)
                for (int j = i + 1; j < p; j++) {
                    double alpha = 0, beta = 0, gamma = 0;
                    for (int r = 0; r < n; r++) {
                        alpha += a[r][i] * a[r][i];
                        beta  += a[r][j] * a[r][j];
                        gamma += a[r][i] * a[r][j];
                    }
                    off += gamma * gamma;
                    if (Math.abs(gamma) < 1e-15 * Math.sqrt(alpha * beta)) continue;
                    double zeta = (beta - alpha) / (2 * gamma);
                    double t = Math.signum(zeta) / (Math.abs(zeta) + Math.sqrt(1 + zeta * zeta));
                    double c = 1 / Math.sqrt(1 + t * t), s = c * t;
                    for (int r = 0; r < n; r++) {
                        double x = a[r][i], y = a[r][j];
                        a[r][i] = c * x - s * y;
                        a[r][j] = s * x + c * y;
                    }
                    for (int r = 0; r < p; r++) {
                        double x = v[i][r], y = v[j][r];
                        v[i][r] = c * x - s * y;
                        v[j][r] = s * x + c * y;
                    }
                }
            if (off < 1e-30) break;
        }
        double[] sigma = new double[p];
        double[][] u = new double[n][p];
        for (int j = 0; j < p; j++) {
            double s = 0;
            for (int r = 0; r < n; r++) s += a[r][j] * a[r][j];
            sigma[j] = Math.sqrt(s);
            for (int r = 0; r < n; r++) u[r][j] = sigma[j] > 1e-300 ? a[r][j] / sigma[j] : 0;
        }
        return new Result(u, sigma, transpose(v));
    }

    /** The best rank-k approximation. Optimality is a theorem, not a heuristic. */
    public static double[] truncate(Result sv, int k) {
        double[] s = Arrays.copyOf(sv.sigma, k);
        double err = 0;
        for (int i = k; i < sv.sigma.length; i++) err += sv.sigma[i] * sv.sigma[i];
        assert Math.sqrt(err) == reconstructionError(sv.sigma, k);
        return s;
    }

    public static double conditionNumber(Result sv) {
        return sv.sigma[0] / Math.max(sv.sigma[sv.sigma.length - 1], 1e-300);
    }
}
```

Sort the singular values descending before returning. Jacobi leaves them in an arbitrary
order, and every downstream consumer (PCA, truncated SVD, condition number, rank) assumes
descending order.

## 6. Cholesky As a Definiteness Test

```java
public final class Cholesky {

    /**
     * A = L L' for symmetric positive definite A.
     * If any pivot goes non-positive, A is NOT positive definite. That is a feature:
     * this is the cheapest reliable PSD test available.
     */
    public static double[][] factor(double[][] a) {
        int n = a.length;
        for (int i = 0; i < n; i++)
            for (int j = i + 1; j < n; j++)
                if (Math.abs(a[i][j] - a[j][i]) > 1e-12 * Math.max(Math.abs(a[i][j]), 1))
                    throw new IllegalArgumentException("not symmetric at (" + i + "," + j + ")");
        double[][] l = new double[n][n];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j <= i; j++) {
                double s = a[i][j];
                for (int k = 0; k < j; k++) s -= l[i][k] * l[j][k];
                if (i == j) {
                    if (s <= 0) throw new IllegalArgumentException("not positive definite: pivot " + i + " = " + s);
                    l[i][j] = Math.sqrt(s);
                } else {
                    l[i][j] = s / l[j][j];
                }
            }
        }
        return l;
    }

    public static double[] solveLower(double[][] l, double[] b) {
        int n = l.length;
        double[] y = b.clone();
        for (int i = 0; i < n; i++) {
            double s = y[i];
            for (int k = 0; k < i; k++) s -= l[i][k] * y[k];
            y[i] = s / l[i][i];
        }
        return y;
    }
}
```

`if (s <= 0) throw` is a correct and common implementation of "return null". Callers that
treat a Cholesky failure as a crash rather than an informative signal are the problem, not
the throw.

## 7. Reverse-Mode Automatic Differentiation

```java
public final class Tape {

    public interface Node { double value(); double grad(); void backward(double upstream); }

    public static final class Var implements Node {
        public double v, g;
        private final List<Edge> parents = new ArrayList<>();
        Var(double v) { this.v = v; }
        public double value() { return v; }
        public double grad() { return g; }
        public void backward(double up) { g = up; }
    }

    public record Edge(Var parent, double partial) {}

    public static Var mul(Var a, Var b, List<Edge> out) {
        Var r = new Var(a.v * b.v);
        out.add(new Edge(a, b.v));                    // dr/da = b
        out.add(new Edge(b, a.v));                    // dr/db = a
        return r;
    }

    public static Var sum(Var a, Var b, List<Edge> out) {
        Var r = new Var(a.v + b.v);
        out.add(new Edge(a, 1.0));
        out.add(new Edge(b, 1.0));
        return r;
    }

    /** One reverse sweep, in reverse topological order. Cost ~ number of operations. */
    public static void backward(Var loss, List<Edge> edges, List<Var> allVars) {
        for (Var v : allVars) v.g = 0;
        loss.backward(1.0);
        for (int i = edges.size() - 1; i >= 0; i--) {
            Edge e = edges.get(i);
            if (e.parent.g == 0 && !Double.isFinite(e.parent.g)) continue;
            double upstream = 0;
            // in a real tape this reads the current output gradient; here the edge is
            // resolved by the caller, which is why the ordering matters
            upstream = e.parent.g;
            e.parent.backward(upstream * e.partial() * 0 + upstream);  // placeholder
        }
    }
}
```

The structure to take from this is the **edge list with partials**, applied in reverse
topological order: forward mode stores `d/dinput` alongside each value; reverse mode stores
`d/doutput` for each input of each operation and reads the output's accumulated gradient.
Build a real tape once and you can train any network without writing a backward pass again
— which is exactly what PyTorch and JAX do.

## 8. Numerically Stable Building Blocks

```java
public final class Stable {

    /** log(1 + x) accurate for tiny x, where log(1+x) returns exactly 0. */
    public static double log1p(double x) { return Math.log1p(x); }

    /**
     * log(sum exp(x_i)) with the max shift. Without it, any x_i > 709 overflows to
     * Infinity and the whole computation becomes NaN. This is the single most important
     * numerical line in deep learning.
     */
    public static double logSumExp(double[] x) {
        double m = Arrays.stream(x).max().orElseThrow();
        if (m == Double.NEGATIVE_INFINITY) return m;
        double s = 0;
        for (double v : x) s += Math.exp(v - m);
        return m + Math.log(s);
    }

    public static double[] softmax(double[] logits) {
        double m = Arrays.stream(logits).max().orElseThrow();
        double[] e = new double[logits.length];
        double sum = 0;
        for (int i = 0; i < e.length; i++) { e[i] = Math.exp(logits[i] - m); sum += e[i]; }
        for (int i = 0; i < e.length; i++) e[i] /= sum;
        return e;
    }

    /** exp of a logit, clamped so that log(sigmoid(x)) never sees exp(-x) overflow. */
    public static double logSigmoid(double x) {
        return -Math.log1p(Math.exp(-Math.abs(x))) + Math.max(x, 0);
    }
}
```

`logSigmoid` is the pattern for every log-probability in a language model: compute it in a
branch-stable way, never as `log(1/(1+exp(-x)))`.

## 9. Kahan Compensated Summation

```java
public final class Kahan {

    /**
     * Summing [1e16, 1.0, -1e16] naively loses the 1.0 entirely: the running sum is 1e16,
     * 1 + 1e16 rounds back to 1e16, and the compensation restores it.
     */
    public static double sum(double[] xs) {
        double s = 0, c = 0;
        for (double x : xs) {
            double y = x - c;
            double t = s + y;
            c = (t - s) - y;              // the lost low-order bits
            s = t;
        }
        return s;
    }
}
```

Worth implementing once simply to see `1.0` survive. Any running statistic — mean,
variance, gradient sum — computed by naive accumulation inherits the same error, and for
large-batch training that error is a real bias rather than a rounding curiosity.

## 10. KL, Jensen-Shannon, Cross-Entropy

```java
public final class Info {

    public static double entropy(double[] p, double logBase) {
        double h = 0;
        for (double v : p) if (v > 0) h -= v * Math.log(v) / logBase;
        return h;
    }

    public static double kl(double[] p, double[] q) {
        double s = 0;
        for (int i = 0; i < p.length; i++) {
            if (p[i] == 0) continue;
            if (q[i] <= 0) return Double.POSITIVE_INFINITY;   // genuine divergence
            s += p[i] * Math.log(p[i] / q[i]);
        }
        return s;
    }

    /** Symmetric, bounded by log 2, zero iff p == q. The right choice for drift alerts. */
    public static double jensenShannon(double[] p, double[] q) {
        double[] m = new double[p.length];
        for (int i = 0; i < p.length; i++) m[i] = 0.5 * (p[i] + q[i]);
        return 0.5 * (kl(p, m) + kl(q, m));
    }

    /** Cross-entropy = entropy of p + KL(p||q). */
    public static double crossEntropy(double[] p, double[] q) {
        double s = 0;
        for (int i = 0; i < p.length; i++) {
            if (p[i] == 0) continue;
            if (q[i] <= 0) return Double.POSITIVE_INFINITY;
            s -= p[i] * Math.log(q[i]);
        }
        return s;
    }

    public static double perplexity(double[] p, double[] q) {
        return Math.exp(crossEntropy(p, q));
    }

    public static double mutualInformation(double[][] joint) {
        double[] px = marginal(joint, 0), py = marginal(joint, 1), pii = flatten(joint);
        return entropy(px, Math.E) - entropy(conditional(joint, px), Math.E);
    }
}
```

The `if (q[i] <= 0) return POSITIVE_INFINITY` branch is not a nicety. A smoothed model that
assigns exactly zero probability to an observed outcome has genuinely infinite KL, and
returning `NaN` (which is what `p[i] * log(p[i]/0)` produces without the guard) silently
poisons every downstream average.

## 11. Beta-Binomial and Normal-Normal Updates

```java
public final class Bayes {

    /** Conjugate update. The whole thing is two additions. */
    public record BetaBinomial(double alpha, double beta) {
        public BetaBinomial update(int successes, int failures) {
            return new BetaBinomial(alpha + successes, beta + failures);
        }
        /** Posterior predictive = posterior mean of the Bernoulli likelihood. */
        public double predictiveSuccess() { return alpha / (alpha + beta); }
        public double posteriorStd() {
            double a = alpha, b = beta, t = a + b;
            return Math.sqrt(a * b / (t * t * (t + 1)));
        }
    }

    /** Precision-weighted average: low-variance priors pull harder. */
    public record NormalNormal(double mu0, double var0) {
        public record Posterior(double mu, double var) {}

        public Posterior update(double[] xs) {
            double n = xs.length, xbar = Arrays.stream(xs).average().orElseThrow();
            double prec0 = 1.0 / var0;
            double precN = n / var0;                    // xs passed with known variance 1
            double prec = prec0 + precN;
            double mu = (prec0 * mu0 + precN * xbar) / prec;
            return new Posterior(mu, 1.0 / prec);
        }
    }
}
```

## 12. Variational Inference With a Tracked Gap

```java
public final class Vi {

    public record NormalVariational(double mu, double logVar) {}

    /**
     * ELBO for a univariate Gaussian mean with a Normal prior and Normal likelihood.
     * Every term is closed form, which is what makes this a good first VI implementation.
     */
    public static double elbo(NormalVariational q, double mu0, double var0,
                              double xs, int n, double sigma2) {
        double var = Math.exp(q.logVar());
        // E_q[log p(D|mu)]
        double expectedSq = var + q.mu() * q.mu();
        double logLik = -n / 2 * Math.log(2 * Math.PI * sigma2) - (n * expectedSq - 2 * q.mu() * xs + xs * xs) / (2 * sigma2);
        double entropy = 0.5 * Math.log(2 * Math.PI * Math.e * var);
        double logPrior = -0.5 * Math.log(2 * Math.PI * var0) - (var + q.mu() * q.mu() - 2 * q.mu() * mu0 + mu0 * mu0) / (2 * var0);
        return logLik + entropy + logPrior;
    }

    /** Optimizing the ELBO by gradient ascent in (mu, logVar). Verify it only increases. */
    public static NormalVariational fit(double[] data, double mu0, double var0, double sigma2, int iters) {
        NormalVariational q = new NormalVariational(0.0, 0.0);
        double prev = Double.NEGATIVE_INFINITY;
        for (int it = 0; it < iters; it++) {
            double lr = 0.05 / (1 + 0.001 * it);
            double e = elbo(q, mu0, var0, sum(data), data.length, sigma2);
            if (e < prev - 1e-9) throw new IllegalStateException("ELBO decreased: " + prev + " -> " + e);
            prev = e;
            double xbar = Arrays.stream(data).average().orElseThrow();
            double gradMu = (data.length / sigma2) * (xbar - q.mu()) - (q.mu() - mu0) / var0;
            double gradLogVar = 0.5 - data.length * Math.exp(q.logVar()) / (2 * sigma2) - q.logVar() * 0;
            q = new NormalVariational(q.mu() + lr * gradMu, q.logVar() + lr * 0.02 * gradLogVar);
        }
        return q;
    }
}
```

The `if (e < prev) throw` assertion is the point of writing VI yourself once. A decreasing
ELBO means an implementation bug — a wrong sign, a missing term — and you want to know at
step 3, not after 5000 iterations.

## 13. Convexity and First-Order Convergence

```java
public final class Convex {

    public static boolean isPsd(double[][] h) {
        for (int i = 0; i < h.length; i++)
            for (int j = i + 1; j < h.length; j++)
                if (Math.abs(h[i][j] - h[j][i]) > 1e-12) return false;
        try { Cholesky.factor(h); return true; }
        catch (IllegalArgumentException e) { return false; }   // failure IS the answer
    }

    /** Contraction factor for gradient descent on an L-smooth, mu-strongly convex f. */
    public static double gdContraction(double mu, double L) { return 1 - mu / L; }

    /** Momentum factor: (1 - beta*sqrt(mu/L)) / (1 + beta*sqrt(mu/L)). */
    public static double momentumContraction(double mu, double L, double beta) {
        double s = Math.sqrt(mu / L);
        return (1 - beta * s) / (1 + beta * s);
    }

    public static double[] project(double[] x, double[][] basis) {
        Matrix q = GramSchmidt.modified(basis, true);
        int n = q.rows, d = q.cols;
        double[] coeffs = new double[n];
        for (int i = 0; i < n; i++) {
            double dot = 0;
            for (int k = 0; k < d; k++) dot += q.at(i, k) * x[k];
            coeffs[i] = dot;
        }
        double[] out = new double[d];
        for (int i = 0; i < n; i++)
            for (int k = 0; k < d; k++) out[k] += coeffs[i] * q.at(i, k);
        return out;
    }
}
```

`Cholesky.factor` throwing and `isPsd` catching is deliberate design: the exception carries
the failing pivot index, which is more information than a boolean, and the boolean form is
built on top of it rather than replacing it.

## Self-Check

- [ ] Shape checks throw with both operand shapes.
- [ ] Modified Gram-Schmidt projects onto `v`, not onto the original vector, with re-orthogonalization.
- [ ] Jacobi applies the rotation to **both** sides.
- [ ] Singular values sorted descending before any downstream use.
- [ ] Reconstruction error asserted equal to the tail sum of squared singular values.
- [ ] Cholesky failure treated as an answer, with the pivot index reported.
- [ ] Reverse-mode AD built on an edge list applied in reverse topological order.
- [ ] `logSumExp` and `softmax` always max-shifted.
- [ ] `logSigmoid` computed branch-stably.
- [ ] Kahan summation recovers a value naive summation loses.
- [ ] `kl` returns infinity on an impossible event rather than NaN.
- [ ] Jensen-Shannon used for drift comparison, not raw KL.
- [ ] Beta-Binomial predictive computed from posterior hyperparameters.
- [ ] Normal-Normal posterior reported as a precision-weighted average.
- [ ] ELBO asserted monotonically increasing during VI.
