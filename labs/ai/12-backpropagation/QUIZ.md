# 12-backpropagation — Quiz

**Instructions**: Answer all 10 questions. Each question has one correct answer unless marked "Select all that apply." Check your answers at the end.

---

### Question 1: Chain Rule Application
In a neural network with Loss $L$, output activation $a^{[L]}$, pre-activation $z^{[L]}$, and weight $w^{[L]}$, the gradient $\frac{\partial L}{\partial w^{[L]}}$ is computed as:
- A) $\frac{\partial L}{\partial w^{[L]}} = \frac{\partial L}{\partial a^{[L]}} \cdot \frac{\partial a^{[L]}}{\partial z^{[L]}} \cdot \frac{\partial z^{[L]}}{\partial w^{[L]}}$
- B) $\frac{\partial L}{\partial w^{[L]}} = \frac{\partial L}{\partial a^{[L]}} \cdot \frac{\partial a^{[L]}}{\partial w^{[L]}}$
- C) $\frac{\partial L}{\partial w^{[L]}} = \frac{\partial L}{\partial z^{[L]}} \cdot \frac{\partial z^{[L]}}{\partial w^{[L]}}$
- D) $\frac{\partial L}{\partial w^{[L]}} = \frac{\partial L}{\partial a^{[L]}} \cdot \frac{\partial z^{[L]}}{\partial w^{[L]}}$

### Question 2: Sigmoid Derivative
The derivative of the sigmoid function $\sigma(z) = \frac{1}{1+e^{-z}}$ with respect to $z$ is:
- A) $\sigma(z)$
- B) $\sigma(z)(1 - \sigma(z))$
- C) $1 - \sigma(z)$
- D) $\sigma'(z) = e^{-z}/(1+e^{-z})^2$

### Question 3: Vanishing Gradient Cause
Why do sigmoid/tanh activations cause vanishing gradients in deep networks?
- A) Their derivatives are always > 1, causing exploding gradients
- B) Their derivatives are bounded: $\sigma'(z) \le 0.25$, $\tanh'(z) \le 1$; multiplying many small numbers $\to 0$
- C) They are not differentiable at $z=0$
- D) They require too much memory to store intermediate activations

### Question 4: ReLU Derivative
The derivative of ReLU: $\text{ReLU}(z) = \max(0, z)$ is:
- A) 1 everywhere
- B) 0 for $z < 0$, 1 for $z > 0$, undefined at $z = 0$
- C) $z$ for $z > 0$, 0 otherwise
- D) Always 0.5

### Question 5: Forward vs Backward Pass
Which statement is correct about the forward and backward passes?
- A) Forward pass computes gradients; backward pass computes loss
- B) Forward pass computes loss; backward pass computes gradients
- C) Both passes compute gradients
- D) Forward pass updates weights; backward pass computes loss

### Question 6: Weight Gradient Formula
For a fully connected layer with input $\mathbf{a}^{[l-1]}$, weights $\mathbf{W}^{[l]}$, bias $\mathbf{b}^{[l]}$, pre-activation $\mathbf{z}^{[l]} = \mathbf{W}^{[l]}\mathbf{a}^{[l-1]} + \mathbf{b}^{[l]}$, and upstream gradient $\frac{\partial L}{\partial \mathbf{z}^{[l]}} = \boldsymbol{\delta}^{[l]}$, the weight gradient is:
- A) $\frac{\partial L}{\partial \mathbf{W}^{[l]}} = \boldsymbol{\delta}^{[l]} (\mathbf{a}^{[l-1]})^T$
- B) $\frac{\partial L}{\partial \mathbf{W}^{[l]}} = \mathbf{a}^{[l-1]} (\boldsymbol{\delta}^{[l]})^T$
- C) $\frac{\partial L}{\partial \mathbf{W}^{[l]}} = \boldsymbol{\delta}^{[l]} \mathbf{W}^{[l]}$
- D) $\frac{\partial L}{\partial \mathbf{W}^{[l]}} = \mathbf{a}^{[l-1]} \boldsymbol{\delta}^{[l]}$

### Question 7: Bias Gradient
For the same layer setup as Q6, the bias gradient $\frac{\partial L}{\partial \mathbf{b}^{[l]}}$ is:
- A) $\boldsymbol{\delta}^{[l]} (\mathbf{a}^{[l-1]})^T$
- B) $\sum_i \boldsymbol{\delta}^{[l]}_i$ (sum over batch)
- C) $\boldsymbol{\delta}^{[l]}$ (for single sample) or mean over batch
- D) $\mathbf{a}^{[l-1]}$

### Question 8: Backprop Through Hidden Layer
Given upstream gradient $\boldsymbol{\delta}^{[l+1]} = \frac{\partial L}{\partial \mathbf{z}^{[l+1]}}$ at layer $l+1$, the downstream gradient at layer $l$ is:
- A) $\boldsymbol{\delta}^{[l]} = (\mathbf{W}^{[l+1]})^T \boldsymbol{\delta}^{[l+1]} \odot \sigma'(\mathbf{z}^{[l]})$
- B) $\boldsymbol{\delta}^{[l]} = \mathbf{W}^{[l+1]} \boldsymbol{\delta}^{[l+1]} \odot \sigma'(\mathbf{z}^{[l]})$
- C) $\boldsymbol{\delta}^{[l]} = \boldsymbol{\delta}^{[l+1]} \odot \sigma'(\mathbf{z}^{[l]})$
- D) $\boldsymbol{\delta}^{[l]} = (\mathbf{W}^{[l]})^T \boldsymbol{\delta}^{[l+1]} \odot \sigma'(\mathbf{z}^{[l]})$

### Question 9: Automatic Differentiation
What is the key advantage of reverse-mode autodiff (backprop) over forward-mode autodiff for neural networks?
- A) Forward-mode is only for scalar outputs
- B) Reverse-mode computes gradient of scalar loss w.r.t. all parameters in one backward pass; forward-mode requires one pass per parameter
- C) Forward-mode is less numerically stable
- D) Reverse-mode works only for linear functions

### Question 10: Gradient Checking
When implementing backprop manually, how do you verify correctness using numerical gradient checking?
- A) Compare $\frac{\partial L}{\partial w} \approx \frac{L(w+\epsilon) - L(w-\epsilon)}{2\epsilon}$ for random weights
- B) Compare loss before and after one gradient step
- C) Check that all gradients are positive
- D) Verify that gradient norm equals loss value

---

## Answer Key

| Question | Answer | Explanation |
|----------|--------|-------------|
| 1 | **A** | Full chain rule: $L \to a^{[L]} \to z^{[L]} \to w^{[L]}$. |
| 2 | **B** | $\sigma'(z) = \sigma(z)(1-\sigma(z))$. Max value 0.25 at $z=0$. |
| 3 | **B** | Sigmoid derivative $\le 0.25$, tanh derivative $\le 1$. Product of many $\ll 1$ numbers $\to 0$. |
| 4 | **B** | $\text{ReLU}'(z) = \mathbb{1}_{z>0}$. Subgradient at 0 is typically set to 0 or 1. |
| 5 | **B** | Forward: input $\to$ output $\to$ loss. Backward: loss $\to$ gradients. |
| 6 | **A** | $\frac{\partial L}{\partial W_{ij}} = \delta_i a_j$. Matrix form: $\boldsymbol{\delta} \mathbf{a}^T$. |
| 7 | **C** | $z = Wa + b$, so $\frac{\partial z}{\partial b} = I$. For batch: mean of $\boldsymbol{\delta}$ over samples. |
| 8 | **A** | Chain rule: $\frac{\partial L}{\partial z^{[l]}} = \frac{\partial z^{[l+1]}}{\partial z^{[l]}} \frac{\partial L}{\partial z^{[l+1]}} = (\mathbf{W}^{[l+1]})^T \boldsymbol{\delta}^{[l+1]} \odot \sigma'(z^{[l]})$. |
| 9 | **B** | Reverse-mode: 1 forward + 1 backward pass for gradient w.r.t. all $N$ params. Forward-mode: $N$ passes. |
| 10 | **A** | Central difference formula gives $O(\epsilon^2)$ error. Compare analytic vs numeric for each weight. |

---

## Scoring

- **9-10 correct**: Excellent — You understand backprop deeply
- **7-8 correct**: Good — Review the chain rule derivations
- **5-6 correct**: Fair — Re-read MATH_FOUNDATION.md and trace through CODE_DEEP_DIVE
- **<5 correct**: Needs work — Implement the MLP from scratch and add print statements

---

## Follow-Up Exercises

For each question you missed, do the corresponding exercise in **EXERCISES.md**:
- Q1, Q2 → Exercise 1 (Chain Rule by Hand)
- Q3 → Exercise 2 (Vanishing Gradient Experiment)
- Q4 → Exercise 3 (ReLU vs Sigmoid)
- Q5 → Exercise 4 (Forward/Backward Pass Implementation)
- Q6, Q7 → Exercise 5 (Vectorized Gradients)
- Q8 → Exercise 6 (Multi-Layer Backprop)
- Q9 → Exercise 7 (Autodiff Comparison)
- Q10 → Exercise 8 (Gradient Checking)