# Variational Autoencoders - MINI PROJECT

## Project: VAE for Image Generation

Build a variational autoencoder for generating images.

### Implementation

```java
public class VAE {
    private NeuralNetwork encoder;
    private NeuralNetwork decoder;
    private int latentDim;
    
    public VAE(int latentDim) {
        this.latentDim = latentDim;
        
        // Encoder: image → mu, log_var
        encoder = new NeuralNetwork(0.001);
        encoder.addLayer(784, 400, "relu");
        encoder.addLayer(400, latentDim * 2, "linear"); // mu and log_var
        
        // Decoder: latent → image
        decoder = new NeuralNetwork(0.001);
        decoder.addLayer(latentDim, 400, "relu");
        decoder.addLayer(400, 784, "sigmoid");
    }
    
    public void train(double[][] images, int epochs) {
        for (int epoch = 0; epoch < epochs; epoch++) {
            double totalLoss = 0;
            for (double[] image : images) {
                // Encode
                double[] encoded = encoder.forward(image);
                double[] mu = Arrays.copyOfRange(encoded, 0, latentDim);
                double[] logVar = Arrays.copyOfRange(encoded, latentDim, latentDim * 2);
                
                // Reparameterization trick
                double[] z = reparameterize(mu, logVar);
                
                // Decode
                double[] reconstructed = decoder.forward(z);
                
                // Compute loss
                double reconLoss = mse(image, reconstructed);
                double klLoss = klDivergence(mu, logVar);
                double loss = reconLoss + klLoss;
                totalLoss += loss;
                
                // Backpropagate
                // ... (gradient computation)
            }
            System.out.printf("Epoch %d: Loss = %.4f%n", epoch, totalLoss / images.length);
        }
    }
    
    public double[] generate() {
        double[] z = randomNoise(latentDim);
        return decoder.forward(z);
    }
    
    private double[] reparameterize(double[] mu, double[] logVar) {
        double[] z = new double[latentDim];
        for (int i = 0; i < latentDim; i++) {
            double epsilon = rand.nextGaussian();
            z[i] = mu[i] + Math.exp(0.5 * logVar[i]) * epsilon;
        }
        return z;
    }
}
```

### Test It

```java
@Test
public void testVAE() {
    VAE vae = new VAE(20);
    double[][] images = loadMNIST(1000);
    vae.train(images, 50);
    double[] generated = vae.generate();
    assertEquals(784, generated.length);
}
```

## Deliverables

- [ ] Encoder network
- [ ] Decoder network
- [ ] Reparameterization trick
- [ ] KL divergence loss
- [ ] Image generation and interpolation
