# Lab 08: Multimodal Models — Code Deep Dive

## 1. Project Structure

```
lab08/
  src/com/genai/lab08/
    image/Patchify.java           HxWx3 -> patches
    image/PatchEmbed.java         linear projection + position + CLS
    image/SynthImage.java         procedural 8x8 grayscale generator
    image/RenderText.java         render glyphs for OCR tests
    vision/TinyVisionEncoder.java patch-MLP
    text/TinyTextEncoder.java     bag-of-tokens-MLP
    clip/ClipLoss.java            symmetric InfoNCE, stable
    clip/ClipGrad.java            analytic gradients
    clip/ClipTrainer.java         contrastive training loop
    clip/HardNegatives.java       in-batch mining
    fusion/CrossModalAttention.java
    fusion/Projector.java         linear + Perceiver resampler
    pipeline/MultimodalRag.java   retrieve images, answer with citations
    eval/Faithfulness.java, BiasAudit.java, OcrEval.java
    Main.java
```

## 2. Patchify

```java
public final class Patchify {

    /** @param img row-major [H][W] intensity 0..255 */
    public static double[][] patchify(int[][] img, int p) {
        int h = img.length, w = img[0].length;
        if (h % p != 0 || w % p != 0)
            throw new IllegalArgumentException(
                "H and W must be divisible by patch size: " + h + "x" + w + " p=" + p);
        int rows = h / p, cols = w / p;
        double[][] out = new double[rows * cols][p * p];
        int idx = 0;
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                double[] patch = out[idx++];
                int k = 0;
                for (int i = 0; i < p; i++)
                    for (int j = 0; j < p; j++)
                        patch[k++] = img[r * p + i][c * p + j] / 255.0;   // scale to [0,1]
            }
        }
        return out;
    }

    public static int tokenCount(int h, int w, int p) { return (h / p) * (w / p); }
}
```

Divisibility must be checked up front — silently dropping the remainder is how a
batch of images ends up with mismatched token counts and a crash three layers later.

## 3. Patch Embedding with CLS

```java
public final class PatchEmbed {
    private final int dim, p;
    private final double[][] w;          // [(p*p) x dim]
    private final double[][] pos;        // [nPatches+1][dim]
    private final Random rnd;

    public double[][] embed(double[][] patches) {
        int n = patches.length, t = n + 1;
        if (t > pos.length) throw new IllegalStateException("token budget exceeded");
        double[][] z = new double[t][dim];
        for (int i = 0; i < t; i++)
            for (int d = 0; d < dim; d++) z[i][d] = pos[i][d];
        for (int i = 0; i < n; i++)                       // patches occupy 1..n
            for (int d = 0; d < dim; d++) {
                double s = 0;
                for (int j = 0; j < p * p; j++) s += patches[i][j] * w[j][d];
                z[i + 1][d] += s;                        // residual-style add
            }
        return z;                                          // z[0] stays the CLS token
    }
}
```

The token budget check at entry — not deep in the transformer — is what lets a
caller fail fast on a 448x448 image fed to a 224-token model.

## 4. Contrastive Loss

```java
public final class ClipLoss {

    public static double[][] logits(double[][] z, double[][] t, double tau) {
        int n = z.length;
        if (t.length != n) throw new IllegalArgumentException("batch mismatch");
        double[][] s = new double[n][n];
        for (int i = 0; i < n; i++)
            for (int j = 0; j < n; j++) {
                double dot = 0;
                for (int d = 0; d < z[i].length; d++) dot += z[i][d] * t[j][d];
                s[i][j] = dot / tau;
            }
        return s;
    }

    public static double value(double[][] z, double[][] t, double tau) {
        double[][] s = logits(z, t, tau);
        double total = 0;
        for (int i = 0; i < s.length; i++) {
            total += crossEntropyRow(s[i], i);            // image -> text
            total += crossEntropyRow(transposeCol(s, i), i); // text -> image
        }
        return total / (2.0 * s.length);
    }

    /** -log softmax_row(s)[label], with max subtraction. */
    static double crossEntropyRow(double[] row, int label) {
        double max = Double.NEGATIVE_INFINITY;
        for (double v : row) max = Math.max(max, v);
        double sum = 0;
        for (double v : row) sum += Math.exp(v - max);
        return (max + Math.log(sum)) - row[label];        // logsumexp - logit
    }

    static double[] transposeCol(double[][] s, int j) {
        double[] col = new double[s.length];
        for (int i = 0; i < s.length; i++) col[i] = s[i][j];
        return col;
    }
}
```

`logsumexp - logit` avoids materializing the softmax vector and is stable without a
separate pass. At `tau -> inf` it reduces to `ln N`, which is the sanity check in
Exercise 4.

## 5. Analytic Gradients

```java
public final class ClipGrad {

    /** @return [dL/dz_i][dL/dt_j] */
    public static double[][][] grads(double[][] z, double[][] t, double tau) {
        int n = z.length, d = z[0].length;
        double[][] s = ClipLoss.logits(z, t, tau);
        double[][] dz = new double[n][d], dt = new double[n][d];

        double[][] p = softmaxRows(s);                    // image -> text
        double[][] q = softmaxRows(transpose(s));         // text -> image

        for (int i = 0; i < n; i++) {
            double c = (p[i][i] - 1.0) / (tau * 2.0 * n);
            for (int k = 0; k < d; k++) dz[i][k] += c * t[i][k];
        }
        for (int j = 0; j < n; j++) {
            double c = (q[j][j] - 1.0) / (tau * 2.0 * n);
            for (int k = 0; k < d; k++) dt[j][k] += c * z[j][k];
        }
        return new double[][][] { dz, dt };
    }
}
```

The `(p_ii - 1)` factor is the whole story: it is exactly zero when the pair is
already matched, so gradients concentrate on errors. Finite-difference verification
(Exercise 5) catches the `2N` normalization factor, which is the most common
derivation slip.

## 6. Tiny Encoders

```java
public final class TinyVisionEncoder {
    private final PatchEmbed embed;
    private final double[][] w1, b1, w2, b2;

    /** returns L2-normalized embedding */
    public double[] encode(double[][] patches) {
        double[][] z = embed.embed(patches);              // [1+N][dim]
        double[] pooled = Vectors.normalize(attentionPool(z));
        return pool2(mlp(pooled));
    }
}
```

`attentionPool` uses a learned query vector (CLS-like); `pool2` mean-pools the MLP
output and normalizes. Both encoders must output normalized vectors or `z_i . t_j`
leaves `[-1,1]` and the temperature stops controlling scale.

## 7. Cross-Modal Attention

```java
public final class CrossModalAttention {

    /**
     * q: [T][d] text queries.  kv: [M+T][d] = [visual ; text].
     * Mask: causal over the TEXT block only; visual keys visible to all queries.
     */
    public static double[][] forward(double[][] q, double[][] kv, int mVisual, int t) {
        int d = q[0].length;
        double[][] k = Vectors.rows(kv, 0, kv.length);
        double[][] out = new double[t][d];
        for (int qi = 0; qi < t; qi++) {
            int textPos = mVisual + qi;                   // absolute position of q[qi]
            double[] scores = new double[textPos + 1];
            for (int j = 0; j <= textPos; j++) {
                double dot = 0;
                for (int kk = 0; kk < d; kk++) dot += q[qi][kk] * k[j][kk];
                scores[j] = dot / Math.sqrt(d);
            }
            double[] w = Vectors.softmax(scores);         // only up to textPos: causal
            double[] ctx = new double[d];
            for (int j = 0; j <= textPos; j++)
                for (int kk = 0; kk < d; kk++) ctx[kk] += w[j] * kv[j][kk];
            System.arraycopy(ctx, 0, out[qi], 0, d);
        }
        return out;
    }
}
```

The causal bound is `mVisual + qi + 1` keys — all `mVisual` visual tokens plus text
up to and including the current one. Getting this off by one either leaks the future
or drops the current token, and the bug is invisible in a smoke test.

## 8. Projector and Resampler

```java
public final class Projector {

    public static double[][] linear(double[][] visual, double[][] w, double[] b) {
        double[][] out = new double[visual.length][b.length];
        for (int i = 0; i < visual.length; i++) {
            for (int j = 0; j < b.length; j++) {
                double s = b[j];
                for (int k = 0; k < visual[i].length; k++) s += visual[i][k] * w[k][j];
                out[i][j] = s;
            }
        }
        return out;
    }

    /** Perceiver-style: K learned queries attend over M visual tokens. */
    public static double[][] resample(double[][] visual, double[][] queries,
                                       int kHeads, double scale) {
        int m = visual.length, k = queries.length, d = queries[0].length;
        double[][] out = new double[k][d];
        for (int qi = 0; qi < k; qi++) {
            double[] att = new double[m];
            for (int j = 0; j < m; j++) {
                double dot = 0;
                for (int c = 0; c < d; c++) dot += queries[qi][c] * visual[j][c];
                att[j] = dot * scale;                      // scale = 1/sqrt(d)
            }
            Vectors.softmaxInPlace(att);
            for (int j = 0; j < m; j++)
                for (int c = 0; c < d; c++) out[qi][c] += att[j] * visual[j][c];
        }
        return out;
    }
}
```

The resampler reduces `M` tokens to `K` regardless of `M`, which is what keeps the
LLM's attention cost independent of image resolution. It is the single highest-leverage
component in a VLM.

## 9. Resolution Fitting

```java
public static double fitScale(int w, int h, int patch, int budget) {
    double alpha = patch * Math.sqrt((double) budget / ((double) w * h));
    double alphaMax = Math.min(1.0, (double) budget / (((double) w / patch) * (h / patch)));
    double alphaMin = (double) budget / ((double) (w * h));    // min tokens guard
    return Math.min(alphaMax, Math.max(alphaMin, alpha));
}
```

Then resize to `round(w*alpha/patch)*patch` x `round(h*alpha/patch)*patch`, so the
grid is full and no partial patches appear.

## 10. Synthetic Image Generator

```java
public final class SynthImage {

    public static int[][] circle(int size, int cx, int cy, int r, int value) {
        int[][] img = new int[size][size];
        for (int y = 0; y < size; y++)
            for (int x = 0; x < size; x++)
                if ((x - cx) * (x - cx) + (y - cy) * (y - cy) <= r * r) img[y][x] = value;
        return img;
    }

    public static String caption(int[][] img) {              // ground truth from the generator
        return LABELS.entrySet().stream()
            .filter(e -> Arrays.stream(img).flatMapToInt(Arrays::stream).anyMatch(v -> v == e.getValue()))
            .map(Map.Entry::getKey).collect(Collectors.joining(" "));
    }
}
```

`caption` reads the labels straight from the generator rather than a model — that is
what makes this a *supervised* contrastive setup, and why recall can actually reach
1.0. Real CLIP captions are noisy; the gap is worth measuring.

## 11. Multimodal RAG Pipeline

```java
public record Retrieved(String imageId, double score) {}

public Result answer(String query, int k) {
    double[] qv = textEncoder.encode(query);
    List<Retrieved> hits = imageIndex.search(qv, k);          // cosine, normalized
    String prompt = renderPrompt(query, hits);                // [image tags][query]
    String answer = vlm.generate(prompt);
    var cited = CitationParser.extract(answer);               // [1], [2], ...
    Set<String> valid = hits.stream().map(Retrieved::imageId).collect(toSet());
    for (int i : cited) {
        if (i < 1 || i > hits.size()) throw new IllegalStateException("BAD_CITATION:" + i);
        if (!valid.contains(hits.get(i - 1).imageId())) throw new IllegalStateException("MISMATCH");
    }
    return new Result(answer, hits, faithful(answer, hits));
}
```

Validating citations against `hits` (not just the range) catches ordering bugs where
the VLM cites `[1]` but the prompt listed the images in a different order.

## 12. Faithfulness Check

```java
public static boolean faithful(String answer, List<Retrieved> hits) {
    Set<String> nouns = NounExtractor.extract(answer);
    Set<String> evidence = new HashSet<>();
    for (Retrieved h : hits) evidence.addAll(NounExtractor.extract(captionOf(h.imageId())));
    return evidence.containsAll(nouns);
}
```

A cheap entailment proxy: every noun in the answer must appear in some retrieved
caption or label. Imperfect (synonyms fail, and it misses relational errors), but it
catches gross language-prior hallucination — which is the dominant failure mode.

## Self-Check

1. Why must `PatchEmbed` check the token budget before projecting?
2. Trace `CrossModalAttention` with `mVisual=2, t=1`: how many keys are attended?
3. Derive the `2N` factor's effect if you forget it (what happens to the LR?).
4. Why compare citations against `hits` ids rather than only checking the range?
5. Compute the compression ratio for `M=576, K=64` and the attention saving.