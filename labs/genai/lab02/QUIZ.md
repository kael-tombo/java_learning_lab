# Lab 02: GPT Architecture — Quiz

## Questions

**Q1.** GPT is which part of the original Transformer?
- a) Encoder only
- b) Decoder only
- c) Both, with cross-attention
- d) Encoder-decoder with cache

**Q2.** The causal mask prevents a token from attending to...
- a) padding tokens
- b) its own position
- c) future tokens
- d) the BOS token

**Q3.** Why add the mask instead of multiplying the attention weights by zero?
- a) Faster
- b) Avoids 0 * Infinity = NaN in softmax
- c) Preserves gradients
- d) Reduces memory

**Q4.** In teacher forcing, targets are the input sequence...
- a) unchanged
- b) reversed
- c) shifted by one position
- d) doubled

**Q5.** What does the KV cache store?
- a) Gradients
- b) Keys and values for previously computed positions
- c) Optimizer state
- d) The vocabulary

**Q6.** Without a KV cache, decoding n tokens costs roughly...
- a) O(n)
- b) O(n log n)
- c) O(n^2)
- d) O(2^n)

**Q7.** BPE starts from which base symbols?
- a) Word tokens
- b) Characters only
- c) Bytes
- d) BPE merges

**Q8.** Why do byte-level BPE vocabularies guarantee no out-of-vocabulary tokens?
- a) They are trained on the target corpus
- b) Every byte sequence is representable
- c) They use a fallback dictionary
- d) They truncate unknown words

**Q9.** Temperature T < 1 in sampling makes the distribution...
- a) Flatter
- b) Sharper / closer to greedy
- c) Uniform
- d) Undefined

**Q10.** Top-p (nucleus) sampling selects tokens until...
- a) k tokens are found
- b) cumulative probability reaches p
- c) all logits are positive
- d) the EOS token appears

**Q11.** What is the SwiGLU FFN variant of the GPT block?
- a) w2 * act(w1 x + b1)
- b) down(silu(gate(x)) * up(x))
- c) two parallel softmaxes
- d) A convolution over positions

**Q12.** Why does per-layer MLP compute dominate parameter count at large scale?
- a) Attention is quadratic
- b) MLP width grows 4-8x d_model while attention grows 4x
- c) MLPs have more layers
- d) Attention has no weights

**Q13.** In the scaling law `L ~ E^(1/alpha) N^(-alpha/beta)`, holding compute E fixed means...
- a) Bigger models always win
- b) Bigger models need proportionally more data
- c) Data does not matter
- d) Loss is independent of N

**Q14.** An instruction-tuned model differs from a base model primarily in...
- a) Layer count
- b) Fine-tuning on instruction/response pairs
- c) Larger vocabulary
- d) Different attention mask

**Q15.** Why subtract the row max before softmax?
- a) To make outputs sum to zero
- b) Numerical stability against overflow
- c) To speed up sampling
- d) To add the mask

---

## Answers

1. **b** — decoder-only stack, causal attention, no encoder.
2. **c** — future positions are masked out.
3. **b** — masking after softmax with zeros requires multiplying by zero and `0 * -inf` becomes NaN.
4. **c** — input `x[0..T-1]`, target `x[1..T]`.
5. **b** — cached K/V per layer for positions already computed.
6. **c** — recomputing the full prefix each step is quadratic.
7. **c** — 256 base symbols, merged upward.
8. **b** — any byte string can be segmented into byte tokens.
9. **b** — dividing logits by T < 1 amplifies gaps.
10. **b** — smallest prefix whose cumulative probability ≥ p.
11. **b** — gated linear unit with SiLU, projected up then down.
12. **b** — MLP has 8d²+ weights per layer vs ~4d² for attention projections.
13. **b** — more parameters need more tokens to avoid saturation.
14. **b** — supervised fine-tuning plus a chat template.
15. **b** — exp of large logits overflows double/even float range.

## Score Guide

- 14-15: ready for Lab 03 (prompting) and Lab 06 (LoRA).
- 11-13: re-read sections 4-6 of THEORY.md.
- 7-10: redo Exercises 2, 4, 7.
- 0-6: restart at Lab 01.