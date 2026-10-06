# Variational Autoencoders - REAL WORLD PROJECT

## Project: Anomaly Detection with VAE

Build a VAE-based anomaly detection system for industrial images.

### Architecture

```
Normal Images → Train VAE → Reconstruction Error → Anomaly Score → Alert
```

### Implementation

```java
public class VAEAnomalyDetector {
    private VAE vae;
    private double threshold;
    
    public void train(List<double[]> normalImages) {
        vae = new VAE(32);
        vae.train(normalImages.toArray(new double[0][]), 100);
        
        // Set threshold based on reconstruction error of training data
        double[] errors = normalImages.stream()
            .mapToDouble(img -> reconstructionError(img))
            .toArray();
        threshold = mean(errors) + 3 * std(errors);
    }
    
    public AnomalyResult detect(double[] image) {
        double error = reconstructionError(image);
        boolean isAnomaly = error > threshold;
        double confidence = sigmoid((error - threshold) / threshold);
        return new AnomalyResult(isAnomaly, confidence, error);
    }
    
    private double reconstructionError(double[] image) {
        double[] encoded = vae.encode(image);
        double[] reconstructed = vae.decode(encoded);
        return mse(image, reconstructed);
    }
    
    public void visualizeAnomaly(double[] image) {
        double[] encoded = vae.encode(image);
        double[] reconstructed = vae.decode(encoded);
        
        // Show original, reconstruction, and difference
        displayComparison(image, reconstructed);
    }
}
```

### Sourced field notes (fetched Oct 2026 — verify before citing)
- VAEs are effective for anomaly detection by learning the distribution of normal data.
- Reference: https://arxiv.org/abs/1312.6114
- Reference: https://blog.keras.io/building-autoencoders-in-keras.html

## Deliverables

- [x] VAE training on normal data
- [x] Reconstruction error computation
- [x] Threshold selection
- [x] Anomaly detection API
- [x] Visualization of anomalies
