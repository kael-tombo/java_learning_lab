# Lab 08: Multimodal Models — Theory

## 1. Why Multimodal

Text-only models are blind. Multimodal models fuse modalities — text, images, audio,
video, point clouds — into one representation space so a single model can reason
across them. The design problem is **alignment**: mapping heterogeneous inputs into a
space where "a photo of a dog" and "a dog" land near each other.

## 2. Two Architectures

```
(a) DUAL ENCODER (contrastive, retrieval-style)
     image ──> vision encoder ──> v ┐
                                    ├──> cosine sim ──> score
     text  ──> text encoder   ──> t ┘

(b) CROSS-ATTENTION (generative, VLM-style)
     image ──> vision encoder ──> visual tokens ──┐
                                                    ├──> LLM decoder
     text   ──> tokenizer ──> text tokens ─────────┘        │
                                                             v
                                                          next text token

dual encoder: cheap retrieval, one embedding per item, no generation
cross-attention: expensive, but handles generation, reasoning, OCR, counting
```

Most production systems use **both**: a dual encoder for retrieval (finding the
right image/passage) and a cross-attention VLM for answering about it.

## 3. Image Representation

### 3.1 Patch Embedding (ViT)

An image `H x W x 3` is split into patches of size `P x P`, giving `N = HW/P^2`
patches. Each patch is flattened and linearly projected:

```
x_patches in R^{N x (P^2 * 3)}
z = x_patches W_patch + b       W_patch in R^{(P^2*3) x D}
```

For 224x224 with P=16: `N = 196` tokens. Prepend a `[CLS]` token -> 197.
Position embeddings are learned and added.

### 3.2 Convolutional Features

CNNs produce feature maps, then either a global average pool (single vector, loses
spatial detail) or flattened region features (multiple tokens, better for
localization and OCR). Vision feature maps: `H/stride x W/stride x C`.

### 3.3 Resolution and Tiling

High-resolution images need more tokens (cost is quadratic in sequence length for
attention). Techniques: tiling into overlapping crops, dynamic resolution (Native
Dynamic Resolution), or multi-scale encoders.

## 4. Contrastive Pre-training (CLIP-style)

Given `N` matched (image, text) pairs, learn two encoders with a symmetric
InfoNCE loss:

```
z_i = normalize(vision(image_i)),  t_i = normalize(text(caption_i))
s_ij = exp(z_i . t_j / tau) / sum_k exp(z_i . t_k / tau)     (image->text)
L = (1/2N) * [ sum_i -log s_ii + sum_i -log t_ii ]          (symmetric)
```

Temperature `tau` is critical (typically 0.01-0.07, learned). Small `tau`
sharpens the distribution and increases the gradient signal.

Gradients couple the two encoders:

```
dL/dz_i = (1/tau) * ( (softmax(z_i . T / tau))_i - 1 ) * t_i
dL/dt_j = (1/tau) * ( (softmax(T . t_j / tau))_j - 1 ) * z_j
```

### Why it works: batch size is a free negative-sampling engine

Every other image in the batch is a negative for `z_i`. Larger batches -> harder
negatives -> better representations. This is why contrastive training wants the
biggest batches the hardware allows.

## 5. Contrastive Loss Mechanics

With logits `s_ij = z_i . t_j / tau`, the loss is:

```
L = (1/N) sum_i [ -log( exp(s_ii) / sum_j exp(s_ij) ) ]
```

Symmetric version averages both directions. Numerically stable form (subtract
row/col max before exponentiating) is mandatory — logits can reach `1/tau` scale.

A useful diagnostic: if the loss plateaus near `ln N`, the batch negatives are too
easy (need hard-negative mining); if it oscillates, the temperature is too low.

## 6. Multimodal Fusion Strategies

| Strategy | Description | Cost | Use |
|----------|-------------|------|-----|
| Early fusion | Concatenate raw features, one encoder | Low | Same modality, aligned data |
| Late fusion | Separate encoders, combine scores/decisions | Low | Retrieval, ensembles |
| Cross-attention | One modality attends to the other | Medium | Captioning, VQA, agents |
| Projector/resampler | Vision -> fixed-length tokens for an LLM | Medium | Feeding a pretrained LLM |
| Mixture of experts | Sparse experts per modality | High | Large-scale generalists |

The **projector** is the component that makes modern VLMs work: a small MLP (or
Perceiver resampler / Q-Former) maps variable-length visual features into the LLM's
embedding space and token budget.

## 7. Cross-Modal Attention Details

```
Q = W_q [text tokens]        (from the LLM)
K = W_k [text ; visual]      V = W_v [text ; visual]
A = softmax(QK^T / sqrt(d) + causal_mask_on_text_part)
```

- **Causal masking** applies only to the text segment; visual tokens are visible to
  every text position (they are "already known" context).
- Visual tokens usually come *before* the text tokens in the sequence.
- Position ids for visual tokens are typically all zeros or 1, while text tokens get
  their true positions.

## 8. Vision Encoders

| Encoder | Idea | Notes |
|---------|------|-------|
| ViT | Pure transformer on patches | Scales well; needs lots of data |
| CLIP ViT | ViT trained contrastively | General visual features |
| SigLIP | Sigmoid loss instead of softmax | Better scaling behavior |
| ConvNeXt | CNN modernized | Strong local features, cheap |
| SAM encoder | Masked image modeling | Excellent dense features |
| BLIP-2 Q-Former | Query transformer | Compresses to fixed tokens |

## 9. Training Recipes

**Stage 1 — vision pretraining**: self-supervised (MAE, DINO) or contrastive (CLIP)
on image-text pairs. Produces the vision tower.

**Stage 2 — projector alignment**: freeze both towers, train only the projector on
image-caption pairs so visual tokens live in the LLM's embedding space.

**Stage 3 — instruction tuning**: freeze vision tower (sometimes unfreeze late), train
projector + LLM on VQA, OCR, grounding, and multi-turn conversation data. LoRA on the
LLM is standard.

**Stage 4 — preference optimization**: DPO on human preference over model answers
(Lab 07), including helpfulness *and* visual faithfulness.

## 10. Multimodal RAG

The dominant production pattern:

```
query (text) --> text encoder --> embedding
                                    |
                          CLIP dual-encoder index (Lab 04 infra)
                                    |
                        top-k images / pages
                                    |
                  VLM answers with visual context + citations
```

Why a dual encoder for retrieval and a VLM for answering: retrieval must be cheap
per million items; answering must be precise per query.

## 11. Evaluation

- **Retrieval**: recall@k on image-text matching, mAP for cross-modal retrieval.
- **Generation**: CIDEr, BLEU, SPICE for captioning; exact-match/F1 for VQA.
- **Faithfulness**: does the answer follow from the *image* (hallucination risk is
  highest here — models describe what they expect rather than what is present)?
- **OCR robustness**: exact string match on rendered text.
- **Counting and spatial reasoning**: separate suites; both are classic failure modes.
- **Bias**: demographic skew in generated descriptions (Lab 09).
- **Safety**: harmful content in both images and text.

## 12. Failure Modes

| Failure | Cause | Mitigation |
|---------|-------|------------|
| Hallucinated objects | Language prior dominates visual evidence | Faithfulness training; ask for evidence quotes |
| Poor OCR | Patches too coarse for small text | Higher resolution, tiling, OCR-aware pretraining |
| Counting errors | No explicit counting supervision | Counting data in stage 3 |
| Spatial confusion | Weak positional signal | Grounding data (bbox supervision) |
| Bias in captions | Training corpus skew | Balanced data; bias audit suite |
| Over-refusal | Safety tuning over-applied | Calibrate refusal thresholds per category |
| Prompt injection via images | Text inside an image is an input | Treat image text as data, never instructions |

## Key Equations

```
L_clip = (1/2N) * [ CE(Z, T) + CE(T, Z) ],  s_ij = z_i . t_j / tau
Attn = softmax(QK^T/sqrt(d) + M_text_causal) V,  M over the text block only
L_VLM = -sum_t m_t log P(y_t | image, y_<t)
```