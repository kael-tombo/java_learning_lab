# Lab 13: Context Window Management — Flashcards

| # | Front | Back |
|---|-------|------|
| 1 | Context is | Memory, input format, KV cache, and billing unit |
| 2 | Four questions | What goes in, what drops, how order is encoded, what it costs |
| 3 | Sinusoidal PE | `sin/cos(pos / 10000^(2i/d))` |
| 4 | Sinusoidal property | `PE(pos+k) = R_k PE(pos)` -> relative by construction |
| 5 | Sinusoidal extrapolation | Poor; no evidence beyond trained range |
| 6 | Learned absolute PE | No extrapolation at all; table grows with context |
| 7 | ALiBi | Linear distance bias added to attention scores |
| 8 | ALiBi slopes | Geometric across heads, e.g. `1/2^(8h/n)` |
| 9 | ALiBi extrapolation | Good: relative distance encoded directly |
| 10 | ALiBi cost | No extra parameters, no added compute |
| 11 | RoPE | Rotate q/k by position-dependent angle |
| 12 | RoPE relative property | `dot(q'_i, k'_j)` depends only on `i-j` |
| 13 | RoPE base | Longest wavelength; controls extrapolation range |
| 14 | Common RoPE bases | 10,000; 100,000 / 1,000,000 for long context |
| 15 | RoPE extrapolation | Good to ~2-4x trained length |
| 16 | Position interpolation | Scale positions into the trained range |
| 17 | Position extrapolation | Keep raw positions, accept degradation |
| 18 | Failure signature | Attention entropy collapse, sharp cliff |
| 19 | NTK-aware scaling | Change base rather than scaling positions |
| 20 | YaRN | Per-dimension NTK scaling + temperature compensation |
| 21 | LongRoPE | Per-dimension scaling with search |
| 22 | Sliding window | Each token attends to last `W` |
| 23 | Window cost | `O(N*W)` instead of `O(N^2)` |
| 24 | Window cache | Bounded at `W` tokens per sequence |
| 25 | Window weakness | No information crosses windows except residual stream |
| 26 | Attention sinks | First 4-5 tokens permanently visible (StreamingLLM) |
| 27 | Sink purpose | Absorb softmax "must attend" pressure |
| 28 | Without sinks | Sliding-window models collapse |
| 29 | Ring buffer | Modular indexing over a fixed-size cache |
| 30 | KV cache formula | `2 * L * H_kv * d_head * S * B * bytes` |
| 31 | GQA | Fewer KV heads than query heads |
| 32 | MQA | One KV head for all queries |
| 33 | GQA saving | `n_q_heads / n_kv_heads` |
| 34 | KV cache INT8 | 2x memory, small accuracy cost |
| 35 | Paged attention | Eliminates fragmentation waste |
| 36 | Prefix sharing | Identical prefixes share KV blocks (copy-on-write) |
| 37 | Token-level compression | Filler, whitespace, boilerplate removal |
| 38 | Sentence-level compression | Keep query-relevant sentences |
| 39 | Provenance rule | Keep the chunk so citations resolve |
| 40 | Document-level | Hierarchical summaries |
| 41 | Map-reduce | Per-document summarize, then synthesize |
| 42 | Question fan-out | Ask the question of each document, then merge |
| 43 | Latent compression | Autoencoder into latent tokens |
| 44 | Token dropping | Importance-based, then fine-tune to tolerate |
| 45 | Compression reporting | Report ratio AND quality delta |
| 46 | Ordering | Ascending score: best chunk last |
| 47 | Instruction repetition | Restate the operative instruction at the end |
| 48 | Lost in the middle | Primacy and recency effects |
| 49 | Question placement | Near the end; optional summary at the top |
| 50 | Prefill cost | `O(N^2 d)` attention |
| 51 | KV at long context | Often exceeds weight memory |
| 52 | Billing | Input tokens billed linearly |
| 53 | Stuffed context | Degrades past useful length |
| 54 | Default answer | Retrieve, do not stuff |
| 55 | Long window use | Multi-document comparison, headroom |
| 56 | Truncation | Drops early context; crude |
| 57 | Sliding history | Last k turns |
| 58 | Summarize older | Digest plus recent window |
| 59 | Retrieve from history | Vector search over past turns |
| 60 | Structured state | Extract facts/slots/decisions |
| 61 | Best combination | Structured state + recent window |
| 62 | Never compact | System message / policy |
| 63 | Compaction cost | Summary quality is a new failure mode |
| 64 | Context budget assembly | Priority order; drop lowest first |
| 65 | Budget invariants | Schema, system message, question survive |
| 66 | Model choice | Long-context models still need retrieval |
| 67 | Retrieval over long context | Shorter prompt, faster, cheaper, often better |
| 68 | TTFT at 64k | Often seconds to minutes |
| 69 | Window vs cache tradeoff | Bigger window = more memory per sequence |
| 70 | Measure entropy | The diagnostic that predicts cliff behavior |

## Self-Check

55+ = solid, 45-54 = redo Exercises 6 and 19, below that reread THEORY 2-7.