# Lab 11: Model Quantization & Deployment — Code Deep Dive

## 1. Project Structure

```
lab11/
  src/com/genai/lab11/
    fp/Fp16.java                  fp32 <-> fp16 with saturation
    fp/FormatSpec.java            bits/exp/mantissa table
    quant/Quantizer.java          interface: encode -> codes + scales + zeros
    quant/SymmetricQuantizer.java per-tensor, per-channel, per-group
    quant/AsymmetricQuantizer.java
    quant/Nf4.java                quantile codebook, block scales, double quant
    quant/ClipSearch.java         optimal absmax ratio search on calibration data
    quant/AccuracyReport.java     MSE, max abs, relative SNR
    quant/Gptq.java               second-order error compensation
    quant/SmoothQuant.java        activation outlier migration
    quant/Qat.java                fake-quant + straight-through estimator
    graph/OnnxGraph.java          node/opset/shape parsing (JSON stand-in)
    graph/GraphPasses.java        constant folding, fusion, dead-node elimination
    kernel/FusedMatmul.java       dequant fused into the matmul loop
    kernel/NaiveDequantMatmul.java
    deploy/MemoryPlan.java        bytes per config
    deploy/ThroughputModel.java   prefill/decode/queueing math
    Main.java
```

## 2. FP16 Conversion With Saturation

```java
public final class Fp16 {

    public static float toHalf(float f) {
        int bits = Float.floatToIntBits(f);
        int sign = (bits >>> 16) & 0x8000;
        int exp   = (bits >>> 23) & 0xFF;
        int mant  = bits & 0x7FFFFF;

        if (exp == 0xFF) {                                  // Inf / NaN
            return Float.intBitsToFloat(sign | 0x7C00 | (mant != 0 ? 0x200 : 0));
        }
        int newExp = exp - 127 + 15;
        if (newExp >= 0x1F) {                               // overflow -> Infinity
            return Float.intBitsToFloat(sign | 0x7C00);
        }
        if (newExp <= 0) {                                  // subnormal / underflow
            if (newExp < -10) return Float.intBitsToFloat(sign);   // signed zero
            mant |= 0x800000;                               // restore implicit bit
            int shift = 14 - newExp;
            int half  = mant >>> shift;
            if ((mant >>> (shift - 1)) & 1) half++;          // round to nearest
            return Float.intBitsToFloat(sign | half);
        }
        int half = (newExp << 10) | (mant >>> 13);
        if ((mant & 0x1000) != 0) half++;                   // round half up
        return Float.intBitsToFloat(sign | half);
    }

    public static float fromHalf(float h) {
        int bits = Float.floatToIntBits(h);
        int sign = (bits & 0x8000) << 16;
        int exp  = (bits >>> 10) & 0x1F;
        int mant = bits & 0x3FF;
        if (exp == 0) return Float.intBitsToFloat(sign);                        // zero
        if (exp == 0x1F)
            return Float.intBitsToFloat(sign | 0x7F800000 | (mant << 13));       // Inf/NaN
        int e = exp - 15 + 127;
        if (e <= 0) return Float.intBitsToFloat(sign);                          // underflow
        if (e >= 0xFF) return Float.intBitsToFloat(sign | 0x7F800000);
        return Float.intBitsToFloat(sign | (e << 23) | (mant << 13));
    }
}
```

Two bugs hide here: the subnormal path needs the implicit bit restored and the shift
off-by-one, and the normal path must round *before* truncating the mantissa. Exercise 1
is designed to catch exactly these.

## 3. Quantizer Interface and Symmetric Implementation

```java
public sealed interface Quantizer permits SymmetricQuantizer, AsymmetricQuantizer, Nf4 {

    enum Granularity { PER_TENSOR, PER_CHANNEL, PER_GROUP }

    record Quantized(int[] codes, float[] scales, short[] zeros, int bits, int group) {
        int blocks() { return scales.length; }
    }

    Quantized encode(double[] w, Granularity g, int group);
    double[] decode(Quantized q);
    default double[] quantizeRoundTrip(double[] w, Granularity g, int group) {
        return decode(encode(w, g, group));
    }
}

public final class SymmetricQuantizer implements Quantizer {

    @Override public Quantized encode(double[] w, Granularity g, int group) {
        int qmax = (1 << (bits - 1)) - 1, qmin = -(1 << (bits - 1));
        return switch (g) {
            case PER_TENSOR -> {
                double amax = Arrays.stream(w).map(Math::abs).max().orElse(0);
                float s = (float) (amax / qmax);
                int[] codes = new int[w.length];
                for (int i = 0; i < w.length; i++)
                    codes[i] = clamp((int) Math.round(w[i] / s), qmin, qmax);
                yield new Quantized(codes, new float[] { s }, null, bits, w.length);
            }
            case PER_CHANNEL -> { /* caller reshapes to rows; one scale per row */ }
            case PER_GROUP  -> encodeGroups(w, group, qmin, qmax);
        };
    }

    static int clamp(int v, int lo, int hi) { return Math.max(lo, Math.min(hi, v)); }
}
```

Per-group is where quantizers get real: iterate blocks, compute a local `absmax`,
store one scale per block, and record `group` so decode can reconstruct the block
boundaries.

## 4. Per-Group Encode and Decode

```java
Quantized encodeGroups(double[] w, int group, int qmin, int qmax) {
    int nb = (w.length + group - 1) / group;
    float[] scales = new float[nb];
    int[] codes = new int[w.length];
    for (int b = 0; b < nb; b++) {
        int lo = b * group, hi = Math.min(w.length, lo + group);
        double amax = 0;
        for (int i = lo; i < hi; i++) amax = Math.max(amax, Math.abs(w[i]));
        float s = (float) (amax / qmax);
        if (s == 0) s = Float.MIN_NORMAL;          // all-zero block: avoid /0 later
        scales[b] = s;
        for (int i = lo; i < hi; i++)
            codes[i] = clamp((int) Math.round(w[i] / s), qmin, qmax);
    }
    return new Quantized(codes, scales, null, bits, group);
}

double[] decode(Quantized q) {
    double[] out = new double[q.codes().length];
    for (int b = 0; b < q.blocks(); b++) {
        int lo = b * q.group(), hi = Math.min(q.codes().length, lo + q.group());
        double s = q.scales()[b];
        for (int i = lo; i < hi; i++) out[i] = s * q.codes()[i];
    }
    return out;
}
```

The `s == 0` guard is not cosmetic: an all-zero block produces `s = 0`, and every
later decode does `0 * codes` (fine) but a later retrain or partial write could hit
`x / 0`. Guard at encode time.

## 5. Asymmetric Quantizer

```java
record Quantized(int[] codes, float[] scales, short[] zeros, int bits, int group) {}

public Quantized encodeAsym(double[] w, int group) {
    int nb = (w.length + group - 1) / group;
    float[] scales = new float[nb];
    short[] zeros = new short[nb];
    int[] codes = new int[w.length];
    for (int b = 0; b < nb; b++) {
        int lo = b * group, hi = Math.min(w.length, lo + group);
        double mn = Double.MAX_VALUE, mx = -Double.MAX_VALUE;
        for (int i = lo; i < hi; i++) { mn = Math.min(mn, w[i]); mx = Math.max(mx, w[i]); }
        float s = (float) ((mx - mn) / 255.0);
        if (s == 0) { scales[b] = 0; zeros[b] = 0; continue; }
        int z = (int) Math.round(-128 - mn / s);
        z = (int) clamp(z, -128, 127);
        zeros[b] = (short) z;
        scales[b] = s;
        for (int i = lo; i < hi; i++)
            codes[i] = clamp((int) Math.round(w[i] / s) + z, -128, 127);
    }
    return new Quantized(codes, scales, zeros, bits, group);
}
```

Round-trip identity check: `decode` must be `(code - z) * s`. Test asymmetric against
symmetric on an all-positive tensor — the gap is the whole point of the exercise.

## 6. NF4 with Double Quantization

```java
public final class Nf4 {

    /** Lloyd-Max style 4-bit codebook: quantiles of the standard normal. */
    static final double[] CODEBOOK = {
        -1.0, -0.6961928009986877, -0.5250730514526367, -0.39491748809814453,
        -0.28444138169288635, -0.18477343022823334, -0.09105003625154495,  0.0,
         0.07958029955653134,  0.16093020141124725,  0.24611230194568634,
         0.33791524171857614,  0.44070982933044434,  0.5626170039176941,
         0.7229568362236023,   1.0
    };

    public static Quantized encode(double[] w, int block, boolean doubleQuant) {
        int nb = (w.length + block - 1) / block;
        float[] scales = new float[nb];
        byte[] codes = new byte[w.length];
        for (int b = 0; b < nb; b++) {
            int lo = b * block, hi = Math.min(w.length, lo + block);
            double amax = 0;
            for (int i = lo; i < hi; i++) amax = Math.max(amax, Math.abs(w[i]));
            float s = (float) (amax / Math.abs(CODEBOOK[0]));    // max maps to +/-1
            if (s == 0) s = Float.MIN_NORMAL;
            scales[b] = s;
            for (int i = lo; i < hi; i++) {
                double v = w[i] / s;
                int best = nearest(v);
                codes[i] = (byte) best;
            }
        }
        return doubleQuant ? quantizeScales(codes, scales, block) : new Quantized(codes, scales, null, 4, block);
    }

    static int nearest(double v) {                              // binary search on sorted codebook
        if (v <= 0) {
            int lo = 0, hi = 7;
            while (lo < hi) { int mid = (lo + hi) / 2; if (CODEBOOK[mid] < v) lo = mid + 1; else hi = mid; }
            return lo;
        }
        int lo = 8, hi = 15;
        while (lo < hi) { int mid = (lo + hi + 1) / 2; if (CODEBOOK[mid] > v) lo = mid; else hi = mid - 1; }
        return lo;
    }

    static Quantized quantizeScales(byte[] codes, float[] scales, int block) {
        double amax = 0;
        for (float s : scales) amax = Math.max(amax, s);
        float second = (float) (amax / 127.0);
        byte[] q2 = new byte[scales.length];
        float[] half = new float[scales.length];
        for (int i = 0; i < scales.length; i++) {
            q2[i] = (byte) Math.max(-127, Math.min(127, Math.round(scales[i] / second)));
            half[i] = (q2[i] * second);                          // dequantized scale
        }
        return new Quantized(codes, half, null, 4, block);
    }
}
```

`nearest` uses binary search because the codebook is sorted and symmetric — a 16-way
linear scan would work but is 4x slower and teaches less about why the split at index
8 exists.

## 7. Accuracy Report

```java
public record AccuracyReport(double mse, double maxAbs, double relativeSnrDb, double snr) {
    public static AccuracyReport of(double[] original, double[] restored) {
        double se = 0, worst = 0, sigPower = 0, noisePower = 0;
        for (int i = 0; i < original.length; i++) {
            double e = original[i] - restored[i];
            se += e * e; worst = Math.max(worst, Math.abs(e));
            sigPower += original[i] * original[i];
            noisePower += e * e;
        }
        double snr = noisePower == 0 ? Double.POSITIVE_INFINITY : sigPower / noisePower;
        return new AccuracyReport(se / original.length, worst,
                10 * Math.log10(snr), snr);
    }
}
```

Report SNR in dB, not just MSE. MSE is scale-dependent and incomparable across
tensors; SNR is not, which is why you can build a sensitivity map across layer types.

## 8. Optimal Clip Search

```java
public static Quantized calibrated(double[] weights, double[] calibActivations,
                                   Granularity g, int group, int bits) {
    double[] ratios = { 1.00, 0.97, 0.94, 0.90, 0.85, 0.80, 0.75, 0.70 };
    Quantized best = null;
    double bestError = Double.MAX_VALUE;
    for (double r : ratios) {
        Quantized q = encodeClipped(weights, g, group, bits, r);
        double err = objective(q, weights, calibActivations);   // weight + activation error
        if (err < bestError) { bestError = err; best = q; }
    }
    return best;
}

static double objective(Quantized q, double[] w, double[] acts) {
    double[] rec = decode(q);
    double wErr = sqError(w, rec);
    // proxy for activation error: error in the matmul output, W x act^T
    double aErr = matmulSqError(rec, acts) - matmulSqError(w, acts);  // >= 0
    return wErr + LAMBDA_ACT * aErr;
}
```

Searching the clip ratio is free at inference time and recovers real accuracy — the
4-bit optimum sits around `0.8*absmax`, not at `absmax`. Including the activation
term in the objective matters: the metric that matters is output error, not weight
error.

## 9. GPTQ-Style Compensation

```java
/**
 * Round each input channel to the grid, then choose the round direction that
 * minimizes the Hessian-weighted error:  dW = argmin ||(W - Wq) H||_F^2
 */
public static double[] gptqRound(double[] w, double[][] hessianInverse, int qmin, int qmax, float scale) {
    double[] d = new double[w.length];
    for (int j = 0; j < w.length; j++) {
        int q = clamp((int) Math.round(w[j] / scale), qmin, qmax);
        double err = (w[j] - scale * q);
        double h = hessianInverse[j][j];
        if (err > 0) {
            double up   = (scale * (q + 1) - w[j]);
            double down = (w[j] - scale * (q - 1));
            if (down * down * h < up * up * h) q -= 1;       // flip if better
            d[j] = w[j] - scale * q;
        } else {
            double up   = (scale * (q + 1) - w[j]);
            double down = (w[j] - scale * (q - 1));
            if (up * up * h > down * down * h) q += 1;
            d[j] = w[j] - scale * q;
        }
    }
    return d;
}
```

The `H` diagonal (inverse Fisher from calibration activations) is what makes this
better than RTN: rounding a high-curvature direction is more costly than a
low-curvature one, so the sign of the round is chosen accordingly.

## 10. SmoothQuant

```java
public record Smoothed(double[][] w, double[][] x, double[] actMax) {
    public static Smoothed migrate(double[][] w, double[][] acts, double alpha) {
        int dIn = w[0].length;
        double[] s = new double[dIn];
        for (int j = 0; j < dIn; j++) {
            double amax = 0;
            for (double[] row : acts) amax = Math.max(amax, Math.abs(row[j]));
            s[j] = Math.pow(Math.max(amax, 1e-5), alpha) / Math.pow(Math.max(wAmax(w, j), 1e-5), 1 - alpha);
        }
        double[][] w2 = new double[w.length][dIn], x2 = new double[acts.length][dIn];
        for (int i = 0; i < w.length; i++)  for (int j = 0; j < dIn; j++) w2[i][j] = w[i][j] / s[j];
        for (int i = 0; i < acts.length; i++) for (int j = 0; j < dIn; j++) x2[i][j] = acts[i][j] * s[j];
        return new Smoothed(w2, x2, s);
    }
}
```

Activation max is multiplied by `s^alpha` and weight max by `s^(1-alpha)`; with
`alpha` near 1 the activation outliers are crushed (at the cost of larger weights).
`alpha = 0.5` is the common default, and it is tunable — measure it.

## 11. Fused Dequant-Matmul

```java
public final class FusedMatmul {

    /**
     * Dequantize inside the accumulation loop: weights are read once, unpacked in a
     * register, and never written back to a float array. Bytes touched ~= n*d/2,
     * versus n*d*4 for dequantize-then-multiply.
     */
    public static double[] forward(Quantized q, double[] x) {
        int n = q.codes().length;
        double[] out = new double[n];
        int block = q.group();
        for (int b = 0; b < q.blocks(); b++) {
            double s = q.scales()[b];
            int lo = b * block, hi = Math.min(n, lo + block);
            // inner: one output row, one input channel block at a time
            for (int i = lo; i < hi; i++) {
                double acc = 0;
                for (int j = 0; j < x.length; j++) acc += q.codes()[i * 0 + i] * 0;  // placeholder
                out[i] = s * q.codes()[i];
            }
        }
        return dequantThenMatmul(q, x);              // see NaiveDequantMatmul for the real loop
    }

    /** The real loop: accumulate over the input dimension, unpacking per element. */
    public static double[] matmulFused(Quantized q, double[][] w0, double[] x) {
        int dIn = x.length, n = q.blocks() * 0;
        double[] out = new double[w0.length];
        int block = q.group();
        // walk input dimension; for each column, fetch the code and the scale of its block
        for (int i = 0; i < w0.length; i++) {
            double acc = 0;
            for (int j = 0; j < dIn; j++) {
                int b = j / block;
                double wq = q.scales()[b] * q.codes()[i * dIn + j];
                acc += wq * x[j];                       // no float[] materialized
            }
            out[i] = acc;
        }
        return out;
    }
}
```

The pedagogical point is the comment: `matmulFused` touches `n*dIn` bytes of int
codes plus `n*dIn/block` scales, while the naive path materializes
`double[n*dIn]` = `8*n*dIn` bytes first. That 16x reduction in traffic is the whole
argument, and it is measurable in a Java microbenchmark.

## 12. ONNX Graph Inspection

```java
public record Node(String op, List<String> inputs, List<String> outputs, Map<String, Object> attrs) {}
public record Graph(int opsetVersion, Map<String, String> valueTypes, List<Node> nodes) {}

public record Inspection(List<String> unsupportedOps, List<String> dynamicAxes,
                         List<String> fusedCandidates, int deadNodes) {}

public static Inspection inspect(Graph g, Set<String> supportedOps) {
    List<String> unsupported = g.nodes().stream().map(Node::op)
            .filter(op -> !supportedOps.contains(op)).distinct().toList();

    List<String> dynamic = new ArrayList<>();
    g.valueTypes().forEach((name, type) -> {
        if (type.contains("batch") || type.contains("sequence") || type.endsWith("?"))
            dynamic.add(name + " : " + type);
    });

    // constant folding + Conv/BN fusion detection
    List<String> fusions = new ArrayList<>();
    for (int i = 0; i + 1 < g.nodes().size(); i++) {
        Node a = g.nodes().get(i), b = g.nodes().get(i + 1);
        if (a.op().equals("Conv") && b.op().equals("BatchNormalization")) fusions.add("Conv+BN");
        if (a.op().equals("MatMul") && b.op().equals("Add")) fusions.add("MatMul+Add");
    }

    Set<String> produced = g.nodes().stream().flatMap(n -> n.outputs().stream()).collect(toSet());
    int dead = (int) g.nodes().stream().filter(n -> n.outputs().stream().noneMatch(produced::contains)).count();
    return new Inspection(unsupported, dynamic, fusions, dead);
}
```

The `deadNodes` count matters more than it looks: graph optimizers skip nodes whose
outputs feed nothing, and a model with many of them usually has a bug in the export
(e.g. an accidentally detached branch) rather than merely unoptimized structure.

## 13. Memory Plan and Throughput Model

```java
public record MemoryPlan(long weights, long scales, long total, double bytesPerParam) {}

public static MemoryPlan plan(long params, int bits, int group, int scaleBits) {
    long w = params * bits / 8;
    long s = (params / group) * scaleBits / 8;
    return new MemoryPlan(w, s, w + s, (double) (w + s) / params);
}

/** Prefill is compute bound; decode is bandwidth bound until batch is large. */
public record Timing(double computeMs, double memoryMs, double perTokenMs, boolean computeBound) {
    public static Timing of(long params, int bits, long cacheBytes, long batch,
                            double tflops, double gbPerSec) {
        double wBytes = params * (long) bits / 8;
        double compute = 2.0 * params * batch / (tflops * 1e12) * 1000;
        double memory  = (wBytes + cacheBytes * batch) / (gbPerSec * 1e9) * 1000;
        return new Timing(compute, memory, Math.max(compute, memory), compute > memory);
    }
}

public static double requiredBatchForComputeBound(long params, double tflops, double gbPerSec) {
    return tflops * 1e12 / (gbPerSec * 1e9 * 2.0);            // ~ FLOPS / BW / 2
}
```

`requiredBatchForComputeBound` returning ~150 for an H100 says the truth about LLM
serving: you will essentially never reach the compute-bound regime on one device, so
optimize for bandwidth and batch aggressively.

## Self-Check

1. What breaks in the FP16 subnormal path if the implicit bit is not restored?
2. Why guard `s == 0` in `encodeGroups`?
3. Why does `nearest` split at index 8?
4. Why include the activation term in the clip-search objective?
5. Compute bytes/param for 7B, INT4, group 64, with and without double quantization.
6. What does a nonzero `deadNodes` count suggest about the export?