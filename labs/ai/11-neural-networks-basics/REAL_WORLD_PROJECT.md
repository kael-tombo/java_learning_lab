# Neural Networks Basics - REAL WORLD PROJECT

## Project: Handwritten Digit Recognition

Build a neural network to classify handwritten digits.

### Architecture

```
28x28 Image → Flatten → Dense(128) → ReLU → Dense(64) → ReLU → Dense(10) → Softmax
```

### Implementation

```java
public class DigitRecognizer {
    private NeuralNetwork network;
    
    public void train(double[][] images, int[] labels) {
        network = new NeuralNetwork(0.001);
        network.addLayer(784, 128, "relu");
        network.addLayer(128, 64, "relu");
        network.addLayer(64, 10, "softmax");
        
        // One-hot encode labels
        double[][] encodedLabels = oneHotEncode(labels, 10);
        
        // Train with mini-batches
        trainMiniBatch(images, encodedLabels, 32, 50);
    }
    
    public int predict(double[] image) {
        double[] output = network.forward(image);
        return argmax(output);
    }
    
    public double evaluate(double[][] testImages, int[] testLabels) {
        int correct = 0;
        for (int i = 0; i < testImages.length; i++) {
            if (predict(testImages[i]) == testLabels[i]) correct++;
        }
        return (double) correct / testImages.length;
    }
    
    private void trainMiniBatch(double[][] X, double[][] y, int batchSize, int epochs) {
        for (int epoch = 0; epoch < epochs; epoch++) {
            // Shuffle data
            int[] indices = shuffleIndices(X.length);
            
            for (int i = 0; i < X.length; i += batchSize) {
                // Forward and backward for batch
                for (int j = i; j < Math.min(i + batchSize, X.length); j++) {
                    network.forward(X[indices[j]]);
                    network.backward(y[indices[j]]);
                }
            }
        }
    }
}
```

### Sourced field notes (fetched Oct 2026 — verify before citing)
- MNIST is the "hello world" of deep learning, consisting of 70,000 handwritten digit images.
- Reference: http://yann.lecun.com/exdb/mnist/
- Reference: https://www.tensorflow.org/datasets/catalog/mnist

## Deliverables

- [x] Neural network implementation
- [x] Mini-batch training
- [x] Data augmentation (rotation, shift)
- [x] Evaluation with accuracy and confusion matrix
- [x] Model saving and loading
