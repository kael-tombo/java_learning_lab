# Lab 01: Transformer Architecture — Code Deep Dive

## 1. Project Structure

```
lab01/
├── src/main/java/com/genai/lab01/
│   ├── attention/
│   │   ├── ScaledDotProductAttention.java
│   │   ├── MultiHeadAttention.java
│   │   └── CausalMask.java
│   ├── layers/
│   │   ├── EncoderLayer.java
│   │   ├── DecoderLayer.java
│   │   └── FeedForward.java
│   ├── norm/
│   │   └── LayerNorm.java
│   ├── pos/
│   │   └── PositionalEncoding.java
│   └── transformer/
│       └── Transformer.java
```

## 2. Scaled Dot-Product Attention

```java
public class ScaledDotProductAttention {

    public double[][] attention(double[][] Q, double[][] K, double[][] V) {
        int n = Q.length;
        int dK = Q[0].length;

        // 1. Compute raw scores: Q · K^T
        double[][] scores = matmul(Q, transpose(K));

        // 2. Scale by 1/sqrt(d_k)
        double scale = 1.0 / Math.sqrt(dK);
        for (int i = 0; i < n; i++)
            for (int j = 0; j < n; j++)
                scores[i][j] *= scale;

        // 3. Softmax row-wise
        double[][] weights = new double[n][n];
        for (int i = 0; i < n; i++)
            weights[i] = softmax(scores[i]);

        // 4. Weighted sum of values
        return matmul(weights, V);
    }

    private double[] softmax(double[] row) {
        double max = Double.NEGATIVE_INFINITY;
        for (double v : row) max = Math.max(max, v);
        double sum = 0;
        double[] exp = new double[row.length];
        for (int i = 0; i < row.length; i++) {
            exp[i] = Math.exp(row[i] - max);
            sum += exp[i];
        }
        for (int i = 0; i < row.length; i++) exp[i] /= sum;
        return exp;
    }
}
```

**Key insight**: The max-subtraction in softmax prevents overflow for large scores.

## 3. Multi-Head Attention

```java
public class MultiHeadAttention {
    private final int numHeads;
    private final int dModel;
    private final int dK;
    private final double[][] Wq, Wk, Wv, Wo;  // learned projections

    public MultiHeadAttention(int dModel, int numHeads) {
        this.dModel = dModel;
        this.numHeads = numHeads;
        this.dK = dModel / numHeads;
        // Initialize weights (Xavier init)
        Wq = xavier(dModel, dModel);
        Wk = xavier(dModel, dModel);
        Wv = xavier(dModel, dModel);
        Wo = xavier(dModel, dModel);
    }

    public double[][] forward(double[][] x) {
        int n = x.length;
        double[][] Q = matmul(x, Wq);
        double[][] K = matmul(x, Wk);
        double[][] V = matmul(x, Wv);

        // Split into heads: [n][dModel] -> [h][n][dK]
        double[][][] heads = new double[numHeads][n][dK];
        for (int h = 0; h < numHeads; h++)
            heads[h] = extractHead(Q, K, V, h);

        // Attention per head
        ScaledDotProductAttention attn = new ScaledDotProductAttention();
        double[][][] headOutputs = new double[numHeads][n][dK];
        for (int h = 0; h < numHeads; h++)
            headOutputs[h] = attn.attention(heads[h][0], heads[h][1], heads[h][2]);

        // Concatenate heads: [h][n][dK] -> [n][dModel]
        double[][] concat = concatenate(headOutputs);

        // Output projection
        return matmul(concat, Wo);
    }
}
```

## 4. Causal Mask

```java
public class CausalMask {
    public static double[][] apply(double[][] scores) {
        int n = scores.length;
        double[][] masked = new double[n][n];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                masked[i][j] = (j > i) ? -1e9 : scores[i][j];
            }
        }
        return masked;
    }
}
```

**Note**: Use -1e9 (not -Infinity) to avoid NaN in softmax when an entire row
is masked (can happen with padding).

## 5. Layer Normalization

```java
public class LayerNorm {
    private final double[] gamma;  // gain
    private final double[] beta;   // bias
    private final double eps = 1e-5;

    public LayerNorm(int dModel) {
        gamma = new double[dModel];  // init to 1
        beta = new double[dModel];   // init to 0
        Arrays.fill(gamma, 1.0);
    }

    public double[][] forward(double[][] x) {
        int n = x.length;
        int d = x[0].length;
        double[][] out = new double[n][d];
        for (int i = 0; i < n; i++) {
            double mean = 0, var = 0;
            for (int j = 0; j < d; j++) mean += x[i][j];
            mean /= d;
            for (int j = 0; j < d; j++) var += (x[i][j] - mean) * (x[i][j] - mean);
            var /= d;
            double std = Math.sqrt(var + eps);
            for (int j = 0; j < d; j++)
                out[i][j] = gamma[j] * (x[i][j] - mean) / std + beta[j];
        }
        return out;
    }
}
```

## 6. Positional Encoding

```java
public class PositionalEncoding {
    public static double[][] generate(int maxLen, int dModel) {
        double[][] pe = new double[maxLen][dModel];
        for (int pos = 0; pos < maxLen; pos++) {
            for (int i = 0; i < dModel / 2; i++) {
                double angle = pos / Math.pow(10000, (2.0 * i) / dModel);
                pe[pos][2 * i] = Math.sin(angle);
                pe[pos][2 * i + 1] = Math.cos(angle);
            }
        }
        return pe;
    }
}
```

## 7. Encoder Layer

```java
public class EncoderLayer {
    private final MultiHeadAttention selfAttn;
    private final FeedForward ffn;
    private final LayerNorm norm1, norm2;

    public double[][] forward(double[][] x) {
        // Sub-layer 1: self-attention with residual
        double[][] attnOut = selfAttn.forward(x);
        x = norm1.forward(add(x, attnOut));

        // Sub-layer 2: FFN with residual
        double[][] ffnOut = ffn.forward(x);
        x = norm2.forward(add(x, ffnOut));

        return x;
    }
}
```

## 8. Common Pitfalls

1. **Forgetting to scale attention scores** → softmax saturation, vanishing gradients.
2. **Using -Infinity in mask** → NaN when entire row is masked.
3. **Wrong head splitting** → ensure contiguous slices of d_model per head.
4. **Missing residual connections** → deep models fail to train.
5. **Post-norm instability** → prefer pre-norm for deep stacks.
6. **Not subtracting max in softmax** → numerical overflow.

## 9. Testing Strategy

- **Unit tests**: Verify shapes at each layer.
- **Gradient checks**: Finite differences vs analytical gradients.
- **Ablation**: Remove components (mask, residuals) and measure degradation.
- **Sanity checks**: Attention weights sum to 1; causal mask blocks future.
