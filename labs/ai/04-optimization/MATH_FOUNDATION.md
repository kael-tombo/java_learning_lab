# Optimization — Math Foundation

## 1. Gradient Descent Fundamentals

### Gradient of a Scalar Function
For a differentiable function $f: \mathbb{R}^n \to \mathbb{R}$, the **gradient** is the vector of partial derivatives:

$$\nabla f(\mathbf{x}) = \begin{bmatrix} \frac{\partial f}{\partial x_1} \\ \frac{\partial f}{\partial x_2} \\ \vdots \\ \frac{\partial f}{\partial x_n} \end{bmatrix}$$

The gradient points in the direction of **steepest ascent**. Gradient descent moves in the opposite direction:

$$\mathbf{x}_{t+1} = \mathbf{x}_t - \eta \nabla f(\mathbf{x}_t)$$

where $\eta > 0$ is the **learning rate** (step size).

### Directional Derivative
The rate of change of $f$ in direction $\mathbf{u}$ (unit vector) is:
$$D_{\mathbf{u}} f(\mathbf{x}) = \nabla f(\mathbf{x})^T \mathbf{u}$$
This is maximized when $\mathbf{u} \propto \nabla f(\mathbf{x})$.

---

## 2. Convergence Analysis

### Lipschitz Continuity
A function $f$ is **$L$-smooth** (gradient is $L$-Lipschitz) if:
$$\|\nabla f(\mathbf{x}) - \nabla f(\mathbf{y})\| \le L \|\mathbf{x} - \mathbf{y}\| \quad \forall \mathbf{x}, \mathbf{y}$$

For $L$-smooth convex functions, gradient descent with $\eta \le 1/L$ guarantees:
$$f(\mathbf{x}_t) - f(\mathbf{x}^*) \le \frac{\|\mathbf{x}_0 - \mathbf{x}^*\|^2}{2\eta t}$$

### Strong Convexity
$f$ is **$\mu$-strongly convex** if:
$$f(\mathbf{y}) \ge f(\mathbf{x}) + \nabla f(\mathbf{x})^T(\mathbf{y} - \mathbf{x}) + \frac{\mu}{2}\|\mathbf{y} - \mathbf{x}\|^2$$

For $\mu$-strongly convex and $L$-smooth functions, gradient descent converges **linearly**:
$$f(\mathbf{x}_t) - f(\mathbf{x}^*) \le \left(1 - \frac{\mu}{L}\right)^t (f(\mathbf{x}_0) - f(\mathbf{x}^*))$$

**Condition number** $\kappa = L/\mu$ determines convergence speed.

---

## 3. Gradient Descent Variants

### Stochastic Gradient Descent (SGD)
For empirical risk $f(\mathbf{x}) = \frac{1}{n}\sum_{i=1}^n f_i(\mathbf{x})$:
$$\mathbf{x}_{t+1} = \mathbf{x}_t - \eta_t \nabla f_{i_t}(\mathbf{x}_t) \quad i_t \sim \text{Uniform}(1..n)$$

**Convergence** (convex, $L$-smooth): $\mathbb{E}[f(\mathbf{x}_t)] - f(\mathbf{x}^*) = O(1/\sqrt{t})$ with $\eta_t = O(1/\sqrt{t})$.

### Momentum (Polyak, 1964)
$$\mathbf{v}_{t+1} = \gamma \mathbf{v}_t + \eta \nabla f(\mathbf{x}_t)$$
$$\mathbf{x}_{t+1} = \mathbf{x}_t - \mathbf{v}_{t+1}$$

Accelerates convergence in ravines; dampens oscillations. Optimal $\gamma \approx 0.9$.

### Nesterov Accelerated Gradient (NAG)
$$\mathbf{v}_{t+1} = \gamma \mathbf{v}_t + \eta \nabla f(\mathbf{x}_t - \gamma \mathbf{v}_t)$$
$$\mathbf{x}_{t+1} = \mathbf{x}_t - \mathbf{v}_{t+1}$$

"Lookahead" gradient evaluation. Achieves optimal $O(1/t^2)$ rate for convex smooth functions.

### AdaGrad
$$G_t = \sum_{\tau=1}^t \nabla f(\mathbf{x}_\tau) \nabla f(\mathbf{x}_\tau)^T \quad \text{(diagonal in practice)}$$
$$\mathbf{x}_{t+1} = \mathbf{x}_t - \frac{\eta}{\sqrt{G_t + \epsilon}} \odot \nabla f(\mathbf{x}_t)$$

Adapts per-coordinate learning rates. Good for sparse gradients. Accumulates squared gradients $\to$ learning rate decays to zero.

### RMSprop
$$\mathbf{s}_t = \beta \mathbf{s}_{t-1} + (1-\beta) \nabla f(\mathbf{x}_t)^2$$
$$\mathbf{x}_{t+1} = \mathbf{x}_t - \frac{\eta}{\sqrt{\mathbf{s}_t + \epsilon}} \odot \nabla f(\mathbf{x}_t)$$

Exponential moving average of squared gradients. Fixes AdaGrad's vanishing learning rate. $\beta \approx 0.99$.

### Adam (Kingma & Ba, 2015)
$$\mathbf{m}_t = \beta_1 \mathbf{m}_{t-1} + (1-\beta_1) \nabla f(\mathbf{x}_t) \quad \text{(1st moment)}$$
$$\mathbf{s}_t = \beta_2 \mathbf{s}_{t-1} + (1-\beta_2) \nabla f(\mathbf{x}_t)^2 \quad \text{(2nd moment)}$$
$$\hat{\mathbf{m}}_t = \frac{\mathbf{m}_t}{1-\beta_1^t}, \quad \hat{\mathbf{s}}_t = \frac{\mathbf{s}_t}{1-\beta_2^t} \quad \text{(bias correction)}$$
$$\mathbf{x}_{t+1} = \mathbf{x}_t - \frac{\eta}{\sqrt{\hat{\mathbf{s}}_t} + \epsilon} \odot \hat{\mathbf{m}}_t$$

Defaults: $\beta_1=0.9, \beta_2=0.999, \epsilon=10^{-8}$. Combines momentum + adaptive learning rates.

### AdamW (Loshchilov & Hutter, 2019)
Decouples weight decay from gradient adaptation:
$$\mathbf{x}_{t+1} = \mathbf{x}_t - \eta \left( \frac{\hat{\mathbf{m}}_t}{\sqrt{\hat{\mathbf{s}}_t} + \epsilon} + \lambda \mathbf{x}_t \right)$$

Better generalization for transformers.

---

## 4. Second-Order Methods

### Newton's Method
$$\mathbf{x}_{t+1} = \mathbf{x}_t - \mathbf{H}^{-1}(\mathbf{x}_t) \nabla f(\mathbf{x}_t)$$
where $\mathbf{H} = \nabla^2 f$ is the **Hessian** matrix.

Quadratic convergence near optimum. But: $\mathcal{O}(n^3)$ per iteration, Hessian may be indefinite.

### Quasi-Newton (BFGS)
Approximate $\mathbf{H}^{-1}$ using gradient differences:
$$\mathbf{y}_t = \nabla f(\mathbf{x}_{t+1}) - \nabla f(\mathbf{x}_t)$$
$$\mathbf{s}_t = \mathbf{x}_{t+1} - \mathbf{x}_t$$
Update inverse Hessian approximation $\mathbf{B}_t$ via BFGS formula.

L-BFGS: Limited-memory version storing only last $m$ vectors ($m \approx 10-20$).

---

## 5. Constrained Optimization

### Projected Gradient Descent
For $\min_{\mathbf{x} \in \mathcal{C}} f(\mathbf{x})$ with convex set $\mathcal{C}$:
$$\mathbf{x}_{t+1} = \Pi_{\mathcal{C}}(\mathbf{x}_t - \eta \nabla f(\mathbf{x}_t))$$
where $\Pi_{\mathcal{C}}(\mathbf{y}) = \arg\min_{\mathbf{x} \in \mathcal{C}} \|\mathbf{x} - \mathbf{y}\|^2$ is the **projection operator**.

### Lagrange Multipliers
For equality constraints $h_i(\mathbf{x}) = 0$:
$$\mathcal{L}(\mathbf{x}, \boldsymbol{\lambda}) = f(\mathbf{x}) + \sum_i \lambda_i h_i(\mathbf{x})$$
KKT conditions: $\nabla_{\mathbf{x}} \mathcal{L} = 0, \quad h_i(\mathbf{x}) = 0$.

### Inequality Constraints
For $g_j(\mathbf{x}) \le 0$:
$$\mathcal{L}(\mathbf{x}, \boldsymbol{\lambda}, \boldsymbol{\mu}) = f(\mathbf{x}) + \sum_i \lambda_i h_i(\mathbf{x}) + \sum_j \mu_j g_j(\mathbf{x})$$
KKT: $\mu_j \ge 0, \quad \mu_j g_j(\mathbf{x}) = 0$ (complementary slackness).

### Proximal Gradient Descent
For composite objectives $f(\mathbf{x}) = g(\mathbf{x}) + h(\mathbf{x})$ where $g$ smooth, $h$ non-smooth but **prox-friendly**:
$$\mathbf{x}_{t+1} = \text{prox}_{\eta h}(\mathbf{x}_t - \eta \nabla g(\mathbf{x}_t))$$
$$\text{prox}_{\eta h}(\mathbf{y}) = \arg\min_{\mathbf{x}} \left( h(\mathbf{x}) + \frac{1}{2\eta}\|\mathbf{x} - \mathbf{y}\|^2 \right)$$

Examples:
- $h(\mathbf{x}) = \lambda \|\mathbf{x}\|_1 \to$ soft-thresholding (LASSO)
- $h(\mathbf{x}) = \mathbb{I}_{\mathcal{C}}(\mathbf{x}) \to$ projection

---

## 6. Learning Rate Schedules

| Schedule | Formula | Use Case |
|----------|---------|----------|
| Constant | $\eta_t = \eta$ | SGD with momentum, Adam |
| Time decay | $\eta_t = \eta_0 / (1 + \alpha t)$ | Convex problems |
| Step decay | $\eta_t = \eta_0 \gamma^{\lfloor t/s \rfloor}$ | Deep learning |
| Exponential | $\eta_t = \eta_0 e^{-\alpha t}$ | Fast initial convergence |
| Cosine annealing | $\eta_t = \eta_{\min} + \frac{1}{2}(\eta_{\max} - \eta_{\min})(1 + \cos(\frac{t\pi}{T}))$ | SOTA training |
| Warmup + cosine | Linear warmup then cosine | Transformer training |

---

## 7. Practical Considerations

### Gradient Clipping
Prevent exploding gradients:
$$\text{if } \|\mathbf{g}\| > \tau: \quad \mathbf{g} \leftarrow \tau \frac{\mathbf{g}}{\|\mathbf{g}\|}$$
or per-coordinate: $\mathbf{g} \leftarrow \text{clip}(\mathbf{g}, -\tau, \tau)$

### Batch Normalization Effect
BN reparameterizes optimization landscape, allowing larger learning rates. Equivalent to preconditioning.

### Weight Decay vs L2 Regularization
- **L2**: Adds $\frac{\lambda}{2}\|\mathbf{w}\|^2$ to loss $\to$ gradient gets $\lambda \mathbf{w}$
- **Weight Decay**: Directly multiplies weights: $\mathbf{w} \leftarrow (1 - \eta\lambda)\mathbf{w}$
- **AdamW**: Decouples them for adaptive methods

---

## 8. Key Formulas Reference

| Concept | Formula |
|---------|---------|
| Gradient Descent | $\mathbf{x}_{t+1} = \mathbf{x}_t - \eta \nabla f(\mathbf{x}_t)$ |
| Momentum | $\mathbf{v}_{t+1} = \gamma \mathbf{v}_t + \eta \nabla f(\mathbf{x}_t)$ |
| NAG | $\mathbf{v}_{t+1} = \gamma \mathbf{v}_t + \eta \nabla f(\mathbf{x}_t - \gamma \mathbf{v}_t)$ |
| Adam Update | $\mathbf{x}_{t+1} = \mathbf{x}_t - \frac{\eta}{\sqrt{\hat{\mathbf{s}}_t}+\epsilon}\hat{\mathbf{m}}_t$ |
| Convergence (convex) | $O(1/\sqrt{t})$ SGD, $O(1/t)$ GD |
| Convergence (strongly convex) | $O((1-\mu/L)^t)$ linear |
| Condition Number | $\kappa = L/\mu$ |
| Projected GD | $\mathbf{x}_{t+1} = \Pi_{\mathcal{C}}(\mathbf{x}_t - \eta \nabla f(\mathbf{x}_t))$ |
| Proximal Operator | $\text{prox}_{\eta h}(\mathbf{y}) = \arg\min_{\mathbf{x}} (h(\mathbf{x}) + \frac{1}{2\eta}\|\mathbf{x}-\mathbf{y}\|^2)$ |

---

## 9. Java Implementation Notes

```java
// Gradient descent with momentum
public class GradientDescent {
    private double learningRate;
    private double momentum;
    private double[] velocity;
    
    public double[] step(double[] x, double[] grad) {
        for (int i = 0; i < x.length; i++) {
            velocity[i] = momentum * velocity[i] + learningRate * grad[i];
            x[i] -= velocity[i];
        }
        return x;
    }
}

// Adam optimizer
public class Adam {
    private double lr = 1e-3, beta1 = 0.9, beta2 = 0.999, eps = 1e-8;
    private double[] m, v;
    private int t = 0;
    
    public double[] step(double[] x, double[] grad) {
        t++;
        for (int i = 0; i < x.length; i++) {
            m[i] = beta1 * m[i] + (1 - beta1) * grad[i];
            v[i] = beta2 * v[i] + (1 - beta2) * grad[i] * grad[i];
            double mHat = m[i] / (1 - Math.pow(beta1, t));
            double vHat = v[i] / (1 - Math.pow(beta2, t));
            x[i] -= lr * mHat / (Math.sqrt(vHat) + eps);
        }
        return x;
    }
}
```

---

## 10. Further Reading

1. **Boyd & Vandenberghe** - *Convex Optimization* (Ch. 9: Unconstrained minimization)
2. **Nocedal & Wright** - *Numerical Optimization* (Ch. 2, 3, 6, 7)
3. **Bottou, Curtis, Nocedal** - "Optimization Methods for Large-Scale Machine Learning" (SIAM Review, 2018)
4. **Ruder** - "An overview of gradient descent optimization algorithms" (arXiv:1609.04747)
5. **Kingma & Ba** - "Adam: A Method for Stochastic Optimization" (ICLR 2015)
6. **Loshchilov & Hutter** - "Decoupled Weight Decay Regularization" (ICLR 2019)