# Performance

| Structure | Build | NN Query | Range Query | Memory |
|-----------|-------|----------|-------------|--------|
| Quadtree | O(n log n) | O(log n) | O(k + log n) | O(n) |
| K-D Tree | O(n log n) | O(log n) | O(n^(1-1/d)) | O(n) |
| Brute force | O(1) | O(n) | O(n) | O(n) |

For n = 10^6 2D points:
- Quadtree nearest neighbor: ~1μs
- K-D tree nearest neighbor: ~0.5μs
- Brute force: ~1ms
