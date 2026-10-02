# 04-optimization — Quiz

**Instructions**: Answer all 10 questions. Each question has one correct answer unless marked "Select all that apply." Check your answers at the end.

---

### Question 1: Gradient Direction
For a differentiable function $f: \mathbb{R}^n \to \mathbb{R}$, the gradient $\nabla f(\mathbf{x})$ points in the direction of:
- A) Steepest descent
- B) Steepest ascent
- C) Zero directional derivative
- D) The global minimum

### Question 2: Learning Rate for L-Smooth Functions
If $f$ is $L$-smooth (gradient is $L$-Lipschitz), what is the maximum constant learning rate $\eta$ that guarantees convergence for gradient descent on convex $f$?
- A) $\eta < 1/L$
- B) $\eta \le 1/L$
- C) $\eta < 2/L$
- D) $\eta \le 2/L$

### Question 3: Condition Number
For a $\mu$-strongly convex and $L$-smooth function, the condition number is $\kappa = L/\mu$. What convergence rate does gradient descent achieve?
- A) Sublinear $O(1/t)$
- B) Linear $O((1 - 1/\kappa)^t)$
- C) Quadratic $O(\kappa^{-2t})$
- D) Exponential $O(e^{-\kappa t})$

### Question 4: Momentum vs NAG
What is the key difference between Polyak Momentum and Nesterov Accelerated Gradient (NAG)?
- A) NAG uses a larger momentum coefficient
- B) NAG evaluates the gradient at a "lookahead" position $\mathbf{x}_t - \gamma \mathbf{v}_t$
- C) Momentum only works for convex functions; NAG works for non-convex
- D) NAG does not require a learning rate

### Question 5: AdaGrad Limitation
What is the main practical limitation of AdaGrad that motivated RMSprop and Adam?
- A) It requires computing the full Hessian
- B) The learning rate monotonically decays to zero, causing premature convergence
- C) It only works for linear models
- D) It diverges on non-convex functions

### Question 6: Adam Bias Correction
In Adam, why are the bias correction terms $\frac{1}{1-\beta_1^t}$ and $\frac{1}{1-\beta_2^t}$ applied?
- A) To prevent division by zero in the first iterations
- B) Because $\mathbf{m}_t$ and $\mathbf{s}_t$ are initialized at zero, causing bias toward zero in early steps
- C) To compensate for the momentum term
- D) To ensure the learning rate stays constant

### Question 7: Projected Gradient Descent
For constrained optimization $\min_{\mathbf{x} \in \mathcal{C}} f(\mathbf{x})$ with convex $\mathcal{C}$, projected gradient descent computes:
- A) $\mathbf{x}_{t+1} = \mathbf{x}_t - \eta \nabla f(\mathbf{x}_t)$ then clips to $\mathcal{C}$
- B) $\mathbf{x}_{t+1} = \Pi_{\mathcal{C}}(\mathbf{x}_t - \eta \nabla f(\mathbf{x}_t))$ where $\Pi_{\mathcal{C}}$ is the Euclidean projection onto $\mathcal{C}$
- C) $\mathbf{x}_{t+1} = \arg\min_{\mathbf{x} \in \mathcal{C}} \|\mathbf{x} - \mathbf{x}_t\|^2 + \eta \nabla f(\mathbf{x}_t)^T \mathbf{x}$
- D) Both B and C are equivalent formulations

### Question 8: Proximal Operator for L1 Regularization
The proximal operator for $h(\mathbf{x}) = \lambda \|\mathbf{x}\|_1$ is:
- A) Hard thresholding: $\text{prox}(y) = y \cdot \mathbb{1}_{|y| > \lambda}$?
- B) Soft thresholding: $\text{prox}(y) = \text{sign}(y) \max(|y| - \lambda, 0)$
- C) Ridge shrinkage: $\text{prox}(y) = y / (1 + \lambda)$
- D) Projection onto $\ell_1$ ball

### Question 9: AdamW vs Adam
What is the key difference between AdamW and Adam regarding weight decay?
- A) AdamW uses a larger weight decay coefficient
- B) AdamW applies weight decay *after* the adaptive learning rate update (decoupled), while Adam adds it to the gradient (coupled)
- C) AdamW only applies weight decay to bias terms
- D) There is no difference; AdamW is just a rebranding

### Question 10: Cosine Annealing Schedule
The cosine annealing learning rate schedule is:
$$\eta_t = \eta_{\min} + \frac{1}{2}(\eta_{\max} - \eta_{\min})\left(1 + \cos\left(\frac{t\pi}{T}\right)\right)$$
What is the learning rate at $t = T/2$ (halfway through training)?
- A) $\eta_{\max}$
- B) $(\eta_{\max} + \eta_{\min}) / 2$
- C) $\eta_{\min}$
- D) $\eta_{\max} / 2$

---

## Answer Key

| Question | Answer | Explanation |
|----------|--------|-------------|
| 1 | **B** | The gradient points in the direction of steepest *ascent*. Gradient *descent* moves opposite to the gradient. |
| 2 | **B** | For $L$-smooth convex functions, $\eta \le 1/L$ guarantees $f(\mathbf{x}_{t+1}) \le f(\mathbf{x}_t)$. |
| 3 | **B** | Linear convergence: $f(\mathbf{x}_t) - f(\mathbf{x}^*) \le (1 - \mu/L)^t (f(\mathbf{x}_0) - f(\mathbf{x}^*)) = (1 - 1/\kappa)^t \cdots$ |
| 4 | **B** | NAG evaluates $\nabla f(\mathbf{x}_t - \gamma \mathbf{v}_t)$ — a "lookahead" step — while momentum uses $\nabla f(\mathbf{x}_t)$. |
| 5 | **B** | AdaGrad accumulates squared gradients $G_t = \sum \nabla^2$, so effective LR $\eta/\sqrt{G_t} \to 0$. RMSprop uses EMA to fix this. |
| 6 | **B** | $\mathbf{m}_0 = \mathbf{s}_0 = 0$ biases early estimates toward zero. Bias correction divides by $1-\beta^t$ to unbias. |
| 7 | **D** | Both B and C are equivalent: projection is the proximal operator of the indicator function of $\mathcal{C}$. |
| 8 | **B** | Soft thresholding is the proximal operator of $\lambda \|x\|_1$. Hard thresholding is non-convex. |
| 9 | **B** | Adam adds $\lambda \mathbf{w}$ to gradient (coupled); AdamW applies $\mathbf{w} \leftarrow (1-\eta\lambda)\mathbf{w}$ separately (decoupled). |
| 10 | **B** | At $t=T/2$, $\cos(\pi/2) = 0$, so $\eta = \eta_{\min} + \frac{1}{2}(\eta_{\max} - \eta_{\min}) = (\eta_{\max}+\eta_{\min})/2$. |

---

## Scoring

- **9-10 correct**: Excellent — You have strong intuition for optimization theory
- **7-8 correct**: Good — Review the questions you missed
- **5-6 correct**: Fair — Re-read the MATH_FOUNDATION sections on convergence and adaptive methods
- **<5 correct**: Needs work — Study the MATH_FOUNDATION.md and implement the optimizers in CODE_DEEP_DIVE

---

## Follow-Up Exercises

For each question you missed, do the corresponding exercise in **EXERCISES.md**:
- Q1, Q2 → Exercise 1 (Gradient Descent Implementation)
- Q3 → Exercise 2 (Convergence Analysis)
- Q4 → Exercise 3 (Momentum vs NAG)
- Q5, Q6 → Exercise 4 (Adaptive Methods)
- Q7 → Exercise 5 (Constrained Optimization)
- Q8 → Exercise 6 (Proximal Operators)
- Q9 → Exercise 7 (Adam vs AdamW)
- Q10 → Exercise 8 (Learning Rate Schedules)