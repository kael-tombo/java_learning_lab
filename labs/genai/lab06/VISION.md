# Lab 06: Fine-Tuning with LoRA/QLoRA — Vision

## Memory Comparison: Full FT vs LoRA vs QLoRA (7B)

```
FULL FINE-TUNING (bf16 weights, fp32 Adam)
  weights         7e9 * 2 B  ================ 14.0 GB
  gradients       7e9 * 2 B  ================ 14.0 GB
  Adam m, v       7e9 * 8 B  ============================ 56.0 GB
  activations     (grad ckpt) .................... 1.5 GB
  ---------------------------------------------------------------
  TOTAL                                                       ~85.5 GB   > 80GB A100

LoRA (bf16 base)
  weights  (frozen) 7e9 * 2 B  ============ 14.0 GB
  LoRA params      20e6 * 2 B  = 0.04 GB
  grads            20e6 * 2 B  = 0.04 GB
  Adam m, v        20e6 * 8 B  ======== 0.16 GB
  activations      (grad ckpt) .......... 1.5 GB
  ---------------------------------------------------------------
  TOTAL                                                       ~15.7 GB   fits 24GB

QLoRA (4-bit NF4 base)
  weights  7e9 * 0.5 B  ===== 3.50 GB
  scales   (blocks 64)           0.22 GB
  scale-quant (dq)               0.03 GB
  LoRA grads + Adam             0.20 GB
  activations                    1.50 GB
  ---------------------------------------------------------------
  TOTAL                                                        ~5.5 GB   fits 8-12GB
```

## Where LoRA Sits in the Weights

```
                 W_q [d x d]              W_mlp [4d x d]
  frozen  W0  ===================    ==========================
                   |                            |
  trainable   A [r x d]  B [d x r]   A [r x d]  B [4d x r]
              (r=16)                 (r=16)
                   |                            |
  effective  W = W0 + s*B*A ============== W0 + s*B*A
              |<---- full matrix ---->|  |<--- full matrix --->|

  trainable params:  r(d + d) = 2*r*d          vs   r(d + 4d) = 5*r*d
  for d=4096, r=16:  131k                     vs   327k

  NOT trained: embeddings, LM head, layer norms (unless you say otherwise)
```

## Initialization and First Step

```
step 0:   A = random(16 x d)      B = 0 (16 -> d)

  W = W0 + s * B A = W0 + s * 0 = W0        <-- IDENTICAL to pretrained

gradients:
  dL/dB = s * dY^T (X A^T)      = NONZERO   -> B moves on step 1
  dL/dA = s * B^T dY X          = 0         -> A frozen on step 1, active from step 2

step 1:   B != 0, A unchanged
step 2:   both move

if you instead initialize B randomly:
  W(0) = W0 + random perturbation   -> loss starts ABOVE base model
  this is the #1 cause of "my LoRA run is worse than no fine-tuning"
```

## Rank Sweep Shape

```
validation loss
  ^
  |  *
  |     *
  |        *------
  |              *--------
  |                      *------
  +---------------------------------> rank r
     1    2   4   8  16  32  64

  most of the gain arrives by r = 4..8;
  r = 64 costs 4x the parameters of r = 16 for ~1% improvement
  measure the singular spectrum before paying for rank
```

## Quantization: Uniform vs NF4

```
standard normal density
  ^
  |            /\
  |          /    \
  |        /        \
  |      /            \
  |    /                \
  +--|---|---|---|---|---|--> value
    -4  -2   0   2   4

UNIFORM 4-bit (equal spacing)      NF4 (normal quantiles)
 |---|---|---|---|               |..|.||.|.|.||.|.||.|.|
 wastes levels in the tails       dense where the density is high
 -> high MSE on typical weights   -> ~2-3x lower MSE
```

## QLoRA Block Structure

```
weights tensor (row-major)

  block 0              block 1              block 2
  [64 int4 codes]  |   [64 int4 codes]  |   [64 int4 codes]  ...
       |
       +-- scale[0] (fp16, 2 bytes)
  scale tensor: [s0, s1, s2, ...]
       |
       +-- double-quantized: q2[i] (int8) * second_scale (fp16)
           saves 1 byte per 64 weights, and again per 256 blocks

bytes/element = 0.5 (codes) + 2/64 (scales) + 1/256/8 (scale-quant) ~= 0.535
7B -> 3.75 GB of weights
```

## Adapter Serving: One Base, Many Adapters

```
            +---------------------------+
            |  base model (bf16, 14GB)  |  loaded ONCE
            +-------------+-------------+
                          |
     +------------+-------+-------+------------+
     |            |               |            |
  +--v-----+  +---v-----+   +-----v----+  +----v-----+
  |adpt A  |  |adpt B  |   |adpt C    |  | no adapter|
  | r=16   |  | r=8    |   | r=32     |  | (base)    |
  | 40 MB  |  | 20 MB  |   | 80 MB    |  | 0 MB      |
  +--------+  +--------+   +----------+  +----------+
     tenant1      tenant2       tenant3     generic

  memory: 14 GB + 140 MB  for 3 tenants
  vs merging per tenant:  3 x 14 GB = 42 GB      <-- never do this
  rollback: swap adapter, instant
```

## Merge vs Runtime Adapter Path

```
RUNTIME PATH (unmerged)              MERGED
  y = W0 x + s B A x                  y = (W0 + s B A) x
  latency: base matmul + r-rank       latency: one matmul (faster)
            overhead (~2-5%)           memory: adapter not needed
  memory: base + adapter               but merging costs d*d per module
  swap: load A,B (fast)                swapping = re-merge (slow)

  use merged for single-adapter deployments
  use runtime path for multi-tenant
```

## Training Loop Anatomy

```
  batch of chat examples
        |
        v
  tokenize -> ids[] with prompt tokens masked to -100
        |
        v
  forward through FROZEN base
  collect activations only where LoRA modules sit
        |
        v
  loss on unmasked assistant positions only
        |
        v
  backward: grads flow to A and B only
        |
        v
  grad clip by global norm (max 1.0)
        |
        v
  AdamW step, decay excluded for B
        |
        v
  every N steps: eval on held-out, log loss + exact match
        |
        v
  save adapter (small!) -- never the base model
```

## Failure Symptom Map

```
symptom                          | likely cause
---------------------------------+----------------------------------
loss > base model at step 0      | B initialized randomly
adapter has no effect            | not merged / scaling mismatch
output copies the input          | prompt tokens not masked in loss
dL/dA stays zero forever         | B frozen by accident (or weight decay)
quality plateaus at r=1 too      | targets missing MLP modules
blows up after 50 steps          | LR too high, no grad clipping
degrades unrelated tasks         | overfit small set; missing KL term
good fit, bad generation         | LoRA-only capacity: try full FT
```

## Self-Check

- [ ] `B = 0` at init, verified numerically.
- [ ] Rank sweep run before committing to a large `r`.
- [ ] Memory plan computed before picking a device.
- [ ] Prompt masking unit-tested both directions.
- [ ] Adapter saved; base model never duplicated per adapter.