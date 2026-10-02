# 20-fine-tuning — Theory

## 1. Why Fine-Tune?

### Pretraining vs Fine-Tuning
| Phase | Data | Objective | Compute |
|-------|------|-----------|---------|
| **Pretraining** | Trillions of tokens | Next-token prediction (self-supervised) | Massive (GPU-months) |
| **Fine-Tuning** | Thousands-Millions tokens | Task-specific (supervised/RL) | Modest (GPU-hours) |

### Transfer Learning Hypothesis
Pretrained models learn **general representations** (syntax, semantics, world knowledge, reasoning patterns). Fine-tuning **specializes** these representations for a specific domain or task.

---

## 2. Fine-Tuning Paradigms

### Full Fine-Tuning
- Update **all** model parameters
- Best performance when data/compute sufficient
- High memory: model + gradients + optimizer states (3-4x model size)
- Risk of **catastrophic forgetting**

### Parameter-Efficient Fine-Tuning (PEFT)
Freeze most pretrained weights, train only a small subset.

| Method | Trainable Params | Memory | Quality |
|--------|------------------|--------|---------|
| **LoRA** | ~0.1-1% | Low | ★★★★★ |
| **QLoRA** | ~0.1-1% | Very Low (4-bit) | ★★★★☆ |
| **Prefix Tuning** | ~0.01% | Low | ★★★☆☆ |
| **Adapters** | ~0.5-1% | Medium | ★★★★☆ |
| **Prompt Tuning** | ~0.001% | Very Low | ★★☆☆☆ |

---

## 3. LoRA Deep Dive

### Mathematical Formulation
For a pretrained weight matrix $W_0 \in \mathbb{R}^{d \times k}$:
$$\Delta W = B A, \quad B \in \mathbb{R}^{d \times r}, A \in \mathbb{R}^{r \times k}$$
$$W = W_0 + \frac{\alpha}{r} \Delta W$$

### Why Low Rank Works
1. **Intrinsic Dimension**: Fine-tuning updates lie in low-dimensional subspace (Aghajanyan et al., 2021)
2. **Overparameterization**: Pretrained models are highly overparameterized
3. **Gradient Alignment**: Pretrained gradients already point in useful directions

### Where to Apply LoRA
| Component | Recommended? | Reason |
|-----------|--------------|--------|
| $W_q, W_k, W_v$ | ✅ Yes | Most impactful |
| $W_o$ | ✅ Yes | Output projection |
| FFN ($W_{up}, W_{down}$) | ⚠️ Optional | More params, diminishing returns |
| Embeddings | ❌ No | Large vocab, different distribution |
| LayerNorm | ❌ No | Few params, critical for stability |

### LoRA Hyperparameters
| Hyperparameter | Typical Range | Notes |
|----------------|---------------|-------|
| **Rank $r$** | 4-64 | 8, 16, 32 common |
| **Alpha $\alpha$** | 16-64 | Often $\alpha = 2r$ or $4r$ |
| **Dropout** | 0.05-0.1 | On LoRA path |
| **Target Modules** | attention only | "all-linear" for max quality |

---

## 4. QLoRA: 4-bit Fine-Tuning

### Innovation Stack
1. **NF4 Quantization**: Optimal quantization for normal-distributed weights
2. **Double Quantization**: Quantize quantization constants (save 0.37 bits/param)
3. **Paged Optimizers**: Offload optimizer states to CPU
4. **LoRA on 4-bit**: Train only LoRA adapters

### Memory Comparison (7B Model)
| Method | Model | Gradients | Optimizer | Total |
|--------|-------|-----------|-----------|-------|
| Full FT (FP16) | 14 GB | 14 GB | 56 GB | **84 GB** |
| LoRA (FP16) | 14 GB | 0.1 GB | 0.4 GB | **14.5 GB** |
| QLoRA (4-bit) | **3.5 GB** | 0.1 GB | 0.4 GB | **4 GB** |

**QLoRA enables 7B fine-tuning on 24GB GPU (or 33B on 48GB)**.

---

## 5. Instruction Tuning & Alignment

### Supervised Fine-Tuning (SFT)
Train on high-quality instruction-response pairs:
```
### Instruction:
Write a Python function to compute fibonacci numbers.

### Response:
def fibonacci(n):
    if n <= 1: return n
    return fibonacci(n-1) + fibonacci(n-2)
```

### RLHF Pipeline
1. **SFT**: Fine-tune on demonstrations
2. **Reward Model**: Train $r_\phi(x, y)$ on human comparisons
3. **PPO**: Optimize $\pi_\theta$ to maximize $r_\phi$ with KL penalty

### DPO (Direct Preference Optimization)
Eliminates reward model + RL:
$$\mathcal{L}_{DPO} = -\mathbb{E}[\log \sigma(\beta \log \frac{\pi_\theta(y_w|x)}{\pi_{ref}(y_w|x)} - \beta \log \frac{\pi_\theta(y_l|x)}{\pi_{ref}(y_l|x)})]$$

**Advantages**: Simpler, no reward model, no PPO instability, works with LoRA.

---

## 6. Data Considerations

### Data Quality > Quantity
- **1000 high-quality examples** > 100k noisy examples
- Curate: deduplicate, filter toxic, verify correctness
- Format: consistent prompt/response template

### Data Mixing
For domain adaptation, mix:
- Target domain data (primary)
- General instruction data (prevent forgetting)
- Synthetic data (augment)

### Length Considerations
- Pack sequences to max length (e.g., 2048, 4096)
- Use **sequence packing** (concatenate multiple examples)
- Attention mask separates examples

---

## 7. Training Best Practices

### Learning Rate
- **LoRA**: $10^{-4}$ to $3 \times 10^{-4}$ (higher than full FT)
- **Full FT**: $10^{-5}$ to $5 \times 10^{-5}$
- **QLoRA**: Same as LoRA

### Scheduler
- **Cosine with warmup** (standard)
- **Constant with warmup** (for LoRA, often works better)
- Warmup: 2-5% of steps

### Batch Size & Gradient Accumulation
- Effective batch: 32-128
- Gradient accumulation for large models
- Sequence packing maximizes GPU utilization

### Regularization
- **Weight decay**: 0.01-0.1 (AdamW)
- **LoRA dropout**: 0.05-0.1
- **Label smoothing**: 0.1 (optional)

### Mixed Precision
- **BF16** (Ampere+ GPUs): Preferred, stable
- **FP16**: Needs loss scaling
- **FP8** (H100): Emerging

---

## 8. Evaluation

### Benchmarks
| Task | Benchmark | Metric |
|------|-----------|--------|
| **General** | MMLU, BBH, AGIEval | Accuracy |
| **Code** | HumanEval, MBPP | Pass@k |
| **Math** | GSM8K, MATH | Accuracy |
| **Chat** | MT-Bench, AlpacaEval | Elo / Win rate |
| **Safety** | TruthfulQA, ToxiGen | Accuracy / Toxicity |

### Qualitative Evaluation
- **Diversity**: n-gram entropy, distinct-n
- **Coherence**: Perplexity on held-out
- **Faithfulness**: Citation accuracy for RAG
- **Safety**: Red-teaming, refusal rates

---

## 9. Deployment Considerations

### Merging LoRA Weights
After training, merge LoRA into base model for inference:
$$W_{merged} = W_0 + \frac{\alpha}{r} B A$$

**Benefits**: No inference overhead, standard model format.

**Caveat**: Cannot easily switch tasks (need separate merges per task).

### Quantized Inference
- **GGUF/GGML**: CPU/MPS inference (llama.cpp)
- **AWQ/GPTQ**: GPU inference (vLLM, TensorRT-LLM)
- **EXL2**: Fast 4-bit GPU

### Serving Stack
| Component | Options |
|-----------|---------|
| **Engine** | vLLM, TensorRT-LLM, TGI, llama.cpp |
| **Batching** | Continuous batching, PagedAttention |
| **Scaling** | Tensor parallel, pipeline parallel |

---

## 10. Common Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| **LR too high** | Loss diverges, NaN | Reduce LR, check gradients |
| **LR too low** | No learning | Increase LR, check scheduler |
| **Rank too low** | Underfitting | Increase $r$ (8→16→32) |
| **Rank too high** | Overfitting, slow | Decrease $r$, add dropout |
| **Catastrophic forgetting** | Poor on original tasks | Add replay data, increase $\alpha$ |
| **OOM** | CUDA OOM | QLoRA, gradient accumulation, smaller batch |
| **Divergent DPO** | Reward hacking | Reduce $\beta$, check reference model |
| **Bad data** | Hallucinations, errors | Clean data, verify samples |

---

## 11. Interview Quick Reference

**Q**: "Explain LoRA in one sentence."
**A**: Freeze pretrained weights, add trainable low-rank matrices $BA$ to approximate fine-tuning updates.

**Q**: "Why zero-initialize $B$ in LoRA?"
**A**: Ensures $\Delta W = 0$ at step 0, so model starts exactly as pretrained. Random init would add noise.

**Q**: "QLoRA vs LoRA — what's the difference?"
**A**: QLoRA quantizes frozen weights to 4-bit (NF4), uses double quantization + paged optimizers. Trains same LoRA adapters.

**Q**: "When would you use full fine-tuning over LoRA?"
**A**: Sufficient compute/memory, large domain shift (code→math), need maximum quality, long training runs.

**Q**: "How does DPO work without a reward model?"
**A**: Uses preference pairs $(y_w, y_l)$ directly. Optimizes policy to increase $\log \pi(y_w) - \log \pi(y_l)$ relative to reference model.

**Q**: "What is catastrophic forgetting and how does LoRA help?"
**A**: Fine-tuning overwrites pretrained knowledge. LoRA helps by keeping $W_0$ frozen — pretrained features preserved.

**Q**: "How do you merge LoRA weights for deployment?"
**A**: $W_{merged} = W_0 + \frac{\alpha}{r}BA$. Single forward pass, no adapter overhead.