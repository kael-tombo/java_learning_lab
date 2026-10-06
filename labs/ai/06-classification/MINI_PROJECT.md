# Classification - MINI PROJECT

## Project: Logistic Regression Classifier

Build a logistic regression classifier with multi-class support.

### Implementation

```java
public class LogisticRegression {
    private double[][] weights;
    private double[] biases;
    private int numClasses;
    
    public void fit(double[][] X, int[] y, double lr, int epochs) {
        int n = X.length;
        int m = X[0].length;
        numClasses = Arrays.stream(y).max().orElse(0) + 1;
        weights = new double[numClasses][m];
        biases = new double[numClasses];
        
        for (int epoch = 0; epoch < epochs; epoch++) {
            for (int i = 0; i < n; i++) {
                double[] probs = softmax(X[i]);
                for (int c = 0; c < numClasses; c++) {
                    double indicator = (y[i] == c) ? 1 : 0;
                    double error = probs[c] - indicator;
                    for (int j = 0; j < m; j++) {
                        weights[c][j] -= lr * error * X[i][j];
                    }
                    biases[c] -= lr * error;
                }
            }
        }
    }
    
    public int predict(double[] x) {
        double[] probs = softmax(x);
        int bestClass = 0;
        double bestProb = probs[0];
        for (int i = 1; i < probs.length; i++) {
            if (probs[i] > bestProb) {
                bestProb = probs[i];
                bestClass = i;
            }
        }
        return bestClass;
    }
    
    private double[] softmax(double[] x) {
        double[] scores = new double[numClasses];
        double max = Arrays.stream(weights[0]).max().orElse(0);
        double sum = 0;
        for (int c = 0; c < numClasses; c++) {
            scores[c] = Math.exp(dot(weights[c], x) + biases[c] - max);
            sum += scores[c];
        }
        for (int c = 0; c < numClasses; c++) scores[c] /= sum;
        return scores;
    }
}
```

### Test It

```java
@Test
public void testLogisticRegression() {
    LogisticRegression lr = new LogisticRegression();
    double[][] X = {{1,2}, {2,3}, {3,4}, {4,5}};
    int[] y = {0, 0, 1, 1};
    lr.fit(X, y, 0.1, 1000);
    assertEquals(1, lr.predict(new double[]{5,6}));
}
```

## Deliverables

- [ ] Binary and multi-class logistic regression
- [ ] Softmax activation
- [ ] Cross-entropy loss
- [ ] Accuracy and confusion matrix
- [ ] Decision boundary visualization
