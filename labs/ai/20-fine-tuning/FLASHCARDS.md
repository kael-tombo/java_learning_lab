# 20-fine-tuning — Flashcards

## Core Concepts

| Term | Definition |
|------|------------|
| **Fine-Tuning** | Adapting pretrained model to downstream task with task-specific data |
| **PEFT** | Parameter-Efficient Fine-Tuning: freeze most weights, train small subset |
| **LoRA** | Low-Rank Adaptation: $\Delta W = BA$, rank $r \ll d$ |
| **QLoRA** | Quantized LoRA: 4-bit base model + LoRA adapters |
| **SFT** | Supervised Fine-Tuning: next-token prediction on instruction data |
| **RLHF** | Reinforcement Learning from Human Feedback (PPO + reward model) |
| **DPO** | Direct Preference Optimization: direct optimization on preference pairs |
| **Catastrophic Forgetting** | Loss of pretrained capabilities after fine-tuning |

---

## LoRA Essentials

### Formula
$$W = W_0 + \frac{\alpha}{r} B A$$
- $W_0 \in \mathbb{R}^{d \times k}$: Frozen pretrained weights
- $B \in \mathbb{R}^{d \times r}$, $A \in \mathbb{R}^{r \times k}$: Trainable
- $r$: Rank (typically 4-64)
- $\alpha$: Scaling factor (typically 16-64, often $\alpha = 2r$ or $4r$)

### Parameter Count
| Layer Size | $r=8$ | $r=16$ | $r=32$ | $r=64$ |
|------------|-------|--------|--------|--------|
| $4096 \times 4096$ | 65K (0.39%) | 131K (0.78%) | 262K (1.56%) | 524K (3.13%) |
| $4096 \times 11008$ (FFN) | 120K | 240K | 480K | 960K |

### Initialization
| Matrix | Initialization | Reason |
|--------|----------------|--------|
| $A$ | $\mathcal{N}(0, 0.02^2)$ | Random direction for exploration |
| $B$ | Zeros | $\Delta W = 0$ at init → matches pretrained exactly |

### Target Modules (Priority Order)
1. **$W_q, W_k, W_v, W_o$** (attention) — Highest impact
2. **FFN $W_{up}, W_{down}, W_{gate}$** — Optional, more params
3. **NOT**: Embeddings, LayerNorm, LM Head

---

## QLoRA (4-bit Fine-Tuning)

### Memory Savings (7B Model)
| Component | FP16 Full FT | LoRA FP16 | QLoRA 4-bit |
|-----------|--------------|-----------|-------------|
| Model | 14 GB | 14 GB | **3.5 GB** |
| Gradients | 14 GB | 0.1 GB | 0.1 GB |
| Optimizer | 56 GB | 0.4 GB | 0.4 GB |
| **Total** | **84 GB** | **14.5 GB** | **4 GB** |

### NF4 Quantization
- **NormalFloat 4-bit**: Quantization levels = quantiles of $\mathcal{N}(0,1)$
- Optimal for normally distributed weights (which pretrained weights are)
- 16 levels: $[-1.0, -0.69, -0.52, -0.39, -0.28, -0.18, -0.09, 0, 0.079, 0.16, 0.24, 0.33, 0.44, 0.56, 0.72, 1.0]$

### Double Quantization
- Quantize the quantization constants (scales) to 8-bit
- Saves additional ~0.37 bits/parameter

### Paged Optimizers
- Offload optimizer states (Adam moments) to CPU RAM
- Page back to GPU when needed for update
- Enables larger models on limited GPU memory

---

## Fine-Tuning Objectives

### SFT (Supervised Fine-Tuning)
$$\mathcal{L}_{SFT} = -\sum_{t=1}^T \log p_\theta(y_t | x, y_{<t})$$
Standard causal LM loss on instruction-response pairs.

### RLHF Pipeline
```
SFT Model → Reward Model (train on comparisons) → PPO → Aligned Model
```
1. Collect comparisons: human ranks $y_1 \succ y_2 \succ \dots$
2. Train reward model $r_\phi(x, y)$ (Bradley-Terry)
3. PPO: maximize $\mathbb{E}[r_\phi(x, y)] - \beta \text{KL}(\pi_\theta \| \pi_{SFT})$

### DPO (Direct Preference Optimization)
$$\mathcal{L}_{DPO} = -\mathbb{E}_{(x, y_w, y_l)} \left[ \log \sigma \left( \beta \log \frac{\pi_\theta(y_w|x)}{\pi_{ref}(y_w|x)} - \beta \log \frac{\pi_\theta(y_l|x)}{\pi_{ref}(y_l|x)} \right) \right]$$

**Key insight**: Optimal policy under Bradley-Terry satisfies:
$$\frac{\pi^*(y_w|x)}{\pi^*(y_l|x)} = \frac{\pi_{ref}(y_w|x)}{\pi_{ref}(y_l|x)} e^{r(x,y_w)/\beta - r(x,y_l)/\beta}$$
DPO directly optimizes this without learning $r$.

**Hyperparameters**: $\beta \in [0.1, 0.5]$ (KL penalty strength)

---

## Other PEFT Methods

| Method | Trainable Params | Mechanism | Best For |
|--------|------------------|-----------|----------|
| **Prefix Tuning** | $2 \cdot n_{virt} \cdot d \cdot L$ | Prepend virtual K,V to each layer | Generation tasks |
| **Prompt Tuning** | $n_{virt} \cdot d$ | Prepend soft prompt to input | Simple adaptation |
| **Adapters** | $\sim 0.5\%$ | Bottleneck MLP between layers | Multi-task (swap adapters) |
| **IA3** | $\sim 0.01\%$ | Scale activations by learned vectors | Extreme compression |

---

## Quantization Methods

| Method | Type | Bits | Fine-Tune? | Use Case |
|--------|------|------|------------|----------|
| **GPTQ** | Post-training | 3-4 | No | Inference only |
| **AWQ** | Post-training | 4 | No | Inference, activation-aware |
| **QLoRA** | **Fine-tuning** | 4 | **Yes** | Training on consumer GPU |
| **FP8** | Training | 8 | Yes | H100 native |

---

## Training Recipes

### LoRA Hyperparameters
| Component | Value |
|-----------|-------|
| **Learning Rate** | $1\text{--}3 \times 10^{-4}$ |
| **Scheduler** | Cosine / Constant with warmup |
| **Warmup** | 2-5% steps |
| **Batch Size** | 16-128 (effective) |
| **Epochs** | 1-3 (SFT), 1 (DPO) |
| **Weight Decay** | 0.01-0.1 |
| **LoRA Dropout** | 0.05-0.1 |
| **Max Length** | 2048-4096 |
| **Packing** | Yes (concatenate sequences) |

### QLoRA Specific
- Same LoRA hyperparams
- **4-bit NF4** base model
- **Paged AdamW** (32-bit optimizer states)
- **Gradient checkpointing** (activation recomputation)

---

## Data Best Practices

### Quality Filters
- ✅ Deduplicate (exact + fuzzy)
- ✅ Remove PII, toxic content
- ✅ Verify format (prompt/response structure)
- ✅ Filter short/low-quality responses
- ✅ Balance topics/domains

### Data Mixing Ratios (Domain Adaptation)
| Data Type | Ratio |
|-----------|-------|
| Target Domain | 50-70% |
| General Instruction | 20-30% |
| Synthetic / Augmented | 10-20% |

---

## Evaluation Checklist

### Quantitative
- [ ] MMLU / BBH (general knowledge)
- [ ] HumanEval / MBPP (coding)
- [ ] GSM8K / MATH (reasoning)
- [ ] MT-Bench / AlpacaEval (chat)
- [ ] Perplexity on held-out domain data

### Qualitative
- [ ] Coherence (no repetition, logical flow)
- [ ] Instruction following (format, constraints)
- [ ] Faithfulness (no hallucination on known facts)
- [ ] Safety (refusals, no toxic output)
- [ ] Style/Tone (matches target domain)

---

## Deployment

### Merging LoRA
```python
# After training
merged_weight = base_weight + (alpha / r) * (B @ A)
# Save as standard model — no adapter code needed!
```

### Quantized Inference Formats
| Format | Platform | Bits | Engine |
|--------|----------|------|--------|
| **GGUF** | CPU/Apple Silicon | 2-8 | llama.cpp |
| **AWQ** | NVIDIA GPU | 4 | vLLM, TGI |
| **GPTQ** | NVIDIA GPU | 3-4 | AutoGPTQ, vLLM |
| **EXL2** | NVIDIA GPU | 4 | ExLlamaV2 |

---

## Common Pitfalls & Fixes

| Problem | Diagnosis | Fix |
|---------|-----------|-----|
| **Loss NaN** | LR too high, bad data | Reduce LR 10x, check data |
| **No learning** | LR too low, frozen wrong | Increase LR, verify trainable params |
| **Overfitting** | Rank too high, epochs too many | Reduce $r$, add dropout, early stop |
| **Forgetting** | No replay data | Mix 10-20% general data |
| **OOM** | Model too big | QLoRA, gradient accumulation, smaller batch |
| **DPO diverges** | $\beta$ too small/large | Try $\beta=0.1, 0.25, 0.5$ |
| **Slow training** | No packing, small batch | Enable packing, gradient accumulation |

---

## Interview Quick Reference

**Q**: "LoRA rank 8 vs 64 — what's the tradeoff?"
**A**: Higher $r$ = more capacity, better quality, more params/memory. $r=8$: ~0.4%, $r=64$: ~3%. Diminishing returns after 32.

**Q**: "Why does LoRA work? What's the theoretical justification?"
**A**: (1) Intrinsic dimension of fine-tuning updates is low (Aghajanyan et al.). (2) Pretrained models are overparameterized. (3) Gradient alignment — pretrained features already useful.

**Q**: "QLoRA uses 4-bit base model. How does backprop work through quantized weights?"
**A**: It **doesn't**! Frozen 4-bit weights are dequantized to FP16/BF16 for forward pass. Gradients flow only through LoRA adapters (FP16/BF16). No gradient through quantized weights.

**Q**: "How does DPO avoid needing a reward model?"
**A**: DPO uses the identity $\pi^*(y|x) \propto \pi_{ref}(y|x) \exp(r(x,y)/\beta)$. Substituting into Bradley-Terry preference probability eliminates $r$, giving loss directly in terms of $\pi_\theta/\pi_{ref}$.

**Q**: "When merging LoRA, why use $\frac{\alpha}{r}$ scaling?"
**A**: Training uses scaled update $\frac{\alpha}{r}BA$. To get identical inference, must merge with same scaling. $\alpha$ is typically $2r$ or $4r$, so effective scale is $2$ or $4$.

**Q**: "What's the difference between LoRA dropout and regular dropout?"
**A**: LoRA dropout applied to $A x$ (the low-dim projection), not to model activations. Regular dropout on hidden states. LoRA dropout = 0.05-0.1 typical.

**Q**: "How do you choose LoRA target modules?"
**A**: Start with all attention ($q,k,v,o$). Add FFN if needed. Never embeddings/LN. Ablate: $q,v$ only often works nearly as well as $q,k,v,o$ with half params.