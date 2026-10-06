# Regression - MINI PROJECT

## Project: Linear Regression from Scratch

Build a complete linear regression implementation with regularization.

### Implementation

```java
public class LinearRegression {
    private double[] weights;
    private double bias;
    private double lambda; // Regularization parameter
    
    public void fit(double[][] X, double[] y, double learningRate, int epochs) {
        int n = X.length;
        int m = X[0].length;
        weights = new double[m];
        bias = 0;
        
        for (int epoch = 0; epoch < epochs; epoch++) {
            double[] gradients = new double[m];
            double biasGrad = 0;
            
            for (int i = 0; i < n; i++) {
                double prediction = predict(X[i]);
                double error = prediction - y[i];
                for (int j = 0; j < m; j++) {
                    gradients[j] += error * X[i][j];
                }
                biasGrad += error;
            }
            
            // Update with regularization (Ridge)
            for (int j = 0; j < m; j++) {
                weights[j] -= learningRate * (gradients[j] / n + lambda * weights[j]);
            }
            bias -= learningRate * biasGrad / n;
        }
    }
    
    public double predict(double[] x) {
        double result = bias;
        for (int i = 0; i < weights.length; i++) {
            result += weights[i] * x[i];
        }
        return result;
    }
    
    public double r2Score(double[][] X, double[] y) {
        double ssRes = 0, ssTot = 0;
        double yMean = Arrays.stream(y).average().orElse(0);
        for (int i = 0; i < y.length; i++) {
            double pred = predict(X[i]);
            ssRes += Math.pow(y[i] - pred, 2);
            ssTot += Math.pow(y[i] - yMean, 2);
        }
        return 1 - ssRes / ssTot;
    }
}
```

### Test It

```java
@Test
public void testLinearRegression() {
    LinearRegression lr = new LinearRegression();
    double[][] X = {{1}, {2}, {3}, {4}, {5}};
    double[] y = {2, 4, 6, 8, 10};
    lr.fit(X, y, 0.01, 1000);
    assertEquals(0.99, lr.r2Score(X, y), 0.01);
}
```

## Deliverables

- [ ] OLS regression implementation
- [ ] Ridge regularization
- [ ] Gradient descent training
- [ ] R² and RMSE metrics
- [ ] Visualization of fit
