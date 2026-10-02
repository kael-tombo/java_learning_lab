# 04-optimization — Exercises

**Prerequisites**: Read MATH_FOUNDATION.md and THEORY.md first. Implement in Java using the starter code in `src/`.

---

## Exercise 1: Gradient Descent from Scratch

**Goal**: Implement vanilla gradient descent for a quadratic function and visualize convergence.

### Task 1.1: Quadratic Objective
Implement $f(\mathbf{x}) = \frac{1}{2}\mathbf{x}^T A \mathbf{x} - \mathbf{b}^T \mathbf{x}$ where $A \in \mathbb{R}^{n \times n}$ is symmetric positive definite.

```java
// In src/main/java/com/ailab/optimization/QuadraticFunction.java
public class QuadraticFunction {
    private final double[][] A;  // n x n symmetric positive definite
    private final double[] b;    // n
    
    public QuadraticFunction(double[][] A, double[] b) {
        this.A = A;
        this.b = b;
    }
    
    // f(x) = 0.5 * x^T A x - b^T x
    public double value(double[] x) {
        // TODO: Implement
    }
    
    // ∇f(x) = A x - b
    public double[] gradient(double[] x) {
        // TODO: Implement
    }
    
    // Hessian is constant: ∇²f(x) = A
    public double[][] hessian() {
        return A;
    }
}
```

### Task 1.2: Gradient Descent Loop
```java
// In src/main/java/com/ailab/optimization/GradientDescent.java
public class GradientDescent {
    public static Result minimize(QuadraticFunction f, double[] x0, 
                                   double learningRate, int maxIter, double tol) {
        double[] x = x0.clone();
        List<Double> history = new ArrayList<>();
        
        for (int t = 0; t < maxIter; t++) {
            double[] grad = f.gradient(x);
            double fVal = f.value(x);
            history.add(fVal);
            
            // TODO: Check convergence (gradient norm < tol)
            // TODO: Update x = x - learningRate * grad
        }
        
        return new Result(x, history);
    }
}
```

### Task 1.3: Experiment
Run with:
- $A = \begin{bmatrix} 10 & 0 \\ 0 & 1 \end{bmatrix}$, $\mathbf{b} = \mathbf{0}$, $\mathbf{x}_0 = [10, 10]^T$
- Learning rates: $\eta \in \{0.01, 0.1, 0.2, 0.5\}$
- Plot $f(\mathbf{x}_t)$ vs iteration for each $\eta$

**Questions**:
1. What happens when $\eta > 2/L$ where $L = \lambda_{\max}(A) = 10$?
2. Why does the trajectory oscillate along the high-curvature direction?
3. What is the optimal $\eta$ for this problem?

---

## Exercise 2: Condition Number & Convergence

**Goal**: Empirically verify the linear convergence rate dependence on $\kappa$.

### Task 2.1: Generate Ill-Conditioned Problems
Create quadratic problems with controlled condition number:
```java
public static QuadraticFunction createIllConditioned(int n, double kappa) {
    // A = Q^T Λ Q where Λ = diag(1, κ, κ, ..., κ) for κ > 1
    // Random orthogonal Q via QR decomposition
}
```

### Task 2.2: Measure Convergence Rate
For $\kappa \in \{10, 100, 1000, 10000\}$:
- Run GD with optimal $\eta = 2/(L+\mu) = 2/(1+\kappa)$
- Record iterations to reach $f(\mathbf{x}_t) - f(\mathbf{x}^*) < 10^{-6}$
- Plot iterations vs $\kappa$ on log-log scale

**Expected**: Slope $\approx 1$ (linear in $\kappa$)

---

## Exercise 3: Momentum vs NAG

**Goal**: Compare momentum and NAG on a "ravine" function.

### Task 3.1: Rosenbrock Function
$$f(x, y) = (a - x)^2 + b(y - x^2)^2$$
with $a=1, b=100$. Global minimum at $(1, 1)$.

```java
public class RosenbrockFunction {
    public double value(double[] x) { /* TODO */ }
    public double[] gradient(double[] x) { /* TODO */ }
}
```

### Task 3.2: Implement Momentum & NAG
```java
public class MomentumOptimizer {
    private double gamma = 0.9;
    private double[] velocity;
    
    public double[] step(double[] x, double[] grad, double lr) {
        // TODO: velocity = gamma * velocity + lr * grad
        //       x = x - velocity
    }
}

public class NAGOptimizer {
    private double gamma = 0.9;
    private double[] velocity;
    
    public double[] step(double[] x, double[] grad, double lr, 
                         Function<double[], double[]> gradFn) {
        // TODO: lookahead = x - gamma * velocity
        //       gradLookahead = gradFn.apply(lookahead)
        //       velocity = gamma * velocity + lr * gradLookahead
        //       x = x - velocity
    }
}
```

### Task 3.3: Compare Trajectories
Start at $[-2, 2]$. Plot optimization paths on contour plot of Rosenbrock.

**Questions**:
1. Why does vanilla GD oscillate across the ravine?
2. How does momentum dampen oscillations?
3. Why does NAG overshoot less than momentum?

---

## Exercise 4: Adaptive Methods (AdaGrad, RMSprop, Adam)

### Task 4.1: Implement All Three
```java
public class AdaGrad {
    private double[] G;  // Accumulated squared gradients
    private double eps = 1e-8;
    
    public double[] step(double[] x, double[] grad, double lr) {
        // TODO: G += grad^2; x -= lr * grad / (sqrt(G) + eps)
    }
}

public class RMSprop {
    private double[] s;  // EMA of squared gradients
    private double beta = 0.99;
    private double eps = 1e-8;
    
    public double[] step(double[] x, double[] grad, double lr) {
        // TODO: s = beta * s + (1-beta) * grad^2
        //       x -= lr * grad / (sqrt(s) + eps)
    }
}

public class Adam {
    private double[] m, v;
    private double beta1 = 0.9, beta2 = 0.999, eps = 1e-8;
    private int t = 0;
    
    public double[] step(double[] x, double[] grad, double lr) {
        // TODO: Implement with bias correction
    }
}
```

### Task 4.2: Sparse Gradient Test
Create a problem where only 10% of coordinates get non-zero gradients:
```java
// Sparse quadratic: only first k coordinates matter
double[][] A = new double[n][n];
for (int i = 0; i < k; i++) A[i][i] = 1.0;
```

Compare convergence speed of AdaGrad vs RMSprop vs Adam.

**Questions**:
1. Why does AdaGrad excel on sparse gradients?
2. Why does RMSprop/Adam catch up on dense problems?
3. What happens to AdaGrad's effective LR over time?

---

## Exercise 5: Constrained Optimization — Projected GD

### Task 5.1: Projection Operators
Implement projections onto common constraint sets:

```java
public class Projections {
    // Box constraints: l_i <= x_i <= u_i
    public static double[] projectBox(double[] x, double[] lower, double[] upper) {
        // TODO: clamp each coordinate
    }
    
    // L2 ball: ||x||_2 <= R
    public static double[] projectL2Ball(double[] x, double R) {
        // TODO: if ||x|| > R, scale to boundary
    }
    
    // Simplex: sum(x_i) = 1, x_i >= 0
    public static double[] projectSimplex(double[] x) {
        // TODO: Sort, find threshold, project (Duchi et al. 2008)
    }
    
    // L1 ball: ||x||_1 <= R
    public static double[] projectL1Ball(double[] x, double R) {
        // TODO: Project onto simplex of absolute values, restore signs
    }
}
```

### Task 5.2: Lasso via Projected GD
Solve $\min_{\|\mathbf{x}\|_1 \le \tau} \frac{1}{2}\|A\mathbf{x} - \mathbf{b}\|^2$:
```java
public class LassoProjectedGD {
    public static double[] solve(double[][] A, double[] b, double tau, 
                                  double lr, int maxIter) {
        // TODO: Gradient of 0.5||Ax-b||^2 is A^T(Ax-b)
        //       Project onto L1 ball of radius tau
    }
}
```

### Task 5.3: Compare with Proximal GD
Implement proximal gradient for Lasso (ISTA):
$$\mathbf{x}_{t+1} = \text{soft-threshold}(\mathbf{x}_t - \eta A^T(A\mathbf{x}_t - \mathbf{b}), \eta\lambda)$$

Compare convergence paths.

---

## Exercise 6: Proximal Operators

### Task 6.1: Implement Key Proximal Operators
```java
public class ProximalOperators {
    // L1: soft thresholding
    public static double[] proxL1(double[] y, double lambda) {
        // TODO: sign(y) * max(|y| - lambda, 0)
    }
    
    // L2: ridge shrinkage
    public static double[] proxL2(double[] y, double lambda) {
        // TODO: y / (1 + lambda)
    }
    
    // Elastic Net: L1 + L2
    public static double[] proxElasticNet(double[] y, double lambda1, double lambda2) {
        // TODO: Combine L1 and L2 proxes (not simply additive!)
    }
    
    // Group Lasso: block-wise L2
    public static double[] proxGroupLasso(double[] y, int[] groupSizes, double lambda) {
        // TODO: For each group, if ||group||_2 > lambda, scale by (1 - lambda/||group||)
    }
}
```

### Task 6.2: Proximal Gradient Descent (ISTA/FISTA)
```java
public class ProximalGradient {
    // ISTA: x_{t+1} = prox_{eta*h}(x_t - eta * grad_g(x_t))
    public static double[] ista(Function<double[], Double> g, 
                                 Function<double[], double[]> gradG,
                                 Function<double[], double[]> proxH,
                                 double[] x0, double lr, int maxIter) {
        // TODO
    }
    
    // FISTA: accelerated version with momentum
    public static double[] fista(/* same args */) {
        // TODO: y_t = x_t + ((t-1)/(t+2)) * (x_t - x_{t-1})
        //       x_{t+1} = prox(y_t - eta * grad_g(y_t))
    }
}
```

---

## Exercise 7: Adam vs AdamW

### Task 7.1: Implement Both
```java
public class AdamW {
    private double lr = 1e-3, beta1 = 0.9, beta2 = 0.999, eps = 1e-8;
    private double weightDecay = 0.01;
    private double[] m, v;
    private int t = 0;
    
    public double[] step(double[] x, double[] grad) {
        t++;
        for (int i = 0; i < x.length; i++) {
            m[i] = beta1 * m[i] + (1 - beta1) * grad[i];
            v[i] = beta2 * v[i] + (1 - beta2) * grad[i] * grad[i];
            double mHat = m[i] / (1 - Math.pow(beta1, t));
            double vHat = v[i] / (1 - Math.pow(beta2, t));
            // AdamW: decoupled weight decay
            x[i] -= lr * (mHat / (Math.sqrt(vHat) + eps) + weightDecay * x[i]);
        }
        return x;
    }
}
```

### Task 7.2: Generalization Test
Train a small neural network (2-layer MLP) on a classification task:
- Use Adam with L2 regularization (added to loss)
- Use AdamW with weight decay
- Compare test accuracy

**Questions**:
1. Why does AdamW generalize better?
2. What happens to effective weight decay in Adam as adaptive LR changes per parameter?
3. When would you *not* use weight decay?

---

## Exercise 8: Learning Rate Schedules

### Task 8.1: Implement Schedules
```java
public interface LRScheduler {
    double getLR(int step, int totalSteps);
}

public class CosineAnnealing implements LRScheduler {
    private double etaMin, etaMax;
    public CosineAnnealing(double etaMin, double etaMax) { ... }
    public double getLR(int step, int totalSteps) {
        // TODO: eta_min + 0.5*(eta_max-eta_min)*(1 + cos(pi * step / totalSteps))
    }
}

public class WarmupCosine implements LRScheduler {
    private int warmupSteps;
    private CosineAnnealing cosine;
    public double getLR(int step, int totalSteps) {
        if (step < warmupSteps) return etaMax * (step + 1) / warmupSteps;
        return cosine.getLR(step - warmupSteps, totalSteps - warmupSteps);
    }
}

public class ReduceLROnPlateau implements LRScheduler {
    // TODO: Track best metric, reduce by factor when no improvement for patience steps
}
```

### Task 8.2: Schedule Comparison
Train on a simple problem (e.g., logistic regression) with:
- Constant LR
- Step decay
- Cosine annealing
- Warmup + cosine

Plot training loss curves. Which reaches lowest loss fastest?

---

## Exercise 9: Full Optimizer Benchmark

### Task 9.1: Benchmark Suite
Create a benchmark comparing all optimizers on:
1. **Quadratic** (convex, ill-conditioned)
2. **Rosenbrock** (non-convex, narrow valley)
3. **Logistic Regression** (convex, real data)
4. **Neural Network** (non-convex, deep)

Metrics:
- Iterations to convergence
- Final objective value
- Wall-clock time
- Robustness to LR (try 5 LR values per optimizer)

### Task 9.2: Results Table
| Optimizer | Quadratic (κ=1000) | Rosenbrock | Logistic Reg | MLP |
|-----------|-------------------|------------|--------------|-----|
| GD        |                   |            |              |     |
| Momentum  |                   |            |              |     |
| NAG       |                   |            |              |     |
| AdaGrad   |                   |            |              |     |
| RMSprop   |                   |            |              |     |
| Adam      |                   |            |              |     |
| AdamW     |                   |            |              |     |

---

## Exercise 10: Distributed Optimization (Bonus)

### Task 10.1: Distributed SGD
Simulate $K$ workers computing gradients on data shards:
```java
public class DistributedSGD {
    // Each worker computes grad on local data
    // Server averages gradients: g = (1/K) sum g_k
    // Server updates: x = x - eta * g
    // Broadcast new x to workers
}
```

### Task 10.2: Communication Compression
Implement gradient quantization (1-bit SGD):
$$\tilde{g}_i = \|g\| \cdot \text{sign}(g_i)$$
Compare convergence with full precision.

---

## Starter Project Structure

```
04-optimization/
├── src/
│   ├── main/
│   │   └── java/com/ailab/optimization/
│   │       ├── QuadraticFunction.java
│   │       ├── RosenbrockFunction.java
│   │       ├── GradientDescent.java
│   │       ├── MomentumOptimizer.java
│   │       ├── NAGOptimizer.java
│   │       ├── AdaGrad.java
│   │       ├── RMSprop.java
│   │       ├── Adam.java
│   │       ├── AdamW.java
│   │       ├── Projections.java
│   │       ├── ProximalOperators.java
│   │       ├── ProximalGradient.java
│   │       ├── LRScheduler.java
│   │       └── Benchmark.java
│   └── test/
│       └── java/com/ailab/optimization/
│           └── OptimizerTest.java
└── pom.xml (optional, for Maven)
```

---

## Deliverables

For each exercise, submit:
1. **Working Java code** in `src/main/java/...`
2. **Plots** (save as PNG in `results/`)
3. **Written answers** to questions in `EXERCISE_ANSWERS.md`
4. **Benchmark table** for Exercise 9

---

## Grading Rubric

| Component | Points |
|-----------|--------|
| Correctness (passes tests) | 40 |
| Code quality & comments | 20 |
| Plot quality & labels | 15 |
| Written explanations | 15 |
| Bonus (Exercise 10) | 10 |
| **Total** | **100** |