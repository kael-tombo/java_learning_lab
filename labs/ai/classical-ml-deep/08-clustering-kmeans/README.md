# 08-clustering-kmeans - K-Means
## Overview
Lloyd's algorithm alternates nearest-centroid assignment with mean recomputation, monotonically decreasing WCSS. Result depends on init; k-means++ seeds spread-out starts.
## Key formulas
- Assign: a_i = argmin_k ||x_i - c_k||^2; update: c_k = mean of members.
- WCSS = sum_k sum_{i in k} ||x_i - c_k||^2.
## What the snippets show
- Cml08A: two Lloyd iterations converging to (0.3333/5.3333) centroids.
- Cml08B: WCSS=2.6667 with per-point 4/9 hand check.
## Try it
Init both centroids inside one blob and observe the empty-cluster failure mode.
## Formula reference
- Assign argmin_k ||x - c_k||^2; update c_k = member mean; WCSS monotone down.
- k-means++ seeds with prob proportional to squared distance.
- Elbow/silhouette select k; empty clusters need re-seeding.
## Worked example
- Init (0,0): corner points attach; mean = (0+1+0)/3, (0+0+1)/3 = (1/3,1/3).
- Per-point cost (1/3)^2+(1/3)^2 = 2/9... corner (1,0): (2/3)^2+(1/3)^2 = 5/9? recompute: (1-1/3)^2 + (0-1/3)^2 = 4/9+1/9 = 5/9; total 6 pts = 8/3 = 2.6667.
- Second iteration unchanged: fixed point reached.
## Pitfalls
- Spherical bias: stretched clusters split wrongly; scale or use GMM.
- k must be chosen; wrong k merges/splits true groups.
- Outliers drag means; trim or use k-medians.
## Connections
- WCSS objective mirrors vector quantization distortion.
- DBSCAN drops the k requirement via density instead.
## Exercises
1. Init both centroids at (0,0) and (1,0); trace assignments.
2. Compute WCSS for k = 1 on the 6 points.
3. Add outlier (20,20) and watch c1 migrate.
