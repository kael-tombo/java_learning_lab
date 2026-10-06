# Lab 06: Fine-Tuning with LoRA/QLoRA — Code Deep Dive

## 1. Project Structure

```
lab06/
  src/com/genai/lab06/
    lora/LoraAdapter.java      holds A, B, scaling, target module names
    lora/LoraInit.java         Kaiming-uniform A, zero B
    lora/LoraMerge.java        W_merged = W0 + s*B*A
    lora/AdapterRegistry.java  named adapters, activate/save/load
    lora/AdapterPruner.java    singular-value energy pruning
    lora/DoRA.java             direction + learned magnitude
    quant/SymmetricQuantizer.java
    quant/AsymmetricQuantizer.java
    quant/Nf4.java             codebook, per-block scales, double quant
    quant/Quantizer.java       interface: encode -> codes + scales
    memory/MemoryPlan.java     the memory formula
    optim/AdamWNoDecay.java    decay excluded for selected LoRA params
    data/ChatDataset.java      prompt masking for chat
    train/Trainer.java         loops, grad clip, eval
    Main.java
```

## 2. Adapter Representation

```java
public final class LoraAdapter {

    private final String name;
    private final int rank;
    private final double alpha;
    private final Map<String, double[][]> a;   // [r][dIn]  per target module
    private final Map<String, double[][]> b;   // [dOut][r]
    private final Set<String> targets;

    public double scaling() { return alpha / rank; }

    /** delta_W(x) = x * A^T * B^T * scaling */
    public double[] apply(String module, double[] x) {
        double[][] A = a.get(module), B = b.get(module);
        int r = rank;
        double[] proj = new double[r];                 // x A^T
        for (int i = 0; i < r; i++) {
            double s = 0;
            for (int j = 0; j < x.length; j++) s += x[j] * A[i][j];
            proj[i] = s;
        }
        double[] out = new double[B.length];           // proj B^T
        for (int o = 0; o < B.length; o++) {
            double s = 0;
            for (int i = 0; i < r; i++) s += B[o][i] * proj[i];
            out[o] = s * scaling();
        }
        return out;
    }
}
```

Two-stage (project then expand) keeps the inner loop over `r` — that is the entire
point of the low-rank factorization: `O(r(d_in+d_out))` instead of `O(d*d)`.

## 3. Initialization

```java
public static LoraAdapter create(String name, int rank, double alpha,
                                 Map<String, int[]> shapes, long seed) {
    Random rnd = new Random(seed);
    Map<String, double[][]> a = new LinkedHashMap<>(), b = new LinkedHashMap<>();
    shapes.forEach((mod, dim) -> {
        int[] d = dim;                               // [dIn, dOut]
        int r = Math.min(rank, Math.min(d[0], d[1])); // r cannot exceed min dim
        a.put(mod, kaimingUniform(r, d[0], rnd));    // bound = sqrt(6 / fan_in)
        b.put(mod, new double[d[1]][r]);             // ZERO, not random
    });
    return new LoraAdapter(name, r, alpha, a, b, shapes.keySet());
}

private static double[][] kaimingUniform(int rows, int cols, Random rnd) {
    double bound = Math.sqrt(6.0 / cols);
    double[][] m = new double[rows][cols];
    for (double[] row : m) for (int j = 0; j < cols; j++)
        row[j] = (rnd.nextDouble() * 2 - 1) * bound;
    return m;
}
```

`rank = min(rank, min(dIn, dOut))` is a real constraint — a rank above `min(d)` is
not expressible and silently truncates. Guarding it avoids a confusing
"trained but flat" result.

## 4. Merging

```java
public static double[][] merge(double[][] w0, LoraAdapter ad, String module) {
    int dOut = w0.length, dIn = w0[0].length;
    double[][] A = ad.a(module), B = ad.b(module);
    double s = ad.scaling();
    double[][] out = new double[dOut][dIn];
    for (int o = 0; o < dOut; o++) {
        for (int i = 0; i < dIn; i++) {
            double delta = 0;
            for (int r = 0; r < ad.rank(); r++) delta += B[o][r] * A[r][i];
            out[o][i] = w0[o][i] + s * delta;
        }
    }
    return out;
}
```

Equivalence test (Exercise 4): run `layer(x)` with `W_merged` and compare with
`W0(x) + ad.apply(module, x)`; they must match to 1e-12. That test is the guard
against a transposition bug in the shapes.

## 5. Quantizers

```java
public interface Quantizer {
    Quantized encode(double[] w);
    double[] decode(Quantized q);
    record Quantized(byte[] codes, float[] scales, short[] zeros, int blocksize) {}
}

public final class SymmetricQuantizer implements Quantizer {
    @Override public Quantized encode(double[] w) {
        int bs = 64, nb = (w.length + bs - 1) / bs;
        float[] scales = new float[nb];
        byte[] codes = new byte[w.length];
        int qmin = -8, qmax = 7;                        // 4-bit signed
        for (int b = 0; b < nb; b++) {
            int lo = b * bs, hi = Math.min(w.length, lo + bs);
            double amax = 0;
            for (int i = lo; i < hi; i++) amax = Math.max(amax, Math.abs(w[i]));
            float s = (float) (amax / qmax);            // symmetric around zero
            scales[b] = s;
            for (int i = lo; i < hi; i++)
                codes[i] = (byte) Math.max(qmin, Math.min(qmax, Math.round(w[i] / s)));
        }
        return new Quantized(codes, scales, null, bs);
    }
}
```

`Math.round` returns `long`; the cast to `byte` plus the clamp is what keeps -8..7
in range. Forgetting the clamp is a classic overflow bug that shows up as garbage
weights after loading.

## 6. NF4

```java
public final class Nf4 {
    // Quantiles of the standard normal (Lloyd-Max style 4-bit codebook).
    static final double[] CODEBOOK = {
        -1.0, -0.6961928009986877, -0.5250730514526367, -0.39491748809814453,
        -0.28444138169288635, -0.18477343022823334, -0.09105003625154495,  0.0,
         0.07958029955653134,  0.16093020141124725,  0.24611230194568634,
         0.33791524171857614,  0.44070982933044434,  0.5626170039176941,
         0.7229568362236023,   1.0
    };

    public static Quantized encode(double[] w, int bs) {
        int nb = (w.length + bs - 1) / bs;
        float[] scales = new float[nb];
        byte[] codes = new byte[w.length];
        for (int b = 0; b < nb; b++) {
            int lo = b * bs, hi = Math.min(w.length, lo + bs);
            double amax = 0;
            for (int i = lo; i < hi; i++) amax = Math.max(amax, Math.abs(w[i]));
            scales[b] = (float) (amax / Math.abs(CODEBOOK[0]));   // scale so max maps to -1/1
            for (int i = lo; i < hi; i++) {
                double v = w[i] / scales[b];
                int best = 0; double bd = Double.MAX_VALUE;
                for (int k = 0; k < CODEBOOK.length; k++) {       // 16-way scan
                    double d = Math.abs(v - CODEBOOK[k]);
                    if (d < bd) { bd = d; best = k; }
                }
                codes[i] = (byte) best;
            }
        }
        return new Quantized(codes, scales, null, bs);
    }
}
```

The 16-way linear scan is fine for a lab and instructive; production uses a lookup
table or binary search on the sorted codebook.

## 7. Double Quantization

```java
public static Quantized quantizeScales(Quantized q) {
    float[] s = q.scales();
    double amax = Arrays.stream(s).map(Math::abs).max().orElse(0);
    float second = (float) (amax / 127.0);
    byte[] q2 = new byte[s.length];
    for (int i = 0; i < s.length; i++)
        q2[i] = (byte) Math.max(-127, Math.min(127, Math.round(s[i] / second)));
    float[] half = new float[s.length];
    for (int i = 0; i < s.length; i++) half[i] = (q2[i] * second);   // dequantized scale
    return new Quantized(q.codes(), half, q2, q.blocksize());         // 8-bit scale storage
}
```

Saving 16-bit -> 8-bit on the scale tensor removes `P/64 * 1` bytes/element — about
0.015 bytes/element here. Small, but it is what makes 7B fit comfortably.

## 8. Memory Planner

```java
public record MemoryPlan(long weightBytes, long gradBytes, long optimBytes,
                         long actBytes, long totalBytes, boolean fits) {

    public static MemoryPlan of(long params, int baseBits, long trainable,
                                boolean gradCheckpointing, long actBytesElsewhere) {
        long w = params * baseBits / 8;
        long g = trainable * 2;                 // bf16 grads
        long o = trainable * 4L * 2;            // fp32 Adam m and v
        long a = gradCheckpointing ? actBytesElsewhere / 4 : actBytesElsewhere;
        long t = w + g + o + a;
        return new MemoryPlan(w, g, o, a, t, t <= 24L * 1024 * 1024 * 1024);
    }
}
```

The `/ 4` on activations under checkpointing is an approximation — good enough to
decide feasibility, which is all this class is for. Print the breakdown; engineers
make capacity decisions from the breakdown, not the total.

## 9. AdamW With Decay Exclusion

```java
public final class AdamWNoDecay {
    private final Set<String> noDecay = new HashSet<>(Set.of("lora_B"));

    public void step(Map<String, double[][]> params, Map<String, double[][]> grads,
                     Map<String, double[][]> m, Map<String, double[][]> v,
                     double lr, double b1, double b2, double eps, double wd, int t) {
        double bc1 = 1 - Math.pow(b1, t), bc2 = 1 - Math.pow(b2, t);
        for (var e : params.entrySet()) {
            String key = e.getKey();
            double decay = noDecay.contains(key) ? 0.0 : wd;
            for (int i = 0; i < e.getValue().length; i++) {
                for (int j = 0; j < e.getValue()[i].length; j++) {
                    double p = e.getValue()[i][j], g = grads.get(key)[i][j];
                    m.get(key)[i][j] = b1 * m.get(key)[i][j] + (1 - b1) * g;
                    v.get(key)[i][j] = b2 * v.get(key)[i][j] + (1 - b2) * g * g;
                    double mh = m.get(key)[i][j] / bc1;
                    double vh = v.get(key)[i][j] / bc2;
                    e.getValue()[i][j] = p - lr * (mh / (Math.sqrt(vh) + eps) + decay * p);
                }
            }
        }
    }
}
```

Decoupled decay `p -= lr * wd * p` is the AdamW form (applied outside the adaptive
step). Applying decay to zero-initialized `B` pulls it toward zero and slows the
first real update — the practical reason `noDecay` exists.

## 10. Prompt Masking

```java
public record Example(int[] inputIds, int[] labels) {}   // labels: -100 == ignore

public static Example toChatExample(List<int[]> turns, boolean trainOnUser) {
    int n = turns.stream().mapToInt(t -> t.length).sum();
    int[] ids = new int[n], labels = new int[n];
    Arrays.fill(labels, -100);                          // default: ignore everything
    int p = 0;
    for (int t = 0; t < turns.size(); t++) {
        int len = turns.get(t).length;
        System.arraycopy(turns.get(t), 0, ids, p, len);
        if (t % 2 == 1 || trainOnUser)                  // assistant turns train
            System.arraycopy(turns.get(t), 0, labels, p, len);
        p += len;
    }
    return new Example(ids, labels);
}
```

`labels[i] == -100` is the ignore index (matching PyTorch's `ignore_index`).
Test: mutate a user token -> loss unchanged; mutate an assistant token -> loss
changes. That test catches the most common chat fine-tuning bug.

## 11. Gradient Clipping by Global Norm

```java
public static double clipGlobalNorm(Map<String, double[][]> grads, double maxNorm) {
    double sq = 0;
    for (double[][] g : grads.values())
        for (double[] row : g) for (double v : row) sq += v * v;
    double norm = Math.sqrt(sq);
    double scale = norm > maxNorm ? maxNorm / (norm + 1e-6) : 1.0;
    if (scale < 1.0) for (double[][] g : grads.values())
        for (double[] row : g) for (int j = 0; j < row.length; j++) row[j] *= scale;
    return norm;
}
```

Return the pre-clip norm — the trend matters more than the value. A norm pinned at
the clip threshold means the learning rate is effectively capped.

## 12. Adapter Pruning

```java
public static int rankForEnergy(double[][] update, int dOut, int dIn, double target) {
    double[] sv = singularValues(update);              // power iteration or Jacobi
    double total = 0; for (double s : sv) total += s * s;
    double acc = 0; int r = 0;
    for (double s : sv) { acc += s * s; if (acc / total >= target) { r++; break; } r++; }
    return r;
}
```

Report `retainedRank / rank` against validation loss. A ratio of 0.1 means you were
paying for 10x more capacity than the update used.

## 13. Adapter Registry

```java
public final class AdapterRegistry {
    private final Map<String, LoraAdapter> adapters = new LinkedHashMap<>();
    private String active;

    public void activate(String name) {
        if (!adapters.containsKey(name)) throw new NoSuchElementException(name);
        active = name;
    }
    public double[] delta(String module, double[] x) {
        LoraAdapter ad = adapters.get(active);
        return ad == null ? new double[x.length] : ad.apply(module, x);
    }
}
```

`delta` returning a zero vector for an inactive adapter keeps the call sites clean
and makes "adapter off" a measured configuration rather than a code branch.

## Self-Check

1. Why clamp after `Math.round` in the symmetric quantizer?
2. Compute `rankForEnergy` for singular values `[3, 2, 1]` at target 0.9.
3. What breaks if `noDecay` is omitted for `B`?
4. Why does `delta()` return zeros instead of null when no adapter is active?