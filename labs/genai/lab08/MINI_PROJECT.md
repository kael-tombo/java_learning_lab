# Lab 08: Multimodal Models — Mini Project

## Project: Contrastive Image-Text Search Engine from Scratch

Build a working multimodal retrieval system in pure Java: generate a synthetic image
corpus, encode images and queries with two trained encoders, index them, and answer
text queries with grounded citations — plus OCR, faithfulness, and bias evaluations.

## Goal

A CLI that takes a text query and returns ranked images with captions and a grounded
answer, where recall@3 on held-out queries exceeds 0.85, every citation resolves, and
the bias audit produces a measurable report.

## Requirements

### Phase 1: Synthetic Corpus
- [ ] Image format: 32x32 grayscale, 0-255.
- [ ] Generators: circle, square, line, triangle, with position/size/intensity params.
- [ ] Scenes composed of 1-5 objects; captions generated from ground truth.
- [ ] Corpus: 2,000 train scenes, 400 test scenes, plus 100 held-out query captions.
- [ ] Deterministic generation from a seed; images serialized to a compact format.

### Phase 2: Encoders
- [ ] Image encoder: patchify (P=8 -> 16 patches) -> linear to D=64 -> 2-layer MLP
      -> attention pool -> L2 normalize.
- [ ] Text encoder: bag-of-words hashing to 128 dims -> 2-layer MLP -> normalize.
- [ ] Verify both outputs are unit-norm (assert in tests).

### Phase 3: Contrastive Training
- [ ] Symmetric InfoNCE with max-subtracted logits.
- [ ] Analytic gradients verified against finite differences.
- [ ] Adam; batch 32; tau learned or fixed at 0.05.
- [ ] Batch-size sweep {8, 32, 128} to demonstrate hard-negative effect.
- [ ] Temperature sweep {0.01, 0.05, 0.1, 0.5}.

### Phase 4: Index and Retrieval
- [ ] Brute-force cosine index over all test images.
- [ ] Metrics: recall@1/3/5/10, MRR, mAP on held-out queries.
- [ ] Hard-negative mining: re-embed each epoch, upweight top-3 non-matching.
- [ ] Tiled encoding variant for 2x upsampled images; measure token-count effect.

### Phase 5: Grounded Answering
- [ ] Cross-modal attention with text-only causal masking (unit test both cases).
- [ ] Projector: linear, then Perceiver resampler to K=16 tokens.
- [ ] Answer stub that composes a response from the top-3 retrieved captions with
      `[i]` citations.
- [ ] `CitationChecker`: every `[i]` resolves to a retrieved image id.
- [ ] `FaithfulnessCheck`: every noun in the answer appears in retrieved captions.

### Phase 6: OCR and Bias
- [ ] Render digits/letters into the image format; OCR stub reads them.
- [ ] Character error rate at 3 rendered sizes; demonstrate the resolution effect.
- [ ] Bias audit: brightness / object size / background sweeps; word-frequency table.

### Phase 7: Injection Defense
- [ ] Render adversarial instruction text into images.
- [ ] Guardrail flags it; assert parser never treats image text as instructions.

## Directory Layout

```
lab08/
  src/com/genai/lab08/{image,vision,text,clip,fusion,pipeline,eval}/
  corpus/images/
  corpus/queries.jsonl
  out/index.bin
  out/metrics.json
  Main.java
  REPORT.md
```

## Milestones

1. **M1** — corpus generator; 2,400 scenes written; captions from ground truth.
2. **M2** — encoders return unit-norm vectors; index built.
3. **M3** — gradient check vs finite differences passes at 1e-6.
4. **M4** — contrastive training: train recall@1 > 0.9.
5. **M5** — held-out recall@3 > 0.85; batch and temperature sweeps written.
6. **M6** — cross-modal attention unit tests pass (visual visible, text causal).
7. **M7** — resampler reduces 16 tokens to K=8 with no recall loss.
8. **M8** — citations 100% valid; faithfulness rate reported.
9. **M9** — OCR CER curve across sizes; bias table; injection canaries all caught.

## Acceptance Criteria

- [ ] recall@3 >= 0.85 on held-out queries with 400 images.
- [ ] recall@3 improves with larger batches (hard-negative effect demonstrated).
- [ ] Temperature sweep shows an interior optimum.
- [ ] 100% of citations resolve to retrieved image ids.
- [ ] Cross-modal attention passes both unit tests.
- [ ] Faithfulness rate reported with failure list.
- [ ] OCR CER strictly increases as rendered size shrinks.
- [ ] All injection canaries flagged.

## Stretch Goals

- [ ] SigLIP-style sigmoid loss and a convergence comparison.
- [ ] Hard-negative mining with a measured recall gain.
- [ ] Grounding: emit bounding boxes, report IoU@0.5 and @0.75.
- [ ] Counting: add a counting head and compare against free-form generation.
- [ ] DPO on faithfulness pairs (chosen faithful, rejected hallucinatory).
- [ ] Streaming video: multi-frame encoding with temporal position handling.
- [ ] Caption generation (autoregressive stub over vocabulary) with CIDEr-like proxy.
- [ ] Multi-vector per image (global + region) and the retrieval gain.
- [ ] Tiled encoding for high-res scenes; compare against downscale.

## Failure Modes to Watch For

| Symptom | Likely cause |
|---------|--------------|
| Loss plateaus at `ln N` | Negatives too easy; need hard-negative mining |
| Gradients ~0 for correct pairs | Working as intended; lower `tau` to keep signal |
| Retrieval good, answers wrong | Projector not trained, or visual tokens misaligned |
| Answers cite images not retrieved | Prompt image ordering differs from citation indexing |
| `ArrayIndexOutOfBounds` in patchify | H or W not divisible by P |
| Faithfulness near 0 | Answer composed from prior, not from retrieved captions |
| Bias table empty | Sweep too small; need controlled variation |
| OCR always wrong | Patches coarser than glyph strokes; reduce P or tile |

## Definition of Done

`REPORT.md` contains: corpus stats, encoder architecture, the batch and temperature
sweeps, retrieval metric table, three example queries with retrieved images and
grounded answers, the OCR CER curve, the bias table, injection canary results, and a
"where does this break first in production" section.