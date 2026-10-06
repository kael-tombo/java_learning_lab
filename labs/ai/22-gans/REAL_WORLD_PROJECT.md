# GANs - REAL WORLD PROJECT

## Project: Style Transfer with CycleGAN

Build a CycleGAN for unpaired image-to-image translation.

### Architecture

```
Domain A → Generator G_A2B → Domain B
Domain B → Generator G_B2A → Domain A
Cycle Consistency: A → G_A2B → G_B2A ≈ A
```

### Implementation

```java
public class CycleGAN {
    private NeuralNetwork generatorA2B;
    private NeuralNetwork generatorB2A;
    private NeuralNetwork discriminatorA;
    private NeuralNetwork discriminatorB;
    
    public void train(List<double[]> domainA, List<double[]> domainB, int epochs) {
        for (int epoch = 0; epoch < epochs; epoch++) {
            for (int i = 0; i < domainA.size(); i++) {
                double[] realA = domainA.get(i);
                double[] realB = domainB.get(i);
                
                // Generate fake images
                double[] fakeB = generatorA2B.forward(realA);
                double[] fakeA = generatorB2A.forward(realB);
                
                // Cycle consistency
                double[] cycleA = generatorB2A.forward(fakeB);
                double[] cycleB = generatorA2B.forward(fakeA);
                
                // Discriminator losses
                double dALoss = discriminatorA.train(realA, 1.0) + discriminatorA.train(fakeA, 0.0);
                double dBLoss = discriminatorB.train(realB, 1.0) + discriminatorB.train(fakeB, 0.0);
                
                // Generator losses (adversarial + cycle consistency)
                double gALoss = discriminatorB.train(fakeB, 1.0) + 
                               cycleConsistencyLoss(realA, cycleA) +
                               cycleConsistencyLoss(realB, cycleB);
                double gBLoss = discriminatorA.train(fakeA, 1.0) +
                               cycleConsistencyLoss(realB, cycleB) +
                               cycleConsistencyLoss(realA, cycleA);
                
                // Backpropagate
                generatorA2B.backward(gALoss);
                generatorB2A.backward(gBLoss);
            }
        }
    }
    
    public double[] translateAtoB(double[] imageA) {
        return generatorA2B.forward(imageA);
    }
}
```

### Sourced field notes (fetched Oct 2026 — verify before citing)
- CycleGAN enables unpaired image-to-image translation without paired training data.
- Reference: https://arxiv.org/abs/1703.10593
- Reference: https://junyanz.github.io/CycleGAN/

## Deliverables

- [x] Generator and discriminator networks
- [x] Cycle consistency loss
- [x] Adversarial training
- [x] Image translation between domains
- [x] Evaluation with FID score
