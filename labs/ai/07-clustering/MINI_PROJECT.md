# Clustering - MINI PROJECT

## Project: K-Means Clustering Implementation

Build a complete k-means clustering algorithm with visualization.

### Implementation

```java
public class KMeans {
    private int k;
    private double[][] centroids;
    private int[] assignments;
    
    public KMeans(int k) {
        this.k = k;
    }
    
    public void fit(double[][] data, int maxIterations) {
        int n = data.length;
        int m = data[0].length;
        assignments = new int[n];
        
        // Initialize centroids randomly
        centroids = new double[k][m];
        Random rand = new Random();
        for (int i = 0; i < k; i++) {
            centroids[i] = data[rand.nextInt(n)].clone();
        }
        
        for (int iter = 0; iter < maxIterations; iter++) {
            // Assign points to nearest centroid
            boolean changed = false;
            for (int i = 0; i < n; i++) {
                int nearest = findNearestCentroid(data[i]);
                if (assignments[i] != nearest) {
                    assignments[i] = nearest;
                    changed = true;
                }
            }
            
            if (!changed) break;
            
            // Update centroids
            updateCentroids(data);
        }
    }
    
    public double inertia(double[][] data) {
        double sum = 0;
        for (int i = 0; i < data.length; i++) {
            sum += distance(data[i], centroids[assignments[i]]);
        }
        return sum;
    }
    
    public int[] getAssignments() { return assignments; }
    public double[][] getCentroids() { return centroids; }
}
```

### Test It

```java
@Test
public void testKMeans() {
    KMeans km = new KMeans(2);
    double[][] data = {{1,2}, {1,4}, {10,2}, {10,4}};
    km.fit(data, 100);
    assertEquals(2, km.getAssignments()[0] == km.getAssignments()[1] ? 1 : 0);
}
```

## Deliverables

- [ ] K-means algorithm implementation
- [ ] Elbow method for choosing k
- [ ] Silhouette score calculation
- [ ] Visualization of clusters
- [ ] Comparison with hierarchical clustering
