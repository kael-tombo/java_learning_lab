# 20-fine-tuning — Math Foundation

## 1. Fine-Tuning as Optimization

### Problem Setup
Given a pretrained model $f_\theta$ with parameters $\theta \in \mathbb{R}^N$, and a downstream task with dataset $\mathcal{D} = \{(x_i, y_i)\}_{i=1}^m$, fine-tuning minimizes:
$$\mathcal{L}(\theta) = \frac{1}{m}\sum_{i=1}^m \ell(f_\theta(x_i), y_i) + \lambda R(\theta)$$

Where $R(\theta)$ is a regularizer (often $\|\theta - \theta_0\|^2$ to stay close to pretrained weights).

---

## 2. Parameter-Efficient Fine-Tuning (PEFT)

### Full Fine-Tuning
Update all $N$ parameters. Cost: $O(N)$ memory for gradients, optimizer states.

### LoRA (Low-Rank Adaptation) — Hu et al., 2021

#### Core Idea
Freeze pretrained weights $W_0 \in \mathbb{R}^{d \times k}$, add trainable low-rank decomposition:
$$W = W_0 + \Delta W = W_0 + B A$$
where $A \in \mathbb{R}^{r \times k}$, $B \in \mathbb{R}^{d \times r}$, $r \ll \min(d, k)$.

#### Forward Pass
$$h = W_0 x + B(A x) = W_0 x + \frac{\alpha}{r} B A x$$

Scaling factor $\frac{\alpha}{r}$ allows same learning rate for different $r$.

#### Parameter Reduction
$$\frac{\text{LoRA params}}{\text{Full params}} = \frac{r(d + k)}{dk} = \frac{r}{k} + \frac{r}{d} \approx \frac{2r}{d} \text{ (if } d \approx k\text{)}$$

For $d=4096, r=8$: $\frac{16}{4096} = 0.39\%$ of parameters.

#### Gradient Computation
$$\frac{\partial \mathcal{L}}{\partial A} = B^T \frac{\partial \mathcal{L}}{\partial h} x^T$$
$$\frac{\partial \mathcal{L}}{\partial B} = \frac{\partial \mathcal{L}}{\partial h} (A x)^T$$

No gradient through $W_0$ — frozen.

#### Initialization
- $A \sim \mathcal{N}(0, \sigma^2)$ (random)
- $B = 0$ (zero initialization)

Ensures $\Delta W = 0$ at start, model behaves exactly like pretrained.

#### LoRA for Attention
Apply to $W_q, W_k, W_v, W_o$ (typically not to FFN):
$$\Delta W_q = B_q A_q, \quad \Delta W_k = B_k A_k, \quad \Delta W_v = B_v A_v, \quad \Delta W_o = B_o A_o$$

---

## 3. QLoRA (Quantized LoRA) — Dettmers et al., 2023

### 4-bit NormalFloat (NF4) Quantization

#### Quantization Function
Map weights to $2^b$ levels using optimal quantization for normal distribution:
$$q = \text{Quantize}(w) = \text{round}\left(\frac{w - \min}{\max - \min} (2^b - 1)\right)$$

NF4 uses quantiles of $\mathcal{N}(0,1)$ as levels for better accuracy.

#### Double Quantization
Quantize the quantization constants themselves (8-bit) to save additional 0.37 bits/param.

#### Paged Optimizers
Move optimizer states to CPU RAM when GPU memory full, page back when needed.

#### QLoRA Forward Pass
1. Dequantize frozen weights: $W_0 = \text{Dequantize}(W_{4bit})$
2. Compute base output: $h_{base} = W_0 x$
3. Compute LoRA output: $h_{lora} = \frac{\alpha}{r} B A x$
4. Combine: $h = h_{base} + h_{lora}$

---

## 4. Other PEFT Methods

### Prefix Tuning (Li & Liang, 2021)
Prepend trainable "virtual tokens" to each layer's key/value:
$$K' = [P_K; K], \quad V' = [P_V; V]$$
where $P_K, P_V \in \mathbb{R}^{n_{virtual} \times d_k}$.

Only $2 \cdot n_{virtual} \cdot d_{model} \cdot L$ parameters.

### Adapter Layers (Houlsby et al., 2019)
Insert bottleneck layers between transformer blocks:
$$\text{Adapter}(x) = W_{down} \sigma(W_{up} x)$$
with residual: $x + \text{Adapter}(x)$.

### Prompt Tuning (Lester et al., 2021)
Only tune soft prompt embeddings prepended to input:
$$x' = [P_{prompt}; x]$$

---

## 5. Fine-Tuning Objectives

### Supervised Fine-Tuning (SFT)
$$\mathcal{L}_{SFT} = -\sum_{t=1}^T \log p_\theta(y_t | x, y_{<t})$$
Standard next-token prediction on instruction/response pairs.

### RLHF / DPO (Alignment)
**RLHF**: Reward model $r_\phi(x, y)$, PPO to maximize $\mathbb{E}[r_\phi(x, y)] - \beta \text{KL}(\pi_\theta \| \pi_{ref})$

**DPO (Direct Preference Optimization)** — Rafailov et al., 2023:
$$\mathcal{L}_{DPO} = -\mathbb{E}_{(x, y_w, y_l)} \left[ \log \sigma \left( \beta \log \frac{\pi_\theta(y_w|x)}{\pi_{ref}(y_w|x)} - \beta \log \frac{\pi_\theta(y_l|x)}{\pi_{ref}(y_l|x)} \right) \right]$$

No reward model, no RL — direct optimization on preference pairs.

### LoRA + DPO
Combine LoRA with DPO for efficient alignment:
$$\nabla_\theta \mathcal{L}_{DPO} \text{ only through LoRA params } A, B$$

---

## 6. Quantization Mathematics

### Symmetric Quantization
$$q = \text{round}\left(\frac{w}{s}\right), \quad s = \frac{\max|w|}{2^{b-1}-1}$$
$$w_{dequant} = q \cdot s$$

### Asymmetric Quantization
$$q = \text{round}\left(\frac{w - z}{s}\right), \quad s = \frac{\max(w) - \min(w)}{2^b-1}, \quad z = \min(w)$$

### Group-wise Quantization
Quantize weights in groups of 64-128 for better accuracy:
$$W_{group} \text{ has own } s, z$$

### GPTQ (Post-Training Quantization)
Layer-wise quantization using Hessian information:
$$\min_{Q} \|W - Q\|^2_{H} \quad \text{where } H = X X^T \text{ (input covariance)}$$
Solves via iterative column updates with Cholesky decomposition.

### AWQ (Activation-aware Weight Quantization)
Scale weights by activation magnitudes before quantization:
$$\tilde{W}_{ij} = W_{ij} \cdot s_j, \quad s_j = \frac{1}{\max|X_{:,j}|^\alpha}$$
Protects salient weights from quantization error.

---

## 7. Gradient Flow in PEFT

### LoRA Gradient Flow
$$\frac{\partial \mathcal{L}}{\partial x} = W_0^T \frac{\partial \mathcal{L}}{\partial h} + A^T B^T \frac{\partial \mathcal{L}}{\partial h}$$

The LoRA path adds a low-rank update to gradient flow.

### Effective Rank During Training
Even though $r$ is small, the product $BA$ can approximate full-rank updates over training steps through gradient accumulation.

### LoRA as Bayesian Approximation
LoRA approximates posterior over weights:
$$\Delta W \sim \mathcal{N}(0, \sigma^2 I) \quad \text{projected to rank-}r \text{ subspace}$$

---

## 8. Scaling Laws for Fine-Tuning

### Data Scaling
Test loss $\mathcal{L} \approx \alpha N^{-\beta} + \gamma D^{-\delta} + \epsilon$
- $N$: model parameters
- $D$: fine-tuning tokens
- Fine-tuning needs less data than pretraining ($\delta_{ft} > \delta_{pt}$)

### Parameter Scaling (LoRA)
Optimal $r$ scales with $\sqrt{d}$ theoretically, but empirically $r \in [8, 64]$ works across scales.

### Compute-Optimal Fine-Tuning
For fixed compute $C = 6ND$ (SFT), balance $N$ and $D$:
- Small $N$ (LoRA): more data, more steps
- Large $N$ (full FT): less data, fewer steps

---

## 9. Catastrophic Forgetting

### Problem
Fine-tuning on new task degrades pretrained knowledge.

### Metrics
$$\text{Forgetting} = \mathcal{L}_{pretrain}(\theta_{ft}) - \mathcal{L}_{pretrain}(\theta_0)$$

### Mitigation
| Method | Mechanism |
|--------|-----------|
| **LoRA** | Frozen $W_0$ preserves pretrained features |
| **Replay** | Mix pretraining data during fine-tuning |
| **Regularization** | $\lambda \|\theta - \theta_0\|^2$ (L2-SP) |
| **Elastic Weight Consolidation** | Fisher-weighted L2: $\sum_i F_i (\theta_i - \theta_{0,i})^2$ |

---

## 10. Key Formulas Reference

| Concept | Formula |
|---------|---------|
| LoRA Update | $W = W_0 + \frac{\alpha}{r} B A$ |
| LoRA Params | $r(d + k)$ per layer |
| QLoRA NF4 | Quantiles of $\mathcal{N}(0,1)$ as levels |
| Prefix Tuning | $K' = [P_K; K], V' = [P_V; V]$ |
| Adapter | $x + W_{down} \sigma(W_{up} x)$ |
| DPO Loss | $-\log \sigma(\beta \log \frac{\pi_\theta(y_w|x)}{\pi_{ref}(y_w|x)} - \beta \log \frac{\pi_\theta(y_l|x)}{\pi_{ref}(y_l|x)})$ |
| Symmetric Quant | $q = \text{round}(w/s), s = \max|w|/(2^{b-1}-1)$ |
| Group Quant | Groups of 64-128 share scale |
| Forgetting | $\mathcal{L}_{pretrain}(\theta_{ft}) - \mathcal{L}_{pretrain}(\theta_0)$ |

---

## 11. Java Implementation Patterns

### LoRA Layer with Proper Gradients
```java
public class LoRALayer {
    private final double[][] A;  // (r, in_features)
    private final double[][] B;  // (out_features, r)
    private final double scale;  // alpha / r
    private final double[][] frozenWeight;  // (out, in) - not trained
    
    public LoRALayer(int inFeatures, int outFeatures, int r, double alpha) {
        this.A = randomMatrix(r, inFeatures, 0.02);
        this.B = zeros(outFeatures, r);  // Zero init!
        this.scale = alpha / r;
        this.frozenWeight = loadPretrainedWeight(inFeatures, outFeatures);
    }
    
    public double[] forward(double[] input) {
        // Base: frozenWeight @ input
        double[] base = matVec(frozenWeight, input);
        
        // LoRA path: B @ (A @ input) * scale
        double[] lora = matVec(B, matVec(A, input));
        scaleInPlace(lora, scale);
        
        // Combine
        return add(base, lora);
    }
    
    public double[] backward(double[] input, double[] gradOutput) {
        // Gradient w.r.t A: B^T @ gradOutput @ input^T
        double[] gradA = outerProduct(matVec(transpose(B), gradOutput), input);
        
        // Gradient w.r.t B: gradOutput @ (A @ input)^T
        double[] gradB = outerProduct(gradOutput, matVec(A, input));
        
        // Gradient w.r.t input: frozenWeight^T @ gradOutput + A^T @ B^T @ gradOutput * scale
        double[] gradInput = add(
            matVec(transpose(frozenWeight), gradOutput),
            scale(matVec(transpose(A), matVec(transpose(B), gradOutput)), scale)
        );
        
        // Update A, B
        updateParams(gradA, gradB);
        
        return gradInput;
    }
}
```

---

## 12. Further Reading

1. **Hu et al.** - "LoRA: Low-Rank Adaptation of Large Language Models" (ICLR 2022)
2. **Dettmers et al.** - "QLoRA: Efficient Finetuning of Quantized LLMs" (NeurIPS 2023)
3. **Rafailov et al.** - "Direct Preference Optimization: Your Language Model is Secretly a Reward Model" (ICML 2024)
4. **Li & Liang** - "Prefix-Tuning: Optimizing Continuous Prompts for Generation" (ACL 2021)
5. **Houlsby et al.** - "Parameter-Efficient Transfer Learning for NLP" (ICML 2019)
6. **Frantar et al.** - "GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers" (ICLR 2023)
7. **Lin et al.** - "AWQ: Activation-aware Weight Quantization for LLM Compression" (2023)