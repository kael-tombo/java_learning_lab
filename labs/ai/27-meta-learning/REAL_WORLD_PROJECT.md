# Meta-Learning - REAL WORLD PROJECT

## Project: Few-Shot Image Classification

Build a complete few-shot image classification system.

### Architecture

```
Support Set (N-way K-shot) → Encoder → Prototypes → Query Classification
```

### Implementation

```java
public class FewShotClassifier {
    private PrototypicalNetworks model;
    private DataAugmenter augmenter;
    
    public void train(List<ImageClass> classes, int epochs) {
        // Prepare support sets
        List<double[]> supportImages = new ArrayList<>();
        List<Integer> supportLabels = new ArrayList<>();
        
        for (int c = 0; c < classes.size(); c++) {
            for (BufferedImage img : classes.get(c).getImages()) {
                supportImages.add(preprocess(img));
                supportLabels.add(c);
            }
        }
        
        // Train model
        model = new PrototypicalNetworks(784, 256, 128);
        model.train(supportImages.toArray(new double[0][]), 
                   supportLabels.stream().mapToInt(i->i).toArray(), epochs);
    }
    
    public ClassificationResult classify(BufferedImage query) {
        double[] features = preprocess(query);
        int predictedClass = model.predict(features);
        double confidence = model.predictProba(features)[predictedClass];
        
        return new ClassificationResult(predictedClass, confidence);
    }
    
    public EvaluationResult evaluate(List<Episode> testEpisodes) {
        int correct = 0;
        int total = 0;
        
        for (Episode episode : testEpisodes) {
            // Compute prototypes from support set
            model.computePrototypes(episode.getSupportSet(), episode.getSupportLabels());
            
            // Classify queries
            for (int i = 0; i < episode.getQueries().length; i++) {
                int pred = model.predict(episode.getQueries()[i]);
                if (pred == episode.getQueryLabels()[i]) correct++;
                total++;
            }
        }
        
        return new EvaluationResult((double) correct / total);
    }
}
```

### Sourced field notes (fetched Oct 2026 — verify before citing)
- Few-shot learning enables models to learn new concepts from very few examples.
- Reference: https://arxiv.org/abs/1703.05175
- Reference: https://github.com/oscarknagg/few-shot

## Deliverables

- [x] Prototypical Networks implementation
- [x] Support set preparation
- [x] Query classification
- [x] Episode-based evaluation
- [x] Comparison with baseline methods
