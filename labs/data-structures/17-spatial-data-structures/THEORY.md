# Theory: Spatial Data Structures

## Fundamentals
Spatial data structures organize multi-dimensional data for efficient queries. Two primary structures are quadtrees (2D space partitioning) and k-d trees (multi-dimensional binary search trees).

## Quadtrees
A quadtree recursively partitions 2D space into four quadrants. Each node covers a rectangular region. When a region contains too many points, it splits into four children.

## K-D Trees
A k-d tree is a binary search tree where each level splits on a different dimension. For 2D, level 0 splits on x, level 1 on y, level 2 on x, etc.

## Operations
- Insert: O(log n) expected for both
- Nearest neighbor: O(log n) expected
- Range search: O(k + log n) for small k
