# Lab 02: GPT Architecture — Flashcards

| # | Front | Back |
|---|-------|------|
| 1 | GPT architecture | Decoder-only Transformer stack (no encoder, no cross-attention) |
| 2 | Causal mask | Additive `-inf` above the diagonal so a token sees only its left context |
| 3 | Why additive mask | Multiplying post-softmax yields `0 * -inf = NaN` |
| 4 | LM objective | Maximize `sum_t log P(x_t \| x_<t)` |
| 5 | Teacher forcing | All positions trained in one forward pass with shifted targets |
| 6 | Input/target offset | Inputs `x[0..T-1]`, targets `x[1..T]` |
| 7 | Pre-norm | LayerNorm before attention/MLP; stabilizes deep stacks |
| 8 | FFN expansion | `4*d_model` (GPT-2) or `8/3*d_model` gated (SwiGLU) |
| 9 | SwiGLU | `down(silu(gate(x)) * up(x))` |
| 10 | GELU vs ReLU in FFN | GELU is smooth (used by GPT-2/3); ReLU is cheaper (LLaMA uses SwiGLU) |
| 11 | BPE | Greedy bottom-up merge of the most frequent adjacent symbol pair |
| 12 | BPE base unit | 256 bytes, so no OOV tokens |
| 13 | Word-boundary marker | `G` / `_` prefix token so " token" != "token" |
| 14 | Vocab tradeoff | Bigger vocab = more embedding params, shorter sequences |
| 15 | Autoregressive step | forward -> filter -> sample -> append |
| 16 | Greedy decode | argmax at every step, T -> 0 |
| 17 | Temperature | `logits / T`; T<1 sharper, T>1 flatter |
| 18 | Top-k | Keep the k highest-probability logits |
| 19 | Top-p / nucleus | Keep smallest prefix with cumulative mass >= p |
| 20 | Top-k vs top-p | Fixed k vs adaptive to per-position entropy |
| 21 | KV cache | Stores K and V for past positions to avoid recompute |
| 22 | Decode without cache | O(n^2) work over the sequence |
| 23 | Decode with cache | O(n) work, one new query row per step |
| 24 | KV cache size formula | `2 * layers * n_kv_heads * head_dim * seq * bytes` |
| 25 | GQA | Share one KV head across a group of query heads, shrinking the cache |
| 26 | MQA | All query heads share a single KV head (smallest cache) |
| 27 | Prefill | The parallel pass over the whole prompt that populates the cache |
| 28 | Decode phase | Token-by-token generation, memory-bandwidth bound |
| 29 | EOS token | Model-learned stop signal; templates add special variants |
| 30 | Chat template | Serializes role/content blocks; part of the model contract |
| 31 | Base vs instruct | Next-token predictor vs fine-tuned instruction follower |
| 32 | Logits | Pre-softmax scores, one per vocabulary entry |
| 33 | Logits processor | Temperature, top-k, top-p applied before sampling |
| 34 | Softmax stability | Subtract row max before exp |
| 35 | Padding loss mask | Exclude pad targets from the loss mean |
| 36 | Scaling law form | Power law in parameters, data, and compute |
| 37 | Chinchilla lesson | For fixed compute, models were over-parameterized vs data |
| 38 | Consequence | Retrieval and fine-tuning beat adding parameters |
| 39 | Logit scale | `1/sqrt(d_k)` keeps softmax gradients alive |
| 40 | Residual stream | Same-width tensor flowing through add-norms |
| 41 | Weight tying | Output projection shares the token embedding matrix |
| 42 | Weight tying benefit | Saves `d_model * vocab` params, improves rare tokens |
| 43 | AdamW default | Betas (0.9, 0.999), eps 1e-8, decoupled weight decay |
| 44 | LM head bias | Usually none; embeddings are the only special-cased layer |
| 45 | Context length train vs serve | Train window bounds positional generalization, cache size bounds serve memory |
| 46 | Sliding window | Attention restricted to last W tokens to bound cache memory |
| 47 | Ring cache | Circular buffer of KV entries for fixed-window decoding |
| 48 | Reproducibility | Log sampling seed, top-p, temperature, and model hash |
| 49 | Perplexity | `exp(mean NLL)`, comparable across tokenizers only with care |
| 50 | Perplexity caveat | Different BPE merges change token count, shifting PPL |
| 51 | Why log PPL | Per-token loss is additive and numerically stable |
| 52 | Byte-level advantage | No unknown-token failure mode, multilingual friendly |
| 53 | Byte-level cost | Longer sequences for Latin text vs word-level vocabs |
| 54 | Merge determinism | Break frequency ties by lowest pair id |
| 55 | Greedy merge order | Apply merges in learned priority, not naive adjacency |
| 56 | Merge table | The learned list of (pair -> new id) used at encode time |
| 57 | Loss masking rule | Mask where target == padId, then mean over remaining rows |
| 58 | Cross-entropy base case | Loss 0 = perfect prediction, `ln(V)` = uniform random |
| 59 | Beam search | Keeps width-k partial sequences, scores by log prob |
| 60 | Length normalization | `score / length^alpha` counteracts short-sequence bias |
| 61 | Beam width cost | Memory and latency scale with k |
| 62 | Beam failure mode | Degenerate generic output; diversity heuristics help |
| 63 | Batch decode effect | Larger batches amortize weight reads, raise throughput |
| 64 | TTFT | Time to first token; dominated by prefill |
| 65 | ITL / TPOT | Inter-token latency; dominated by decode and cache reads |
| 66 | Speculative decoding | Draft model proposes k tokens, target verifies in one pass |
| 67 | Acceptance criterion | A drafted token is kept if target probability exceeds uniform draw |
| 68 | Inference harness responsibility | Batching, cache, sampling, stop conditions, streaming |
| 69 | Java float choice | `double` logits for clarity, `float`/int8 cache for realism |
| 70 | Java RNG | Seed `java.util.Random`; log seed with every eval run |

## Self-Check

Score: 55+ = solid, 45-54 = review exercises, <45 = reread THEORY sections 2-6.