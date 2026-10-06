# Lab 02: GPT Architecture — Code Deep Dive

## 1. Project Structure

```
lab02/
  src/com/genai/lab02/
    CausalMask.java           additive mask construction
    Sampling.java             temperature, top-k, top-p, RNG
    BpeTokenizer.java         merge training + encode/decode
    KvCache.java              per-layer ring cache
    MiniGpt.java              decoder block stack, forward, generate
    Loss.java                 cross-entropy with padding mask
    Main.java                 ablation harness entry point
```

## 2. CausalMask

```java
public final class CausalMask {

    private CausalMask() {}

    public static double[][] additive(int n, int dHead) {
        double[][] m = new double[n][n];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                m[i][j] = (j <= i) ? 0.0 : Double.NEGATIVE_INFINITY;
            }
        }
        return m;
    }

    /** Apply mask to raw scores, then row-softmax. */
    public static double[] softmaxMasked(double[] logits, double[][] mask, int row) {
        double max = Double.NEGATIVE_INFINITY;
        for (int j = 0; j < logits.length; j++) {
            double s = logits[j] + mask[row][j];
            if (s > max) max = s;                 // -inf never wins the max
        }
        double sum = 0.0;
        double[] out = new double[logits.length];
        for (int j = 0; j < logits.length; j++) {
            out[j] = Math.exp(logits[j] + mask[row][j] - max);
            sum += out[j];
        }
        for (int j = 0; j < out.length; j++) out[j] /= sum;
        return out;
    }
}
```

Key detail: the running max must be computed over **masked** values, otherwise
a row of all `-inf` scores makes `max = -inf` and `z - max = NaN`.

## 3. BpeTokenizer

```java
public final class BpeTokenizer {

    public record Merge(int left, int right, int newId) {}

    private final int vocabSize;
    private final List<Merge> merges = new ArrayList<>();

    public List<Merge> train(List<int[]> sentences) {
        List<int[]> docs = sentences.stream().map(this::withBoundaryToken).toList();
        while (merges.size() < vocabSize - 256) {
            Map<Long, Integer> counts = new LinkedHashMap<>();
            for (int[] doc : docs) countPairs(doc, counts);
            Map.Entry<Long, Integer> best = counts.entrySet().stream()
                .max(Comparator.<Map.Entry<Long, Integer>>comparingInt(Map.Entry::getValue)
                      .thenComparingInt(Map.Entry::getKey))   // deterministic tie-break
                .orElse(null);
            if (best == null || best.getValue() < 2) break;     // stop: no useful pair
            applyMerge(best.getKey(), merges.size() + 256);
        }
        return merges;
    }
}
```

`applyMerge` rewrites every document in place. Because training rewrites all docs
each round, cost is `O(rounds * totalTokens)` — fine for a lab corpus, and a
good excuse to learn the linked-list tricks used in production BPE.

## 4. KvCache

```java
public final class KvCache {
    private final int layers;
    private final List<List<double[][]>> keys;   // [layer][pos][head*headDim]
    private final List<List<double[][]>> values;
    private int length;

    public void put(int layer, int pos, double[] k, double[] v) {
        while (keys.get(layer).size() <= pos) { keys.get(layer).add(null); }
        keys.get(layer).set(pos, k);
        values.get(layer).set(pos, v);
        length = Math.max(length, pos + 1);
    }

    public double[][] keys(int layer) { return prefix(keys.get(layer)); }
    public double[][] values(int layer) { return prefix(values.get(layer)); }
    public int length() { return length; }
}
```

For a fixed context window, replace the `ArrayList` with a `double[][]` plus a
`start` offset ring index so `put` never reallocates.

## 5. MiniGpt Forward With Cache

```java
public double[] forwardLast(int[] ids, KvCache cache) {
    int t = ids.length;
    double[][] h = embed(ids);                       // [t][dModel]
    addPositional(h);
    for (int layer = 0; layer < layers; layer++) {
        h = residual(layerNorm(h), causalSelfAttention(h, cache, layer));
        h = residual(layerNorm(h), mlp(h));
    }
    return lmHead(h[t - 1]);
}

private void causalSelfAttention(double[][] x, KvCache cache, int layer) {
    double[][] q = project(x, Wq[layer], heads);
    double[][] k = project(x, Wk[layer], heads);
    double[][] v = project(x, Wv[layer], heads);
    int pos = cache == null ? x.length : cache.length();
    if (cache != null) {
        cache.put(layer, pos, flatten(k), flatten(v));
        k = unflatten(cache.keys(layer));
        v = unflatten(cache.values(layer));
    }
    // scores = q_row · k_col / sqrt(headDim) + causalMask
}
```

The single-token case in decode makes `q` a 1 x d row, so the inner loop is
`s d_k` multiply-adds against `s` cached keys — no `n x n` score matrix at all.

## 6. Loss

```java
public static double crossEntropy(double[][] logits, int[] targets, int padId) {
    double sum = 0.0;
    int n = 0;
    for (int t = 0; t < targets.length; t++) {
        if (targets[t] == padId) continue;             // mask padded rows
        double z = logits[t][targets[t]];
        double zMax = Arrays.stream(logits[t]).max().orElseThrow();
        double lse = zMax + Math.log(Arrays.stream(logits[t])
            .map(v -> Math.exp(v - zMax)).sum());
        sum += lse - z;                               // == -log softmax[target]
        n++;
    }
    return n == 0 ? Double.NaN : sum / n;             // never divide by zero
}
```

The log-sum-exp form avoids materializing the probability vector and is stable
for large vocabularies.

## 7. Sampling

```java
public static int sample(double[] logits, double temp, int k, double p, Random rng) {
    double[] z = logits.clone();
    for (int i = 0; i < z.length; i++) z[i] /= Math.max(temp, 1e-6);
    if (k > 0 && k < z.length) {                       // top-k
        double cut = nthLargest(z, k);
        for (int i = 0; i < z.length; i++) if (z[i] < cut) z[i] = Double.NEGATIVE_INFINITY;
    }
    if (p > 0 && p < 1) {                              // top-p on sorted probs
        Integer[] idx = argsortDesc(z);
        double c = 0; int keep = z.length;
        for (int i = 0; i < idx.length; i++) {
            c += softmax1(z[idx[i]]);
            if (c >= p) { keep = i + 1; break; }
        }
        for (int i = keep; i < idx.length; i++) z[idx[i]] = Double.NEGATIVE_INFINITY;
    }
    return sampleFromSoftmax(z, rng);
}
```

## 8. Performance Notes

- Reuse buffers per call; allocation dominates for small models.
- Store the cache as `float[][]` (or int8 + per-head scale) in the memory
  benchmark; `double[][]` doubles the bytes for no accuracy need at inference.
- Fuse the QK^T loop with the mask add to avoid a second pass over scores.
- Parallelize over batch dimension with `Executors.newVirtualThreadPerTaskExecutor()`
  for the Java-side orchestration; the matmul itself still needs a BLAS.

## Self-Check

1. Trace `softmaxMasked` with `logits = [1, 2, 3]`, row 0 of a 3x3 causal mask.
2. Why must `max` be computed after masking?
3. How many cache entries does `forwardLast` add on the first call vs later calls?