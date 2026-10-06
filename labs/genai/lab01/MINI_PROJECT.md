# Lab 01: Transformer Architecture — Mini Project

## Project: Character-Level Transformer for Text Generation

Build a working character-level language model using the Transformer
architecture implemented from scratch in Java.

## Goal

Train a small Transformer on a text corpus (e.g., Shakespeare, Wikipedia
dump, or any text file) that can generate coherent character sequences
when given a prompt.

## Requirements

### Phase 1: Data Pipeline
- [ ] Load a text corpus (minimum 100KB).
- [ ] Build a character vocabulary (unique characters).
- [ ] Implement a `Dataset` class that yields (input, target) pairs.
- [ ] Input: sequence of `seqLen` characters. Target: same sequence shifted by 1.

### Phase 2: Model Components
- [ ] Token embedding layer (char → vector).
- [ ] Sinusoidal positional encoding.
- [ ] Multi-head self-attention (causal).
- [ ] Feed-forward network (ReLU or GELU).
- [ ] Layer normalization (pre-norm).
- [ ] Residual connections.
- [ ] Final linear projection to vocabulary size.

### Phase 3: Training Loop
- [ ] Cross-entropy loss.
- [ ] SGD or Adam optimizer (implement from scratch).
- [ ] Learning rate schedule (warmup + decay).
- [ ] Gradient clipping (max norm = 1.0).
- [ ] Training loop with periodic loss reporting.

### Phase 4: Generation
- [ ] Greedy decoding.
- [ ] Temperature sampling.
- [ ] Top-k sampling.
- [ ] Generate text from a seed prompt.

### Phase 5: Evaluation
- [ ] Track training loss over time.
- [ ] Compute perplexity on held-out data.
- [ ] Generate sample text at different temperatures.

## Architecture Specifications

```
d_model = 128
num_heads = 4
num_layers = 4
d_ff = 512
seq_len = 64
vocab_size = ~70 (characters)
dropout = 0.1
```

## Milestones

| Milestone | Deliverable | Success Criteria |
|-----------|-------------|------------------|
| M1 | Data pipeline | Can load corpus and produce batches |
| M2 | Model forward pass | Produces [batch, seq, vocab] logits |
| M3 | Training loop | Loss decreases over 1000 steps |
| M4 | Generation | Produces plausible character sequences |
| M5 | Evaluation | Perplexity < 5.0 on held-out data |

## Stretch Goals

- [ ] Implement beam search decoding.
- [ ] Add learned positional embeddings (compare with sinusoidal).
- [ ] Implement label smoothing.
- [ ] Add weight tying between embedding and output projection.
- [ ] Visualize attention weights for a sample input.
- [ ] Implement gradient accumulation for larger effective batch sizes.

## Success Criteria

1. Training loss decreases monotonically (with noise).
2. Generated text shows learned patterns (common words, punctuation).
3. Model can complete simple prompts plausibly.
4. Perplexity on held-out data is below 5.0.
5. Code is modular and well-documented.

## Tips

- Start with a tiny model (2 layers, d_model=64) to verify correctness.
- Use gradient checking before full training.
- Monitor attention entropy — if it collapses to uniform, reduce learning rate.
- Character-level models need more training than token-level — be patient.
- Save checkpoints periodically.

## Deliverables

- [ ] Source code in `src/main/java/com/genai/lab01/`
- [ ] Training script with configurable hyperparameters
- [ ] Generated text samples (at temperatures 0.5, 1.0, 1.5)
- [ ] Loss curve plot or log
- [ ] Brief report: what worked, what didn't, lessons learned
