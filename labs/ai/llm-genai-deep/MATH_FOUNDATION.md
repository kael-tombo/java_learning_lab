# llm-genai-deep — Math Foundation

## 1. Word2Vec Objective

Skip-gram maximizes

```
log P(w_o | w_c) = log sigma( u_wc' v_wo ) + sum_{k=1..K} E_{w_k ~ P_n(w_c)} log sigma( -u_wc' v_wk )
```

CBOW swaps the roles: predict the center from a bag of context words.

With negative sampling `K` negatives from the unigram distribution raised to power `3/4`
(`P_n(w) ~ count(w)^{3/4}`, which down-weights frequent words), the objective approximates
the full softmax.

**Why the `3/4` exponent**: it is a compromise between the unigram distribution (which
over-samples frequent words) and the uniform one (which over-samples rare words). Empirically
it best matches the true distribution of similarity.

Cost: `O(|V| * d)` parameters. At `|V| = 10^5, d = 300` that is 30M parameters per table,
60M with both — which is why static embeddings are replaced by contextual encoders.

## 2. The Bi-Encoder Retrieval Bound

A bi-encoder scores `s(q, d) = f(q)' g(d)`. Because `f` and `g` are independent, the
maximum achievable recall over a corpus is limited by the expressiveness of the inner
product — a bilinear form cannot represent arbitrary matching functions.

Formally: for any `q, d`, `f(q)'g(d) = sum_k (e_k'f(q))(e_k'g(d))` for an orthonormal basis
`{e_k}`. The score is a **sum of products of independent projections**, so interactions are
additive in projection space rather than conditional.

A cross-encoder computes `s(q,d) = h([q; d])` — a function of the pair, so it can condition.
This is the mathematical reason for the retrieve-then-rerank architecture, not an
engineering convenience.

## 3. Recall@k, MRR, NDCG

```
Recall@k  = |Rel ∩ Top_k| / |Rel|
MRR       = (1/|Q|) sum_q 1 / rank_q(first relevant)
NDCG@k    = DCG@k / IDCG@k
DCG@k     = sum_{i=1..k} rel_i / log2(i + 1)
IDCG@k    = sum_{i=1..k} sorted_rel_i / log2(i + 1)
```

`log2(i+1)` (rather than `i`) keeps the first position finite. The `1/4` discount weight at
rank 2 versus `1/2` at rank 1 encodes "a relevant result at rank 2 is worth much less than
at rank 1" — an empirical property of search behaviour, not a mathematical necessity.

**Recall@k against a small `|Rel|`**: if there are 2 relevant documents and `k = 5`,
recall takes values in `{0, 0.5, 1}` only. A 5% recall difference on a 2-relevant query set
of 100 queries is 10 queries — which is why confidence intervals matter on retrieval metrics.

## 4. Vector Search: Recall Versus Latency

For ANN search, a useful bound: with graph degree `M`, HNSW search is approximately
`O(log(N) * M)` distance computations. `efSearch` multiplies the layer-0 beam.

| Method | Build | Query | Query-time knob |
|--------|-------|-------|-----------------|
| Flat | O(Nd) | O(Nd) | none |
| LSH | O(Nd) | O(N^(1/c)) | tables, `b` |
| IVF | O(Nd) | O(nprobe * N/nlist * d) | `nprobe` |
| HNSW | O(N log M) | ~O(log N * M) | `efSearch` |

Worked: `N = 1e6, d = 768`. Flat search at 10 qps needs `1e6 * 768 = 7.68e8` distances per
query, ~0.77 s single-threaded. HNSW with `M=16, efSearch=64` needs roughly
`20 * 16 * 2 = 640` distances, ~0.64 ms — a 1000x reduction with `recall@10` typically
0.95-0.99.

## 5. BLEU

```
BLEU-n = BP * exp( (1/n) sum_{k=1..n} p_k )
p_k    = clipped n-gram precision
BP     = 1 if c > r else exp(1 - r/c)
```

Clipping caps each candidate n-gram count at the reference count, which is what prevents
rewarding repetition. The brevity penalty is exponential because under-generation is far
more damaging than over-generation for translation.

Weaknesses that matter for RAG: corpus-level (not per-sentence) aggregation, insensitivity
to paraphrase (a correct paraphrase scores 0), and n-gram overlap rewarding copying.

## 6. ROUGE-L and LCS

```
ROUGE-L = LCS-based F-measure over the token sequence
LCS-recall    = LCS / len(reference)
LCS-precision = LCS / len(candidate)
F             = 2PR / (P + R)
```

Recall-oriented (the recall variant was the original), which makes it easy to score highly
by emitting many tokens. For a generative system, high ROUGE-L with low factuality is a
common and misleading outcome — which is why faithfulness needs its own metric.

## 7. LoRA Parameter Count and Gradient Flow

```
W' = W + delta W,   delta W = B A,   A in R^{r x d_in},  B in R^{d_out x r}
trainable = r*(d_in + d_out)
```

For `d_in = d_out = 4096, r = 8`: `8 * 8192 = 65,536` versus `4096^2 = 16,777,216` — **256x**
fewer trainable parameters.

Gradient flows to `A` and `B` but not to `W`:

```
dL/dB = delta * A',   dL/dA = B' * delta,   dL/dW = 0 (frozen)
```

Initialization `A = 0, B ~ small` makes `delta W = 0` exactly at step 0, so the adapted model
starts identical to the base. `A ~ random, B = 0` also works; the asymmetry only matters for
which tensor receives gradient immediately.

Memory for the optimizer state drops proportionally: Adam stores 2 floats per trainable
parameter, so full fine-tuning of 7B in FP32 with Adam needs `7e9 * (4 weights + 4 grad +
4 m + 4 v) = 112 GB`. QLoRA moves the frozen base to 4 bits (3.5 GB) and keeps only the
adapters in full precision.

## 8. QLoRA Quantization Error

NF4 places quantiles of the standard normal into the 16 bins of the 4-bit grid:

```
quantile i/16 of N(0,1), for i = 0..15
```

which minimizes expected squared error for normally distributed weights. Blockscale `s` per
64-element block: `s = max|x| / 8`; quantized value `q = round(x/s) in [-8, 7]`.

Expected error per weight:

```
E[(x - dequant(q))^2] = s^2 / 12 * E[residual^2] / E[(x/s)^2]
```

For a Gaussian with `max|x| ~ 3.5 sigma` over a 64-block: `s = 3.5 sigma / 8 = 0.4375 sigma`,
so the maximum error is `s/2 = 0.219 sigma` and the mean squared error is roughly
`0.03 sigma^2` — a relative error around 17% per weight, but accumulated over thousands of
weights the errors partially cancel, which is why the practical quality loss is small.

Double quantization quantizes the block scales themselves to 8 bits: `d = |V| / 64` blocks
times 4 bytes becomes 1 byte, saving `0.375 GB` on a 7B model.

## 9. DPO Derivation

Start with the reward-maximizing policy under a KL constraint to a reference `pi_ref`:

```
max_pi  E_pi[r(x,y)] - beta * KL( pi || pi_ref )

solution:  pi*(y|x) = pi_ref(y|x) * exp( r(x,y) / beta ) / Z(x)
```

Invert for the reward:

```
r(x,y) = beta * log( pi*(y|x) / pi_ref(y|x) ) + beta * log Z(x)
```

Substituting into the Bradley-Terry preference likelihood
`P(y_w > y_l) = sigma( r(x,y_w) - r(x,y_l) )` and cancelling the `log Z(x)` terms:

```
L_DPO = -log sigma( beta * ( log pi(y_w|x)/pi_ref(y_w|x) - log pi(y_l|x)/pi_ref(y_l|x) ) )
```

Everything the RLHF pipeline needs — the reward model, the value function, the RL loop —
disappears because the reference-model log-ratios **parameterize the reward implicitly**.

Two practical consequences:

1. **`beta` is a KL controller in disguise.** Small `beta` means the implicit reward scale is
   large relative to the log-ratio, so the loss pushes harder. `beta` in 0.05-0.5 is typical.
2. **DPO needs off-policy preference data.** The log-ratios are relative to `pi_ref`, not to
   the current policy, which is what makes it stable.

## 10. Reward Over-Optimization

Let the true reward be `r_true` and the learned one `r_hat`. `r_hat` is trained on
`pi_ref`'s samples, so its error grows as the policy moves:

```
pi_theta  ->  regions where r_hat is extrapolating  ->  r_hat increases
          ->  but r_true decreases there
```

Empirically the reward-model score is monotonically increasing in optimization steps while
held-out human preference peaks and then declines. Two mitigations, both necessary:

- **KL penalty** (`beta` in PPO, or DPO's implicit `beta`) constrains distance from `pi_ref`.
- **Periodic human evaluation** on a fixed prompt set. The reward model cannot detect its own
  over-optimization; humans can, at a cost.

The measurable symptom to watch for: reward up, KL up, human preference down.

## 11. Context Position ("Lost in the Middle")

For a needle in a haystack test with `k` retrieved documents, accuracy as a function of the
needle's position is **U-shaped**:

```
accuracy
   ^        *                    *
   |      *   *                *   *
   |    *       *            *       *
   |  *           *        *           *
   +--------------------------------------> position in context
   beginning                        end
```

Mechanism: attention receives more weight from the first and last tokens, because those
positions have attended to more tokens in the causal prefix and because the final token's
representation directly influences every subsequent prediction.

Practical consequence: put the highest-relevance passage **at the end** of the context (or
duplicated at both ends). Measure it on your own distribution rather than assuming.

## 12. Precision Under a Low Base Rate

```
precision = TPR * pi / (TPR * pi + FPR * (1 - pi))
```

| `pi` | TPR 0.95, FPR 0.01 → precision |
|------|---------------------------------|
| 0.50 | 0.989 |
| 0.10 | 0.909 |
| 0.02 | 0.660 |
| 0.005 | 0.324 |
| 0.001 | 0.087 |

At a 0.1% disallowed rate, **91% of flags are wrong**. Every false flag costs a human
review, so the true harm is `FPR * (1-pi)` reviews, which is enormous.

Two-stage design:

```
stage 1: cheap, high recall    blocks 95% of harmful, 5% of benign    cost C1
stage 2: precise classifier    on the surviving 5%                    cost C2

cost per request = C1 + 0.05 * C2
```

With `C1 = 2e-5`, `C2 = 4e-4`: `$4e-5` versus `$4e-4` — 10x cheaper, and false refusals
drop from `0.999 * 0.004 = 4e-3` to `0.05 * 0.999 * 0.004 = 2e-4`, a 20x reduction.

## 13. Error Compounding in Agent Loops

An `n`-step task with per-step success probability `p`:

```
P(success) = p^n
```

| steps | p=0.99 | p=0.95 | p=0.90 |
|-------|--------|--------|--------|
| 5 | 0.951 | 0.774 | 0.590 |
| 10 | 0.904 | 0.599 | 0.349 |
| 20 | 0.818 | 0.358 | 0.122 |

This is the arithmetic behind three design rules:

1. **Fewer steps beats better steps**, because the exponent punishes length.
2. **Per-step reliability must be very high** — 99% is not enough for a 20-step task.
3. **Independent verification of the final result** is worth more than improving any single
   step, because it changes the exponent structure from `p^n` to `p^(n-1) + (1 - p^(n-1)) * q`
   where `q` is the verification accuracy.

At `p = 0.95, n = 10, q = 0.9`: naive `0.599`; with verification `0.401 + 0.599 * 0.9 =
0.939`. A 57% improvement from one extra step.

## 14. Abstention Frontier

With an abstention option, define:

```
coverage  = fraction of queries answered (not abstained)
accuracy  = correct / answered
```

Abstention trades coverage for accuracy monotonically: abstaining more raises accuracy and
lowers coverage. The operating point is a business decision — a support system with 95%
coverage at 88% accuracy usually beats 70% coverage at 96% accuracy, because the 25% of
users who get nothing abandon.

Report both numbers always. Reporting accuracy alone hides a system that answers 12% of
questions and is very accurate on those.

## Worked Numbers

- **LoRA**: `d = 4096, r = 8` → `8 * 8192 = 65,536` trainable versus `16,777,216`. Ratio
  256x. On a 7B model with 32 layers at `d = 4096`, full fine-tuning trains ~6.7B
  parameters; LoRA at `r=8` trains `32 * 4 * 65,536 = 8.4M` — **0.12%**.
- **QLoRA memory**: 7B at NF4 = `7e9 / 2 = 3.5 GB` (plus block scales). Adapters `8.4M` at
  FP32 with Adam: `8.4e6 * 16 = 134 MB`. Activations dominate what remains. Full fine-tuning
  with Adam would need `112 GB`, so QLoRA is the difference between one 48 GB GPU and eight.
- **NF4 error**: for `w ~ N(0, sigma^2)` with `sigma = 0.02`, 64-block, `max|w| ~ 3.5 sigma =
  0.07`, `s = 0.07/8 = 0.00875`. Max error `s/2 = 0.0044`, i.e. 22% of `sigma`. Uniform 4-bit
  with the same range has the same `s`; NF4's advantage shows in the *distribution* of
  error — small weights near zero get finer bins, which uniform wastes. Measured MSE for NF4
  is typically 15-25% below uniform RTN.
- **DPO loss**: `beta = 0.1`, chosen log-ratio `2.0`, rejected `0.5`.
  `margin = 0.1 * (2.0 - 0.5) = 0.15`. `L = -log sigma(0.15) = -log(0.5374) = 0.621`.
  With `beta = 1.0`: `margin = 1.5`, `L = -log sigma(1.5) = 0.371`. Smaller `beta` means a
  weaker gradient signal on the same preference — which is why `beta = 0.1` under-trains and
  `beta = 1.0` can destabilize.
- **Retrieval ablation** (1000 queries, 1 relevant document each): no rerank recall@10 = 0.82,
  after bi-encoder rerank 0.88, after cross-encoder rerank 0.94. Latency 120 ms → 340 ms →
  1.9 s. The accuracy/latency curve is the actual decision, not the top number.
- **Chunking ablation**: fixed 256 with no overlap recall@5 = 0.71; fixed 256 with 15%
  overlap 0.79; semantic 0.83; structural 0.87. The split-fact cases are exactly what overlap
  recovers.
- **Position**: 8 retrieved documents, answer in one. Accuracy with the answer at document
  1: 0.91; document 4: 0.72; document 8: 0.84. Duplicating the answer passage at both ends:
  0.93.
- **Self-consistency**: single sample 0.62; 5 samples majority vote 0.78. At 5x cost,
  break-even against a 1.6x better single model is roughly `0.78/0.62 = 1.26` accuracy per
  unit cost.
- **Chain-of-verification**: faithfulness 0.81 → 0.93 at 2.1x cost.
- **Abstention frontier**: always-answer 0.81 accuracy at 100% coverage; with abstention at
  95% coverage 0.88; at 85% coverage 0.93. Report all three.
- **Base rate**: 1M requests/day, 0.5% disallowed, TPR 0.97, FPR 0.004. Harmful reaching
  users `5000 * 0.03 = 150/day`. Benign refused `995000 * 0.004 = 3980/day`. Precision
  `4850/8830 = 0.549` — over half the refusals are wrong. Two-stage drops false refusals to
  `200/day`, a 20x improvement.
- **Agent compounding**: 12-step task at `p = 0.97` → `0.97^12 = 0.694`. Adding one
  verification step at `q = 0.95`: `0.694 * 0.95 + (1 - 0.694) * 0.95 = 0.95`... more
  precisely, if verification catches 95% of failures: `0.694 + 0.306 * 0.95 * 0.9 = 0.956`.
  One added step takes 69.4% to 95.6%.

## Self-Check Questions

1. Compute the LoRA parameter ratio for `d = 4096, r = 16`.
2. Compute the DPO loss for `beta = 0.1`, chosen log-ratio 1.2, rejected 0.4.
3. Compute precision at `pi = 0.005`, TPR 0.95, FPR 0.01.
4. Compute end-to-end agent success for a 15-step task at `p = 0.98`, and with one
   verification step at `q = 0.9`.
5. Compute NDCG@3 for relevance `[3, 0, 2]` retrieved against ideal `[3, 2, 0]`.
6. Compute the expected number of accepted draft tokens for speculative retrieval
   re-ranking at acceptance 0.7, draft size 4.
7. Compute KV cache bytes per token for a 40-layer, 32-head, `d_head=128` model in INT8, and
   the GQA-8 equivalent.
8. Compute NF4 mean squared quantization error relative to `sigma` for a Gaussian weight
   distribution with a 64-element block.
9. Compute the two-stage filtering cost per request for `C1 = 1e-5`, `C2 = 3e-4`, stage-1
   pass rate 5%.
10. Compute the accuracy/coverage trade for an abstaining system at two thresholds.
11. Explain why the position of the retrieved passage matters, using attention weights.
12. Compute BLEU-4 for a candidate with clipped precisions `(0.5, 0.4, 0.3, 0.2)`, candidate
    length 12, reference length 15.
