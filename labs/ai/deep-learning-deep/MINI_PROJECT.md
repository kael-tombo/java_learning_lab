# deep-learning-deep — Mini Project

## Project: A Transformer Library and a Working Language Model

Build a small deep learning library in Java 21 — tensors, convolution, LSTM/GRU, attention,
positional encodings, normalization, KV cache — and use it to train a character-level
language model with a real inference engine: cache, batching, quantization, and speculative
decoding.

## Goal

`Main` trains a 4-6 layer transformer on a text corpus, reports perplexity and training
curves, generates text, and then runs an inference benchmark reporting throughput, latency,
memory, and the effect of every optimization. No frameworks, no dependencies.

## Requirements

### Phase 1: Tensor Core
- [ ] `Tensor` with shape assertions on every operation; rank and dimension checks that throw
      with a readable message.
- [ ] Flat `double[]` storage; matmul, transpose, reshape, slicing, softmax, layernorm.
- [ ] Broadcasting limited to the cases you actually need, and asserted rather than inferred.
- [ ] A `Printer` that dumps a tensor as an ASCII grid — indispensable for debugging.

### Phase 2: CNN
- [ ] `Conv2d` nested-loop reference plus an im2col path; assert equality.
- [ ] Stride, padding (valid/same), dilation; output-size formula verified for 12
      combinations.
- [ ] Max and average pooling; backward pass for both, gradient-checked.
- [ ] Depthwise separable convolution; report parameters against a standard conv.
- [ ] A small image classifier trained end to end; report per-layer output shapes.

### Phase 3: Recurrent Networks
- [ ] Vanilla RNN with BPTT; gradient-checked.
- [ ] LSTM cell with four gates; gradient-checked.
- [ ] GRU cell; report the parameter ratio to LSTM.
- [ ] Copy task of length 30 for all three models; report success rates.
- [ ] Gradient-norm decay across timesteps: the vanishing-gradient demonstration.

### Phase 4: Attention and the Transformer Block
- [ ] Scaled dot-product attention with causal masking; verify a future `V` change has no
      effect on earlier positions.
- [ ] Multi-head attention; verify shapes and parameter count `4 d^2`.
- [ ] Pre-norm block: attention, residual, LayerNorm, FFN, residual.
- [ ] Cross-attention variant for an encoder-decoder.
- [ ] Positional encodings: sinusoidal, learned, RoPE, ALiBi, relative bias, none.
- [ ] Gradient-check every sublayer of a 4-layer stack.

### Phase 5: Language Model
- [ ] Character tokenizer with a fixed vocabulary; report the vocabulary size.
- [ ] Causal pretraining with next-character prediction; loss is exactly the mean
      cross-entropy over positions.
- [ ] 4 to 6 layers, `d_model` 128-256, 4-8 heads. Training curve printed per step.
- [ ] Train to a perplexity target; report best validation perplexity.
- [ ] Greedy and temperature-sampled generation; report samples at three temperatures.

### Phase 6: Positional Encoding Comparison
- [ ] Train the same model with each of the six encodings.
- [ ] Report perplexity at context lengths 128, 512, and 2048.
- [ ] Train at 256 and evaluate at 1024 for each encoding; report the extrapolation result.

### Phase 7: Normalization Study
- [ ] LayerNorm versus RMSNorm at equal quality; benchmark both.
- [ ] Pre-norm versus post-norm at depth 24 with and without warmup; report all four curves.
- [ ] Sandwich norm at depth 24.
- [ ] Per-layer gradient norms for pre-norm and post-norm.
- [ ] Verify the final norm is required after a pre-norm stack.

### Phase 8: KV Cache and Decoding
- [ ] Cached decoding; assert outputs identical to uncached.
- [ ] Per-step latency at context 128/512/2048; report the growth curve.
- [ ] Cache memory measured and compared to the formula.
- [ ] MQA, GQA at several group counts, and a sliding window; report memory and perplexity.
- [ ] Prefix caching for a repeated prefix; report the measured speedup.
- [ ] Paged cache with a free list and copy-on-write fork; report fragmentation.

### Phase 9: Inference Optimization
- [ ] Continuous batching; report throughput versus static batching on a mixed-length
      workload.
- [ ] Speculative decoding with a smaller draft model; verify the output distribution
      matches by sampling statistics.
- [ ] Report acceptance rate and speedup for draft sizes 2, 4, 8.
- [ ] INT8 per-channel and FP16 quantization; report perplexity delta and memory.
- [ ] Combined pipeline: continuous batching + GQA + INT8 + speculative decoding.

### Phase 10: Benchmark and Report
- [ ] Roofline analysis: FLOPs per token, bytes per token, arithmetic intensity; compare
      the predicted and measured times/second.
- [ ] Full parameter count and memory accounting: weights, cache, activations.
- [ ] `REPORT.md`.

## Directory Layout

```
deep-learning-deep/
  src/com/ailab/dl/
    tensor/{Tensor,Shape,Printer}.java
    conv/{Conv2d,Pool,Im2col,Separable}.java
    rnn/{Rnn,Lstm,Gru}.java
    attn/{Attention,MultiHead,TiledAttention}.java
    pos/{Sinusoidal,Rope,Alibi,RelBias}.java
    norm/{LayerNorm,RmsNorm,Block}.java
    model/{Transformer,CharTokenizer,Trainer,Generator}.java
    cache/{KvCache,PagedCache,PrefixCache}.java
    infer/{Batcher,Speculative,Quant}.java
    bench/Roofline.java
  Main.java
  out/train_curve.txt
  out/gen_samples.txt
  REPORT.md
```

## Milestones

1. **M1** — tensor core with shape assertions and an ASCII printer.
2. **M2** — Conv2d reference plus im2col, verified equal.
3. **M3** — pooling with gradient-checked backward.
4. **M4** — RNN, LSTM, GRU with gradient checks; copy task results.
5. **M5** — attention and multi-head, causal mask verified.
6. **M6** — pre-norm block and full 4-layer stack, gradient-checked.
7. **M7** — character tokenizer and causal training loop; loss matches cross-entropy.
8. **M8** — trained model generating text; perplexity target met.
9. **M9** — six positional encodings compared at three context lengths, with extrapolation.
10. **M10** — normalization study: four variants at depth 24.
11. **M11** — KV cache verified identical to uncached; latency curve measured.
12. **M12** — MQA/GQA/sliding-window/paged/prefix cache memory results.
13. **M13** — continuous batching throughput gain measured.
14. **M14** — speculative decoding with distribution equivalence verified.
15. **M15** — quantization results and the combined optimization pipeline.
16. **M16** — roofline analysis and `REPORT.md`.

## Acceptance Criteria

- [ ] im2col convolution equals the nested-loop reference elementwise.
- [ ] Attention verified causal: changing `V[j]` for `j > i` leaves `out[i]` unchanged.
- [ ] Attention with `1/sqrt(d_k)` has softmax entropy above 3 nats at initialization;
      without it, below 0.2.
- [ ] Every sublayer gradient-checks at relative error below 1e-6.
- [ ] Training loss equals the independently computed mean cross-entropy to 1e-9.
- [ ] Cached decoding produces byte-identical output to uncached decoding.
- [ ] Measured cache memory matches the formula within 5%.
- [ ] GQA-8 reduces cache memory by 4x with the perplexity delta reported.
- [ ] Continuous batching improves throughput over static batching on mixed lengths.
- [ ] Speculative output distribution matches the target by sampling statistics.
- [ ] Roofline-predicted tokens/second within 30% of measured.
- [ ] Re-running `Main` reproduces identical perplexity and samples.

## Stretch Goals

- [ ] FlashAttention-style tiled attention benchmarked against naive attention for time and
      memory.
- [ ] Encoder-decoder with cross-attention on a summarization task.
- [ ] Learning-rate range test by doubling until divergence.
- [ ] Gradient checkpointing across the stack; identical gradients, lower peak memory.
- [ ] Mixture-of-experts routing with a load-balancing loss.
- [ ] ALiBi bias sweep per head, reporting the learned slope spread.
- [ ] RoPE context extension by frequency interpolation; quality at 2x and 4x.
- [ ] Weight tying between embedding and output projection.
- [ ] A deliberately injected bug located using gradient checks alone.

## Failure Modes to Watch For

| Symptom | Likely cause |
|---------|--------------|
| Loss plateaus near uniform | Causal mask wrong, or attention not scaled by `sqrt(d_k)` |
| NaN in the loss from step 1 | Positional encoding too large, or no normalization |
| Post-norm diverges at depth | Expected — this is the finding, not a bug |
| Cached output differs from uncached | Off-by-one in the cache write or the read length |
| `bytesPerToken` far below the measured cache | A head count is wrong somewhere |
| Attention softmax entropy ~0 at init | Scaling factor missing |
| Throughput barely improves with continuous batching | Admitting from the waiting queue only at batch boundaries |
| Speculative output diverges from target | Discarding the mismatched token instead of substituting it |
| INT8 perplexity collapse | Per-tensor scale instead of per-channel |
| Training does not reproduce | Unseeded randomness in init, shuffling, or sampling |
| Slower with tiling | Naive implementation materializing the score matrix inside the tile loop |

## Definition of Done

`REPORT.md` contains: the tensor core verification results, the convolution reference-versus-
im2col comparison, pooling gradient checks, the recurrent results (gradient decay curves
across timesteps, copy-task success rates, the LSTM/GRU parameter ratio), the attention
verifications (causality, entropy with and without scaling), the gradient-check matrix for
every sublayer and every positional encoding, the language model configuration and best
validation perplexity, generated samples at three temperatures, the positional-encoding
comparison at three context lengths including the extrapolation test, the normalization
study with all four curves and per-layer gradient norms, the KV cache latency curve and
measured-versus-formula memory, the MQA/GQA/sliding-window/paged/prefix cache memory and
quality table, the continuous batching throughput comparison, the speculative decoding
acceptance rates and distribution equivalence test, the quantization perplexity deltas, the
combined optimization throughput, the roofline analysis with predicted versus measured,
and a list of known failure modes with mitigations.
