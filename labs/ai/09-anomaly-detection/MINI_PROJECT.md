# Anomaly Detection - MINI PROJECT

## Project: Isolation Forest Implementation

Build an isolation forest for anomaly detection.

### Implementation

```java
public class IsolationForest {
    private List<IsolationTree> trees;
    private int numTrees;
    private int subSampleSize;
    
    public IsolationForest(int numTrees, int subSampleSize) {
        this.numTrees = numTrees;
        this.subSampleSize = subSampleSize;
        this.trees = new ArrayList<>();
    }
    
    public void fit(double[][] X) {
        Random rand = new Random();
        for (int t = 0; t < numTrees; t++) {
            // Subsample data
            double[][] sample = subSample(X, subSampleSize, rand);
            // Build tree
            IsolationTree tree = new IsolationTree();
            tree.build(sample, 0, (int)Math.ceil(Math.log(subSampleSize) / Math.log(2)));
            trees.add(tree);
        }
    }
    
    public double anomalyScore(double[] x) {
        double avgPath = 0;
        for (IsolationTree tree : trees) {
            avgPath += tree.pathLength(x);
        }
        avgPath /= numTrees;
        return Math.pow(2, -avgPath / averagePathLength(subSampleSize));
    }
    
    public boolean[] predict(double[][] X, double threshold) {
        boolean[] results = new boolean[X.length];
        for (int i = 0; i < X.length; i++) {
            results[i] = anomalyScore(X[i]) > threshold;
        }
        return results;
    }
}
```

### Test It

```java
@Test
public void testIsolationForest() {
    IsolationForest forest = new IsolationForest(100, 256);
    double[][] normalData = generateNormalData(1000);
    forest.fit(normalData);
    
    double[] anomaly = {100, 100, 100};
    assertTrue(forest.anomalyScore(anomaly) > 0.6);
}
```

## Deliverables

- [ ] Isolation tree implementation
- [ ] Forest construction with subsampling
- [ ] Anomaly score computation
- [ ] Threshold selection
- [ ] Comparison with LOF and One-Class SVM
