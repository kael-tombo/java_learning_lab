# Lab 06: Fine-Tuning with LoRA/QLoRA — Quiz

## Questions

**Q1.** LoRA's core assumption is that the fine-tuning update has...
- a) High rank
- b) Low intrinsic rank
- c) Zero mean
- d) Sparse gradients

**Q2.** How are LoRA parameters initialized?
- a) Both A and B random
- b) A random (small), B zero
- c) A zero, B random
- d) Both from the pretrained weights

**Q3.** With `B = 0` at init, the adapted model behaves as...
- a) A randomly perturbed model
- b) Exactly the pretrained model
- c) An untrained model
- d) A quantized model

**Q4.** Why is `B = 0` initialization a correctness requirement?
- a) It saves memory
- b) It guarantees `W = W0` exactly at step 0
- c) It speeds up the optimizer
- d) It prevents overfitting

**Q5.** Immediately after init, the gradient w.r.t. `A` is...
- a) Nonzero
- b) Zero, because `B = 0`
- c) Infinite
- d) Undefined

**Q6.** LoRA scaling is `alpha / r` (or `alpha/sqrt(r)` in rsLoRA). Its purpose is...
- a) Normalizing the input
- b) Setting the effective learning rate on the update
- c) Reducing parameter count
- d) Quantizing weights

**Q7.** For a 4096x4096 projection at r=16, LoRA parameters are about...
- a) 16M
- b) 131k (~0.8% of the full matrix)
- c) 8M
- d) 262k per layer, unchanged by r

**Q8.** Which modules normally receive LoRA adapters?
- a) Only the LM head
- b) Attention q/k/v/o and MLP gate/up/down
- c) Only embeddings
- d) Layer norms only

**Q9.** Merging LoRA into base weights produces...
- a) A larger model
- b) A standalone checkpoint with no adapter needed at inference
- c) A quantized model
- d) A distilled model

**Q10.** Why keep adapters unmerged in production?
- a) Faster inference always
- b) Cheap adapter swapping, rollback, and no base duplication
- c) Merging loses accuracy
- d) Required by some APIs

**Q11.** NF4's design rationale is...
- a) Uniform bin spacing
- b) Quantile bins of a normal distribution
- c) Random bin placement
- d) Logarithmic spacing

**Q12.** Double quantization in QLoRA removes...
- a) The base weights
- b) The fp16 scale constants (by quantizing them too)
- c) The optimizer
- d) The LoRA matrices

**Q13.** Paged optimizers address...
- a) Slow kernels
- b) Memory fragmentation during gradient checkpointing
- c) Low accuracy
- d) Slow data loading

**Q14.** Typical 4-bit QLoRA training memory for a 7B model is about...
- a) 84 GB
- b) 6-8 GB
- c) 140 GB
- d) 2 GB

**Q15.** Symmetric quantization is inferior to asymmetric mainly when...
- a) Weights are zero-mean
- b) The value range is offset from zero
- c) Bits are fewer than 8
- d) Blocks are small

**Q16.** When training a chat model, prompt tokens should usually be...
- a) Included in the loss
- b) Masked out of the loss
- c) Duplicated
- d) Replaced with EOS

**Q17.** LoRA typically uses a learning rate roughly...
- a) 10x higher than full fine-tuning
- b) 10x lower
- c) Identical, always
- d) Zero

**Q18.** If your adapter has no effect at inference, the most likely cause is...
- a) The corpus was too small
- b) The adapter was not merged, or `scaling` mismatched
- c) Too many epochs
- d) Wrong rank

---

## Answers

1. **b** — the update is approximated with rank `r`.
2. **b** — random `A`, zero `B`, so the product vanishes.
3. **b** — `W = W0 + scaling*0 = W0`.
4. **b** — you want to start from the pretrained function, not a perturbation of it.
5. **b** — `dL/dA` is proportional to `B`, which is zero.
6. **b** — it controls how strongly the update moves the weights.
7. **b** — `16 * (4096 + 4096) = 131,072` vs `16.7M` full = 0.78%.
8. **b** — those are the linear projections; embeddings/LM head usually stay frozen.
9. **b** — `W0 + scaling*B*A` is a plain weight matrix.
10. **b** — multi-tenant swapping and rollback, at the cost of adapter loading.
11. **b** — bins sit where normal-distributed weights actually cluster.
12. **b** — otherwise the scales themselves cost fp16 memory.
13. **b** — allocator spikes fragment the pool; paging defers to host memory.
14. **b** — ~3.5 GB weights + ~0.4 GB scales + small optimizer/activations.
15. **b** — asymmetric adds a zero-point to center the range.
16. **b** — otherwise you train the model to echo user turns.
17. **a** — only ~0.1-1% of parameters are trained, so a larger LR is stable.
18. **b** — check merge and `alpha/r` before blaming the data.

## Score Guide

16-18: ready for Lab 07 (RLHF) and ai-engineering lab10.
12-15: redo Exercises 3, 4, 11.
0-11: reread THEORY sections 2-9.