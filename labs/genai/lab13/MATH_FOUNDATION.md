# Lab 13: Context Window Management — Math Foundation

## 1. Sinusoidal Encoding

```
PE(pos, 2i)     = sin( pos / 10000^(2i/d) )
PE(pos, 2i + 1) = cos( pos / 10000^(2i/d) )
```

Relative property: writing `omega_i = 10000^(-2i/d)`,

```
PE(pos + k, 2i)   = sin((pos+k) omega_i) = sin(pos omega_i)cos(k omega_i) + cos(pos omega_i)sin(k omega_i)
```

which is exactly `R(k omega_i) * [sin(pos omega_i), cos(pos omega_i)]`. So

```
PE(pos + k) = R_k * PE(pos),   R_k = rotation by k*omega_i in each 2D plane
```

and a dot product between two relative-encoded vectors depends only on the difference.

## 2. RoPE

```
theta_{i,j} = pos * base^(-2j/d)      (per pair of dimensions j, j+d/2)
q'_i = R(theta_i) q_i,  k'_i = R(theta_i) k_i

dot(q'_i, k'_j) = sum_p dot(R(theta_p) q_i, R(theta_p') k_j)
```

Because rotation preserves norms and the sum telescopes into a function of `theta_i -
theta_j`, the attention score depends only on `i - j` when the two vectors come from
the same rotation family. Concretely for the 2D case:

```
dot(R(a)u, R(b)v) = u_R . v_R  where R(a) = [[cos a, -sin a],[sin a, cos a]]
```

so the score is a relative function.

Base controls the longest wavelength: dimension `j = 0` has `omega = 1`, so the
period is `2*pi`. Increasing `base` to 1e6 gives `omega_0 = 1`, `omega_{d/2-1} =
1e-6`, so low frequencies stretch across the full range.

## 3. ALiBi

```
score(i, j) = q_i . k_j / sqrt(d) - m_h * (i - j),     j <= i
```

With `m_h = 2^(-8h/H)` for head `h` in `H` heads, slopes are geometrically spaced
from 1 down to about `2^-8 = 0.004`. Sum over head types:

```
P_local(i,j) ∝ sum_h exp( q.k/sqrt(d) - m_h (i-j) )
             = sum_h exp(-m_h |i-j|) * exp(q.k/sqrt(d))
```

so the effective distance prior is a mixture of exponentials over distances — a
soft, multi-scale locality prior. No parameters, no position vectors, and distance
decays monotonically so extrapolation to unseen distances is smooth.

## 4. Attention Entropy as a Diagnostic

For a row of scores `s` with softmax `p`:

```
H(p) = -sum_k p_k log p_k,    0 <= H <= log K
```

For ideal behavior `H ≈ log(n_valid)`. Under extrapolation failure, the score scale
is wrong and:

```
case A (peaked):  s inflated  -> p_k -> one-hot     -> H -> 0
case B (flat):    s deflated  -> p_k ~ uniform      -> H -> log K, no discrimination
```

Either way, the model loses the ability to select, and accuracy falls off a cliff
rather than a slope. `H/log K` normalized against the valid-key count is a cheap
early-warning metric — worth logging in any long-context system.

## 5. Position Interpolation

Original max position `L`. To support `N = s*L`:

```
interpolation:  pos' = pos / s        (then add offset for RoPE's 1-index)
extrapolation:  pos' = pos            (out of distribution)
NTK scaling:    base' = base * s^(d/(d-2))
```

Interpolation compresses positions into `[0, L]`, so resolution per position drops by
`s`. Without fine-tuning that hurts even *inside* the trained window, because nearby
positions are now harder to distinguish. With fine-tuning on interpolated positions,
the model recovers.

Interpolation vs extrapolation perplexity (illustrative, relative to the trained-window
baseline):

```
position       unscaled    interpolated   NTK-scaled
L              1.00        1.02           1.01
2L             2.10        1.15           1.06
4L             8.40        1.35           1.12
8L             31.0        4.20           2.40
```

## 6. Sliding Window Cost

```
full attention:   sum_i i = N(N+1)/2            -> O(N^2)
windowed (W):     sum_i min(i+1, W) ≈ N*W - W^2/2 -> O(N*W)
```

For `N = 8*W`: full `= 64*W^2/2 = 32 W^2`; windowed `≈ 7.5 W^2`. Ratio ≈ `4.3x` fewer
score computations. For `N = 32*W`: full `≈ 512 W^2`, windowed `≈ 31.5 W^2` -> `16x`.

## 7. Attention Sink Mechanism

Without sinks, in a windowed model the earliest tokens in each window have fewer than
`W` predecessors, so their softmax has fewer candidates — but the deeper problem is
that with a fixed `W`, the *total* attention mass available is constant and there is
no position for the model to "dump" unavoidable attention. Attention entropy
collapses. Empirically, reserving 4 sink positions at the start keeps entropy stable
and preserves accuracy; sink tokens frequently receive large attention weights
precisely because they absorb this pressure.

## 8. KV Cache Bytes

```
bytes = 2 * L * H_kv * d_head * S * B * bytes_per_elem
```

Worked example (32 layers, 32 query heads, 8 KV heads, d_head 128, S = 32768,
B = 8, fp16):

```
MHA: 2*32*32*128*32768*8*2 = 137 GB
GQA(8):                                             34.3 GB   (4x less)
GQA(8) + INT8 cache:                                 17.2 GB
GQA(8) + INT8 + sliding W=4096:                       2.1 GB
GQA(8) + INT8 + sliding W=4096 + batch 2:            0.54 GB
```

Multiplicative levers compose. Note that at 32k context the cache is ~5x the weight
memory in fp16 — long context is a memory problem before it is a compute problem.

## 9. Prefill Attention FLOPs

Per layer:

```
attention: 2 * 2 * S^2 * d   (QK^T then AV)     ~ 4 S^2 d
FFN:       2 * 2 * S * d * 4d                 ~ 16 S d^2
```

Ratio attention:FFN `= S/(4d)`. At `S = 2048, d = 4096`: `0.125` — FFN dominates.
At `S = 32768, d = 4096`: `2.0` — attention dominates. Crossover is `S = 4d`.

Practical implication: below `4d` tokens, prefill cost is roughly linear in `S`
(anyway, chunks work fine); above it, prefill becomes quadratically expensive and
long-context requests need their own lane.

## 10. TTFT Scaling

```
TTFT(S) ≈ a*S (FFN, linear) + b*S^2 (attention)
```

With crossover at `S* = 4d`, TTFT has an inflection at `S*`. Empirically for a 70B
class model: 1k ~ 0.3 s, 4k ~ 0.9 s, 16k ~ 5 s, 64k ~ 70 s. The jump from 16k to 64k
is where prefill attention and memory pressure both bite.

## 11. Compression Ratio and Utility

```
compression_ratio = T_orig / T_comp
token_reduction   = 1 - T_comp / T_orig
utility(comp)     = quality(comp) / T_comp        (quality per token)
```

Choosing a compression operating point maximizes utility subject to a quality floor:

```
maximize quality(c)/T(c)   subject to   quality(c) >= quality_orig - delta
```

If quality falls faster than tokens drop, compression is counterproductive even
before it hurts quality.

## 12. Map-Reduce Cost

For `D` documents, per document `t` tokens:

```
stuff:        cost = D*t input tokens, attention O((D*t)^2 d)
map-reduce:   cost = D*(t + s) where s = summary length
              synthesis: D*s + t' output tokens
```

With `s = t/10`, map-reduce input is `D*1.1t` — comparable to stuffing — but the
synthesis stage operates on `D*s = 0.1 D t` tokens instead of `D t`, so the *second*
stage's attention cost drops by 100x. Net: map-reduce wins on the quadratic term,
which is the term that dominates at long context.

## 13. Information Density

When documents are stuffed and only one is relevant, the relevant fraction is `1/D`:

```
signal_density = relevant_tokens / total_stuffed_tokens = 1/D
```

For `D = 50`, 2% of the context is relevant. Retrieval replaces that with ~100%
density at 1/50 the tokens. This is the quantitative reason retrieval beats stuffing:
two effects compound — fewer tokens (cost) and higher density (accuracy).

## 14. Eviction Policy Comparison

Under a Zipf-distributed prefix reuse pattern with capacity `C`:

```
LRU:  hit rate ≈ sum_{k<=C} p_k         (p_k = reuse probability of rank-k prefix)
LFU:  hit rate ≈ sum_{k<=C} p_k         (same by the rank-frequency duality)
random: hit rate ≈ C/N
```

For skewed workloads LRU and LFU converge; for **temporal** skew (a prompt template
popular this week, dead next week) LFU with a TTL beats LRU. The practical choice is
**LRU + TTL**, because staleness is the failure mode that matters (stale answers), not
scan resistance.

## Worked Numbers

32 layers, `d_model = 4096`, 32 query heads, 8 KV heads, `d_head = 128`.

1. GQA cache saving: `32/8 = 4x`.
2. INT8 cache: another `2x` -> `8x` total.
3. Sliding `W = 4096` at `S = 32768`: `8x` more -> `64x` total.
   Cache for `B = 8`: `137 GB / 64 = 2.14 GB`. Fits comfortably.
4. Prefill crossover: `S* = 4d = 16384`. Above 16k, attention dominates.
5. Stuffing 50 documents of 1000 tokens: `S = 50000`, density `1/50 = 2%`.
   Retrieval of 2 chunks: `S = 800`, density ~`100%`, 62x fewer tokens.
6. Sliding window savings at `S = 8W`: `4.3x` fewer score computations.

Net effect of items 1-3 and 5 together: a long-context system that fits 30x more
concurrent sessions at 62x lower prompt cost, with better answer quality because
density went from 2% to ~100%.

## Self-Check Questions

1. Prove `dot(R(a)u, R(b)v)` depends only on `a - b` in 2D.
2. Compute normalized attention entropy for a peaked vs uniform row of 16 keys.
3. Derive the prefill attention:FFN crossover and evaluate at `d = 8192`.
4. Compute cache bytes for `B = 32`, `S = 8192`, GQA(8), INT8.
5. Explain why LRU+TTL beats pure LFU on a template-popularity workload.