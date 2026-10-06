# Lab 08: Multimodal Models — Math Foundation

## 1. Patch Geometry

For an image `H x W x 3` and patch size `P`:

```
N = (H/P) * (W/P)
patch dim = P^2 * 3
```

- 224/16 -> `14*14 = 196` patches; flattened dim `16*16*3 = 768`.
- 224/14 -> `16*16 = 256` patches; flattened dim `14*14*3 = 588`.
- 336/14 -> `24*24 = 576` patches.

Embedding projection matrix: `(P^2*3) x D`. For P=16, D=768: `768x768` params per
patch-embed layer — negligible compared to the transformer body.

## 2. Attention Cost and Resolution

With `N` tokens and head dim `d`, per layer attention FLOPs scale as:

```
attention cost ~ N^2 * d  (score + weighted sum)
FFN cost        ~ N * d^2
```

Ratio: `N^2 d / (N d^2) = N/d`. So attention dominates when `N > d` (typical:
N = 197-576, d = 768 — borderline). Doubling resolution from 224 to 448 squares the
patch count (196 -> 784) and quadruples the attention cost. This is why tiling with
a fixed token budget per tile beats a single huge image.

## 3. Cross-Entropy for a Token Vocabulary

```
p_j(z) = e^z_j / sum_k e^z_k
L = - sum_{t=1}^T m_t log p_{y_t}(z^t)
L(0) = T ln V        (uniform over V)
L(y) -> 0            (perfect)
```

Temperature `T`: at `T -> 0` this becomes greedy selection, and gradients vanish
(exponentially); at `T -> inf` it approaches uniform. Typical `T = 0.5-1.0`,
sometimes tuned per modality.

## 4. InfoNCE / Contrastive Loss

Given batch of `N` matched pairs, normalized embeddings `z_i` (image) and `t_i` (text),
logits `s_ij = z_i . t_j / tau` with `z_i . t_j` in `[-1, 1]`:

```
L_i = -log( exp(s_ii) / sum_{j=1}^{N} exp(s_ij) )
L   = (1/(2N)) sum_i [ L_i^{i->t} + L_i^{t->i} ]
```

Random baseline: `L = ln N`. Perfect: `L -> 0`. The useful dynamic range is
`[0, ln N]`, so with N=32k, `ln N = 10.4` — a loss of 2.0 already means strong
retrieval.

### Stability

Subtract the row max `c_i = max_j s_ij`:

```
p_ij = exp(s_ij - c_i) / sum_k exp(s_ik - c_i)
```

Since `|s_ij| <= 1/tau` and `tau = 0.01` gives `s_ij` up to 100, `exp(100)` overflows
double's ~709 limit nowhere, but `exp(1000)` would; with fp16 it overflows at ~11.
Always subtract the max.

## 5. Gradients of the Contrastive Loss

Let `p_ij` be the row softmax over `j` for image `i` (`p` = row-softmax of `s`, `q` =
column-softmax, i.e. softmax over `i` for each `j`).

```
dL_i/dz_i = (1/tau) * (p_ii - 1) * t_i
dL_j/dt_j = (1/(2N)) * (1/tau) * (q_jj - 1) * z_j
```

The `(p_ii - 1)` factor is **zero exactly when the model is already correct** for
that pair. Gradients vanish on solved examples — that is why temperature is so
important: small `tau` inflates `1/tau` and keeps the gradient alive on near-misses.

## 6. Temperature Trade-off

```
effective sharpness ~ 1/tau
gradient scale on a near-miss ~ (p_ii - 1)/tau
```

- `tau` too small: `1/tau` huge -> unstable, oscillation, gradient explosion.
- `tau` too large: `p_ii ~ 1/N` for all -> tiny gradients, near-random performance.

Empirically the optimum is `0.01-0.07`. One diagnostic: with `N` items and random
embeddings, `s_ij ~ N(0, 1/tau^2)` approximately, so the gap between `s_ii` and the
mean off-diagonal is about `1/tau`; you want that gap to be a few units, not a few
hundred.

## 7. Similarity and Retrieval Metrics

Given a query `q` and its true match `g`, rank all `N` items by `s`:

```
recall@1 = 1[rank(g) == 1]
recall@k = 1[rank(g) <= k]
MRR      = 1/rank(g)
```

For `K` queries:

```
R@k = (1/K) sum_q 1[rank_q(g) <= k]
MRR = (1/K) sum_q 1/rank_q(g)
```

Note recall@k rises fast initially then flattens: with random data, `R@1 = 1/N`,
`R@10 = 10/N`, and only very large `k` gets near 1. So `R@10` is the metric to
watch for practical retrieval.

## 8. Interpolated / Tiled Token Budget

For an image resized to `W x H` with target token count `B`, choose a scale
`alpha`:

```
N = (alpha*W/P) * (alpha*H/P)  <= B
alpha = P * sqrt(B) / sqrt(W*H)
```

Caps:
```
alpha_max <= 1.0            (never upsample beyond native)
alpha_min = B_min / ((W/P)*(H/P))   (require min tokens)
```

Solve the constrained problem by clamping `alpha` to `[alpha_min, alpha_max]`. Then
crop/pad to the aspect ratio so the patch grid stays full.

## 9. Projection Head Capacity

Projector `f: R^{M x D_v} -> R^{K x D_l}` via learned queries `Q in R^{K x D_l}`:

```
X' = f(Attn(Q, K=X, V=X))      K queries attend to M visual tokens
```

Cost: `O(K * M * D_l)` — independent of `M` after the first layer. Parameters:
`K*D_l*D_l` for Q plus the attention block. With `K = 32..64` and `D_l = 4096`, the
projector is ~0.5-1 GB in bf16 — nontrivial but far cheaper than feeding 576 visual
tokens through 32 LLM layers.

Compression ratio: `M/K`; with `M = 576, K = 64`, that's `9x` fewer tokens.

## 10. Masked Sequence Construction

```
[ v_1 ... v_M ][ t_1 t_2 ... t_L ]
  position: 0   1   ... M-1      M  M+1 ... M+L-1
  attends:  all tokens            t_j attends to all v_i and t_k for k <= j
```

Attention cost: `O((M+L)^2 d)`. With `M = 576, L = 128`, `N = 704` vs
`N = 128` for text-only — 30x the attention cost. **Visual tokens dominate the
sequence**, so KV cache and prefill cost are driven by `M`.

## 11. Softmax Numerics for the Contrastive Term

If embeddings are unnormalized, a high-norm outlier pair can dominate. Use
`z_norm = z / ||z||`. Then `s in [-1, 1]` and `s/tau in [-1/tau, 1/tau]`, which makes
the temperature the only scale control — cleaner, and it prevents the known
"embedding norm" failure mode where a single high-norm item acts as a hub.

## 12. IoU for Grounding Evaluation

```
IoU = area(A ∩ B) / area(A ∪ B)
```

`area(A ∪ B) = area(A) + area(B) - area(A ∩ B)`. Report `mAP@IoU=0.5` and
`@IoU=0.75` — small objects separate sharply between these thresholds.

## Worked Numbers

Batch `N = 256`, `tau = 0.02`, one image `448x448`, patch `P = 14`:

- tokens: `(448/14)^2 = 32^2 = 1024` visual tokens.
- If the prompt is 64 text tokens: `N_seq = 1088`, vs 64 for text-only -> **17x**
  attention cost.
- Attention FLOPs (one layer, `d = 4096`, 2 matmuls, 2 flops/MAC):
  `2 * 2 * N^2 * d = 4 * 1088^2 * 4096 ≈ 1.94e10` = 19.4 GFLOP per layer.
- With 32 layers: `6.2e11` = 620 GFLOP just for attention prefill on that one image.
- Projector to `K = 64`: `1024/64 = 16x` compression, cutting `N_seq` to 128 ->
  `64x` less attention cost than naive concatenation.

## Self-Check Questions

1. Compute patch count and flattened dim for `336x336`, `P = 14`.
2. Derive `dL/dz_i` from `L_i = -log p_ii`.
3. Why does `tau = 0.02` with `N = 256` risk instability, and what is the fix?
4. Solve for `alpha` to fit `B = 256` tokens on a `2000x1000` image with `P = 14`.
5. Compute `IoU` for two boxes `[0,0,10,10]` and `[5,5,15,15]`.