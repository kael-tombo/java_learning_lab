# 20-fine-tuning — Quiz

**Instructions**: Answer all 10 questions. Each question has one correct answer unless marked "Select all that apply." Check your answers at the end.

---

### Question 1: LoRA Parameter Count
For a linear layer $W \in \mathbb{R}^{4096 \times 4096}$ with LoRA rank $r=16$, how many trainable parameters does LoRA add?
- A) 65,536
- B) 131,072
- C) 262,144
- D) 16,777,216

### Question 2: LoRA Initialization
In LoRA, matrix $A$ is initialized randomly and matrix $B$ is initialized to zeros. Why?
- A) To make the model train faster
- B) To ensure $\Delta W = BA = 0$ at initialization, so model matches pretrained exactly
- C) To prevent overfitting
- D) To reduce memory usage

### Question 3: QLoRA Quantization
QLoRA uses **NF4 (NormalFloat 4-bit)** quantization. What makes NF4 special?
- A) It uses uniform quantization levels
- B) It uses quantization levels based on quantiles of $\mathcal{N}(0,1)$ distribution
- C) It quantizes to 8 bits instead of 4
- D) It doesn't require dequantization during forward pass

### Question 4: LoRA Scaling Factor
The LoRA forward pass computes $W_0 x + \frac{\alpha}{r} B A x$. What is the purpose of $\frac{\alpha}{r}$?
- A) To normalize the input $x$
- B) To allow using the same learning rate for different ranks $r$
- C) To prevent gradient explosion
- D) To match the scale of $W_0$

### Question 5: PEFT Method Comparison
Which PEFT method has the **fewest** trainable parameters?
- A) LoRA ($r=16$)
- B) Prefix Tuning (10 virtual tokens)
- C) Adapter Layers (bottleneck 64)
- D) Prompt Tuning (20 soft tokens)

### Question 6: DPO Loss Function
The DPO loss is:
$$\mathcal{L}_{DPO} = -\mathbb{E}[\log \sigma(\beta \log \frac{\pi_\theta(y_w|x)}{\pi_{ref}(y_w|x)} - \beta \log \frac{\pi_\theta(y_l|x)}{\pi_{ref}(y_l|x)})]$$
What does $\pi_{ref}$ represent?
- A) The reward model
- B) The pretrained/base model (frozen reference)
- C) The optimal policy
- D) The human preference distribution

### Question 7: Catastrophic Forgetting
What is catastrophic forgetting in fine-tuning?
- A) The model forgets the fine-tuning data
- B) Fine-tuning on new task degrades performance on pretrained capabilities
- C) The optimizer forgets the learning rate schedule
- D) The model forgets how to generate tokens

### Question 8: LoRA Applied to Attention
Which attention weight matrices are **typically** targeted by LoRA?
- A) Only $W_q$ and $W_k$
- B) $W_q, W_k, W_v, W_o$ (all attention projections)
- C) Only FFN layers
- D) Embeddings and LayerNorm

### Question 9: Merging LoRA Weights
After training, LoRA weights can be merged into the base model: $W_{merged} = W_0 + \frac{\alpha}{r}BA$. What is the **main benefit**?
- A) Reduces training time
- B) Eliminates inference overhead (single matrix multiply)
- C) Improves model quality
- D) Reduces memory during training

### Question 10: Quantization Methods
Which quantization method is **post-training** (no fine-tuning needed)?
- A) QLoRA
- B) GPTQ
- C) LoRA
- D) DPO

---

## Answer Key

| Question | Answer | Explanation |
|----------|--------|-------------|
| 1 | **B** | LoRA params = $r(d + k) = 16(4096 + 4096) = 131,072$. Full layer = 16,777,216. Ratio = 0.78%. |
| 2 | **B** | Zero-init $B$ ensures $BA=0$ at start. Model behaves identically to pretrained. Random $A$ provides exploration direction. |
| 3 | **B** | NF4 uses quantiles of standard normal as quantization levels, optimal for normally distributed weights. |
| 4 | **B** | Scaling $\alpha/r$ means effective LR for $A,B$ is independent of $r$. Without it, larger $r$ = larger effective update. |
| 5 | **D** | Prompt tuning: $20 \times d_{model} \approx 80,000$ params. LoRA: $\sim 131K$. Prefix: $\sim 2 \times 10 \times d_{model} \times L$. Adapter: $\sim 2 \times 64 \times d_{model}$. |
| 6 | **B** | $\pi_{ref}$ is the frozen reference model (usually SFT model). DPO optimizes relative to this reference. |
| 7 | **B** | Catastrophic forgetting = losing pretrained knowledge/abilities after fine-tuning on new task. |
| 8 | **B** | Standard practice: apply LoRA to all attention projections $W_q, W_k, W_v, W_o$. Sometimes FFN too. |
| 9 | **B** | Merged model has identical forward pass to LoRA but single matmul instead of two. No adapter code needed at inference. |
| 10 | **B** | GPTQ is post-training quantization. QLoRA requires fine-tuning (it's a fine-tuning method). |

---

## Scoring

- **9-10 correct**: Excellent — Ready for production fine-tuning
- **7-8 correct**: Good — Review LoRA math and QLoRA details
- **5-6 correct**: Fair — Re-read THEORY.md and MATH_FOUNDATION.md
- **<5 correct**: Needs work — Implement LoRA from scratch in EXERCISES

---

## Follow-Up Exercises

For each question you missed, do the corresponding exercise in **EXERCISES.md**:
- Q1, Q2 → Exercise 1 (LoRA Implementation)
- Q3 → Exercise 2 (4-bit Quantization)
- Q4 → Exercise 3 (LoRA Scaling Analysis)
- Q5 → Exercise 4 (PEFT Comparison)
- Q6 → Exercise 5 (DPO Implementation)
- Q7 → Exercise 6 (Forgetting Measurement)
- Q8 → Exercise 7 (Attention LoRA)
- Q9 → Exercise 8 (Weight Merging)
- Q10 → Exercise 9 (Quantization Comparison)