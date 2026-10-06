# Lab 13: Context Window Management — Theory

## 1. Why Context Is a Managed Resource

The context window is simultaneously the model's memory, its input format, its KV
cache, and your billing unit. Managing it means answering four questions for every
request:

```
1. What goes IN?      (retrieval, history, instructions)
2. What gets DROPPED? (which tokens are least useful)
3. How is ORDER encoded? (position representations)
4. What does it COST? (cache bytes, latency, money)
```

Naive approaches fail in three ways: filling the window with whatever is available,
truncating from the left, and assuming position encodings generalize beyond the
training window.

## 2. Positional Representations

### Sinusoidal (original Transformer)

```
PE(pos, 2i)     = sin(pos / 10000^(2i/d))
PE(pos, 2i + 1) = cos(pos / 10000^(2i/d))
```

Properties: unique per (position, dimension), no learned parameters, and a relative
offset identity:

```
PE(pos + k) = R_k * PE(pos),   R_k a rotation matrix
```

which is why relative attention scores work out. Problem: no evidence of extrapolation
beyond the trained range — the model has never seen those frequencies.

### Learned Absolute Positions

A trainable embedding table per position. Cannot extrapolate at all, and the table
size grows with context.

### ALiBi (Attention with Linear Biases)

No positional vectors. Instead add a linear bias to attention scores:

```
score(i, j) = q_i . k_j / sqrt(d) - m_h * (i - j)      for j <= i
```

with a per-head slope `m_h`, and heads assigned geometrically spaced slopes. Two
consequences:
- Relative distance is encoded directly and linearly, so **extrapolation works** — a
  model trained to 2k works at 4k with modest degradation.
- No positional embedding table, no added compute.

### RoPE (Rotary Position Embedding)

Rotate the query and key vectors by an angle proportional to position:

```
q'_i = R(theta_i) q_i,   k'_j = R(theta_j) k_j,   theta_i = i * base^(-2i'/d)
dot(q'_i, k'_j) depends only on (i - j)
```

Properties: relative position encoded in the attention score, no embedding table,
high quality at the trained length, and extrapolation works well up to ~2-4x the
training window with a mild "sawtooth" degradation beyond that.

The base controls the longest wavelength. Common values: 10,000 (original),
100,000 or 1,000,000 for extended-context models.

## 3. Scaling Laws for Position Extrapolation

| Method | Beyond trained length | Quality cost |
|--------|----------------------|--------------|
| Learned absolute | Fails entirely | Unusable |
| Sinusoidal | Degrades quickly | Sharp drop past ~1.5x |
| ALiBi | Graceful | Mild, gradual |
| RoPE | Good to ~4x | Gradual "sawtooth" |
| RoPE scaling (linear/interp) | Predictable | Small, tunable |
| NTK-aware scaling | Good | Small, non-uniform |
| YaRN | Best | Very small |
| LongRoPE / per-dim scaling | Best | Small, per-dimension tuned |

The interpolation family: divide positions by a factor `s` before encoding, then
optionally fine-tune. At `s = 4`, positions within the trained window are compressed
into a quarter of the range, so resolution drops — fine-tuning recovers it.

NTK-aware scaling changes `base` rather than scaling positions, preserving resolution
at near positions while extending the range. YaRN blends per-dimension NTK scaling
with attention temperature compensation.

## 4. Position Interpolation Failure Mode

At inference, positions must be within the trained range. Two mitigations:

```
extrapolation:  pos_final = pos_raw * base_scale      (LLaMA-style linear)
interpolation:  pos_final = pos_raw * s + offset     (divide then re-scale)
```

The failure mode is not uniform degradation — it is **attention entropy collapse**.
Attention scores are mis-scaled, softmax becomes peaked or flat, and information from
distant tokens is lost or dominates. The empirical signature is a sharp accuracy
cliff, not a gentle slope.

## 5. Sliding Window Attention

Restrict each token to attend only to the previous `W` tokens:

```
attention set(i) = { j : max(0, i-W+1) <= j <= i }
```

Properties:
- KV cache bounded at `W` tokens per sequence regardless of length.
- No information crossing between windows except through the residual stream — so
  long-range dependencies degrade.
- Attention cost is `O(N * W)` instead of `O(N^2)`. For `N = 10 * W`, that is a 10x
  reduction.
- Implementation: a ring buffer of KV entries, or block tables that map the logical
  window to physical memory.

StreamingLLM's insight: if you *do* use attention sinks, keep 4-5 initial tokens as
permanent "attention sink" positions. Without them, sliding-window models collapse —
those first tokens absorb the "I must attend to something" pressure, which keeps
softmax from degenerating.

## 6. KV Cache and Context Memory

```
cache_bytes = 2 * layers * n_kv_heads * head_dim * seq_len * batch * bytes_per_elem
```

Levers, in order of impact:
1. **GQA / MQA** — fewer KV heads (8 vs 32 gives 4x).
2. **Sliding window** — bound `seq_len` to `W`.
3. **KV cache quantization** — INT8/FP8 per head (2x).
4. **Prefix caching** — share blocks across requests with identical prefixes.
5. **Paged attention** — eliminate fragmentation waste (Lab 11).
6. **Early exit / layer skipping** — compute fewer layers for cached entries.

## 7. Context Compression

Reduce tokens *before* they reach the model.

### Token-Level
- Remove filler, whitespace artifacts, repeated boilerplate.
- Merge common patterns into single tokens.

### Sentence-Level
- Keep sentences scoring above a threshold against the query (Lab 12).
- Preserve provenance: the chunk stays in the context so citations work.

### Document-Level
- Hierarchical summarization: per-chunk summary plus full text for the top chunks.
- Extractive then abstractive: keep salient sentences, replace the rest with a summary.

### Latent / Learned Compression
- Train an autoencoder to compress a token sequence into fewer latent tokens that a
  fine-tuned model can still attend to. Powerful, requires training, opaque.
- Token dropping with importance scores, then fine-tune to tolerate the drop.

### Learned Compression Trade-off
```
compression_ratio = original_tokens / compressed_tokens
quality_delta     = quality(compressed) - quality(original)
```
Report both. A 4x compression that costs 5 quality points is a different product than
a 2x compression that costs 0.5.

## 8. Context Ordering

Models weight the beginning and end of context most strongly ("lost in the middle").
Practical layouts:

```
[system + policy]  ...instructions...  [evidence ranked ascending]  [question]
                    ^ most important stuff near the edges
```

- Highest-scoring evidence **last**, nearest the question.
- Repeat the operative instruction at the end (recency).
- Keep the schema adjacent to the instruction that mentions it.
- Do not bury the question under 8k tokens of context; consider placing a short
  question summary at the top too.

## 9. History Management for Chat

Multi-turn sessions blow the window quickly. Strategies:

| Strategy | Keeps | Loses | Use when |
|----------|-------|-------|----------|
| Truncate oldest | recent turns | early context | Cheap, short sessions |
| Sliding window | last k turns | everything older | Long chats, casual |
| Summarize older | summary + recent | detail in old turns | Long chats, factual |
| Retrieve from history | relevant old turns | non-retrieved turns | Long chats, specific recall |
| Structured state | extracted facts/slots | nuance | Agent workflows, bookings |
| Re-ask | fresh question | everything | Statutory forms |

Best practice: combine **structured state extraction** (facts, decisions, open items)
with a **recent window** (verbatim). That combination gets most of the benefit
without the loss.

Never compact the system message or the safety policy (Lab 10).

## 10. Long Context Is Not Free Attention

Claims that "the model can read 200k tokens" usually omit:

- **Prefill cost**: `O(N^2 d)` attention — 128k tokens is ~1000x the attention of 4k.
- **TTFT**: minutes for very long prompts on limited hardware.
- **KV cache**: often more memory than the weights at long context.
- **Cost**: input tokens are billed linearly, so 128k tokens is 32x a 4k request.
- **Retrieval degradation**: accuracy does not scale linearly with context; it
  frequently *degrades* past the point where relevant evidence is buried.

The practical recommendation: **retrieve, do not stuff**. Use long windows as headroom
for multi-document comparison, not as a substitute for retrieval.

## 11. Chunking for Long-Context Reasoning

When a task genuinely needs many documents (legal review, multi-contract comparison):
- **Map-reduce**: summarize each document separately, then synthesize.
- **Hierarchical**: summarize groups, then summarize summaries.
- **Question-first retrieval per document**: ask the specific question of each
  document, then combine answers.
- **Map over long windows with citations**: force grounding per chunk.

These are prompt-and-orchestration patterns, not architecture changes, and they work
with any model.

## 12. Choosing a Strategy

```
question needs 1 fact from a huge corpus?    -> retrieval, short context, long window as headroom
question needs comparison across 20 docs?    -> map-reduce over documents
session exceeds window?                      -> structured state + recent window
model trained to 4k but you need 128k?       -> GQA + RoPE scaling + fine-tune + sliding window
memory-bound at 32k?                         -> INT8 KV cache + paged attention
quality degrades with stuffed context?       -> context ordering + compression (not more tokens)
```

## Key Equations

```
PE(pos, 2i) = sin(pos / 10000^(2i/d))
ALiBi score(i,j) = q_i.k_j/sqrt(d) - m_h * (i - j)
RoPE: theta_i = i * base^(-2i'/d);  q'_i = R(theta_i) q_i
sliding window attention cost = O(N * W)
cache_bytes = 2 * L * H_kv * d_head * S * B * bytes
compression_ratio = T_original / T_compressed
```