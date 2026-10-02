# 04-optimization — Flashcards

## Core Concepts

| Term | Definition |
|------|------------|
| **Gradient** $\nabla f(\mathbf{x})$ | Vector of partial derivatives; direction of steepest ascent |
| **Gradient Descent** | $\mathbf{x}_{t+1} = \mathbf{x}_t - \eta \nabla f(\mathbf{x}_t)$; moves opposite to gradient |
| **Learning Rate** $\eta$ | Step size; too large → divergence, too small → slow convergence |
| **L-smooth** | $\|\nabla f(\mathbf{x}) - \nabla f(\mathbf{y})\| \le L \|\mathbf{x} - \mathbf{y}\|$; gradient is Lipschitz |
| **$\mu$-strongly convex** | $f(\mathbf{y}) \ge f(\mathbf{x}) + \nabla f(\mathbf{x})^T(\mathbf{y}-\mathbf{x}) + \frac{\mu}{2}\|\mathbf{y}-\mathbf{x}\|^2$ |
| **Condition Number** $\kappa$ | $\kappa = L/\mu$; ratio of smoothness to strong convexity; determines convergence speed |
| **Computational Graph** | DAG representing function composition; enables automatic differentiation |

---

## Convergence Rates

| Setting | GD Rate | SGD Rate | Accelerated (NAG) |
|---------|---------|----------|-------------------|
| Convex, L-smooth | $O(1/t)$ | $O(1/\sqrt{t})$ | $O(1/t^2)$ |
| $\mu$-strongly convex, L-smooth | $O((1-1/\kappa)^t)$ | $O(1/t)$ | $O((1-1/\sqrt{\kappa})^t)$ |
| Non-convex | Stationary point | Stationary point | Stationary point |

**Remember**: $\kappa = L/\mu$. Large $\kappa$ = ill-conditioned = slow convergence.

---

## Gradient Descent Variants

| Method | Update Rule | Key Idea | Best For |
|--------|-------------|----------|----------|
| **Vanilla GD** | $\mathbf{x} \leftarrow \mathbf{x} - \eta \nabla f$ | Simple, deterministic | Small/medium convex problems |
| **Momentum** | $\mathbf{v} \leftarrow \gamma \mathbf{v} + \eta \nabla f$; $\mathbf{x} \leftarrow \mathbf{x} - \mathbf{v}$ | Accumulate velocity in consistent directions | Ravines, ill-conditioned |
| **NAG** | $\mathbf{v} \leftarrow \gamma \mathbf{v} + \eta \nabla f(\mathbf{x} - \gamma \mathbf{v})$; $\mathbf{x} \leftarrow \mathbf{x} - \mathbf{v}$ | "Lookahead" gradient | Optimal $O(1/t^2)$ for convex |
| **AdaGrad** | $\mathbf{x} \leftarrow \mathbf{x} - \frac{\eta}{\sqrt{G_t}+\epsilon} \odot \nabla f$; $G_t = \sum \nabla^2$ | Per-coordinate adaptive LR | Sparse gradients (NLP) |
| **RMSprop** | $\mathbf{s} \leftarrow \beta \mathbf{s} + (1-\beta)\nabla^2$; $\mathbf{x} \leftarrow \mathbf{x} - \frac{\eta}{\sqrt{\mathbf{s}}+\epsilon} \odot \nabla f$ | EMA of squared gradients | Non-convex, online learning |
| **Adam** | $\mathbf{m} \leftarrow \beta_1 \mathbf{m} + (1-\beta_1)\nabla f$; $\mathbf{s} \leftarrow \beta_2 \mathbf{s} + (1-\beta_2)\nabla^2$; bias-corrected | Momentum + adaptive LR | **Default for deep learning** |
| **AdamW** | Adam update + $\mathbf{x} \leftarrow \mathbf{x} - \eta \lambda \mathbf{x}$ | Decoupled weight decay | Transformers, better generalization |

**Default Hyperparameters**:
- Momentum: $\gamma = 0.9$
- RMSprop: $\beta = 0.99$
- Adam: $\beta_1 = 0.9, \beta_2 = 0.999, \epsilon = 10^{-8}$

---

## Second-Order Methods

| Method | Update | Complexity | Notes |
|--------|--------|------------|-------|
| **Newton** | $\mathbf{x} \leftarrow \mathbf{x} - \mathbf{H}^{-1} \nabla f$ | $O(n^3)$ | Quadratic convergence near optimum |
| **BFGS** | Approx $\mathbf{H}^{-1}$ via rank-2 updates | $O(n^2)$ | Superlinear convergence |
| **L-BFGS** | Limited memory (last $m$ vectors) | $O(mn)$ | $m \approx 10-20$; practical for medium $n$ |

---

## Constrained Optimization

| Concept | Formula / Definition |
|---------|---------------------|
| **Projected GD** | $\mathbf{x}_{t+1} = \Pi_{\mathcal{C}}(\mathbf{x}_t - \eta \nabla f(\mathbf{x}_t))$ |
| **Projection** $\Pi_{\mathcal{C}}(\mathbf{y})$ | $\arg\min_{\mathbf{x} \in \mathcal{C}} \|\mathbf{x} - \mathbf{y}\|^2$ |
| **Lagrangian** | $\mathcal{L}(\mathbf{x}, \boldsymbol{\lambda}) = f(\mathbf{x}) + \sum \lambda_i h_i(\mathbf{x})$ |
| **KKT Conditions** | Stationarity, primal feasibility, dual feasibility, complementary slackness |
| **Proximal Operator** | $\text{prox}_{\eta h}(\mathbf{y}) = \arg\min_{\mathbf{x}} (h(\mathbf{x}) + \frac{1}{2\eta}\|\mathbf{x}-\mathbf{y}\|^2)$ |
| **Soft Thresholding** | $\text{prox}_{\lambda\|·\|_1}(y) = \text{sign}(y)\max(|y|-\lambda, 0)$ |

---

## Learning Rate Schedules

| Schedule | Formula | When to Use |
|----------|---------|-------------|
| **Constant** | $\eta_t = \eta$ | Adam, momentum methods |
| **Time Decay** | $\eta_t = \eta_0 / (1 + \alpha t)$ | Convex, theoretical guarantees |
| **Step Decay** | $\eta_t = \eta_0 \gamma^{\lfloor t/s \rfloor}$ | CNNs, simple scheduling |
| **Exponential** | $\eta_t = \eta_0 e^{-\alpha t}$ | Fast initial convergence needed |
| **Cosine Annealing** | $\eta_t = \eta_{\min} + \frac{1}{2}(\eta_{\max}-\eta_{\min})(1+\cos(t\pi/T))$ | **SOTA for transformers** |
| **Warmup + Cosine** | Linear warmup $0 \to \eta_{\max}$, then cosine | Large models, prevents early instability |
| **ReduceLROnPlateau** | Reduce by factor when metric plateaus | Validation-based, adaptive |

---

## Practical Tricks

| Trick | Purpose | Implementation |
|-------|---------|----------------|
| **Gradient Clipping** | Prevent exploding gradients | $\mathbf{g} \leftarrow \tau \mathbf{g}/\|\mathbf{g}\|$ if $\|\mathbf{g}\| > \tau$ |
| **Weight Decay** | L2 regularization | $\mathbf{w} \leftarrow (1-\eta\lambda)\mathbf{w}$ (decoupled in AdamW) |
| **Gradient Accumulation** | Simulate large batch | Accumulate grads over $k$ steps, then update |
| **Mixed Precision** | Speed + memory | FP16 compute, FP32 master weights |
| **Lookahead** | Stabilize training | Slow weights track fast weights every $k$ steps |
| **SAM (Sharpness-Aware Minimization)** | Better generalization | Minimize loss at $\mathbf{w} + \epsilon \nabla L$ |

---

## Common Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| LR too high | Loss diverges, NaN | Reduce LR, add gradient clipping |
| LR too low | Extremely slow convergence | Increase LR, use schedule |
| No warmup (transformers) | Early divergence | Add 1-5% warmup steps |
| AdaGrad on deep nets | LR → 0 too fast | Use RMSprop/Adam instead |
| Momentum on sharp minima | Oscillation | Reduce $\gamma$, try NAG |
| Weight decay in Adam | Suboptimal regularization | Use AdamW |
| No gradient clipping (RNNs) | Exploding gradients | Clip at 1.0 or 5.0 |

---

## Interview Quick Reference

**Q**: "Why does momentum help in ravines?"
**A**: Accumulates velocity along the ravine floor (consistent gradient direction), dampens oscillations across steep walls (alternating gradient signs).

**Q**: "Why does Adam need bias correction?"
**A**: $\mathbf{m}_0 = \mathbf{s}_0 = 0$. Early estimates are biased toward zero. Division by $1-\beta^t$ corrects this.

**Q**: "What's the difference between L2 regularization and weight decay in Adam?"
**A**: In SGD they're equivalent. In Adam, L2 adds to gradient (scaled by adaptive LR), weight decay directly shrinks weights. AdamW decouples them.

**Q**: "When would you use L-BFGS over Adam?"
**A**: Small/medium problems ($n < 10^4$), deterministic, high-accuracy needed, convex or near-convex.

**Q**: "How does cosine annealing help?"
**A**: Starts high for exploration, gradually decreases for exploitation, ends with small LR for fine-tuning. No manual step scheduling.