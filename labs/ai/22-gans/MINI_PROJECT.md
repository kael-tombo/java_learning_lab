# GANs - MINI PROJECT

## Project: DCGAN for MNIST Generation

Build a Deep Convolutional GAN to generate handwritten digits.

### Implementation

```java
public class DCGAN {
    private NeuralNetwork generator;
    private NeuralNetwork discriminator;
    
    public DCGAN() {
        // Generator: noise → image
        generator = new NeuralNetwork(0.0002);
        generator.addLayer(100, 256, "relu");
        generator.addLayer(256, 512, "relu");
        generator.addLayer(512, 784, "tanh");
        
        // Discriminator: image → real/fake
        discriminator = new NeuralNetwork(0.0002);
        discriminator.addLayer(784, 512, "leaky_relu");
        discriminator.addLayer(512, 256, "leaky_relu");
        discriminator.addLayer(256, 1, "sigmoid");
    }
    
    public void train(double[][] realImages, int epochs) {
        for (int epoch = 0; epoch < epochs; epoch++) {
            for (int i = 0; i < realImages.length; i++) {
                // Train discriminator
                double[] noise = randomNoise(100);
                double[] fakeImage = generator.forward(noise);
                
                double realLoss = discriminator.train(realImages[i], 1.0);
                double fakeLoss = discriminator.train(fakeImage, 0.0);
                
                // Train generator
                double[] genOutput = generator.forward(noise);
                double genLoss = discriminator.train(genOutput, 1.0);
                generator.backward(discriminator.getGradients());
            }
            System.out.printf("Epoch %d: D_loss=%.4f, G_loss=%.4f%n", epoch, realLoss + fakeLoss, genLoss);
        }
    }
    
    public double[] generate() {
        double[] noise = randomNoise(100);
        return generator.forward(noise);
    }
}
```

### Test It

```java
@Test
public void testDCGAN() {
    DCGAN gan = new DCGAN();
    double[][] realImages = loadMNIST(1000);
    gan.train(realImages, 10);
    double[] generated = gan.generate();
    assertEquals(784, generated.length);
}
```

## Deliverables

- [ ] Generator network
- [ ] Discriminator network
- [ ] Adversarial training loop
- [ ] Image generation
- [ ] Visualization of generated samples
