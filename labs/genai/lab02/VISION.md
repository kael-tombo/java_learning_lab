# Lab 02: GPT Architecture — Vision

## The Decoder-Only Block

```
                     x  [T x d]
                          |
              +-----------+-----------+
              |                       |
        (1) RMSNorm              (2) Causal Self-Attention
        LayerNorm(x)             Q = xWq   K = xWk   V = xWv
              |                       |    scores = QK^T / sqrt(d_k)
              |                       |    scores += causal mask (-inf above diag)
              |                       |    weights = softmax_row(scores)
              |                       |    out = weights V  -> concat heads -> W_o
              |                       |
              +-----------+-----------+
                          |  residual add
              +-----------+-----------+
              |                       |
        (3) RMSNorm              (4) SwiGLU MLP
        LayerNorm(x)             down( silu(gate(x)) * up(x) )
              |                       |
              +-----------+-----------+
                          |  residual add
                          v
                    x  [T x d]
```

## Prefill vs Decode — Same Block, Different Regimes

```
PREFILL (prompt = 500 tokens)              DECODE (1 token at a time)
----------------------                     ----------------------------
x = [500 x d]                               x = [1 x d]
Q,K,V = [500 x d]                           Q = [1 x d]        <- new only
scores = [500 x 500]  <-- big               K,V = [500 x d]    <- from CACHE
mask = [500 x 500]                          scores = [1 x 500] <- tiny
compute bound                              memory-bandwidth bound
one pass, high parallelism                  sequential, batch to amortize
writes 500 KV entries                       writes 1 KV entry
```

## KV Cache Visual

```
step 1   prompt: [BOS  the  cat  sat]
         cache:  [k1  k2   k3   k4 ]     <-- filled during prefill
         write:  k5

step 2   token:  [ on ]
         read:   k1 k2 k3 k4 k5   (no recompute)
         scores:  [1 x 6]
         write:  k6

step 3   token:  [ the ]
         read:   k1 ... k6
         write:  k7

Without cache each step would recompute k1..kn from scratch:
step 3 cost = 4 rows of QKV vs 1 row.
```

## Tokenization: Bytes to Merges

```
raw text   "low lower lowest"
bytes      l o w _ l o w e r _ l o w e s t
merge 1    (l,o)->ĺ        l ĺ w _ l ĺ w e r _ l ĺ w e s t
merge 2    (ĺ,w)->ĺw       l ĺw _ l ĺw e r _ l ĺw e s t
merge 3    (l,ĺw)->ĺẃ      ĺẃ _ ĺw e r _ ĺẃ e s t
...
decode     reverse the merges, exactly restores the original bytes
```

## Sampling Landscape (same logits, three configs)

```
logits:  [3.0, 2.4, 1.8, 1.2, 0.6]
probs:   [.318, .220, .121, .066, .033] (plus tail mass)

temperature=0.1 -> one token ~always
  [.9998, .0002, ~0 ...]

temperature=1.0 -> sample from full distribution

top-k=2, top-p=0.9 -> keep the first two, renormalize
  [.591, .409, 0, 0, 0]

Ladder: greedy -> top-p -> top-k -> temperature (each adds randomness back)
```

## Where the Parameters Live (d = 4096, 32 layers, 32 heads)

```
per layer:   Attention  4 * d^2       =  67.1 M
             MLP (SwiGLU) 8 * d^2      = 134.2 M
             => attention is 1/3 of non-embedding params

embeddings:  V * d = 50000 * 4096     = 204.8 M  (tied with lm_head)
total params ~ 32 * 201 M + 205 M     ~ 6.6 B
```

## Scaling Picture

```
loss
 |  \  small data (underfit)
 |   \
 |    \___
 |        \______  large data (better)
 |               \______  large data + big model (best)
 +-------------------------------> params (log scale)

rule of thumb: N and D should scale together at fixed compute
```

## Checklist

- [ ] Mask added before softmax, not after.
- [ ] Inputs/targets offset by one.
- [ ] KV cache present during decode.
- [ ] Padded targets excluded from the loss mean.
- [ ] Sampling parameters (seed, temp, k, p) recorded with results.