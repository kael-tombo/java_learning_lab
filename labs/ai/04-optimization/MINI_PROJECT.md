# Optimization - MINI PROJECT

## Project: Gradient Descent Optimizer Library

Build a comprehensive optimization library with various gradient-based methods.

### Implementation

```java
public class Optimizer {
    private double learningRate;
    private double momentum;
    private double[] velocity;
    
    public Optimizer(double lr, double momentum) {
        this.learningRate = lr;
        this.momentum = momentum;
    }
    
    public double[] gradientDescent(double[] params, double[] gradients) {
        double[] newParams = new double[params.length];
        for (int i = 0; i < params.length; i++) {
            newParams[i] = params[i] - learningRate * gradients[i];
        }
        return newParams;
    }
    
    public double[] momentumUpdate(double[] params, double[] gradients) {
        if (velocity == null) velocity = new double[params.length];
        double[] newParams = new double[params.length];
        for (int i = 0; i < params.length; i++) {
            velocity[i] = momentum * velocity[i] - learningRate * gradients[i];
            newParams[i] = params[i] + velocity[i];
        }
        return newParams;
    }
    
    public double[] adamUpdate(double[] params, double[] gradients, 
                                double[] m, double[] v, int t, 
                                double beta1, double beta2, double epsilon) {
        double[] newParams = new double[params.length];
        for (int i = 0; i < params.length; i++) {
            m[i] = beta1 * m[i] + (1 - beta1) * gradients[i];
            v[i] = beta2 * v[i] + (1 - beta2) * gradients[i] * gradients[i];
            double mHat = m[i] / (1 - Math.pow(beta1, t));
            double vHat = v[i] / (1 - Math.pow(beta2, t));
            newParams[i] = params[i] - learningRate * mHat / (Math.sqrt(vHat) + epsilon);
        }
        return newParams;
    }
}
```

### Test It

```java
@Test
public void testGradientDescent() {
    Optimizer opt = new Optimizer(0.1, 0.9);
    double[] params = {1.0, 2.0};
    double[] grads = {0.5, 0.5};
    double[] result = opt.gradientDescent(params, grads);
    assertEquals(0.95, result[0], 0.001);
}
```

## Deliverables

- [ ] Gradient descent implementation
- [ ] Momentum-based updates
- [ ] Adam optimizer
- [ ] Learning rate scheduling
- [ ] Convergence visualization
