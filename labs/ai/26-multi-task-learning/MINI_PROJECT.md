# Multi-Task Learning - MINI PROJECT

## Project: Multi-Task Neural Network

Build a neural network that learns multiple tasks simultaneously.

### Implementation

```java
public class MultiTaskNetwork {
    private NeuralNetwork sharedLayers;
    private NeuralNetwork task1Head;
    private NeuralNetwork task2Head;
    
    public MultiTaskNetwork(int inputDim, int hiddenDim, int task1Dim, int task2Dim) {
        // Shared layers
        sharedLayers = new NeuralNetwork(0.001);
        sharedLayers.addLayer(inputDim, hiddenDim, "relu");
        sharedLayers.addLayer(hiddenDim, hiddenDim, "relu");
        
        // Task-specific heads
        task1Head = new NeuralNetwork(0.001);
        task1Head.addLayer(hiddenDim, task1Dim, "softmax");
        
        task2Head = new NeuralNetwork(0.001);
        task2Head.addLayer(hiddenDim, task2Dim, "linear");
    }
    
    public void train(double[][] X, int[] y1, double[] y2, int epochs) {
        for (int epoch = 0; epoch < epochs; epoch++) {
            double totalLoss = 0;
            for (int i = 0; i < X.length; i++) {
                // Forward through shared layers
                double[] shared = sharedLayers.forward(X[i]);
                
                // Task 1 forward
                double[] out1 = task1Head.forward(shared);
                double loss1 = crossEntropy(out1, y1[i]);
                
                // Task 2 forward
                double[] out2 = task2Head.forward(shared);
                double loss2 = mse(out2, y2[i]);
                
                // Combined loss
                double loss = loss1 + loss2;
                totalLoss += loss;
                
                // Backward through task heads
                task1Head.backward(y1[i]);
                task2Head.backward(y2[i]);
                
                // Backward through shared layers
                // Combine gradients from both tasks
                sharedLayers.backward(combineGradients());
            }
            System.out.printf("Epoch %d: Loss = %.4f%n", epoch, totalLoss / X.length);
        }
    }
    
    public double[] predictTask1(double[] x) {
        double[] shared = sharedLayers.forward(x);
        return task1Head.forward(shared);
    }
    
    public double predictTask2(double[] x) {
        double[] shared = sharedLayers.forward(x);
        return task2Head.forward(shared);
    }
}
```

### Test It

```java
@Test
public void testMultiTaskNetwork() {
    MultiTaskNetwork mtl = new MultiTaskNetwork(10, 20, 3, 1);
    double[][] X = randomData(100, 10);
    int[] y1 = randomLabels(100, 3);
    double[] y2 = randomValues(100);
    mtl.train(X, y1, y2, 50);
    assertEquals(3, mtl.predictTask1(X[0]).length);
}
```

## Deliverables

- [ ] Shared layer architecture
- [ ] Task-specific heads
- [ ] Multi-task loss computation
- [ ] Gradient combination
- [ ] Comparison with single-task models
