# Lab 08: Multimodal Models — Quiz

**Q1.** A dual-encoder CLIP model produces...
- a) Generated captions
- b) One embedding per modality, compared by similarity
- c) Bounding boxes
- d) Token logits

**Q2.** CLIP's contrastive loss temperature `tau` matters because...
- a) It sets the image resolution
- b) It controls the sharpness of the similarity distribution and the gradient scale
- c) It defines the batch size
- d) It regularizes the encoder weights

**Q3.** In InfoNCE, every other item in the batch acts as...
- a) A positive
- b) A negative
- c) A neutral
- d) A mask

**Q4.** This is why contrastive training wants large batches:
- a) Larger batches reduce memory traffic
- b) More negatives make the task harder and improve representations
- c) Larger batches converge in fewer steps regardless of data
- d) It is required by the API

**Q5.** CLIP loss plateaus near `ln N` typically because...
- a) The model has converged perfectly
- b) The in-batch negatives are too easy
- c) The learning rate is too low
- d) The temperature is too high

**Q6.** A projector in a VLM is used to...
- a) Compress images to disk
- b) Map visual features into the LLM's embedding space and token budget
- c) Increase image resolution
- d) Generate captions

**Q7.** In cross-modal attention inside a decoder, the causal mask applies...
- a) To everything including visual tokens
- b) Only to the text segment; visual tokens are visible to all text positions
- c) Only to visual tokens
- d) Nowhere

**Q8.** Where do visual tokens usually sit in the sequence?
- a) After the text
- b) Before the text
- c) Interleaved per token
- d) In a separate attention pass

**Q9.** Patch count for 224x224 with P=16 is...
- a) 14
- b) 196
- c) 3136
- d) 224

**Q10.** Splitting a 1024x1024 image into tiles is motivated by...
- a) Lower file size
- b) Attention cost grows quadratically with token count, so resolution is expensive
- c) Better color accuracy
- d) Simpler augmentation

**Q11.** Standard multimodal training order is...
- a) SFT -> project -> pretrain vision
- b) Vision pretrain -> projector alignment -> instruction tuning -> preference
- c) Instruction tuning -> vision pretrain -> project
- d) Project -> preference -> pretrain

**Q12.** In stage 2 (projector alignment) you typically freeze...
- a) Only the projector
- b) Both encoders and train only the projector
- c) Only the LLM
- d) Nothing

**Q13.** For small text in images, the most likely failure is...
- a) Hallucinated objects
- b) Poor OCR due to coarse patches
- c) Counting errors
- d) Bias in captions

**Q14.** The dominant multimodal hallucination cause is...
- a) Weak vision encoder
- b) The language prior dominating weak visual evidence
- c) Low temperature
- d) Small batch size

**Q15.** Faithfulness evaluation for a VLM asks...
- a) Is the answer correct according to human preference?
- b) Is the answer supported by what is actually present in the image?
- c) Is the answer fluent?
- d) Is the answer short?

**Q16.** Counting and spatial reasoning are usually evaluated as...
- a) One combined score
- b) Separate dedicated suites, because they fail independently
- c) Only via CLIP score
- d) Human preference only

**Q17.** Text rendered inside an image must be treated as...
- a) System instructions
- b) Data, never instructions (prompt injection vector)
- c) Ignore entirely
- d) A tool call

**Q18.** Why use a dual encoder for retrieval but a VLM for answering?
- a) Retrieval must be cheap per item; answering must be precise per query
- b) The dual encoder is more accurate
- c) VLMs cannot search
- d) To avoid training the projector

---

## Answers

1. **b** — one embedding each, compared with cosine similarity.
2. **b** — `s_ij = z_i·t_j/tau`; small tau sharpens and enlarges gradients.
3. **b** — all non-matching in-batch items are negatives.
4. **b** — harder negatives improve the representation.
5. **b** — random negatives are trivially separable; use hard-negative mining.
6. **b** — the bridge from vision features into the LLM token space.
7. **b** — visual tokens are prior context; text tokens are causal.
8. **b** — visual tokens first, then the text prompt.
9. **b** — `(224/16)^2 = 14^2 = 196`.
10. **b** — token count drives quadratic attention cost and KV cache.
11. **b** — pretrain -> align -> instruct -> preference.
12. **b** — align the projector while the towers stay frozen.
13. **b** — fine detail needs finer patches or tiling.
14. **b** — the LM's prior fills in what the vision signal does not support.
15. **b** — grounded in image evidence, not in plausibility.
16. **b** — they are distinct, independent failure modes.
17. **b** — images are untrusted input; same rule as retrieved documents.
18. **a** — retrieval cost scales with corpus size, generation cost with query count.

## Score Guide

16-18: ready for ai-engineering labs 02, 03, 06.
12-15: redo Exercises 4, 9, 11.
0-11: reread THEORY sections 2-6.