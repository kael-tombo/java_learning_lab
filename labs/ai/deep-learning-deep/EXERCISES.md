# deep-learning-deep — Exercises

Difficulty: **E** easy, **M** medium, **H** hard. Java 21, no dependencies. Convolution,
recurrence, and attention are all hand-implemented; every shape is asserted.

## Module 01 — CNN Fundamentals

- [ ] **E1.1** Implement 2D convolution from nested loops. Verify against hand-computed
      values for a 5x5 input with a 3x3 kernel, stride 1, pad 0.
- [ ] **E1.2** Output size formula: verify `(n + 2p - k)/s + 1` for 12 combinations of
      `n, p, k, s`.
- [ ] **M1.3** Same-padded convolution; verify the output size equals the input size and
      that the border behaves sensibly.
- [ ] **M1.4** Max pool and average pool; verify a 2x2 pool halves both dimensions.
- [ ] **M1.5** Parameter count versus a dense layer of the same receptive field. Report the
      ratio for `C=64, k=3`.
- [ ] **M1.6** Stride-2 convolution: verify it matches 2x2 max pooling followed by a stride-1
      conv (approximately) and discuss why it is not identical.
- [ ] **M1.7** Receptive field: for `L` layers of 3x3 with stride 1, verify `2L+1`. Then
      with stride 2 every other layer, compute the field and the effective step.
- [ ] **H1.8** Dilation: verify a dilated 3x3 with rate `d` sees a `3 + 2(d-1)` field with
      the same parameter count.
- [ ] **H1.9** Implement im2col convolution and gradient-check it against the nested-loop
      version's analytic gradient.

## Module 02 — CNN Architectures

- [ ] **E2.1** LeNet-5 on a small image dataset. Report per-layer output shapes.
- [ ] **E2.2** ReLU versus sigmoid versus tanh on the same CNN; report epochs to target
      loss.
- [ ] **M2.3** Depth study: 8 conv layers versus 16 versus 32, no residuals. Report whether
      training degrades with depth.
- [ ] **M2.4** Add residual connections to the 32-layer net; report the improvement.
- [ ] **M2.5** VGG-style homogeneous blocks: verify a 3x3 stack of `n` equals a single
      `3n x 3n` receptive field, and compare parameter counts.
- [ ] **M2.6** Depthwise separable convolution. Implement both parts; report parameters and
      accuracy against a standard conv of matched width.
- [ ] **M2.7** Global average pooling versus flatten-plus-dense; report parameter reduction
      and accuracy.
- [ ] **H2.8** Inception-style multi-scale branches; verify shape arithmetic after
      concatenation and report accuracy against a single-scale baseline.
- [ ] **H2.9** Compound scaling: sweep depth, width, and resolution independently and
      together. Plot the accuracy/FLOP frontier and check whether independent scaling
      reaches it.

## Module 03 — RNN, LSTM, GRU

- [ ] **E3.1** Vanilla RNN forward on a length-5 sequence; verify hidden-state recurrence
      against hand values.
- [ ] **E3.2** BPTT backward through the unrolled graph; gradient-check against finite
      differences.
- [ ] **M3.3** Vanishing gradient demonstration: gradient norm at `t=1` versus `t=T` for
      `T = 10, 50, 100` with vanilla RNN, tanh RNN, LSTM.
- [ ] **M3.4** LSTM cell with all four gates; verify the cell-state recurrence is additive.
- [ ] **M3.5** LSTM backward; gradient-check.
- [ ] **M3.6** GRU cell: two gates, no cell state. Report parameter count versus LSTM
      (expect ~25% fewer).
- [ ] **M3.7** Copy task: train vanilla RNN, LSTM, GRU to copy a length-30 sequence. Report
      success rate per model.
- [ ] **H3.8** Highway connection in a 20-layer RNN; compare against plain deep RNN.
- [ ] **H3.9** Truncated BPTT: gradient-check that truncation gives an unbiased gradient
      estimate of a given sub-window.

## Module 04 — Seq2Seq with Attention

- [ ] **E4.1** Encoder-decoder with a fixed bottleneck vector. Show the degradation on a
      length-20 reversal task.
- [ ] **E4.2** Add Bahdanau (additive) attention; verify `alpha` rows sum to 1 and show the
      task now solves.
- [ ] **E4.3** Luong (multiplicative) attention; report speed and accuracy versus additive.
- [ ] **M4.4** Visualize alignment weights on the reversal task; verify they form a diagonal.
- [ ] **M4.5** Teacher forcing versus scheduled sampling (epsilon 1.0 -> 0.1). Report
      exposure-bias effect at inference.
- [ ] **M4.6** Greedy decoding versus beam search with beam 5. Report exact-match accuracy.
- [ ] **M4.7** Length normalization in beam search: show unnormalized beam favours short
      outputs, and that `len^alpha` with `alpha = 0.7` fixes it.
- [ ] **H4.8** Implement attention caching for inference; report the speedup and the
      equivalence of the outputs.
- [ ] **H4.9** Compare seq2seq attention against self-attention on the same task; report
      parameters and accuracy.

## Module 05 — Transformer From Scratch

- [ ] **E5.1** Scaled dot-product attention; verify output shape and that rows are convex
      combinations of `V`.
- [ ] **E5.2** Causal mask; verify position `i` cannot see position `> i` (test by changing a
      future `V` and confirming no effect).
- [ ] **E5.3** Demonstrate the scaling factor: attention with `d_k = 64` and unscaled
      scores versus scaled. Report the softmax entropy in each case.
- [ ] **M5.4** Multi-head attention; verify the concatenation and output projection shape.
- [ ] **M5.5** Full encoder block: attention, residual, LayerNorm, FFN, residual, LayerNorm.
      Verify pre-norm ordering.
- [ ] **M5.6** Full decoder block with cross-attention.
- [ ] **M5.7** Stack 6 layers and 12 layers; report training loss curves.
- [ ] **H5.8** Teacher-forced training and greedy decoding on a small character-level task.
      Verify the loss matches cross-entropy on the targets.
- [ ] **H5.9** Gradient checkpointing on the FFN; verify identical gradients with lower peak
      memory.

## Module 06 — Attention Variants

- [ ] **E6.1** Implement self-attention, cross-attention, and causal self-attention; report
      shapes for each.
- [ ] **M6.2** RoPE: apply rotations to `Q` and `K`. Verify that the attention score
      depends only on the relative distance for a fixed query.
- [ ] **M6.3** ALiBi: add `-m * |i - j|` per head. Sweep `m` per head; report effect on
      long-range retrieval.
- [ ] **M6.4** MQA: share one KV head across all query heads. Report KV cache memory and
      accuracy.
- [ ] **M6.5** GQA with 8 groups on a 32-head model; report the memory/accuracy trade-off
      against MQA and full MHA.
- [ ] **M6.6** Relative position bias: learn a bias per relative distance; verify bias shape
      and that it is added before softmax.
- [ ] **H6.7** FlashAttention-style tiling: implement block-wise attention with online
      softmax. Verify the output matches naive attention to 1e-10.
- [ ] **H6.8** Sliding-window attention with `w = 128` on a length-2048 sequence; report
      cache memory and the degradation on a needle-retrieval task.

## Module 07 — Positional Encoding

- [ ] **E7.1** Sinusoidal encoding; verify every position has a unique vector and that
      relative offsets are (approximately) linear combinations.
- [ ] **E7.2** Extrapolation: evaluate PE at positions beyond the trained range and report
      cosine similarity patterns.
- [ ] **M7.3** Learned absolute positional embedding; show it fails beyond the trained
      length.
- [ ] **M7.4** Relative position bias; train on length 256, evaluate on 512, report
      degradation against sinusoidal.
- [ ] **M7.5** NoPE: train with causal attention and no positional signal. Report
      autoregressive quality and inspect whether position is still implicitly encoded.
- [ ] **H7.6** RoPE scaling for context extension: interpolate the rotation frequencies and
      report quality at 2x and 4x the trained length.
- [ ] **H7.7** Compare sinusoidal, learned, RoPE, ALiBi, and NoPE on one task at three
      context lengths.

## Module 08 — Normalization in Transformers

- [ ] **E8.1** LayerNorm over hidden dims; verify independence from batch composition.
- [ ] **M8.2** RMSNorm; verify identical to LayerNorm when gamma=1, beta=0; benchmark both.
- [ ] **M8.3** Pre-norm versus post-norm residual blocks at depth 24 without warmup. Report
      both loss curves; post-norm should diverge.
- [ ] **M8.4** Add warmup to the post-norm stack; report whether it trains.
- [ ] **M8.5** Sandwich norm (norm before and after the sublayer) at depth 24.
- [ ] **M8.6** Gradient norms per layer for pre-norm and post-norm; show the difference in
      gradient flow.
- [ ] **H8.7** Final-norm placement: verify that removing the final LayerNorm after a
      pre-norm stack degrades stability.
- [ ] **H8.8** Activation checkpointing across a 24-layer stack; report peak memory and wall
      time, and verify identical gradients.

## Module 09 — KV Cache

- [ ] **E9.1** Implement decoding with and without a KV cache. Verify identical outputs.
- [ ] **E9.2** Measure per-step latency at context 128, 512, 2048. Report the growth curve
      with and without cache.
- [ ] **M9.3** Cache memory formula: compute per-token bytes for a 32-layer, 32-head,
      `d_head = 128` FP16 model. Verify against a measured allocation.
- [ ] **M9.4** MQA: reduce cache memory by the group ratio; measure and verify.
- [ ] **M9.5** GQA with several group counts; report memory and quality.
- [ ] **M9.6** Sliding-window cache: fixed-size allocation; report memory and
      needle-retrieval quality.
- [ ] **M9.7** Prefix caching: a shared system prompt. Measure the speedup for the second
      request with the same prefix.
- [ ] **H9.8** PagedAttention-style block allocation: fixed pages, a free list, copy-on-write
      on fork. Report fragmentation before and after.
- [ ] **H9.9** Batch size sweep: find where cache memory caps the batch, and show why
      throughput flattens.

## Module 10 — Inference Optimization

- [ ] **E10.1** Continuous batching: implement a scheduler that admits new sequences as
      others finish. Report GPU utilization and throughput versus static batching.
- [ ] **M10.2** Speculative decoding with a small draft model. Verify the output
      distribution matches the target model exactly (sample both, compare statistics).
- [ ] **M10.3** Report the acceptance rate and the speedup for draft sizes 2, 4, 8.
- [ ] **M10.4** INT8 weight-only quantization: implement per-channel symmetric quantization
      and report accuracy delta and memory.
- [ ] **M10.5** AWQ-style activation-aware scaling: protect the top-`p%` salient channels.
      Report accuracy versus plain RTN quantization.
- [ ] **M10.6** FP16 versus BF16 versus INT8: report accuracy, memory, and throughput.
- [ ] **M10.7** Combined: continuous batching + GQA + INT8 + speculative decoding. Report
      cumulative throughput.
- [ ] **H10.8** Memory-bound demonstration: show decode time scales with weight bytes read
      per token, not FLOPs. Measure and fit.
- [ ] **H10.9** End-to-end serving simulation: report tokens/second, p50 and p99 latency,
      and the memory ceiling as a function of context and batch size.

## Cross-Module

- [ ] **X1** Build a small character-level language model three ways — RNN, LSTM,
      attention-only — and compare perplexity at matched parameter counts.
- [ ] **X2** Implement a 4-layer transformer and gradient-check every sublayer.
- [ ] **X3** Profile a full forward pass; report time per sublayer and identify the top
      three costs.
- [ ] **X4** Reproducibility: same seed, byte-identical logits. Audit for unseeded
      randomness.
