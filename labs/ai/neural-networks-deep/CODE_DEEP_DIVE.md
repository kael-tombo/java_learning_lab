# neural-networks-deep — Code Deep Dive

Java 21, no dependencies. One `Mat` core, one generic autograd-free MLP with a hand-written
backward pass, and every module's trick implemented explicitly.

## 1. Project Structure

```
neural-networks-deep/
  src/com/ailab/nn/
    core/{Mat,Rng,GradCheck}.java
    activations/{Activations,Derivatives}.java
    init/{Init}.java
    optim/{Sgd,Momentum,Nesterov,Adagrad,Rmsprop,Adam,AdamW,Schedules}.java
    losses/{Losses}.java
    layers/{Dense,Relu,Softmax,Flatten,Residual}.java
    norm/{BatchNorm,LayerNorm,RmsNorm,GroupNorm}.java
    models/{Perceptron,Mlp,ResnetTiny}.java
    compress/{Prune,Quantize,Distill}.java
    Main.java
```

## 2. Matrix Core With a Cache-Friendly Layout

```java
public final class Mat {

    public static double[][] matmul(double[][] a, double[][] b) {
        int n = a.length, m = b[0].length, k = b.length;
        double[][] c = new double[n][m];
        for (int i = 0; i < n; i++)
            for (int p = 0; p < k; p++) {
                double aip = a[i][p];
                if (aip == 0.0) continue;
                double[] brow = b[p], crow = c[i];
                for (int j = 0; j < m; j++) crow[j] += aip * brow[j];
            }
        return c;
    }

    /** Row-major flat array beats double[][] for cache behaviour and for BLAS interop. */
    public static double[] flatMatmul(double[] a, double[] b, int n, int k, int m) {
        double[] c = new double[n * m];
        for (int i = 0; i < n; i++) {
            int rowC = i * m, rowA = i * k;
            for (int p = 0; p < k; p++) {
                double aip = a[rowA + p];
                if (aip == 0.0) continue;
                int rowB = p * m;
                for (int j = 0; j < m; j++) c[rowC + j] += aip * b[rowB + j];
            }
        }
        return c;
    }

    public static double[][] transpose(double[][] a) {
        double[][] t = new double[a[0].length][a.length];
        for (int i = 0; i < a.length; i++)
            for (int j = 0; j < a[0].length; j++) t[j][i] = a[i][j];
        return t;
    }
}
```

The `double[]` flat variant is what to use for anything repeated in a training loop. Java
arrays are objects, so `double[][]` costs an extra indirection per row access and prevents
the JIT from keeping a row in registers.

## 3. Activations With Matched Derivatives

```java
public final class Act {

    /** softsign-ish stable GELU using the tanh approximation, matching most frameworks. */
    public static double gelu(double x) {
        return 0.5 * x * (1 + Math.tanh(Math.sqrt(2 / Math.PI) * (x + 0.044715 * x * x * x)));
    }

    public static double geluExact(double x) {
        return x * 0.5 * (1 + Math.erf(x / Math.SQRT2));
    }

    public static double swish(double x, double beta) {
        double s = 1.0 / (1.0 + Math.exp(-beta * x));
        return x * s;
    }

    public static double elu(double x, double alpha) {
        return x > 0 ? x : alpha * (Math.exp(x) - 1);
    }
}

public final class DAct {

    public static double dGeluTanh(double x) {
        double k = Math.sqrt(2 / Math.PI), c = 0.044715;
        double u = k * (x + c * x * x * x);
        double t = Math.tanh(u);
        return 0.5 * (1 + t) + 0.5 * x * (1 - t * t) * k * (1 + 3 * c * x * x);
    }

    public static double dSwish(double x, double beta) {
        double s = 1.0 / (1.0 + Math.exp(-beta * x));
        return s + beta * x * s * (1 - s);      // NOT just sigmoid(x): the beta*x term matters
    }

    public static double dElu(double x, double alpha) {
        return x > 0 ? 1.0 : alpha * Math.exp(x);
    }
}
```

The classic mistake is forgetting the second term of the Swish derivative. With
`beta = 1` the error is small enough to look fine while subtly slowing learning — which is
precisely the kind of bug that survives to production.

## 4. Initializers

```java
public final class Init {

    /** Xavier: Var = 2/(fan_in + fan_out). Preserves forward AND backward variance. */
    public static double[] xavier(int fanIn, int fanOut, Rng rng) {
        double std = Math.sqrt(2.0 / (fanIn + fanOut));
        return normal(fanIn * fanOut, std, rng);
    }

    /** He: Var = 2/fan_in. ReLU halves forward variance, so double the gain. */
    public static double[] he(int fanIn, int fanOut, Rng rng) {
        double std = Math.sqrt(2.0 / fanIn);
        return normal(fanIn * fanOut, std, rng);
    }

    public static double[] lecun(int fanIn, int fanOut, Rng rng) {
        return normal(fanIn * fanOut, Math.sqrt(1.0 / fanIn), rng);
    }

    public static double[] orthogonal(int rows, int cols, Rng rng) {
        double[] a = normal(rows * cols, 1.0, rng);
        double[][] q = gramSchmidt(Mat.unflatten(a, rows, cols));
        double[] out = new double[rows * cols];
        for (int i = 0; i < rows; i++)
            for (int j = 0; j < cols; j++) out[i * cols + j] = q[i][j % q.length];
        return out;
    }

    /** The bug this whole section exists to prevent. */
    public static double[] zeros(int n) { return new double[n]; }
}
```

`zeros` exists in the file on purpose so that calling it is a visible, greppable choice
rather than `new double[n]` scattered through a model constructor.

## 5. MLP Forward and Backward With Explicit Caching

```java
public final class Mlp {

    public static final class Cache {
        final double[][] a;        // activations per layer, a[0] is the input
        final double[][] z;        // pre-activation per layer
        Cache(double[][] a, double[][] z) { this.a = a; this.z = z; }
    }

    private final int[] sizes;
    private final double[][] W, b;
    private final String act;

    public Mlp(int[] sizes, String act, Rng rng) {
        this.sizes = sizes.clone();
        this.act = act;
        this.W = new double[sizes.length - 1][];
        this.b = new double[sizes.length - 1][];
        for (int l = 0; l < W.length; l++) {
            W[l] = "relu".equals(act) ? Init.he(sizes[l], sizes[l + 1], rng)
                                      : Init.xavier(sizes[l], sizes[l + 1], rng);
            b[l] = new double[sizes[l + 1]];      // biases ZERO, always
        }
    }

    public Cache forward(double[] x) {
        int L = W.length;
        double[][] a = new double[L + 1][], z = new double[L][];
        a[0] = x.clone();
        for (int l = 0; l < L; l++) {
            z[l] = new double[sizes[l + 1]];
            for (int j = 0; j < sizes[l + 1]; j++) {
                double s = b[l][j];
                for (int k = 0; k < sizes[l]; k++) s += W[l][j * sizes[l] + k] * a[l][k];
                z[l][j] = s;
            }
            boolean last = l == L - 1;
            a[l + 1] = last ? z[l].clone() : applyAct(z[l]);
        }
        return new Cache(a, z);
    }

    /** Backward. dOut is dL/d(a_L); returns parameter gradients in the same flat layout. */
    public double[][] backward(Cache c, double[] dOut) {
        int L = W.length;
        double[][] gW = new double[L][], gb = new double[L][];
        double delta = dOut;                       // dL/d a_L ; identity for the linear output

        for (int l = L - 1; l >= 0; l--) {
            gW[l] = new double[sizes[l + 1] * sizes[l]];
            gb[l] = new double[sizes[l + 1]];
            for (int j = 0; j < sizes[l + 1]; j++) {
                double d = delta[j], ai = c.a[l][j < sizes[l] ? j : sizes[l] - 1];
                gb[l][j] = d;
                int off = j * sizes[l];
                for (int k = 0; k < sizes[l]; k++) gW[l][off + k] = d * c.a[l][k];
            }
            if (l > 0) {
                double[] dPrev = new double[sizes[l]];
                for (int j = 0; j < sizes[l + 1]; j++) {
                    double d = delta[j], off = j * sizes[l];
                    for (int k = 0; k < sizes[l]; k++) dPrev[k] += d * W[l][off + k];
                }
                for (int k = 0; k < sizes[l]; k++)
                    dPrev[k] *= "relu".equals(act) ? (c.z[l - 1][k] > 0 ? 1 : 0)
                                                   : Act.dTanh(c.z[l - 1][k]);
                delta = dPrev;
            }
        }
        return new double[][][] { gW, gb };
    }
}
```

Two things to notice. The last layer is linear (activation applied only to hidden layers)
so that softmax cross-entropy can be used without an extra transform. And the ReLU mask
uses `> 0` — using `>= 0` at exactly zero lets gradient through a unit that should be dead.

## 6. Numerical Gradient Check

```java
public final class GradCheck {

    /** Central difference: error O(eps^2) rather than O(eps). Worth the extra forward pass. */
    public static double maxRelError(Mlp net, double[] x, int[] y, double eps) {
        Cache c = net.forward(x);
        int L = net.layers();
        double worst = 0;
        for (int l = 0; l < L; l++)
            for (int k = 0; k < net.W(l).length; k++) {
                double orig = net.W(l)[k];
                net.W(l)[k] = orig + eps; double lp = loss(net.forward(x).z[L - 1], y);
                net.W(l)[k] = orig - eps; double lm = loss(net.forward(x).z[L - 1], y);
                net.W(l)[k] = orig;
                double analytic = net.backward(c, dLossOverOutput(c.z[L - 1], y))[0][l][k];
                double numeric = (lp - lm) / (2 * eps);
                worst = Math.max(worst, Math.abs(analytic - numeric)
                        / (Math.abs(analytic) + Math.abs(numeric) + 1e-12));
            }
        return worst;
    }
}
```

Run this on **every** model you write, before you write the training loop. Every backprop
bug ever found could have been caught in five minutes by this check; the ones that were not
cost days.

## 7. Softmax Cross-Entropy Fused

```java
public final class Losses {

    /** FUSED: never form p then log(p). This is numerically the only safe formulation. */
    public static double crossEntropyFromLogits(double[] logits, int label) {
        double max = Arrays.stream(logits).max().orElseThrow();
        double sum = 0;
        for (double z : logits) sum += Math.exp(z - max);       // log-sum-exp shift
        double lse = max + Math.log(sum);
        return lse - logits[label];                              // >= 0 always
    }

    public static double[] crossEntropyGrad(double[] logits, int label) {
        double[] p = softmax(logits);
        p[label] -= 1.0;                                          // dL/dz = p - y
        return p;
    }

    public static double[] softmax(double[] logits) {
        double max = Arrays.stream(logits).max().orElseThrow();
        double sum = 0;
        double[] e = new double[logits.length];
        for (int i = 0; i < e.length; i++) { e[i] = Math.exp(logits[i] - max); sum += e[i]; }
        for (int i = 0; i < e.length; i++) e[i] /= sum;
        return e;
    }

    public static double huber(double err, double delta) {
        double a = Math.abs(err);
        return a <= delta ? 0.5 * err * err : delta * (a - 0.5 * delta);
    }

    public static double focal(double pT, double label, double gamma, double alpha) {
        double at = label == 1 ? pT : 1 - pT;
        double alphaT = label == 1 ? alpha : 1 - alpha;
        return -alphaT * Math.pow(1 - at, gamma) * Math.log(Math.max(at, 1e-15));
    }
}
```

`logsumexp(z) - z_label` is the whole trick. It also lets you assert the loss is
non-negative, which catches sign errors that would otherwise train "successfully" in the
wrong direction.

## 8. Optimizer Family With One Interface

```java
public interface Optimizer {
    void step(int layer, double[] w, double[] grad, int t);
    default double lr(int t) { return 1e-3; }
}

public record Adam(double eta, double b1, double b2, double eps, double wd,
                   Map<String, double[]> m, Map<String, double[]> v) implements Optimizer {

    @Override public void step(int layer, double[] w, double[] grad, int t) {
        String key = "l" + layer;
        double[] mk = m.computeIfAbsent(key, k -> new double[w.length]);
        double[] vk = v.computeIfAbsent(key, k -> new double[w.length]);
        double bc1 = 1 - Math.pow(b1, t), bc2 = 1 - Math.pow(b2, t);
        for (int i = 0; i < w.length; i++) {
            mk[i] = b1 * mk[i] + (1 - b1) * grad[i];
            vk[i] = b2 * vk[i] + (1 - b2) * grad[i] * grad[i];
            double mh = mk[i] / bc1, vh = vk[i] / bc2;
            w[i] -= lr(t) * (mh / (Math.sqrt(vh) + eps) + wd * w[i]);  // AdamW: decay OUTSIDE
        }
    }
}
```

`wd * w[i]` sits **outside** the `sqrt(vh)` denominator. Move it inside and you no longer
have weight decay — you have a data-dependent regularizer, and the tuned `wd` will not
transfer between layers or learning rates.

## 9. Learning-Rate Schedules

```java
public final class Schedules {

    /** Linear warmup then cosine decay. Warmup exists because early transformer gradients
     *  are enormous and unscaled; decaying alone does not fix that. */
    public static double warmupCosine(double baseLr, int warmupSteps, int totalSteps, int step) {
        if (step < warmupSteps) return baseLr * (step + 1) / warmupSteps;
        double progress = (step - warmupSteps) / (double) Math.max(1, totalSteps - warmupSteps);
        return baseLr * 0.5 * (1 + Math.cos(Math.PI * Math.min(progress, 1.0)));
    }

    public static double stepDecay(double lr, double gamma, int step, int dropEvery) {
        return lr * Math.pow(gamma, step / dropEvery);
    }

    /** Re-evaluate only on EPOCH boundaries, not per step. */
    public static double reduceOnPlateau(double lr, double prevLoss, double curLoss, double factor) {
        return curLoss > prevLoss ? lr * factor : lr;
    }
}
```

Per-step `reduceOnPlateau` decays continuously toward zero on any noisy bump, which reads
like careful tuning and is actually just decay. Batch or epoch granularity is what the
intent requires.

## 10. Batch Normalization, Both Modes

```java
public final class BatchNorm {

    private final double eps, momentum, gamma, beta;
    private double runMean, runVar = 1;
    private boolean training = true;

    public double[] forward(double[] x, double[][] batch) {
        int n = batch.length;
        double mu = 0;
        for (double[] row : batch) mu += row[0];
        mu /= n;
        double var = 0;
        for (double[] row : batch) var += (row[0] - mu) * (row[0] - mu);
        var /= n;                                   // BIASED estimate, divided by n

        double std = Math.sqrt(var + eps);
        runMean = training ? (1 - momentum) * runMean + momentum * mu : runMean;
        runVar  = training ? (1 - momentum) * runVar  + momentum * var : runVar;

        // eval uses RUNNING stats; training uses BATCH stats. Mixing them up is the bug.
        double useMean = training ? mu : runMean;
        double useStd  = training ? std : Math.sqrt(runVar + eps);
        return new double[] { (x[0] - useMean) / useStd * gamma + beta, useMean, useStd };
    }

    /**
     * The backward pass, including the two terms that depend on how mu and sigma^2
     * themselves depend on x. Omitting them still trains, just incorrectly.
     */
    public static double[] backward(double[] upstream, double x, double mu, double std, double n) {
        double xHat = (x - mu) / std;
        double dXhat = upstream;                                 // gamma folded into upstream
        double mean1 = dXhat / n;
        double mean2 = dXhat * xHat / n;
        return new double[] { (dXhat - mean1 - xHat * mean2) / std };
    }
}
```

Track `training` explicitly and default it to `true`. In production the failure is silent:
outputs are close to correct but wrong, metrics dip slightly, and nobody can say why.

## 11. LayerNorm and RMSNorm

```java
public final class LayerNorm {

    /** Normalizes WITHIN a sample: independent of the other rows in the batch. */
    public static double[] forward(double[] x, double gamma, double beta, double eps) {
        int d = x.length;
        double mu = 0;
        for (double v : x) mu += v;
        mu /= d;
        double var = 0;
        for (double v : x) var += (v - mu) * (v - mu);
        var /= d;
        double inv = 1.0 / Math.sqrt(var + eps);
        double[] out = new double[d];
        for (int i = 0; i < d; i++) out[i] = (x[i] - mu) * inv * gamma + beta;
        return out;
    }
}

public final class RmsNorm {

    /** One pass, no mean. Empirically equivalent quality and measurably cheaper,
     *  which is why large LLM stacks standardise on it. */
    public static double[] forward(double[] x, double gamma, double eps) {
        double ss = 0;
        for (double v : x) ss += v * v;
        double inv = 1.0 / Math.sqrt(ss / x.length + eps);
        double[] out = new double[x.length];
        for (int i = 0; i < x.length; i++) out[i] = x[i] * inv * gamma;
        return out;
    }
}
```

## 12. Residual Block With Shape Guards

```java
public final class Residual {

    /**
     * F(x) must be shape-compatible with x. A mismatched residual is silently skipped by
     * some frameworks and silently summed by others; assert it.
     */
    public static double[] forward(double[] x, java.util.function.DoubleUnaryOperator f) {
        double[] fx = f.applyAsDouble(x);
        if (fx.length != x.length)
            throw new IllegalArgumentException(
                    "residual shape mismatch: x=" + x.length + " F(x)=" + fx.length);
        double[] out = new double[x.length];
        for (int i = 0; i < x.length; i++) out[i] = x[i] + fx[i];
        return out;
    }

    public static double[] identityJacobian(int n) {
        double[] j = new double[n * n];
        for (int i = 0; i < n; i++) j[i * n + i] = 1.0;      // I + J_F with J_F = 0
        return j;
    }
}
```

## 13. Magnitude Pruning and Per-Channel INT8

```java
public final class Compress {

    public static double[] pruneGlobal(double[] w, double sparsity, boolean[] mask) {
        double[] abs = Arrays.stream(w).map(Math::abs).sorted().toArray();
        int cutoffIndex = (int) (sparsity * w.length);
        double cutoff = abs[Math.min(cutoffIndex, abs.length - 1)];
        for (int i = 0; i < w.length; i++) {
            mask[i] = Math.abs(w[i]) <= cutoff;
            if (mask[i]) w[i] = 0.0;
        }
        return w;
    }

    /**
     * Per-CHANNEL scale. One outlier channel inflates a per-tensor scale and degrades
     * every other channel; per-channel removes that failure mode entirely.
     */
    public static byte[] quantizePerChannel(double[][] w) {
        byte[] out = new byte[w.length * w[0].length];
        double[] scales = new double[w.length];
        for (int c = 0; c < w.length; c++) {
            double max = 0;
            for (double v : w[c]) max = Math.max(max, Math.abs(v));
            double s = max / 127.0;
            scales[c] = s == 0 ? 1e-8 : s;
            for (int i = 0; i < w[c].length; i++)
                out[c * w[0].length + i] = (byte) Math.round(Math.clamp(w[c][i] / scales[c], -127, 127));
        }
        return out;
    }

    /** Distillation: teacher SOFT probabilities carry the transferable signal. */
    public static double distillationLoss(double[] teacherLogits, double[] studentLogits,
                                          double temperature) {
        double[] pt = softmax(Arrays.stream(teacherLogits).map(z -> z / temperature).toArray());
        double[] ps = softmax(Arrays.stream(studentLogits).map(z -> z / temperature).toArray());
        double kl = 0;
        for (int i = 0; i < pt.length; i++) {
            if (pt[i] > 1e-12) kl += pt[i] * Math.log(pt[i] / Math.max(ps[i], 1e-12));
        }
        return kl * temperature * temperature;   // T^2: keeps gradient magnitude T-independent
    }
}
```

## Self-Check

- [ ] Flat `double[]` layout used in training loops.
- [ ] GELU, Swish, and ELU derivatives include every term.
- [ ] He init for ReLU nets, Xavier otherwise; biases zero; zero init is greppable.
- [ ] Output layer linear so fused softmax cross-entropy applies.
- [ ] ReLU mask uses `> 0`, not `>= 0`.
- [ ] Central-difference gradient check passes at relative error below 1e-6 before training.
- [ ] Cross-entropy computed as `logsumexp(z) - z_label`, never `log(softmax)`.
- [ ] Adam bias correction applied; `eps` present; AdamW decay outside the denominator.
- [ ] Schedule boundaries checked on the right granularity.
- [ ] BatchNorm `training` flag defaults to true and running stats are used at eval.
- [ ] BatchNorm backward includes the two covariance-dependent terms.
- [ ] LayerNorm normalizes within a sample; RMSNorm omits the mean pass.
- [ ] Residual block asserts shape compatibility.
- [ ] INT8 scales computed per channel.
- [ ] Distillation loss multiplies KL by `T^2`.
