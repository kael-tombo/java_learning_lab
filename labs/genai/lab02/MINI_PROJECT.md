# Lab 02: GPT Architecture — Mini Project

## Project: Character-Level GPT Language Model in Java

Build, train, and sample from a decoder-only language model from scratch — no ML
framework, plain Java 21 arrays and loops.

## Goal

A model that, given a prompt, generates coherent character sequences. Measure
training loss, perplexity, and generation quality against a random-weight and
bigram baseline.

## Requirements

### Phase 1: Data Pipeline
- [ ] Load a text corpus (min 200 KB). Sources: a public-domain book, a repo
      `README`, or a synthetic template generator.
- [ ] Byte-level vocabulary (256 symbols) — no OOV handling needed.
- [ ] `Dataset` yields fixed-length windows with a stride; targets = input + 1.
- [ ] Print corpus stats: chars, tokens, unique bytes, avg bytes/char.

### Phase 2: Model
- [ ] `MiniGpt(config)` with dModel, nHeads, nLayers, context, vocab.
- [ ] Token embedding + sinusoidal positional encoding.
- [ ] Causal self-attention with additive mask.
- [ ] SwiGLU MLP (or GELU MLP for simplicity).
- [ ] Pre-norm residual blocks.
- [ ] Tied embedding / LM head.
- [ ] Deterministic weight init (seeded `java.util.Random`, documented scale).

### Phase 3: Training
- [ ] SGD with momentum, then AdamW; warmup + cosine decay.
- [ ] Gradient clipping by global norm (threshold 1.0).
- [ ] Track: loss, tokens/sec, lr, grad norm per step.
- [ ] Hold out 5% for validation loss.

### Phase 4: Generation
- [ ] `generate(prompt, maxNew, temp, topK, topP, seed)`.
- [ ] KV cache enabled; toggle to show the speed difference.
- [ ] Stream output character by character to a `PrintWriter` flush per char.

### Phase 5: Evaluation
- [ ] Perplexity on the validation split.
- [ ] Bigram baseline perplexity for comparison.
- [ ] Greedy vs temperature-0.8 sampling: three samples each.
- [ ] Latency table: tokens/sec with and without KV cache at context 128/512/2048.

## Suggested Config

| Field | Value |
|-------|-------|
| dModel | 128 |
| nHeads | 4 |
| nLayers | 4 |
| context | 256 |
| vocab | 256 (bytes) |
| batch | 16 |
| lr | 3e-4 (AdamW) |
| steps | 3000 |
| params | ~0.9M |

## Directory Layout

```
lab02/
  src/com/genai/lab02/
    config/ModelConfig.java
    data/Corpus.java, Window.java
    model/MiniGpt.java, Block.java, Attention.java, Mlp.java
    norm/RmsNorm.java
    token/ByteVocab.java
    cache/KvCache.java
    optim/AdamW.java
    sample/Sampler.java
    eval/Perplexity.java
    Main.java
  out/classes/
  out/samples/
  REPORT.md
```

## Milestones

1. **M1** — corpus loads, windows iterate, vocab round-trips.
2. **M2** — forward pass runs; loss decreases over 200 steps (overfit one batch).
3. **M3** — attention mask verified by a unit test asserting future positions
   have exactly zero weight.
4. **M4** — full training run, validation loss below the unigram baseline.
5. **M5** — generation produces the prompt as a prefix plus plausible continuation.
6. **M6** — KV cache correctness: cached vs uncached logits match within 1e-9.
7. **M7** — benchmark table written into `REPORT.md`.

## Acceptance Criteria

- [ ] `javac`/`java` runs from a clean checkout with no external libraries.
- [ ] Validation perplexity < 60% of the unigram baseline.
- [ ] Generated text contains at least one long (8+ char) substring from training.
- [ ] A unit test proves the causal mask: perturbing token at t=5 does not change
      the loss contribution at t=2.
- [ ] KV cache speeds up 100-token decoding by >3x at context 2048.

## Stretch Goals

- [ ] Grouped-query attention: drop KV heads by 4x, measure perplexity change.
- [ ] Beam search with length normalization; compare to greedy on 20 prompts.
- [ ] Digram-level perplexity floor as a sanity bound.
- [ ] Mini-BPE (merge up to 512 symbols) and show bytes-per-char improvement.
- [ ] Sample from a temperature sweep `[0.3, 0.7, 1.0, 1.3]` and write a
      qualitative diversity analysis.
- [ ] Export the trained weights to a simple binary format and a tiny inference CLI.

## Failure Modes to Watch For

| Symptom | Likely cause |
|---------|--------------|
| Loss stuck at ln(256) = 5.55 | Mask or target offset bug |
| Loss explodes at step ~200 | lr too high, or no grad clipping |
| NaN after warmup | softmax without max subtraction |
| Generated text repeats one char | undertrained, or top-k=1 with degenerate logits |
| Cached != uncached logits | mask indexing uses cached length vs current length |

## Definition of Done

`REPORT.md` contains: config, loss curve (ASCII plot), perplexity table, five
generated samples, latency table, and a "what I'd change next" section.