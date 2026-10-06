# Meta-Learning - MINI PROJECT

## Project: Prototypical Networks for Few-Shot Learning

Build a Prototypical Networks implementation for few-shot classification.

### Implementation

```java
public class PrototypicalNetworks {
    private NeuralNetwork encoder;
    private double[][] prototypes;
    private int numClasses;
    
    public PrototypicalNetworks(int inputDim, int hiddenDim, int embeddingDim) {
        encoder = new NeuralNetwork(0.001);
        encoder.addLayer(inputDim, hiddenDim, "relu");
        encoder.addLayer(hiddenDim, embeddingDim, "linear");
    }
    
    public void computePrototypes(double[][] supportSet, int[] labels) {
        numClasses = Arrays.stream(labels).max().orElse(0) + 1;
        prototypes = new double[numClasses][];
        
        for (int c = 0; c < numClasses; c++) {
            // Get all examples of class c
            List<double[]> classExamples = new ArrayList<>();
            for (int i = 0; i < labels.length; i++) {
                if (labels[i] == c) classExamples.add(supportSet[i]);
            }
            
            // Compute mean embedding
            double[] mean = new double[embeddingDim];
            for (double[] example : classExamples) {
                double[] embedding = encoder.forward(example);
                for (int j = 0; j < embeddingDim; j++) mean[j] += embedding[j];
            }
            for (int j = 0; j < embeddingDim; j++) mean[j] /= classExamples.size();
            prototypes[c] = mean;
        }
    }
    
    public int predict(double[] query) {
        double[] queryEmbedding = encoder.forward(query);
        
        // Find nearest prototype
        int bestClass = 0;
        double bestDist = Double.MAX_VALUE;
        for (int c = 0; c < numClasses; c++) {
            double dist = euclideanDistance(queryEmbedding, prototypes[c]);
            if (dist < bestDist) {
                bestDist = dist;
                bestClass = c;
            }
        }
        return bestClass;
    }
    
    public void train(double[][] supportSet, int[] labels, int epochs) {
        for (int epoch = 0; epoch < epochs; epoch++) {
            computePrototypes(supportSet, labels);
            
            double totalLoss = 0;
            for (int i = 0; i < supportSet.length; i++) {
                int pred = predict(supportSet[i]);
                double loss = (pred == labels[i]) ? 0 : 1;
                totalLoss += loss;
                
                // Backpropagate through encoder
                // ... (gradient computation)
            }
            System.out.printf("Epoch %d: Loss = %.4f%n", epoch, totalLoss / supportSet.length);
        }
    }
}
```

### Test It

```java
@Test
public void testPrototypicalNetworks() {
    PrototypicalNetworks pn = new PrototypicalNetworks(784, 128, 64);
    double[][] support = randomData(10, 784);
    int[] labels = {0,0,0,0,0,1,1,1,1,1};
    pn.train(support, labels, 100);
    assertTrue(pn.predict(support[0]) == 0);
}
```

## Deliverables

- [ ] Encoder network
- [ ] Prototype computation
- [ ] Euclidean distance classification
- [ ] Few-shot training loop
- [ ] Evaluation on N-way K-shot tasks
