# 12-backpropagation — Exercises

**Prerequisites**: Read THEORY.md, MATH_FOUNDATION.md, and CODE_DEEP_DIVE.md first. Implement in Java using the starter code in `src/`.

---

## Exercise 1: Chain Rule by Hand

**Goal**: Manually compute gradients for a simple network to internalize the chain rule.

### Task 1.1: Scalar Network
Consider a 2-layer network with 1 input, 1 hidden neuron, 1 output:
- $z_1 = w_1 x + b_1$
- $a_1 = \sigma(z_1)$
- $z_2 = w_2 a_1 + b_2$
- $a_2 = \sigma(z_2)$
- $L = \frac{1}{2}(a_2 - y)^2$

**Compute by hand** (show all steps):
1. $\frac{\partial L}{\partial w_2}$
2. $\frac{\partial L}{\partial b_2}$
3. $\frac{\partial L}{\partial w_1}$
4. $\frac{\partial L}{\partial b_1}$

Use values: $x=1.0, y=1.0, w_1=0.5, b_1=0.1, w_2=0.3, b_2=0.2$

### Task 1.2: Verify with Java
Implement a `ScalarNetwork` class and verify your hand calculations match.

```java
// src/main/java/com/ailab/backprop/ScalarNetwork.java
public class ScalarNetwork {
    double w1, b1, w2, b2;
    
    public double forward(double x) { /* TODO */ }
    public double[] backward(double x, double y) { 
        // Returns [dL/dw1, dL/db1, dL/dw2, dL/db2]
        // TODO: Implement using chain rule
    }
}
```

---

## Exercise 2: Vanishing Gradient Experiment

**Goal**: Empirically observe vanishing gradients with sigmoid vs ReLU.

### Task 2.1: Deep Network Gradient Norms
Create networks of varying depth (2 to 20 layers) with:
- Sigmoid activations
- ReLU activations

Initialize with Xavier (sigmoid) / He (ReLU). Input: random Gaussian. Target: random.

**Measure**: Gradient norm $\|\frac{\partial L}{\partial W^{[1]}}\|_F$ at layer 1 after one backward pass.

```java
// src/main/java/com/ailab/backprop/VanishingGradientExperiment.java
public class VanishingGradientExperiment {
    public static void run() {
        for (int depth : new int[]{2, 4, 6, 8, 10, 15, 20}) {
            double sigmoidGradNorm = measureGradNorm(depth, "sigmoid");
            double reluGradNorm = measureGradNorm(depth, "relu");
            System.out.printf("Depth %d: Sigmoid=%.2e, ReLU=%.2e%n", 
                depth, sigmoidGradNorm, reluGradNorm);
        }
    }
}
```

### Task 2.2: Plot Results
Plot gradient norm vs depth (log scale y-axis) for both activations.

**Questions**:
1. At what depth does sigmoid gradient become negligible (< 1e-10)?
2. Why does ReLU maintain gradient flow?
3. What happens if you use He initialization with sigmoid?

---

## Exercise 3: ReLU vs Sigmoid — Dying ReLU Problem

**Goal**: Understand the "dying ReLU" phenomenon and how Leaky ReLU fixes it.

### Task 3.1: Dying ReLU Demonstration
Train a 3-layer ReLU network on a simple regression task where the optimal weights require negative pre-activations.

```java
// Target function: y = -2 * x + 1 (requires negative slope)
double[] X = {1, 2, 3, 4, 5};
double[] Y = {-1, -3, -5, -7, -9};
```

Track how many neurons become permanently inactive (always output 0) during training.

### Task 3.2: Leaky ReLU Fix
Replace ReLU with Leaky ReLU ($\alpha=0.01$). Compare:
- Final loss
- Number of dead neurons
- Gradient flow to early layers

**Questions**:
1. Why does standard ReLU "die"?
2. How does Leaky ReLU maintain gradient flow for negative inputs?
3. What's a good value for $\alpha$? Why not make it larger?

---

## Exercise 4: Forward/Backward Pass Implementation

**Goal**: Implement a complete vectorized forward/backward pass for an MLP.

### Task 4.1: Layer Abstraction
```java
// src/main/java/com/ailab/backprop/Layer.java
public interface Layer {
    double[] forward(double[] input);           // Returns output, caches input
    double[] backward(double[] upstreamGrad);   // Returns grad w.r.t input
    void update(double lr);                     // Update params using cached grads
    Map<String, double[]> getParams();          // For inspection
    Map<String, double[]> getGrads();           // For inspection
}
```

### Task 4.2: Linear Layer
```java
public class LinearLayer implements Layer {
    private double[][] W;   // (out, in)
    private double[] b;     // (out)
    private double[][] dW;
    private double[] db;
    private double[] cachedInput;  // (in)
    
    public double[] forward(double[] input) {
        // TODO: cache input, compute W @ input + b
    }
    
    public double[] backward(double[] upstreamGrad) {
        // upstreamGrad shape: (out)
        // dW = upstreamGrad @ input.T
        // db = upstreamGrad
        // return W.T @ upstreamGrad (shape: in)
    }
    
    public void update(double lr) { /* TODO */ }
}
```

### Task 4.3: Activation Layer
```java
public class SigmoidLayer implements Layer {
    private double[] cachedOutput;  // For derivative: a * (1 - a)
    
    public double[] forward(double[] input) { /* TODO */ }
    public double[] backward(double[] upstreamGrad) {
        // dL/dz = upstreamGrad * sigmoid'(z) = upstreamGrad * a * (1 - a)
        // return dL/dz
    }
    public void update(double lr) {}  // No params
}
```

### Task 4.4: MLP Assembly
```java
public class MLP {
    private List<Layer> layers = new ArrayList<>();
    
    public void addLayer(Layer layer) { layers.add(layer); }
    
    public double[] forward(double[] input) {
        double[] x = input;
        for (Layer layer : layers) x = layer.forward(x);
        return x;
    }
    
    public void backward(double[] lossGrad) {
        double[] grad = lossGrad;
        for (int i = layers.size() - 1; i >= 0; i--) {
            grad = layers.get(i).backward(grad);
        }
    }
    
    public void update(double lr) {
        for (Layer layer : layers) layer.update(lr);
    }
}
```

### Task 4.5: Train on XOR
```java
double[][] X = {{0,0}, {0,1}, {1,0}, {1,1}};
double[][] Y = {{0}, {1}, {1}, {0}};
```

Train until loss < 0.01. Print decision boundary.

---

## Exercise 5: Vectorized Gradients (Batch Processing)

**Goal**: Extend single-sample implementation to mini-batch processing.

### Task 5.1: Batch Linear Layer
```java
public class BatchLinearLayer implements Layer {
    // Input: (batch, in), Weight: (out, in), Bias: (out)
    // Output: (batch, out)
    // dW: (out, in) = upstreamGrad.T @ input  [then divide by batch]
    // db: (out) = mean(upstreamGrad, axis=0)
    // dInput: (batch, in) = upstreamGrad @ W
}
```

### Task 5.2: Batch Activation Layer
```java
public class BatchSigmoidLayer implements Layer {
    // Input: (batch, n)
    // Output: (batch, n)
    // Backward: upstreamGrad * output * (1 - output)  [element-wise]
}
```

### Task 5.3: Mini-Batch Training Loop
```java
public void trainBatch(double[][] X, double[][] Y, int batchSize, double lr) {
    for (int epoch = 0; epoch < epochs; epoch++) {
        // Shuffle data
        // For each mini-batch:
        //   forward, compute loss, backward, update
    }
}
```

**Verify**: Gradient norms match single-sample * batch_size (before dividing by batch).

---

## Exercise 6: Multi-Layer Backprop (Deep Network)

**Goal**: Build and train a 5-layer network on a non-linear problem.

### Task 6.1: Spiral Dataset
Generate 2D spiral classification data (3 classes):
```java
// Use parametric equations to create interleaving spirals
// Each class gets different phase offset
```

### Task 6.2: Architecture
- Input: 2D
- Hidden: [64, 64, 64, 64] with ReLU
- Output: 3 with Softmax
- Loss: Cross-Entropy

### Task 6.3: Softmax + CrossEntropy Layer
```java
public class SoftmaxCrossEntropy {
    // Forward: logits -> softmax -> CE loss
    // Backward: returns (probs - one_hot_labels) / batch_size
    // This is the key simplification!
}
```

### Task 6.4: Train & Visualize
Train to > 95% accuracy. Plot decision boundaries.

**Questions**:
1. Why does softmax+CE gradient simplify to `probs - labels`?
2. What happens if you use MSE with softmax instead?
3. How does depth help with spiral dataset?

---

## Exercise 7: Automatic Differentiation Comparison

**Goal**: Compare manual backprop vs autograd (using a simple autograd engine).

### Task 7.1: Simple Autograd Engine
```java
// src/main/java/com/ailab/backprop/autograd/Value.java
public class Value {
    public double data;
    public double grad;
    public List<Value> prev = new ArrayList<>();
    public Runnable backwardFn;
    
    public Value(double data) { this.data = data; }
    
    public Value add(Value other) { /* TODO */ }
    public Value mul(Value other) { /* TODO */ }
    public Value sigmoid() { /* TODO */ }
    
    public void backward() {
        // Topological sort then reverse pass
        // TODO
    }
}
```

### Task 7.2: Compare Implementations
Build the same XOR network using:
1. Manual backprop (Exercise 4)
2. Autograd engine

Compare:
- Lines of code
- Ease of adding new activations
- Performance (forward+backward time)
- Gradient correctness (both should match)

---

## Exercise 8: Gradient Checking

**Goal**: Implement numerical gradient checking to verify backprop correctness.

### Task 8.1: Gradient Checker
```java
// src/main/java/com/ailab/backprop/GradientChecker.java
public class GradientChecker {
    public static boolean check(MLP model, double[] x, double[] y, double eps) {
        // 1. Compute analytic gradients via backprop
        model.forward(x);
        double loss = mse(model.output, y);
        model.backward(lossGrad);  // Assume lossGrad = output - y for MSE
        double[] analyticGrads = model.getAllGradientsFlattened();
        
        // 2. Compute numeric gradients
        double[] numericGrads = new double[analyticGrads.length];
        double[] params = model.getAllParamsFlattened();
        
        for (int i = 0; i < params.length; i++) {
            double orig = params[i];
            
            params[i] = orig + eps;
            model.setParamsFlattened(params);
            double lossPlus = mse(model.forward(x), y);
            
            params[i] = orig - eps;
            model.setParamsFlattened(params);
            double lossMinus = mse(model.forward(x), y);
            
            numericGrads[i] = (lossPlus - lossMinus) / (2 * eps);
            
            params[i] = orig;  // Restore
        }
        model.setParamsFlattened(params);
        
        // 3. Compare
        double diff = relativeError(analyticGrads, numericGrads);
        System.out.printf("Relative error: %.2e%n", diff);
        return diff < 1e-7;
    }
}
```

### Task 8.2: Test on Various Architectures
Run gradient check on:
- 1-layer linear network
- 2-layer with sigmoid
- 3-layer with ReLU
- Network with batch norm (bonus)

**Questions**:
1. What relative error threshold indicates correct backprop?
2. Why use central difference instead of forward difference?
3. Why disable dropout/batchnorm during gradient checking?

---

## Exercise 9: Custom Activation — Swish

**Goal**: Implement a custom activation function and its derivative.

### Task 9.1: Swish Activation
$$\text{Swish}(x) = x \cdot \sigma(\beta x)$$
where $\beta$ is a learnable parameter (or fixed to 1).

**Derivative**:
$$\text{Swish}'(x) = \sigma(\beta x) + x \cdot \sigma(\beta x)(1 - \sigma(\beta x)) \cdot \beta$$
$$= \sigma(\beta x) + \beta x \cdot \sigma(\beta x)(1 - \sigma(\beta x))$$
$$= \sigma(\beta x) [1 + \beta x (1 - \sigma(\beta x))]$$

### Task 9.2: Implement Swish Layer
```java
public class SwishLayer implements Layer {
    private double beta = 1.0;  // Could be learnable
    private double[] cachedInput;
    
    public double[] forward(double[] input) { /* TODO */ }
    public double[] backward(double[] upstreamGrad) { 
        // Use derivative formula above
    }
}
```

### Task 9.3: Compare on Spiral Dataset
Train identical networks with ReLU vs Swish. Compare:
- Training speed (epochs to 95%)
- Final accuracy
- Gradient flow in deep layers

---

## Exercise 10: Debugging Challenge (Bonus)

**Goal**: Fix broken backprop implementations.

### Task 10.1: Bug 1 — Missing Transpose
```java
// BROKEN: dW = input @ upstreamGrad.T  (wrong shapes!)
// FIX: dW = upstreamGrad @ input.T
```

### Task 10.2: Bug 2 — Wrong Activation Derivative
```java
// BROKEN: dSigmoid = z * (1 - z)  (uses pre-activation!)
// FIX: dSigmoid = a * (1 - a)  (uses post-activation!)
```

### Task 10.3: Bug 3 — Bias Gradient Shape
```java
// BROKEN: db = upstreamGrad  (shape: batch, out)
// FIX: db = mean(upstreamGrad, axis=0)  (shape: out)
```

### Task 10.4: Bug 4 — Gradient Accumulation
```java
// BROKEN: dW = upstreamGrad @ input.T  (overwrites each batch)
// FIX: dW += upstreamGrad @ input.T  (accumulate, then divide by batch at update)
```

For each bug:
1. Run gradient checker — it will fail
2. Identify the bug
3. Fix it
4. Verify gradient checker passes

---

## Starter Project Structure

```
12-backpropagation/
├── src/
│   ├── main/
│   │   └── java/com/ailab/backprop/
│   │       ├── ScalarNetwork.java
│   │       ├── VanishingGradientExperiment.java
│   │       ├── Layer.java
│   │       ├── LinearLayer.java
│   │       ├── SigmoidLayer.java
│   │       ├── ReLULayer.java
│   │       ├── LeakyReLULayer.java
│   │       ├── SoftmaxCrossEntropy.java
│   │       ├── MLP.java
│   │       ├── BatchLinearLayer.java
│   │       ├── BatchSigmoidLayer.java
│   │       ├── SwishLayer.java
│   │       ├── autograd/
│   │       │   ├── Value.java
│   │       │   └── AutogradMLP.java
│   │       └── GradientChecker.java
│   └── test/
│       └── java/com/ailab/backprop/
│           └── BackpropTest.java
```

---

## Deliverables

For each exercise, submit:
1. **Working Java code** in `src/main/java/...`
2. **Plots** (save as PNG in `results/`)
3. **Written answers** to questions in `EXERCISE_ANSWERS.md`
4. **Gradient check results** for Exercises 4, 6, 8

---

## Grading Rubric

| Component | Points |
|-----------|--------|
| Correctness (passes tests) | 35 |
| Code quality & vectorization | 20 |
| Plot quality & labels | 15 |
| Written explanations | 15 |
| Bonus (Exercise 10) | 15 |
| **Total** | **100** |