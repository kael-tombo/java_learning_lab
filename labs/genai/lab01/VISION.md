# Lab 01: Transformer Architecture — Vision

## The Transformer Block Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    ENCODER (× N)                         │
│                                                         │
│  Input Embeddings + Positional Encoding                  │
│         │                                               │
│         ▼                                               │
│  ┌──────────────────────┐                               │
│  │  Multi-Head Attention │ ◄── Q, K, V all from input   │
│  └──────────┬───────────┘                               │
│             │                                           │
│         Add & Norm (residual + layer norm)               │
│             │                                           │
│             ▼                                           │
│  ┌──────────────────────┐                               │
│  │  Feed-Forward Network │ ◄── position-wise MLP        │
│  └──────────┬───────────┘                               │
│             │                                           │
│         Add & Norm                                       │
│             │                                           │
│             ▼                                           │
│        Memory ──────────────────────────────┐           │
└─────────────────────────────────────────────┼───────────┘
                                              │
┌─────────────────────────────────────────────┼───────────┐
│                    DECODER (× N)             │           │
│                                             │           │
│  Output Embeddings + Positional Encoding    │           │
│         │                                   │           │
│         ▼                                   │           │
│  ┌──────────────────────┐                   │           │
│  │ Masked Multi-Head Attn│ ◄── causal mask  │           │
│  └──────────┬───────────┘                   │           │
│             │                               │           │
│         Add & Norm                           │           │
│             │                               │           │
│             ▼                               │           │
│  ┌──────────────────────┐                   │           │
│  │   Cross-Attention     │ ◄── Q: decoder    │           │
│  │                       │    K,V: memory ──┘           │
│  └──────────┬───────────┘                               │
│             │                                           │
│         Add & Norm                                       │
│             │                                           │
│             ▼                                           │
│  ┌──────────────────────┐                               │
│  │  Feed-Forward Network │                               │
│  └──────────┬───────────┘                               │
│             │                                           │
│         Add & Norm                                       │
│             │                                           │
│             ▼                                           │
│        Linear + Softmax ──► Output Probabilities         │
└─────────────────────────────────────────────────────────┘
```

## Attention Visualization

```
Query: "it" (position 5)
Keys:  "The cat sat on the mat because it was tired"

Attention weights (hypothetical):

  The   cat   sat   on   the   mat  because   it   was  tired
 0.02  0.01  0.01  0.01  0.02  0.05   0.03   0.78  0.04  0.03
                                              ▲
                                         "it" attends strongly to "it"
                                         (resolving coreference)
```

## Multi-Head Attention Pattern

```
Head 1: syntactic relationships (subject → verb)
Head 2: positional relationships (adjacent tokens)
Head 3: semantic relationships (synonyms)
Head 4: coreference (pronouns → nouns)
...
Head 8: long-range dependencies

Each head produces its own attention map → concatenated → projected
```

## Causal Mask Visualization

```
        t0   t1   t2   t3   t4
t0  [  0   -∞   -∞   -∞   -∞  ]
t1  [  0    0   -∞   -∞   -∞  ]
t2  [  0    0    0   -∞   -∞  ]
t3  [  0    0    0    0   -∞  ]
t4  [  0    0    0    0    0  ]

Each position can only attend to itself and previous positions.
This is what enables autoregressive generation.
```

## Positional Encoding Heatmap (conceptual)

```
dim:  0  1  2  3  4  5  6  7  ...  d
pos0:  0  1  0  1  0  1  0  1
pos1:  s  c  s  c  s  c  s  c     (s=sin, c=cos of increasing angle)
pos2:  s  c  s  c  s  c  s  c
pos3:  s  c  s  c  s  c  s  c
...

Low dimensions: fast oscillation (fine position detail)
High dimensions: slow oscillation (coarse position detail)
Together: unique "fingerprint" for every position
```

## Residual Stream Concept

```
x ─────────────────────────────────────────►
    │                                       │
    ▼                                       │
  Sublayer(x)                               │
    │                                       │
    ▼                                       │
  x + Sublayer(x) ◄─────────────────────────┘
    │
    ▼
  LayerNorm(x + Sublayer(x))

The "residual stream" carries information forward unchanged,
while sub-layers read from and write to it.
```
