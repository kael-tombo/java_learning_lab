# Recommendation Systems - MINI PROJECT

## Project: Collaborative Filtering Recommender

Build a collaborative filtering recommendation system.

### Implementation

```java
public class CollaborativeFiltering {
    private double[][] userItemMatrix;
    private double[][] userFactors;
    private double[][] itemFactors;
    private int numFactors;
    
    public void fit(double[][] ratings, int numFactors, double lr, double reg, int epochs) {
        this.numFactors = numFactors;
        int numUsers = ratings.length;
        int numItems = ratings[0].length;
        
        // Initialize factors randomly
        userFactors = randomMatrix(numUsers, numFactors);
        itemFactors = randomMatrix(numItems, numFactors);
        
        // SGD training
        for (int epoch = 0; epoch < epochs; epoch++) {
            for (int u = 0; u < numUsers; u++) {
                for (int i = 0; i < numItems; i++) {
                    if (ratings[u][i] > 0) {
                        double pred = predict(u, i);
                        double error = ratings[u][i] - pred;
                        
                        for (int f = 0; f < numFactors; f++) {
                            double uF = userFactors[u][f];
                            double iF = itemFactors[i][f];
                            userFactors[u][f] += lr * (error * iF - reg * uF);
                            itemFactors[i][f] += lr * (error * uF - reg * iF);
                        }
                    }
                }
            }
        }
    }
    
    public double predict(int user, int item) {
        double sum = 0;
        for (int f = 0; f < numFactors; f++) {
            sum += userFactors[user][f] * itemFactors[item][f];
        }
        return sum;
    }
    
    public List<Integer> recommend(int user, int n) {
        // Return top-n items with highest predicted ratings
        return IntStream.range(0, itemFactors.length)
            .boxed()
            .sorted((i1, i2) -> Double.compare(predict(user, i2), predict(user, i1)))
            .limit(n)
            .collect(Collectors.toList());
    }
}
```

### Test It

```java
@Test
public void testCollaborativeFiltering() {
    double[][] ratings = {{5,3,0,1},{4,0,0,1},{1,1,0,5},{1,0,0,4},{0,1,5,4}};
    CollaborativeFiltering cf = new CollaborativeFiltering();
    cf.fit(ratings, 2, 0.01, 0.02, 100);
    assertTrue(cf.predict(0, 2) > 0);
}
```

## Deliverables

- [ ] Matrix factorization implementation
- [ ] SGD training with regularization
- [ ] Rating prediction
- [ ] Top-N recommendations
- [ ] Evaluation with RMSE and precision@k
