# Optimization - REAL WORLD PROJECT

## Project: Training a Neural Network for MNIST

Build a complete training pipeline for MNIST digit classification using custom optimizers.

### Architecture

```
MNIST Images → Flatten → Dense(128) → ReLU → Dense(10) → Softmax → Cross-Entropy Loss
```

### Implementation

```java
public class MNISTTrainer {
    private NeuralNetwork network;
    private Optimizer optimizer;
    
    public void train(double[][] images, int[] labels, int epochs) {
        for (int epoch = 0; epoch < epochs; epoch++) {
            double totalLoss = 0;
            for (int i = 0; i < images.length; i++) {
                // Forward pass
                double[] output = network.forward(images[i]);
                double loss = crossEntropy(output, labels[i]);
                totalLoss += loss;
                
                // Backward pass
                double[] gradients = network.backward(output, labels[i]);
                
                // Update weights
                optimizer.update(network.getWeights(), gradients);
            }
            System.out.printf("Epoch %d: Loss = %.4f%n", epoch, totalLoss / images.length);
        }
    }
    
    public double evaluate(double[][] testImages, int[] testLabels) {
        int correct = 0;
        for (int i = 0; i < testImages.length; i++) {
            double[] output = network.forward(testImages[i]);
            int predicted = argmax(output);
            if (predicted == testLabels[i]) correct++;
        }
        return (double) correct / testImages.length;
    }
}
```

### Sourced field notes (fetched Oct 2026 — verify before citing)
- Adam optimizer is widely used in practice due to its adaptive learning rates.
- Reference: https://arxiv.org/abs/1412.6980
- Reference: https://www.tensorflow.org/api_docs/python/tf/keras/optimizers/Adam

## Deliverables

- [x] Neural network implementation
- [x] Custom optimizer integration
- [x] Training loop with loss tracking
- [x] Evaluation on test set
- [x] Hyperparameter tuning results
