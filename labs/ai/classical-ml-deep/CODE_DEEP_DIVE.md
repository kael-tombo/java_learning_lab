# classical-ml-deep — Code Deep Dive

Java 21, no dependencies. Everything is `double[][]` and hand-written loops so the maths
is visible.

## 1. Matrix Core

```java
public final class Mat {

    public static double[][] matmul(double[][] a, double[][] b) {
        int n = a.length, m = b[0].length, k = b.length;
        require(a[0].length == k, "shape mismatch");
        double[][] c = new double[n][m];
        // i-k-j loop order: the k-iteration touches both a and c contiguously,
        // which is what makes this cache-friendly. i-j-k strides a row repeatedly.
        for (int i = 0; i < n; i++)
            for (int k2 = 0; k2 < k; k2++) {
                double aik = a[i][k2];
                if (aik == 0.0) continue;                 // skip structural zeros
                for (int j = 0; j < m; j++) c[i][j] += aik * b[k2][j];
            }
        return c;
    }

    public static double[] matvec(double[][] a, double[] v) {
        double[] out = new double[a.length];
        for (int i = 0; i < a.length; i++) {
            double s = 0;
            for (int j = 0; j < v.length; j++) s += a[i][j] * v[j];
            out[i] = s;
        }
        return out;
    }

    public static double[][] transpose(double[][] a) {
        double[][] t = new double[a[0].length][a.length];
        for (int i = 0; i < a.length; i++)
            for (int j = 0; j < a[0].length; j++) t[j][i] = a[i][j];
        return t;
    }

    /** Householder QR. Preferred over the normal equations: no X'X, no squaring cond. */
    public static double[][] qrSolve(double[][] a, double[] b) {
        int n = a.length, m = a[0].length;
        double[][] r = deepCopy(a);
        double[] y = b.clone();
        for (int k = 0; k < Math.min(m, n - 1); k++) {
            double norm = 0;
            for (int i = k; i < n; i++) norm += r[i][k] * r[i][k];
            norm = Math.sqrt(norm);
            if (norm == 0.0) continue;
            double alpha = r[k][k] > 0 ? -norm : norm;    // sign to avoid cancellation
            double[] v = new double[n];
            for (int i = k; i < n; i++) v[i] = r[i][k];
            v[k] -= alpha;
            double vtv = 0;
            for (int i = k; i < n; i++) vtv += v[i] * v[i];
            if (vtv == 0.0) continue;

            for (int j = k; j < m; j++) {
                double dot = 0;
                for (int i = k; i < n; i++) dot += v[i] * r[i][j];
                double f = 2 * dot / vtv;
                for (int i = k; i < n; i++) r[i][j] -= f * v[i];
            }
            double dot = 0;
            for (int i = k; i < n; i++) dot += v[i] * y[i];
            double f = 2 * dot / vtv;
            for (int i = k; i < n; i++) y[i] -= f * v[i];
        }
        // back substitution on the upper triangle
        double[] w = new double[m];
        for (int i = m - 1; i >= 0; i--) {
            double s = y[i];
            for (int j = i + 1; j < m; j++) s -= r[i][j] * w[j];
            w[i] = Math.abs(r[i][i]) < 1e-12 ? 0.0 : s / r[i][i];
        }
        return w;
    }
}
```

The `alpha` sign choice in Householder (`-sign(r[k][k]) * norm`) is the cancellation-avoidance
trick: it makes `v[k] - alpha` an addition of like-signed magnitudes instead of a
subtraction of near-equals.

## 2. Linear Regression With Ridge and Honest Metrics

```java
public final class LinearRegression {

    private final double lambda;
    private double[] w = new double[0];
    private double b;
    private double r2Train, r2AdjTrain;

    public record Fit(double[] w, double b, double r2, double adjR2, int n, int p) {}

    public Fit fit(double[][] X, double[] y) {
        int n = X.length, p = X[0].length;
        double[][] Xb = addInterceptColumn(X);              // [1 | X]
        int d = p + 1;

        // (X'X + lambda*I) w = X'y   with lambda NOT applied to the intercept
        double[][] A = Mat.matmul(Mat.transpose(Xb), Xb);
        double[] rhs = Mat.matvec(Mat.transpose(Xb), y);
        for (int i = 1; i < d; i++) A[i][i] += lambda;      // index 0 is the intercept

        double[] wFull = Mat.qrSolve(A, rhs);
        this.w = Arrays.copyOfRange(wFull, 1, d);
        this.b = wFull[0];

        double[] pred = predict(X);
        double sse = 0, sst = 0, ybar = mean(y);
        for (int i = 0; i < n; i++) {
            sse += sq(y[i] - pred[i]);
            sst += sq(y[i] - ybar);
        }
        double r2 = 1 - sse / sst;
        // adjusted R^2 penalises parameters: this is the number that can DECREASE
        // when you add a junk column, which is exactly the point
        double adj = 1 - (1 - r2) * (n - 1) / (n - d);
        return new Fit(w, b, r2, adj, n, p);
    }
}
```

Two details worth stating: the intercept is excluded from the penalty (penalizing it
would bias predictions toward zero), and adjusted R^2 uses `n - d` in the denominator
because `d` parameters were estimated, not `p`.

## 3. Logistic Regression: Numerically Stable Log-Loss and IRLS

```java
public final class LogisticRegression {

    /** log(1 + e^-x) computed without overflow. Math.log1p does the hard part. */
    private static double softplusNeg(double z) {          // log(1 + exp(-z))
        return z > 0 ? Math.log1p(Math.exp(-z)) : -z + Math.log1p(Math.exp(z));
    }

    public double[] probabilities(double[] z) {
        double[] p = new double[z.length];
        for (int i = 0; i < z.length; i++) p[i] = 1.0 / (1.0 + Math.exp(-z[i]));
        return p;
    }

    public double logLoss(double[] p, int[] y) {
        double s = 0;
        for (int i = 0; i < p.length; i++) {
            // clamp: log(0) is -inf and will poison the whole objective
            double pi = Math.clamp(p[i], 1e-15, 1 - 1e-15);
            s += y[i] == 1 ? -Math.log(pi) : -Math.log1p(-pi);
        }
        return s / p.length;
    }

    /** Newton-Raphson / IRLS: w <- (X'WX)^-1 X'W(z - eta) with p = sigmoid(z). */
    public double[] irls(double[][] X, int[] y, int iters, double tol) {
        int n = X.length, p = X[0].length;
        double[] w = new double[p];
        for (int it = 0; it < iters; it++) {
            double[] z = new double[n], pr = new double[n], wt = new double[n];
            for (int i = 0; i < n; i++) {
                z[i] = dot(X[i], w);
                pr[i] = 1.0 / (1.0 + Math.exp(-z[i]));
                wt[i] = Math.max(pr[i] * (1 - pr[i]), 1e-9);   // sigmoid Hessian; clamp at 0
            }
            double[][] Xt = Mat.transpose(X);
            double[][] H = Mat.matmul(Xt, scaleRows(X, wt));
            for (int j = 0; j < p; j++) H[j][j] += 1e-8;       // ridge-ish jitter for invertibility

            double[] grad = new double[p];
            for (int j = 0; j < p; j++) {
                double s = 0;
                for (int i = 0; i < n; i++) s += X[i][j] * wt[i] * (y[i] - pr[i]);
                grad[j] = s;
            }
            double[] delta = Mat.qrSolve(H, grad);
            for (int j = 0; j < p; j++) w[j] += delta[j];
            if (norm(delta) < tol) break;
        }
        return w;
    }
}
```

`w_i = p_i(1 - p_i)` is the sigmoid's second derivative and vanishes as `p -> 0` or
`1`, which is exactly why the Hessian becomes singular under separation. The `1e-9`
clamp and the jitter are not decoration; they are the difference between "converges" and
"throws".

## 4. Softmax With Log-Sum-Exp

```java
public static double[][] softmax(double[][] logits) {
    int n = logits.length, k = logits[0].length;
    double[][] p = new double[n][k];
    for (int i = 0; i < n; i++) {
        double max = Arrays.stream(logits[i]).max().orElseThrow();
        double sum = 0;
        double[] shifted = new double[k];
        for (int j = 0; j < k; j++) {
            shifted[j] = Math.exp(logits[i][j] - max);   // subtract max: exp cannot overflow
            sum += shifted[j];
        }
        for (int j = 0; j < k; j++) p[i][j] = shifted[j] / sum;
    }
    return p;
}
```

Subtracting the row max leaves the result unchanged mathematically and is the standard
guard. `sum_j p_ij == 1` is the invariant to assert in a test — it catches the log-sum-exp
mistake immediately, whereas a subtly wrong model just scores a bit lower.

## 5. Decision Tree: Split Criteria and Surrogate Splits

```java
public final class Tree {

    public enum Criterion { GINI, ENTROPY, GAIN_RATIO, VARIANCE }

    public static double gini(int[] counts, int total) {
        double g = 1.0, s = 0;
        for (int c : counts) { double p = (double) c / total; g -= p * p; s += 1.0; }
        return g;
    }

    public static double impurity(int[] counts, int total, Criterion c) {
        double left = 0, right = 0;
        for (int k : counts) { left += (double) k * k; right += (double) (total - k) * (total - k); }
        double v = switch (c) {
            case GINI      -> 1.0;
            case ENTROPY, GAIN_RATIO -> -1.0;                 // scaled; only ratios matter
            case VARIANCE  -> total;
        };
        // gini = 1 - left/total^2 - right/total^2 ;  variance = (1 - sum sq / total^2) * total
        return 1.0 - left / ((double) total * total) - right / ((double) total * total);
    }

    /** Surrogate: find the feature that best mimics the primary split, for missing values. */
    public static int[] surrogateSplit(double[][] X, int[] y, int primary, double threshold, Criterion crit) {
        int best = -1;
        double bestGain = -1;
        for (int f = 0; f < X[0].length; f++) {
            if (f == primary) continue;
            double gain = splitGain(X, y, f, median(X, f), crit);
            if (gain > bestGain) { bestGain = gain; best = f; }
        }
        return new int[] { best };
    }

    public static double route(double v, double threshold, boolean goLeftWhenBelow) {
        // a MISSING value is NaN, and both comparisons are false -> default branch.
        // That silent default is why surrogate splits exist.
        return Double.isNaN(v) ? Double.NaN : (v < threshold) == goLeftWhenBelow ? 0 : 1;
    }
}
```

Routing `NaN` down a deliberate default branch is the honest behaviour: silently treating
NaN as "less than threshold" puts missing values on the left for every node.

## 6. Random Forest With Bootstrap and OOB

```java
public final class RandomForest {

    private final int nTrees, mtry;
    private final long seed;

    public List<Tree> fit(double[][] X, int[] y, int n) {
        List<Tree> forest = new ArrayList<>(nTrees);
        for (int t = 0; t < nTrees; t++) {
            // A FRESH Random per tree, seeded from the master. Sharing one Random
            // across trees makes the bootstraps correlated and quietly ruins the variance
            // reduction the whole method depends on.
            Random rng = new Random(seed * 31 + t);
            int[] boot = new int[n];
            for (int i = 0; i < n; i++) boot[i] = rng.nextInt(n);
            forest.add(new Tree().grow(X, y, boot, mtry(xWidth), rng));
        }
        return forest;
    }

    /** OOB error: every tree predicts the rows it never saw. No holdout split needed. */
    public double oobError(List<Tree> forest, double[][] X, int[] y) {
        int n = X.length, votes = 0, wrong = 0;
        for (int i = 0; i < n; i++) {
            int sum = 0, count = 0;
            for (Tree t : forest) {
                if (!t.trainedOn(i)) continue;
                sum += t.predict(X[i]); count++;              // ~36.8% of trees
            }
            if (count == 0) continue;
            if (Math.round((double) sum / count) != y[i]) wrong++;
            votes++;
        }
        return votes == 0 ? Double.NaN : (double) wrong / votes;
    }
}
```

Bootstrap rows repeat, so `trainedOn(i)` must be a set membership test, not a flag set
during sampling — the same row appears multiple times in one bootstrap and a boolean
would still answer correctly, but the count is what tells you how many trees can vote.

## 7. Gradient Boosting With Second-Order Leaf Values

```java
public final class GradientBoosting {

    public interface Loss {
        double[] gradient(double[] y, double[] pred);   // dL/dF
        double[] hessian(double[] y, double[] pred);    // d2L/dF2
    }

    /** Squared error: g = y - F, h = 1.  Logistic: g = p - y, h = p(1-p). */
    public static final Loss SQUARED = new Loss() {
        public double[] gradient(double[] y, double[] f) {
            double[] g = new double[y.length];
            for (int i = 0; i < y.length; i++) g[i] = y[i] - f[i];
            return g;
        }
        public double[] hessian(double[] y, double[] f) { return new double[y.length]; } // h = 1
    };

    public double[] fit(double[][] X, double[] y, int rounds, double eta, double lambda, int k) {
        int n = X.length;
        double[] pred = new double[n];
        Arrays.fill(pred, mean(y));                      // F_0, the constant baseline
        for (int m = 0; m < rounds; m++) {
            double[] g = loss.gradient(y, pred);
            double[] h = loss.hessian(y, pred);
            Tree tree = new Tree().fitResiduals(X, g, h, k, lambda);
            for (int i = 0; i < n; i++) pred[i] += eta * tree.predict(X[i]);
            if (m % 10 == 0) logLoss(y, pred);
        }
        return pred;
    }

    /** Optimal leaf value. This is the whole second-order contribution. */
    public static double leafValue(double G, double H, double lambda) {
        if (H + lambda < 1e-12) return 0.0;               // unbounded optimum -> regularize
        return -G / (H + lambda);
    }
}
```

The `H + lambda < 1e-12` guard is not defensive noise. It is the exact case that occurs
when every sample in a leaf is confidently classified: `h -> 0`, `G -> 0`, and the ratio
becomes numerically arbitrary. Without `lambda` you get a leaf predicting 400.

## 8. PCA via SVD (Jacobi One-Sided)

```java
public final class Pca {

    /** One-sided Jacobi: orthogonalize columns of A until converged. A is n x p, p small. */
    public static Svd svd(double[][] a) {
        int n = a.length, p = a[0].length;
        double[][] v = identity(p);
        for (int sweep = 0; sweep < 60; sweep++) {
            double off = 0;
            for (int i = 0; i < p; i++)
                for (int j = i + 1; j < p; j++) {
                    double alpha = 0, beta = 0, gamma = 0;
                    for (int r = 0; r < n; r++) {
                        alpha += sq(a[r][i]); beta += sq(a[r][j]); gamma += a[r][i] * a[r][j];
                    }
                    off += sq(gamma);
                    if (Math.abs(gamma) < 1e-14 * Math.sqrt(alpha * beta) + 1e-300) continue;
                    double zeta = (beta - alpha) / (2 * gamma);
                    double t = Math.signum(zeta) / (Math.abs(zeta) + Math.sqrt(1 + zeta * zeta));
                    double c = 1 / Math.sqrt(1 + t * t), s = c * t;
                    for (int r = 0; r < n; r++) {           // rotate columns
                        double x = a[r][i], y = a[r][j];
                        a[r][i] = c * x - s * y;
                        a[r][j] = s * x + c * y;
                    }
                    for (int r = 0; r < p; r++) {           // accumulate U
                        double x = v[i][r], y = v[j][r];
                        v[i][r] = c * x - s * y;
                        v[j][r] = s * x + c * y;
                    }
                }
            if (off < 1e-24) break;
        }
        double[] sigma = new double[p];
        double[][] u = new double[n][p];
        for (int j = 0; j < p; j++) {
            double norm = 0;
            for (int r = 0; r < n; r++) norm += sq(a[r][j]);
            sigma[j] = Math.sqrt(norm);
            for (int r = 0; r < n; r++) u[r][j] = sigma[j] > 1e-300 ? a[r][j] / sigma[j] : 0;
        }
        return new Svd(u, sigma, transpose(v));
    }

    public static Pca fit(double[][] raw) {
        double[][] x = center(raw);
        Svd s = svd(x);
        double total = 0;
        for (double v : s.sigma) total += sq(v);
        // explained variance ratio: sigma^2 / sum(sigma^2). The ratio, not the value.
        return new Pca(s.u, s.sigma, Arrays.stream(s.sigma).map(v -> sq(v) / total).toArray());
    }

    public double[][] transform(double[][] raw, int k) {
        double[][] x = center(raw);
        double[][] out = new double[x.length][k];
        for (int i = 0; i < x.length; i++)
            for (int j = 0; j < k; j++) out[i][j] = dot(x[i], u[i0(j)]);
        return out;
    }
}
```

`fit` centers a **copy** of the input. `center(raw)` returning a new array is not
optional: centering in place mutates the caller's data, and if that same array is later
used to compute a validation score you have silently destroyed it.

## 9. K-Means With k-means++ Seeding

```java
public final class KMeans {

    public static double[][] initKMeansPlusPlus(double[][] x, int k, Random rng) {
        int n = x.length;
        double[][] c = new double[k][];
        c[0] = x[rng.nextInt(n)].clone();
        double[] d2 = new double[n];
        Arrays.fill(d2, Double.MAX_VALUE);

        for (int j = 1; j < k; j++) {
            double total = 0;
            for (int i = 0; i < n; i++) {
                d2[i] = Math.min(d2[i], sq(dist2(x[i], c[j - 1])));
                total += d2[i];
            }
            // D^2 weighting: sample proportional to distance^2. This is the entire
            // difference between k-means++ and random seeding, and it is why k-means++
            // reliably beats random on the same objective.
            double r = rng.nextDouble() * total, acc = 0;
            int pick = n - 1;
            for (int i = 0; i < n; i++) { acc += d2[i]; if (acc >= r) { pick = i; break; } }
            c[j] = x[pick].clone();
        }
        return c;
    }

    public static Result lloyd(double[][] x, int k, int maxIter, Random rng) {
        double[][] c = initKMeansPlusPlus(x, k, rng);
        double prevJ = Double.MAX_VALUE;
        int[] assign = new int[x.length];
        for (int it = 0; it < maxIter; it++) {
            for (int i = 0; i < x.length; i++) {
                int best = 0; double bestD = Double.MAX_VALUE;
                for (int j = 0; j < k; j++) {
                    double d = dist2(x[i], c[j]);
                    if (d < bestD) { bestD = d; best = j; }
                }
                assign[i] = best;
            }
            double[][] sum = new double[k][x[0].length];
            int[] cnt = new int[k];
            for (int i = 0; i < x.length; i++) {
                cnt[assign[i]]++;
                for (int d = 0; d < x[0].length; d++) sum[assign[i]][d] += x[i][d];
            }
            for (int j = 0; j < k; j++)                      // empty cluster -> reseed
                if (cnt[j] == 0) c[j] = x[rng.nextInt(x.length)].clone();
                else for (int d = 0; d < x[0].length; d++) c[j][d] = sum[j][d] / cnt[j];

            double J = 0;
            for (int i = 0; i < x.length; i++) J += dist2(x[i], c[assign[i]]);
            if (J > prevJ - 1e-12) break;                    // J is monotone; this ends it
            prevJ = J;
        }
        return new Result(c, assign, prevJ);
    }
}
```

Assert `J_new <= J_old` on every iteration. If it ever increases, an assignment or update
step is wrong — that assertion catches more bugs than any amount of eyeballing centroids.

## 10. DBSCAN With the Region-Query Done Properly

```java
public final class Dbscan {

    public enum Kind { CORE, BORDER, NOISE }

    public static Result run(double[][] x, double eps, int minPts) {
        int n = x.length;
        Kind[] kind = new Kind[n];
        Arrays.fill(kind, Kind.NOISE);
        boolean[] visited = new boolean[n];
        List<List<Integer>> clusters = new ArrayList<>();
        double[][] d2 = pairwiseDist2(x);                    // precompute: queries are many

        for (int i = 0; i < n; i++) {
            if (visited[i]) continue;
            visited[i] = true;
            List<Integer> region = regionQuery(i, eps, d2);   // includes i itself
            if (region.size() < minPts) continue;            // noise: stays NOISE

            List<Integer> cluster = new ArrayList<>();
            for (int j : region) {
                kind[j] = Kind.CORE;
                cluster.add(j);
                if (visited[j]) continue;
                visited[j] = true;
                List<Integer> r2 = regionQuery(j, eps, d2);
                if (r2.size() >= minPts) {                   // j is core -> EXPAND
                    for (int k : r2) if (kind[k] == Kind.NOISE) cluster.add(k);
                }
            }
            clusters.add(cluster);
        }
        // promote: any point claimed by a core point is BORDER, not CORE
        for (List<Integer> cl : clusters)
            for (int i : cl) if (kind[i] == Kind.CORE && regionQuery(i, eps, d2).size() < minPts)
                kind[i] = Kind.BORDER;
        return new Result(clusters, kind);
    }
}
```

The expansion order is the algorithm: a visited point is still expanded **iff** it is
itself core. That conditional is what makes clusters grow transitively, and forgetting it
is the classic bug that yields one tiny cluster per core point.

## 11. Isolation Forest and LOF

```java
public final class Anomaly {

    /** Anomaly score = average path length over trees. Short path = isolated = anomalous. */
    public static double c(double n) {
        return 2.0 * harmonic(n - 1) - 2.0 * (n - 1) / n;
    }

    public static double pathLength(int leafSize, int depth) {
        if (leafSize <= 1) return depth;
        return depth + c(leafSize);
    }

    public static double score(double avgPath, int n) {
        return Math.pow(2, -avgPath / c(n));
    }

    /** LOF: low density RELATIVE to k neighbours, which catches what global cutoffs miss. */
    public static double[] lof(double[][] x, int k) {
        int n = x.length;
        double[][] d2 = pairwiseDist2(x);
        double[] lrd = new double[n];
        for (int i = 0; i < n; i++) {
            double[] nn = sortedNeighbourDistances(d2[i], k);
            double sum = 0;
            for (double r : nn) sum += 1.0 / Math.max(Math.sqrt(r), 1e-12);
            lrd[i] = sum / k;                                 // local reachability density
        }
        double[] out = new double[n];
        for (int i = 0; i < n; i++) {
            double ratio = 0; int cnt = 0;
            for (int j = 0; j < n; j++) {
                if (i == j) continue;
                if (d2[i][j] > kthNeighbourDistance(d2[i], k)) continue;
                ratio += lrd[j] / Math.max(lrd[i], 1e-12);
                cnt++;
            }
            out[i] = cnt == 0 ? 0 : ratio / cnt;             // > 1 means sparse
        }
        return out;
    }
}
```

`c(n)` is the average path length of an unsuccessful BST search over `n` points — without
it, trees over large samples look artificially deep and every score compresses toward 0.5.
The `Math.max(r, 1e-12)` guard matters when duplicate points make a neighbour distance zero.

## 12. Evaluation Metrics That Survive Imbalance

```java
public final class Metrics {

    public record Confusion(int tp, int fp, int fn, int tn) {}

    public static Confusion confusion(int[] y, double[] score, double threshold) {
        int tp = 0, fp = 0, fn = 0, tn = 0;
        for (int i = 0; i < y.length; i++) {
            boolean pred = score[i] >= threshold;
            if (y[i] == 1 && pred) tp++;
            else if (y[i] == 0 && pred) fp++;
            else if (y[i] == 1) fn++;
            else tn++;
        }
        return new Confusion(tp, fp, fn, tn);
    }

    public static double prAuc(int[] y, double[] score) {
        Integer[] idx = IntStream.range(0, y.length).boxed()
                .sorted(Comparator.comparingDouble(i -> -score[i])).toArray(Integer[]::new);
        int P = 0, tp = 0, prevTp = 0;
        double area = 0;
        for (int k = 0; k < idx.length; k++) {
            P++;
            if (y[idx[k]] == 1) { tp++; area += (tp - prevTp) / (double) P; prevTp = tp; }
        }
        return area;
    }

    public static double accuracy(Confusion c) {
        int t = c.tp() + c.tn();
        return (double) t / (c.tp() + c.fp() + c.fn() + c.tn());
    }

    /**
     * Choose the threshold that minimises EXPECTED COST, not accuracy.
     * This is the decision layer the model has no opinion about.
     */
    public static double costOptimalThreshold(int[] y, double[] score, double cFN, double cFP) {
        Integer[] idx = IntStream.range(0, y.length).boxed()
                .sorted(Comparator.comparingDouble(i -> -score[i])).toArray(Integer[]::new);
        double best = Double.MAX_VALUE, bestT = Double.MAX_VALUE;
        int tp = 0, fp = 0;
        for (int k = 0; k < idx.length; k++) {
            if (y[idx[k]] == 1) tp++; else fp++;
            double cost = cFN * (P - tp) + cFP * fp;           // FN = positives we missed
            if (cost < best) { best = cost; bestT = score[idx[k]]; }
        }
        return bestT;
    }
}
```

`prAuc` here is the average-precision form of PR-AUC (step-wise interpolation), which is
the variant to report: trapezoidal PR-AUC on raw scores overstates performance because
it interpolates between thresholds that were never achieved.

## Self-Check

- [ ] Matrix multiply uses a cache-friendly loop order and skips structural zeros.
- [ ] Linear solve uses QR, never `X'X` inversion.
- [ ] Ridge penalty excludes the intercept; adjusted R^2 uses `n - d`.
- [ ] Log-loss clamps probabilities and uses `log1p`.
- [ ] IRLS hessian weight `p(1-p)` is clamped and the system is jittered.
- [ ] Softmax subtracts the row max and rows sum to 1.
- [ ] Missing tree values route to a deliberate default, not an accidental one.
- [ ] Each forest tree gets its own `Random` derived from a master seed.
- [ ] Boosting leaf value guards the `H + lambda -> 0` case.
- [ ] `c(n)` correction present in isolation forest scores.
- [ ] DBSCAN expands visited points only when they are core.
- [ ] PCA centers a copy; the caller's array is never mutated.
- [ ] k-means asserts monotone `J` and handles empty clusters.
- [ ] Threshold selection minimizes expected cost, not accuracy.
