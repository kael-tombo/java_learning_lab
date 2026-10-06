# Explainable AI - MINI PROJECT

## Project: SHAP Values Implementation

Build a SHAP (SHapley Additive exPlanations) implementation for model interpretability.

### Implementation

```java
public class SHAPExplainer {
    private Model model;
    private double[][] backgroundData;
    
    public SHAPExplainer(Model model, double[][] backgroundData) {
        this.model = model;
        this.backgroundData = backgroundData;
    }
    
    public double[] explain(double[] instance) {
        int numFeatures = instance.length;
        double[] shapValues = new double[numFeatures];
        
        // Compute base value (expected model output)
        double baseValue = computeBaseValue();
        
        // Compute SHAP values for each feature
        for (int f = 0; f < numFeatures; f++) {
            shapValues[f] = computeSHAPValue(instance, f, baseValue);
        }
        
        return shapValues;
    }
    
    private double computeSHAPValue(double[] instance, int feature, double baseValue) {
        double shapValue = 0;
        int numSamples = 100;
        
        for (int s = 0; s < numSamples; s++) {
            // Sample a coalition
            Set<Integer> coalition = sampleCoalition(feature);
            
            // Create two instances: with and without the feature
            double[] withFeature = createInstance(instance, coalition, feature, true);
            double[] withoutFeature = createInstance(instance, coalition, feature, false);
            
            // Compute marginal contribution
            double marginal = model.predict(withFeature) - model.predict(withoutFeature);
            
            // Weight by coalition size
            double weight = coalitionWeight(coalition.size(), instance.length);
            shapValue += weight * marginal;
        }
        
        return shapValue / numSamples;
    }
    
    public void plotSHAP(double[] instance, String[] featureNames) {
        double[] shapValues = explain(instance);
        
        // Sort by absolute SHAP value
        Integer[] indices = IntStream.range(0, featureNames.length).boxed().toArray(Integer[]::new);
        Arrays.sort(indices, (i1, i2) -> Double.compare(Math.abs(shapValues[i2]), Math.abs(shapValues[i1])));
        
        // Print waterfall plot
        for (int i = 0; i < Math.min(10, featureNames.length); i++) {
            int idx = indices[i];
            System.out.printf("%s: %.4f%n", featureNames[idx], shapValues[idx]);
        }
    }
}
```

### Test It

```java
@Test
public void testSHAP() {
    Model model = loadModel();
    double[][] background = loadBackgroundData();
    SHAPExplainer explainer = new SHAPExplainer(model, background);
    
    double[] instance = {5.1, 3.5, 1.4, 0.2};
    double[] shapValues = explainer.explain(instance);
    
    assertEquals(4, shapValues.length);
}
```

## Deliverables

- [ ] SHAP value computation
- [ ] Coalition sampling
- [ ] Marginal contribution calculation
- [ ] Waterfall plot visualization
- [ ] Comparison with LIME
