# deep-learning-deep

Deep track for deep learning in Java 21 — ten modules from convolution through recurrent
networks, seq2seq attention, transformers, positional encodings, normalization, KV cache,
and inference optimization. Everything hand-implemented, no frameworks.

## Track Contents

Ten sub-modules, each with its own theory, exercises, quiz, and an `*Algorithm.java` plus
test pair under `src/`:

| # | Module | Focus |
|---|--------|-------|
| 01 | `01-cnn-fundamentals` | Convolution 2D, stride, padding, dilation, feature maps, receptive field |
| 02 | `02-cnn-architectures` | LeNet, AlexNet, VGG, ResNet, EfficientNet, MobileNet, ConvNeXt |
| 03 | `03-rnn-lstm-gru` | RNN math, BPTT derivation, vanishing gradient, LSTM gates, GRU gates |
| 04 | `04-seq2seq-attention` | Encoder-decoder, Bahdanau/Luong attention, teacher forcing, beam search |
| 05 | `05-transformer-from-scratch` | Scaled dot-product attention, multi-head, positional encoding, FFN |
| 06 | `06-attention-variants` | Self/cross/causal attention, RoPE, ALiBi, flash attention intuition |
| 07 | `07-positional-encoding` | Sinusoidal, learned, RoPE, ALiBi, relative position bias, NoPE |
| 08 | `08-normalization-transformers` | LayerNorm, RMSNorm, pre-norm vs post-norm, sandwich norm |
| 09 | `09-kv-cache` | Transformer inference cache, memory overhead, GQA, MQA, sliding window, PagedAttention |
| 10 | `10-inference-optimization` | Speculative decoding, GPTQ/AWQ/GGUF, vLLM, continuous batching |

## Track-Level Documents

| File | What it is |
|------|-----------|
| `INDEX.md` | Module list with one-line focus per module |
| `THEORY.md` | Mechanism, reason, and failure for each of the ten modules |
| `EXERCISES.md` | ~95 tagged exercises plus four cross-module tasks |
| `QUIZ.md` | 15 multiple-choice questions with answer key and score guide |
| `FLASHCARDS.md` | 60-row recall table |
| `MATH_FOUNDATION.md` | Derivations with worked numbers: conv as linear map, attention scaling, RoPE rotations, LSTM gradients, KV cache arithmetic, arithmetic intensity, online softmax |
| `CODE_DEEP_DIVE.md` | Java implementations: im2col conv, LSTM cell, masked attention, tiled FlashAttention, RoPE/ALiBi, pre-norm block, KV cache, continuous batcher, speculative decoding, quantization |
| `VISION.md` | Mastery path, milestones, anti-goals, 30-day plan |
| `MINI_PROJECT.md` | Transformer library + working language model: 10 phases, 16 milestones |
| `REAL_WORLD_PROJECT.md` | On-device ASR pipeline under a memory and latency budget |
| `DEEP_LEARNING_ACADEMY_GUIDE.md` | Track guide |

## Two Lines That Must Be Right

If you remember nothing else from this track:

1. **`softmax(Q K' / sqrt(d_k)) V`** — the `sqrt(d_k)` is not tuning. Without it, dot
   products have variance `d_k`, the softmax saturates, and its gradient vanishes.
2. **`-inf` before the softmax for the causal mask** — not zeroed probabilities afterwards.
   `softmax(-inf)` is exactly zero and renormalizes the rest.

Everything else is engineering, and engineering is learnable by doing.

## The Third Idea: Decode Is Memory-Bound

```
arithmetic_intensity = FLOPs / bytes = 2 / bytes_per_weight
```

At FP16 that is **1 FLOP per byte**. Decode does one multiply-accumulate per weight read, so
it is bandwidth-bound, not compute-bound. Every optimization that reduces bytes moved per
token — INT8 (4x), GQA (cache /4), paged cache (no fragmentation), speculative decoding
(~3x accepted tokens) — multiplies throughput directly. Optimizations that add FLOPs do
not help at all. This is the single most useful fact in the track for anyone who will
actually ship a model.

## How to Work Through This Track

1. **Read `THEORY.md`**, focusing on *why* each component exists. Attention replaced
   recurrence because it removes the sequential dependency; the cache exists because
   autoregressive decoding is memory-bound.
2. **Work `EXERCISES.md`** in module order, E to H. The causality test in module 05 and the
   gradient checks throughout are non-negotiable.
3. **Retake `QUIZ.md`** until 13/15 with no misses on the scaling factor, pre-norm, KV
   cache, FlashAttention, and speculative decoding questions.
4. **Drill `FLASHCARDS.md`** daily.
5. **Do `MATH_FOUNDATION.md`** — the KV cache arithmetic and the roofline analysis are the
   two sections that transfer directly to production decisions.
6. **Implement from `CODE_DEEP_DIVE.md`** without reading ahead. The tiled attention and
   speculative verification implementations are worth writing by hand once.
7. **Build the mini project**, then design the real-world project for a domain with a real
   budget.

## Debugging Order

1. **Shapes** — assert at every matmul boundary. A silent broadcast error trains to a worse
   loss rather than crashing.
2. **Causality and masking** — change a future value and check that earlier positions do not
   move.
3. **Attention entropy at initialization** — should be near `log(n)`; near zero means missing
   the scale or a mask bug.
4. **Gradient checks** on every sublayer.
5. **Loss arithmetic** — verify training loss equals independently computed cross-entropy.
6. **Memory accounting** — cache formula against measured allocation.

## What You Will Be Able To Do

- Implement convolution, recurrence, and attention from scratch with verified gradients.
- Explain why each transformer component exists and what breaks when it is removed.
- Design a streaming decoder with a bounded cache and a stated latency budget.
- Apply quantization, GQA, batching, and speculative decoding with the throughput arithmetic
  to justify each choice.
- Reason about inference as a memory-bandwidth problem rather than a FLOP problem.
