# Mini Spark - Mathematical Foundation

## Key Formulas

### 1. Similarity Metrics

- **Cosine Similarity**: sim(A,B) = (A·B) / (||A|| × ||B||)
- **L2 Distance**: d(A,B) = v(S(Ai-Bi)²)
- **Inner Product**: IP(A,B) = S(Ai × Bi)

### 2. Data Structures

- **Consistent Hashing**: hash(key) on [0, 2^64-1], node = min{hash = key}
- **PSI (Drift Detection)**: PSI = S(Pi-Qi) × ln(Pi/Qi)
- **HNSW**: Multi-layer graph with log(1/random) level assignment

### 3. Algorithmic Complexity

- Hash-based lookups: O(1) average
- Tree operations: O(log n)
- Linear scans: O(n)
- Sort-based shuffle: O(n log n)
- Collaborative filtering: O(u × p) where u=users, p=products

