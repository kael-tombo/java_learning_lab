# Lab 08: Multimodal Models — Flashcards

| # | Front | Back |
|---|-------|------|
| 1 | Multimodal | Fuse text/image/audio/video into one representation space |
| 2 | Alignment | Making "photo of a dog" and "dog" land near each other |
| 3 | Dual encoder | Separate vision/text towers compared by similarity |
| 4 | Cross-attention VLM | Visual tokens attended by an LLM decoder |
| 5 | Production pattern | Dual encoder for retrieval + VLM for answering |
| 6 | Patch count | `N = (H/P) * (W/P)`; 224/16 -> 196 |
| 7 | Patch embed | Flatten `P*P*3` then linear project to `D` |
| 8 | CLS token | Prepended summary token; index 0 |
| 9 | Position embedding | Learned, added to patch embeddings |
| 10 | Conv features | Feature map; global pool loses spatial detail |
| 11 | Region features | Flattened map cells as tokens; better for OCR/grounding |
| 12 | Tiling | Overlapping crops to keep resolution without huge token counts |
| 13 | CLIP logits | `s_ij = z_i . t_j / tau` |
| 14 | InfoNCE | Softmax CE over in-batch candidates |
| 15 | Symmetric loss | Average image->text and text->image directions |
| 16 | Temperature typical | 0.01-0.07, often learned |
| 17 | Small tau | Sharper distribution, larger gradients |
| 18 | Loss plateau at ln N | Negatives too easy |
| 19 | Batch as negative miner | Every other in-batch item is a negative |
| 20 | Bigger batch benefit | Harder negatives, better representations |
| 21 | Stable log-softmax | Subtract row max before exp |
| 22 | dL/dz | `(1/tau)(softmax_ii - 1) * t_i` |
| 23 | dL/dt | `(1/tau)(softmaxT_jj - 1) * z_j` |
| 24 | Hard negatives | Top-k non-matching items by similarity |
| 25 | SigLIP | Sigmoid pairwise loss + learned biases |
| 26 | Vision encoders | ViT, CLIP ViT, ConvNeXt, SAM encoder, BLIP-2 Q-Former |
| 27 | MAE/DINO | Masked and self-distillation vision pretraining |
| 28 | Stage 1 | Vision tower pretraining |
| 29 | Stage 2 | Projector alignment, both towers frozen |
| 30 | Stage 3 | Instruction tuning (projector + LLM, LoRA on LLM) |
| 31 | Stage 4 | Preference optimization (DPO) |
| 32 | Projector | `D_v -> D_l` linear, or Perceiver resampler to K tokens |
| 33 | Q-Former | Learned queries compressing visual features |
| 34 | Cross-attn Q | From text/LLM states |
| 35 | Cross-attn KV | Concatenated `[text ; visual]` |
| 36 | Causal mask scope | Text block only; visual tokens fully visible |
| 37 | Visual token placement | Before the text tokens |
| 38 | Visual position ids | Usually constant (0/1), text gets true positions |
| 39 | Early fusion | Concatenate raw features |
| 40 | Late fusion | Separate encoders, combine scores |
| 41 | MoE fusion | Sparse modality experts |
| 42 | Multimodal RAG | Text query -> CLIP index -> top-k images -> VLM answer |
| 43 | Retrieval metrics | recall@k, mAP for cross-modal retrieval |
| 44 | Captioning metrics | CIDEr, BLEU, SPICE |
| 45 | VQA metrics | Exact match, F1 |
| 46 | Faithfulness | Supported by actual image content |
| 47 | Hallucination cause | Language prior beats weak visual evidence |
| 48 | OCR failure | Coarse patches miss small text |
| 49 | OCR fix | Higher resolution, tiling, OCR-aware pretraining |
| 50 | Counting failure | No counting supervision |
| 51 | Spatial failure | Weak positional signal; needs grounding data |
| 52 | Grounding data | Bounding-box supervision; IoU metric |
| 53 | Caption bias | Corpus skew in attribute descriptions |
| 54 | Bias audit | Controlled attribute sweeps, word counts |
| 55 | Over-refusal | Safety tuning over-applied; calibrate per category |
| 56 | Image injection | Text inside images is untrusted input |
| 57 | Injection defense | Data labeling + schema validation, not pixel regex |
| 58 | Refusal threshold | Per-category calibration |
| 59 | Aspect ratio | Non-square inputs resized or padded |
| 60 | Normalization | Images scaled to a documented mean/std |
| 61 | Patch embedding dim | D often 768-1024 for ViT-L/14 |
| 62 | ViT-L/14 | 224/14 = 16x16 = 256 patches |
| 63 | Attention cost | Quadratic in token count; resolution is expensive |
| 64 | Token budget | Visual tokens compete with text for the LLM context |
| 65 | KV cache impact | Visual tokens cache once, text grows per step |
| 66 | Streaming video | Frame sampling, temporal position handling |
| 67 | Audio towers | Whisper-style encoders feeding the same projector |
| 68 | Late fusion vs cross | Late for retrieval, cross for reasoning |
| 69 | Retrieval cost scales | With corpus size |
| 70 | Generation cost scales | With query count |

## Self-Check

55+ = solid, 45-54 = redo Exercises 4 and 9, below that reread THEORY 2-6.