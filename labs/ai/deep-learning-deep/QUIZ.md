# deep-learning-deep — Quiz

15 multiple-choice questions across the ten modules. Answer key and score guide at the
bottom.

## Questions

**Q1.** Why is attention divided by `sqrt(d_k)`?
- A) To reduce memory usage
- B) Because the dot product of `d_k` unit-variance vectors has variance `d_k`, and
      without scaling the softmax saturates and its gradient vanishes
- C) To make the computation faster
- D) To normalize the values

**Q2.** Which padding preserves spatial resolution?
- A) `valid`
- B) `same`
- C) Neither
- D) It depends on the kernel size only

**Q3.** A 3x3 convolution with dilation rate `d=2` has what receptive field and parameter
  count?
- A) 5x5 with 4x the parameters
- B) 5x5 with the same parameters as a plain 3x3
- C) 3x3 with the same parameters
- D) 9x9 with the same parameters

**Q4.** Depthwise separable convolution's main saving comes from:
- A) Using smaller kernels
- B) Separating spatial filtering per channel from 1x1 channel mixing, cutting parameters
      by roughly `k^2 x C` versus `k^2 x C x C'`
- C) Skipping activation functions
- D) Using stride 2

**Q5.** LSTM's cell update is `c_t = f_t .* c_{t-1} + i_t .* tanh(...)`. Why is this better
  than a vanilla RNN state?
- A) It uses fewer parameters
- B) The gradient path through time is additive with a gate bounded by 1, so it does not
      shrink or blow up like a repeated product
- C) It runs faster
- D) It removes the need for an output gate

**Q6.** Pre-norm residual blocks are preferred at depth because:
- A) They use fewer parameters
- B) The residual path stays clean, so gradients reach early layers without traversing
      normalization at every layer
- C) Post-norm cannot be implemented
- D) They eliminate the need for a final norm

**Q7.** KV cache memory per token for `L` layers, `H` heads, `d` head dim, FP16 is:
- A) `2 * L * H * d * 2` bytes
- B) `L * H * d` bytes
- C) `2 * L * H * d * seq_len * 2` bytes
- D) Independent of layer count

**Q8.** Which change most reduces KV cache memory with the smallest quality cost?
- A) Removing the value projection
- B) Grouped-query attention (fewer KV heads than query heads)
- C) Increasing the head dimension
- D) Lowering the layer count

**Q9.** FlashAttention's speedup comes from:
- A) An approximation of attention
- B) Tiling and online softmax to avoid materializing the `n x n` score matrix in HBM —
      mathematically exact, IO-aware
- C) Using fewer heads
- D) Quantizing the keys

**Q10.** Multi-query attention (MQA) versus multi-head attention (MHA):
- A) MQA uses more KV heads
- B) MQA shares one KV head across query heads, cutting cache memory by the head count at
      a small quality cost
- C) They are identical
- D) MQA removes the need for the value projection

**Q11.** Sinusoidal positional encoding's key property for length generalization is:
- A) It is smaller than learned embeddings
- B) Relative offsets are (approximately) linear combinations of the encoding, so it
      extends to positions never seen in training
- C) It uses no parameters
- D) It is rotation-invariant

**Q12.** ALiBi adds what to the attention scores?
- A) A learned embedding per absolute position
- B) A head-specific linear penalty on distance, `-m * (i - j)`, requiring no parameters
- C) A sinusoidal rotation
- D) A normalization term

**Q13.** Continuous batching improves throughput by:
- A) Running a larger static batch
- B) Admitting new sequences into a running batch as others finish, so the device stays
      saturated
- C) Using shorter sequences
- D) Quantizing the weights

**Q14.** Speculative decoding's key property is:
- A) It approximates the target distribution for speed
- B) It produces output from the same distribution as the target model exactly, by having
      the target verify draft tokens in one pass
- C) It requires a larger target model
- D) It works only for greedy decoding

**Q15.** Modern LLM inference is primarily:
- A) Compute-bound, so FLOP reduction matters most
- B) Memory-bandwidth-bound during decode, so reducing bytes moved per token matters more
      than reducing FLOPs
- C) Latency-free
- D) Limited by the attention matrix only

## Answer Key

| Q | Answer | Why |
|---|--------|-----|
| 1 | B | Unscaled scores grow as `sqrt(d_k)`, pushing softmax to saturation. |
| 2 | B | `same` padding keeps `n` constant; `valid` shrinks by `k-1`. |
| 3 | B | Receptive field `3 + 2(d-1) = 5`, parameter count unchanged. |
| 4 | B | Separating spatial and channel mixing reduces `k^2*C*C'` to `k^2*C + C*C'`. |
| 5 | B | Additive recurrence with a bounded gate avoids exponential gradient decay. |
| 6 | B | Pre-norm keeps the residual path free of normalization layers. |
| 7 | A | Two tensors (K and V) times layers times heads times head dim times 2 bytes. |
| 8 | B | Fewer KV heads shrink the cache by the group ratio. |
| 9 | B | Exactness is preserved; the win is IO, not arithmetic. |
| 10 | B | One KV head shared across all query heads; cache divided by head count. |
| 11 | B | The sinusoidal structure makes offsets expressible as combinations. |
| 12 | B | A parameter-free linear distance bias, per head. |
| 13 | B | Device utilization stays high instead of draining at batch end. |
| 14 | B | Verification plus rejection sampling yields the target distribution exactly. |
| 15 | B | Each decode step reads the whole weight set; arithmetic intensity is ~1. |

## Score Guide

| Score | Verdict |
|-------|---------|
| 15/15 | Ready to design transformer-scale systems. Push into module 09 and 10. |
| 12-14 | Solid. Revisit your misses against THEORY.md. |
| 9-11 | Knows the components, not the interactions. Redo Q1, Q5, Q6, Q7, Q9. |
| 6-8 | Re-read THEORY.md, then redo EXERCISES for modules 01, 05, 09. |
| 0-5 | Restart with modules 01, 03, 05 before touching inference optimization. |

## Scoring Notes

- Single answer per question; no partial credit.
- Retake after re-reading the relevant module.
- Mastery threshold: 13/15 with no misses on Q1, Q6, Q7, Q9, Q14.
