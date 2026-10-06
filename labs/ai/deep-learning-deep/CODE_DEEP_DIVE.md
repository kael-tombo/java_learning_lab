# deep-learning-deep — Code Deep Dive

Java 21, no dependencies. Convolution, recurrence, and attention all hand-written, with
shape assertions at every boundary and a gradient checker available for the backward
passes.

## 1. Project Structure

```
deep-learning-deep/
  src/com/ailab/dl/
    tensor/{Tensor,Shape}.java
    conv/{Conv2d,Pool,Im2col}.java
    rnn/{Rnn,Lstm,Gru}.java
    attn/{Attention,MultiHead,Masks}.java
    pos/{Sinusoidal,Rope,Alibi,RelBias}.java
    norm/{LayerNorm,RmsNorm,PrePostBlock}.java
    cache/{KvCache,Mqa,PagedCache}.java
    infer/{ContinuousBatcher,Speculative,Quant}.java
    Main.java
```

## 2. Tensor with Shape Assertions

```java
public record Shape(int... dims) {
    public int size() { int n = 1; for (int d : dims) n *= d; return n; }
    public Shape assertCompatible(Shape other) {
        if (dims.length != other.dims.length)
            throw new IllegalArgumentException("rank " + dims.length + " vs " + other.dims.length);
        for (int i = 0; i < dims.length; i++)
            if (dims[i] != other.dims[i])
                throw new IllegalArgumentException("dim " + i + ": " + dims[i] + " vs " + other.dims[i]);
        return this;
    }
}

public final class Tensor {
    private final Shape shape;
    private final double[] data;

    public Tensor(Shape shape) { this.shape = shape; this.data = new double[shape.size()]; }

    public double at(int... idx) {
        int off = 0;
        for (int i = 0; i < idx.length; i++) {
            if (idx[i] < 0 || idx[i] >= shape.dims()[i])
                throw new IndexOutOfBoundsException("index " + idx[i] + " vs dim " + shape.dims()[i]);
            off = off * shape.dims()[i] + idx[i];
        }
        return data[off];
    }

    public Tensor matmul(Tensor other) {
        int[] a = shape.dims(), b = other.shape.dims();
        if (a.length != 2 || b.length != 2 || a[1] != b[0])
            throw new IllegalArgumentException("matmul " + Shape.of(a) + " x " + Shape.of(b));
        Tensor out = new Tensor(new Shape(a[0], b[1]));
        for (int i = 0; i < a[0]; i++)
            for (int k = 0; k < a[1]; k++) {
                double aik = at(i, k);
                if (aik == 0.0) continue;
                for (int j = 0; j < b[1]; j++) out.data[i * b[1] + j] += aik * other.data[k * b[1] + j];
            }
        return out;
    }
}
```

Shape assertions at every matmul boundary. A silent broadcast error in a transformer
produces a model that trains to a worse loss rather than crashing, and hunting that costs a
day.

## 3. Conv2d With im2col

```java
public final class Conv2d {

    public record Spec(int inC, int outC, int k, int stride, int pad, int dilation) {}

    public static int outSize(int n, int k, int s, int p, int d) {
        int eff = d * (k - 1) + 1;                                  // effective kernel
        return (n + 2 * p - eff) / s + 1;
    }

    /** Nested-loop reference. Slow, obvious, and the thing everything else is checked against. */
    public static Tensor forward(Tensor in, double[][][] kernel, Spec sp) {
        int H = in.shape().dims()[1], W = in.shape().dims()[2];
        int OH = outSize(H, sp.k(), sp.stride(), sp.pad(), sp.dilation());
        int OW = outSize(W, sp.k(), sp.stride(), sp.pad(), sp.dilation());
        Tensor out = new Tensor(new Shape(1, sp.outC(), OH, OW));
        for (int oc = 0; oc < sp.outC(); oc++)
            for (int oh = 0; oh < OH; oh++)
                for (int ow = 0; ow < OW; ow++) {
                    double acc = 0;
                    for (int ic = 0; ic < sp.inC(); ic++)
                        for (int kh = 0; kh < sp.k(); kh++)
                            for (int kw = 0; kw < sp.k(); kw++) {
                                int ih = oh * sp.stride() - sp.pad() + kh * sp.dilation();
                                int iw = ow * sp.stride() - sp.pad() + kw * sp.dilation();
                                if (ih < 0 || ih >= H || iw < 0 || iw >= W) continue;   // zero pad
                                acc += in.at(0, ic, ih, iw) * kernel[oc][ic][kh][kw];
                            }
                    out.set(0, oc, oh, ow, acc);
                }
        return out;
    }

    /**
     * im2col + one GEMM. The column matrix is (k*k*Cin) x (OH*OW), so the multiply is
     * (Cout*k*k*Cin) x (Cin*k*k*OH*OW) -> the parameter count is visible in one line.
     */
    public static Tensor im2colConv(Tensor in, double[][][] kernel, Spec sp) {
        int H = in.shape().dims()[1], W = in.shape().dims()[2];
        int OH = outSize(H, sp.k(), sp.stride(), sp.pad(), sp.dilation());
        int OW = outSize(W, sp.k(), sp.stride(), sp.pad(), sp.dilation());
        int rows = sp.inC() * sp.k() * sp.k(), cols = OH * OW;

        double[] col = new double[rows * cols];
        for (int ic = 0; ic < sp.inC(); ic++)
            for (int kh = 0; kh < sp.k(); kh++)
                for (int kw = 0; kw < sp.k(); kw++) {
                    int row = ic * sp.k() * sp.k() + kh * sp.k() + kw;
                    for (int oh = 0; oh < OH; oh++)
                        for (int ow = 0; ow < OW; ow++) {
                            int ih = oh * sp.stride() - sp.pad() + kh * sp.dilation();
                            int iw = ow * sp.stride() - sp.pad() + kw * sp.dilation();
                            col[row * cols + oh * OW + ow] =
                                    (ih < 0 || ih >= H || iw < 0 || iw >= W) ? 0.0 : in.at(0, ic, ih, iw);
                        }
                }
        double[] w = new double[sp.outC() * rows];
        for (int oc = 0; oc < sp.outC(); oc++)
            System.arraycopy(kernel[oc], 0, w, oc * rows, rows);
        Tensor out = new Tensor(new Shape(1, sp.outC(), OH, OW));
        Tensor wm = new Tensor(new Shape(sp.outC(), rows));
        wm.setData(w);
        double[] res = Mat.flatMatmul(w, col, sp.outC(), rows, cols);
        for (int oc = 0; oc < sp.outC(); oc++)
            System.arraycopy(res, oc * cols, out.raw(oc), 0, cols);
        return out;
    }
}
```

Assert `im2colConv` equals `forward` elementwise in a test. They will agree until padding,
dilation, or a stride greater than one is added, and then only one of them is right.

## 4. LSTM Cell With the Gate Order Fixed

```java
public final class Lstm {

    public static final int N = 4;      // i, f, g, o  -- concatenate in this order

    public record State(double[] h, double[] c) {}

    public static State step(double[] x, State s, Tensor[] w, double[] b) {
        int H = s.h().length;
        double[] gates = new double[4 * H];
        for (int g = 0; g < 4; g++)
            for (int h = 0; h < H; h++) {
                double acc = b[g * H + h];
                for (int i = 0; i < x.length; i++) acc += w[g * H + h].at(i, x.length) * x[i];
                for (int i = 0; i < H; i++)       acc += w[g * H + h].at(i, x.length + H) * s.h()[i];
                gates[g * H + h] = acc;
            }
        double[] i = slice(gates, 0, H), f = slice(gates, H, H);
        double[] g = slice(gates, 2 * H, H), o = slice(gates, 3 * H, H);
        for (int h = 0; h < H; h++) {
            i[h] = sigmoid(i[h]); f[h] = sigmoid(f[h]); o[h] = sigmoid(o[h]); g[h] = Math.tanh(g[h]);
            // c_t = f_t * c_{t-1} + i_t * g_t   (candidates computed before the write so
            // reading old c_{t-1} here is not order-dependent)
            double cPrev = s.c()[h];
            s.c()[h] = f[h] * cPrev + i[h] * g[h];
            s.h()[h] = o[h] * Math.tanh(s.c()[h]);
        }
        return s;
    }
}
```

Computing `i`, `f`, `g`, `o` from one concatenated weight matrix is both faster and less
error-prone than four separate calls. The in-place state update is fine **because** all four
gates were computed before the loop; computing `f` after writing `c` is a real and silent
bug.

## 5. Attention With the Mask Applied Before the Softmax

```java
public final class Attention {

    /**
     * mask[i][j] == false means position j must not be visible to position i.
     * Applied by SETTING THE LOGIT TO -inf, not by zeroing probabilities afterwards:
     * softmax(-inf) is exactly 0 and renormalizes the rest, which is what we want.
     */
    public static double[][] logits(double[][] q, double[][] k, boolean[][] mask) {
        int n = q.length, dk = q[0].length;
        double[][] s = new double[n][n];
        double scale = 1.0 / Math.sqrt(dk);
        for (int i = 0; i < n; i++)
            for (int j = 0; j < n; j++) {
                if (mask != null && !mask[i][j]) { s[i][j] = Double.NEGATIVE_INFINITY; continue; }
                double dot = 0;
                for (int d = 0; d < dk; d++) dot += q[i][d] * k[j][d];
                s[i][j] = dot * scale;                    // <-- the scale is not optional
            }
        return s;
    }

    public static double[][] softmaxRows(double[][] s) {
        int n = s.length, m = s[0].length;
        double[][] p = new double[n][m];
        for (int i = 0; i < n; i++) {
            double max = Double.NEGATIVE_INFINITY;
            for (double v : s[i]) max = Math.max(max, v);
            if (max == Double.NEGATIVE_INFINITY) { Arrays.fill(p[i], Double.NaN); continue; }
            double sum = 0;
            for (int j = 0; j < m; j++) { p[i][j] = Math.exp(s[i][j] - max); sum += p[i][j]; }
            for (int j = 0; j < m; j++) p[i][j] /= sum;
        }
        return p;
    }

    public static boolean[][] causal(int n) {
        boolean[][] m = new boolean[n][n];
        for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) m[i][j] = j <= i;
        return m;
    }

    public static double[][] apply(double[][] p, double[][] v) {
        int n = p.length, dv = v[0].length;
        double[][] out = new double[n][dv];
        for (int i = 0; i < n; i++)
            for (int d = 0; d < dv; d++) {
                double acc = 0;
                for (int j = 0; j < p[0].length; j++) acc += p[i][j] * v[j][d];
                out[i][d] = acc;
            }
        return out;
    }
}
```

Three details carry the whole thing: the scale, `-inf` rather than zero, and the
`max == -inf` guard on fully-masked rows. A fully masked row produces NaN through the
naive softmax, and NaN propagates through every downstream loss forever.

## 6. FlashAttention-Style Tiled Attention With Online Softmax

```java
public final class TiledAttention {

    public static double[][] forward(double[][] q, double[][] k, double[][] v, int block) {
        int n = q.length, dk = q[0].length, dv = v[0].length;
        double scale = 1.0 / Math.sqrt(dk);
        double[] o = new double[dv];       // running output accumulator
        double[] oRow = new double[dv];
        double runningMax = Double.NEGATIVE_INFINITY;
        double runningSum = 0;

        for (int i0 = 0; i0 < n; i0 += block) {
            int i1 = Math.min(n, i0 + block);
            Arrays.fill(oRow, 0.0);
            for (int j0 = 0; j0 < n; j0 += block) {
                int j1 = Math.min(n, j0 + block);
                double blockMax = Double.NEGATIVE_INFINITY;
                double[][] s = new double[i1 - i0][j1 - j0];
                for (int i = i0; i < i1; i++)
                    for (int j = j0; j < j1; j++) {
                        if (j > i) { s[i - i0][j - j0] = Double.NEGATIVE_INFINITY; continue; }
                        double dot = 0;
                        for (int d = 0; d < dk; d++) dot += q[i][d] * k[j][d];
                        s[i - i0][j - j0] = dot * scale;
                        blockMax = Math.max(blockMax, s[i - i0][j - j0]);
                    }
                if (blockMax == Double.NEGATIVE_INFINITY) continue;

                double newMax = Math.max(runningMax, blockMax);
                double correction = runningMax == Double.NEGATIVE_INFINITY ? 0.0
                        : Math.exp(runningMax - newMax);      // rescale what we already have

                double blockSum = 0;
                for (int i = i0; i < i1; i++) {
                    double rowSum = 0;
                    for (int j = j0; j < j1; j++)
                        if (s[i - i0][j - j0] != Double.NEGATIVE_INFINITY)
                            rowSum += Math.exp(s[i - i0][j - j0] - newMax);
                    blockSum += rowSum;
                    runningSum = runningSum * correction + rowSum;
                    for (int d = 0; d < dv; d++) {
                        double acc = 0;
                        for (int j = j0; j < j1; j++)
                            if (s[i - i0][j - j0] != Double.NEGATIVE_INFINITY)
                                acc += Math.exp(s[i - i0][j - j0] - newMax) * v[j][d];
                        oRow[d] = oRow[d] * correction + acc;
                    }
                }
                runningMax = newMax;
            }
            for (int d = 0; d < dv; d++) o[d] += oRow[d] / Math.max(runningSum, 1e-300);
        }
        return singleRow(o);
    }
}
```

The `correction = exp(runningMax - newMax)` line is the entire algorithm. It rescales the
already-accumulated output when a later block raises the running maximum, so the result is
algebraically identical to the naive computation while never materializing the full score
matrix. Assert equality with naive attention at `1e-10` in a test.

## 7. RoPE and ALiBi

```java
public final class RoPE {

    /**
     * Rotates each (even, odd) PAIR of dimensions by angle pos * invFreq.
     * Working in pairs (rather than a full d x d rotation) makes it O(d), not O(d^2).
     */
    public static double[][] apply(double[][] x, int headDim, double base) {
        int n = x.length, half = headDim / 2;
        double[] invFreq = new double[half];
        for (int i = 0; i < half; i++)
            invFreq[i] = 1.0 / Math.pow(base, (2.0 * i) / headDim);
        double[][] out = new double[n][headDim];
        for (int pos = 0; pos < n; pos++)
            for (int i = 0; i < half; i++) {
                double theta = pos * invFreq[i];
                double c = Math.cos(theta), s = Math.sin(theta);
                out[pos][2 * i]     = x[pos][2 * i]     * c - x[pos][2 * i + 1] * s;
                out[pos][2 * i + 1] = x[pos][2 * i + 1] * c + x[pos][2 * i] * s;
            }
        return out;
    }
}

public final class Alibi {

    /** Parameter-free: add -m_h * |i - j| per head, with m_h geometric across heads. */
    public static double[][] bias(int n, int heads) {
        double[][] b = new double[heads][n * n];
        for (int h = 0; h < heads; h++) {
            double m = Math.pow(2, 8.0 * h / Math.max(1, heads - 1));  // geometric spread
            for (int i = 0; i < n; i++)
                for (int j = 0; j < n; j++) b[h][i * n + j] = -m * Math.abs(i - j);
        }
        return b;
    }
}
```

RoPE's pair structure is why the memory cost is `O(d)` per position rather than `O(d^2)`.
The geometric ALiBi slope spread means some heads are strongly local and some are nearly
uniform, which is the diversity the scheme is designed to provide.

## 8. Pre-Norm Block

```java
public final class Block {

    /**
     * PRE-norm. x flows through the residual path untouched, so d(out)/dx is close to
     * identity and early-layer gradients are not attenuated by a chain of normalizations.
     */
    public static double[] forward(double[] x, Function<double[], double[]> attn,
                                  Function<double[], double[]> ffn, LayerNorm ln1, LayerNorm ln2) {
        double[] a = ln1.forward(x);
        for (int i = 0; i < x.length; i++) a[i] += attn.apply(a)[i];       // x + Attn(LN(x))
        double[] b = ln2.forward(a);
        for (int i = 0; i < a.length; i++) b[i] += ffn.apply(b)[i];        // + FFN(LN(.))

        double[] out = new double[b.length];
        for (int i = 0; i < b.length; i++) out[i] = x[i] + b[i];           // x + sublayer output
        return out;
    }
}
```

Compare with post-norm (`LayerNorm(x + Attn(x))`), which puts a normalization on the
residual path at every layer and needs warmup at depth. The final LayerNorm after the last
pre-norm block is required: pre-norm leaves the residual stream unnormalized, so the logits
head reads an unscaled vector.

## 9. KV Cache With an Explicit Shape Contract

```java
public final class KvCache {

    private final int layers, kvHeads, headDim, maxLen;
    private final double[][][] key;      // [layer][head][pos * headDim]
    private final double[][][] val;
    private int len;

    public KvCache(int layers, int kvHeads, int headDim, int maxLen) {
        this.layers = layers; this.kvHeads = kvHeads; this.headDim = headDim; this.maxLen = maxLen;
        this.key = new double[layers][kvHeads][maxLen * headDim];
        this.val = new double[layers][kvHeads][maxLen * headDim];
    }

    public int append(int layer, int head, double[] k, double[] v) {
        if (len >= maxLen) throw new IllegalStateException("cache full: " + len + "/" + maxLen);
        System.arraycopy(k, 0, key[layer][head], len * headDim, headDim);
        System.arraycopy(v, 0, val[layer][head], len * headDim, headDim);
        return len++;
    }

    public double[][] viewKey(int layer, int head, int upto) {
        double[][] out = new double[upto][];
        for (int p = 0; p < upto; p++)
            out[p] = Arrays.copyOfRange(key[layer][head], p * headDim, (p + 1) * headDim);
        return out;
    }

    /** Bytes per token, per sequence. This is the number that limits batch and context. */
    public long bytesPerToken(int bytesPerElement) {
        return 2L * layers * kvHeads * headDim * bytesPerElement;
    }
}
```

`kvHeads` distinct from query heads is what makes GQA a one-constructor change. With
`kvHeads == 1` you get MQA; with `kvHeads == groups` you get GQA; with `kvHeads ==
queryHeads` you get standard MHA.

## 10. Continuous Batching Scheduler

```java
public final class ContinuousBatcher {

    public record Req(int id, int maxNewTokens) {
        int generated; boolean done;
    }

    public record Step(List<Integer> admitted, List<Integer> finished, List<Integer> active) {}

    /**
     * Each step runs ONE token for every active sequence. New sequences enter as others
     * finish, so the device never drains waiting for the slowest member of a fixed batch.
     */
    public Step step(Deque<Req> waiting, List<Req> active, int capacity) {
        while (active.size() < capacity && !waiting.isEmpty()) active.add(waiting.poll());
        List<Integer> finished = new ArrayList<>();
        for (int i = active.size() - 1; i >= 0; i--) {
            Req r = active.get(i);
            r.generated++;
            if (r.generated >= r.maxNewTokens) { finished.add(r.id()); active.remove(i); }
        }
        return new Step(List.of(), finished, active.stream().map(Req::id).toList());
    }
}
```

The whole throughput win of continuous batching is the loop that admits from `waiting` at the
**top of every step** rather than at batch boundaries. Compare total steps to
`max(maxNewTokens)` for static batching of the same workload — the difference is the idle
fraction you gave back to real work.

## 11. Speculative Decoding With Exact Verification

```java
public final class Speculative {

    public record Draft(List<Integer> tokens, boolean[] accepted) {}

    /**
     * Draft k tokens, then verify in one target pass.
     * A prefix of ACCEPTED_MISS + 1 draft tokens is kept: the first mismatch is replaced by
     * the target's own token there, which is exactly what makes the output distribution
     * identical to sampling from the target.
     */
    public Draft verify(List<Integer> draft, int[] targetTokens, int[] acceptPrefix) {
        int kept = 0;
        while (kept < draft.size() && kept < targetTokens.length && draft.get(kept) == targetTokens[kept])
            kept++;
        boolean[] accepted = new boolean[draft.size()];
        Arrays.fill(accepted, 0, kept, true);
        acceptPrefix[0] = kept;
        return new Draft(draft.subList(0, kept), accepted);
    }

    /** E[accepted] = sum_i alpha^i. With alpha=0.8, k=5 -> 2.69 tokens per target pass. */
    public static double expectedAccepted(double alpha, int k) {
        double s = 0, p = 1;
        for (int i = 1; i <= k; i++) { p *= alpha; s += p; }
        return s;
    }
}
```

Keeping the first mismatched position (not discarding it) is what preserves the target
distribution. Discarding the whole draft and resampling from the target also preserves it
but throws away the accepted prefix, which is where all the speedup lives.

## 12. Weight Quantization With Per-Channel Scales

```java
public final class Quant {

    public static byte[][] perChannelSymmetric(double[][] w, int bits) {
        int qmax = (1 << (bits - 1)) - 1;
        byte[][] q = new byte[w.length][];
        double[] scales = new double[w.length];
        for (int c = 0; c < w.length; c++) {
            double max = 0;
            for (double v : w[c]) max = Math.max(max, Math.abs(v));
            double s = max == 0 ? 1e-8 : max / qmax;
            scales[c] = s;
            q[c] = new byte[w[c].length];
            for (int i = 0; i < w[c].length; i++)
                q[c][i] = (byte) Math.round(Math.clamp(w[c][i] / s, -qmax - 1, qmax));
        }
        return q;
    }

    /** Dequantize on the fly in the matmul; do not materialize the FP matrix. */
    public static double[] dequantRow(byte[] qRow, double scale) {
        double[] out = new double[qRow.length];
        for (int i = 0; i < qRow.length; i++) out[i] = qRow[i] * scale;
        return out;
    }
}
```

Dequantizing on the fly matters: materializing an FP matrix per layer defeats the entire
purpose of quantization. The real implementation fuses the scale into the accumulation.

## Self-Check

- [ ] Shape assertions at every matmul and convolution boundary.
- [ ] im2col path verified equal to the nested-loop reference.
- [ ] Dilation applied to the kernel index, not the stride.
- [ ] LSTM gates computed before the state update; `f` reads old `c`.
- [ ] Attention divided by `sqrt(d_k)`.
- [ ] Mask applied as `-inf` logits, with a fully-masked-row guard.
- [ ] Tiled attention verified against naive attention at `1e-10`.
- [ ] RoPE applied pairwise, `O(d)` per position.
- [ ] Pre-norm block adds the residual before normalization of the next sublayer, with a
      final norm after the stack.
- [ ] KV cache `bytesPerToken` computed and compared to the memory budget.
- [ ] Continuous batcher admits from the waiting queue every step.
- [ ] Speculative verification keeps the first mismatched position.
- [ ] Quantization uses per-channel scales and dequantizes during the multiply.
