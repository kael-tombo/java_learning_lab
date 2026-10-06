# Fine-Tuning - MINI PROJECT

## Project: Fine-Tune a Pretrained Model

Build a fine-tuning pipeline for a pretrained neural network.

### Implementation

```java
public class FineTuner {
    private NeuralNetwork pretrained;
    private NeuralNetwork classifier;
    
    public void loadPretrained(String path) {
        pretrained = NeuralNetwork.load(path);
        // Freeze early layers
        for (int i = 0; i < pretrained.numLayers() - 2; i++) {
            pretrained.getLayer(i).freeze();
        }
    }
    
    public void addClassifier(int numClasses) {
        classifier = new NeuralNetwork(0.0001);
        classifier.addLayer(pretrained.outputSize(), 256, "relu");
        classifier.addLayer(256, numClasses, "softmax");
    }
    
    public void fineTune(double[][] X, int[] y, int epochs) {
        for (int epoch = 0; epoch < epochs; epoch++) {
            double totalLoss = 0;
            for (int i = 0; i < X.length; i++) {
                // Forward through pretrained (frozen)
                double[] features = pretrained.forward(X[i]);
                
                // Forward through classifier
                double[] output = classifier.forward(features);
                double loss = crossEntropy(output, y[i]);
                totalLoss += loss;
                
                // Backward only through classifier
                classifier.backward(y[i]);
            }
            System.out.printf("Epoch %d: Loss = %.4f%n", epoch, totalLoss / X.length);
        }
    }
}
```

### Test It

```java
@Test
public void testFineTuning() {
    FineTuner ft = new FineTuner();
    ft.loadPretrained("pretrained_model.bin");
    ft.addClassifier(10);
    ft.fineTune(trainX, trainY, 10);
    assertTrue(ft.evaluate(testX, testY) > 0.8);
}
```

## Deliverables

- [ ] Pretrained model loading
- [ ] Layer freezing
- [ ] Classifier head addition
- [ ] Fine-tuning with differential learning rates
- [ ] Evaluation and comparison with baseline
