# Self-Supervised Learning - MINI PROJECT

## Project: Contrastive Learning with SimCLR

Build a SimCLR-style contrastive learning system.

### Implementation

```java
public class SimCLR {
    private NeuralNetwork encoder;
    private NeuralNetwork projectionHead;
    private double temperature;
    
    public SimCLR(int inputDim, int hiddenDim, int projDim, double temperature) {
        this.temperature = temperature;
        
        // Encoder (ResNet-like)
        encoder = new NeuralNetwork(0.001);
        encoder.addLayer(inputDim, hiddenDim, "relu");
        encoder.addLayer(hiddenDim, hiddenDim, "relu");
        
        // Projection head
        projectionHead = new NeuralNetwork(0.001);
        projectionHead.addLayer(hiddenDim, projDim, "linear");
    }
    
    public void train(double[][] images, int epochs) {
        for (int epoch = 0; epoch < epochs; epoch++) {
            double totalLoss = 0;
            for (double[] image : images) {
                // Create two augmented views
                double[] view1 = augment(image);
                double[] view2 = augment(image);
                
                // Encode and project
                double[] z1 = projectionHead.forward(encoder.forward(view1));
                double[] z2 = projectionHead.forward(encoder.forward(view2));
                
                // Normalize
                z1 = normalize(z1);
                z2 = normalize(z2);
                
                // Compute NT-Xent loss
                double loss = ntXentLoss(z1, z2);
                totalLoss += loss;
                
                // Backpropagate
                // ... (gradient computation)
            }
            System.out.printf("Epoch %d: Loss = %.4f%n", epoch, totalLoss / images.length);
        }
    }
    
    private double ntXentLoss(double[] z1, double[] z2) {
        double positive = dot(z1, z2) / temperature;
        double negative = 0;
        // Compute negative pairs
        // ...
        return -Math.log(Math.exp(positive) / (Math.exp(positive) + negative));
    }
    
    public double[] encode(double[] image) {
        return encoder.forward(image);
    }
}
```

### Test It

```java
@Test
public void testSimCLR() {
    SimCLR simclr = new SimCLR(784, 128, 64, 0.5);
    double[][] images = loadUnlabeledData(1000);
    simclr.train(images, 100);
    double[] embedding = simclr.encode(images[0]);
    assertEquals(128, embedding.length);
}
```

## Deliverables

- [ ] Data augmentation pipeline
- [ ] Encoder network
- [ ] Projection head
- [ ] NT-Xent loss
- [ ] Contrastive training loop
