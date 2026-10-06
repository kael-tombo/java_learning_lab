# Backpropagation - REAL WORLD PROJECT

## Project: Train a Deep Network with Custom Autograd

Build and train a deep neural network using a custom automatic differentiation engine.

### Architecture

```
Input → Dense(256) → BatchNorm → ReLU → Dense(128) → BatchNorm → ReLU → Dense(10) → Softmax
```

### Implementation

```java
public class DeepNetworkTrainer {
    private AutogradEngine engine;
    private List<Layer> layers;
    
    public void train(double[][] X, int[] y, int epochs) {
        for (int epoch = 0; epoch < epochs; epoch++) {
            double totalLoss = 0;
            
            for (int i = 0; i < X.length; i++) {
                // Forward pass
                Value[] inputs = Arrays.stream(X[i]).mapToObj(Value::new).toArray(Value[]::new);
                Value[] output = forward(inputs);
                
                // Compute loss
                Value loss = crossEntropy(output, y[i]);
                totalLoss += loss.data;
                
                // Backward pass
                engine.zeroGrad();
                loss.backward();
                
                // Update parameters
                updateParameters(0.001);
            }
            
            if (epoch % 10 == 0) {
                System.out.printf("Epoch %d: Loss = %.4f%n", epoch, totalLoss / X.length);
            }
        }
    }
    
    public void gradientCheck() {
        // Numerical gradient checking
        double epsilon = 1e-5;
        for (Layer layer : layers) {
            for (int i = 0; i < layer.weights.length; i++) {
                for (int j = 0; j < layer.weights[0].length; j++) {
                    double original = layer.weights[i][j].data;
                    
                    layer.weights[i][j].data = original + epsilon;
                    double lossPlus = computeLoss();
                    
                    layer.weights[i][j].data = original - epsilon;
                    double lossMinus = computeLoss();
                    
                    double numericalGrad = (lossPlus - lossMinus) / (2 * epsilon);
                    double analyticalGrad = layer.weights[i][j].grad;
                    
                    assert Math.abs(numericalGrad - analyticalGrad) < 1e-5;
                    
                    layer.weights[i][j].data = original;
                }
            }
        }
    }
}
```

### Sourced field notes (fetched Oct 2026 — verify before citing)
- Gradient checking is essential for verifying backpropagation implementations.
- Reference: http://cs231n.github.io/optimization-1/
- Reference: https://pytorch.org/docs/stable/autograd.html

## Deliverables

- [x] Custom autograd engine
- [x] Deep network training
- [x] Gradient checking
- [x] Batch normalization
- [x] Learning rate scheduling
