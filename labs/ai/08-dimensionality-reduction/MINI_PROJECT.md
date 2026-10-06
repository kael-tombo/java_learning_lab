# Dimensionality Reduction - MINI PROJECT

## Project: PCA Implementation from Scratch

Build a complete PCA implementation with visualization.

### Implementation

```java
public class PCA {
    private double[][] components;
    private double[] explainedVariance;
    private double[] mean;
    
    public void fit(double[][] X) {
        int n = X.length;
        int m = X[0].length;
        
        // Center the data
        mean = new double[m];
        for (int j = 0; j < m; j++) {
            for (int i = 0; i < n; i++) mean[j] += X[i][j];
            mean[j] /= n;
        }
        
        double[][] centered = new double[n][m];
        for (int i = 0; i < n; i++)
            for (int j = 0; j < m; j++)
                centered[i][j] = X[i][j] - mean[j];
        
        // Compute covariance matrix
        double[][] cov = new double[m][m];
        for (int i = 0; i < m; i++)
            for (int j = 0; j < m; j++)
                for (int k = 0; k < n; k++)
                    cov[i][j] += centered[k][i] * centered[k][j];
        
        // Eigendecomposition
        EigenDecomposition eig = new EigenDecomposition(cov);
        components = eig.getEigenvectors();
        explainedVariance = eig.getEigenvalues();
    }
    
    public double[][] transform(double[][] X, int nComponents) {
        double[][] result = new double[X.length][nComponents];
        for (int i = 0; i < X.length; i++)
            for (int j = 0; j < nComponents; j++)
                for (int k = 0; k < X[0].length; k++)
                    result[i][j] += (X[i][k] - mean[k]) * components[j][k];
        return result;
    }
    
    public double explainedVarianceRatio(int nComponents) {
        double total = Arrays.stream(explainedVariance).sum();
        double sum = 0;
        for (int i = 0; i < nComponents; i++) sum += explainedVariance[i];
        return sum / total;
    }
}
```

### Test It

```java
@Test
public void testPCA() {
    PCA pca = new PCA();
    double[][] X = {{1,2}, {2,3}, {3,4}, {4,5}};
    pca.fit(X);
    double[][] reduced = pca.transform(X, 1);
    assertEquals(4, reduced.length);
    assertEquals(1, reduced[0].length);
}
```

## Deliverables

- [ ] PCA implementation from scratch
- [ ] Explained variance calculation
- [ ] Data transformation
- [ ] Visualization of principal components
- [ ] Comparison with SVD-based PCA
