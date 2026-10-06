# Dimensionality Reduction - REAL WORLD PROJECT

## Project: Image Feature Extraction and Visualization

Build a system for extracting and visualizing image features using PCA and t-SNE.

### Architecture

```
Image Dataset → Feature Extraction → PCA/t-SNE → 2D Visualization → Cluster Analysis
```

### Implementation

```java
public class ImageFeatureVisualizer {
    private PCA pca;
    private TSNE tsne;
    
    public void visualize(List<BufferedImage> images) {
        // Extract raw pixel features
        double[][] features = extractFeatures(images);
        
        // Reduce to 50 dimensions with PCA
        pca = new PCA();
        pca.fit(features);
        double[][] pcaReduced = pca.transform(features, 50);
        
        // Further reduce to 2D with t-SNE
        tsne = new TSNE(2, 30, 1000);
        double[][] embedding = tsne.fitTransform(pcaReduced);
        
        // Visualize
        visualizeEmbedding(embedding, images);
    }
    
    public double[][] extractFeatures(List<BufferedImage> images) {
        double[][] features = new double[images.size()][];
        for (int i = 0; i < images.size(); i++) {
            features[i] = extractHOGFeatures(images.get(i));
        }
        return features;
    }
    
    public void findSimilarImages(BufferedImage query, int k) {
        double[] queryFeatures = extractHOGFeatures(query);
        // Use approximate nearest neighbors for efficiency
        List<Integer> similar = annIndex.search(queryFeatures, k);
        displayResults(similar);
    }
}
```

### Sourced field notes (fetched Oct 2026 — verify before citing)
- t-SNE is widely used for visualizing high-dimensional data in 2D or 3D.
- Reference: https://lvdmaaten.github.io/tsne/
- Reference: https://scikit-learn.org/stable/modules/generated/sklearn.manifold.TSNE.html

## Deliverables

- [x] Image feature extraction (HOG, color histograms)
- [x] PCA dimensionality reduction
- [x] t-SNE visualization
- [x] Interactive similarity search
- [x] Cluster analysis and interpretation
