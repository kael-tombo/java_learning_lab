# Graph Neural Networks - MINI PROJECT

## Project: Graph Convolutional Network

Build a GCN for node classification.

### Implementation

```java
public class GCN {
    private double[][] weights1, weights2;
    private double[][] adjacency;
    private double[][] features;
    
    public GCN(int inputDim, int hiddenDim, int outputDim) {
        weights1 = randomMatrix(inputDim, hiddenDim);
        weights2 = randomMatrix(hiddenDim, outputDim);
    }
    
    public void setGraph(double[][] adjacency, double[][] features) {
        this.adjacency = adjacency;
        this.features = features;
    }
    
    public double[][] forward() {
        // A_hat = A + I
        double[][] A_hat = addIdentity(adjacency);
        
        // D_hat^(-1/2) * A_hat * D_hat^(-1/2)
        double[][] D_hat = degreeMatrix(A_hat);
        double[][] normalized = normalize(A_hat, D_hat);
        
        // H1 = ReLU(A_hat * X * W1)
        double[][] H1 = matmul(matmul(normalized, features), weights1);
        H1 = relu(H1);
        
        // H2 = A_hat * H1 * W2
        double[][] H2 = matmul(matmul(normalized, H1), weights2);
        
        return softmax(H2);
    }
    
    public void train(int[] labels, int epochs) {
        for (int epoch = 0; epoch < epochs; epoch++) {
            double[][] output = forward();
            double loss = crossEntropy(output, labels);
            
            // Backpropagation
            double[][] grad = subtract(output, oneHot(labels));
            // ... (gradient computation for weights)
            
            if (epoch % 10 == 0) {
                System.out.printf("Epoch %d: Loss = %.4f%n", epoch, loss);
            }
        }
    }
    
    public int[] predict() {
        double[][] output = forward();
        return argmax(output);
    }
}
```

### Test It

```java
@Test
public void testGCN() {
    double[][] adj = {{0,1,1},{1,0,1},{1,1,0}};
    double[][] feat = {{1,0},{0,1},{1,1}};
    GCN gcn = new GCN(2, 4, 2);
    gcn.setGraph(adj, feat);
    gcn.train(new int[]{0,1,0}, 100);
    int[] pred = gcn.predict();
    assertEquals(3, pred.length);
}
```

## Deliverables

- [ ] Graph convolution operation
- [ ] Adjacency matrix normalization
- [ ] Forward and backward passes
- [ ] Node classification
- [ ] Visualization of node embeddings
