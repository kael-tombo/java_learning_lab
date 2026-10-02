# MATH_FOUNDATION — Bytecode Introduction (Part 2)

## 2. Information Theory Bounds

### Entropy Lower Bound

For a tree with N nodes, each with value from alphabet of size V:

```
Minimum bits = log₂(V) * N + log₂(Catalan(N))  ≈ N * log₂(V) + 2N
```

Where Catalan(N) ≈ 4^N / (N√(πN)) counts N-node ordered trees.

### Practical vs Theoretical

| Format | Bits/node (V=1000) | Overhead |
|--------|-------------------|----------|
| Theoretical min | log₂(1000) + 2 ≈ 12 | Optimal |
| Binary (this lab) | 32 + 32 = 64 | 5x overhead |
| With varint + Huffman | ~15-20 | Near optimal |

---

## 2. Compression Bounds

For trees with repetitive structure:

| Technique | Savings |
|-----------|---------|
| gzip on binary | 30-50% |
| Delta encoding (parent delta) | 20-40% |
| Dictionary (shared subtrees) | 50-80% |
| Combined (delta + gzip) | 60-80% |

---

## 3. Complexity Summary

| Metric | Formula |
|--------|---------|
| Serialization time | Θ(N) |
| Deserialization time | Θ(N) |
| Space (binary) | 8N + O(1) bytes |
| Space (JSON) | Θ(N log N) chars |
| Height (balanced) | log_b(N) |
| Height (degenerate) | N |
| Stack depth (recursive) | O(h) |
| Stack depth (iterative) | O(h) explicit |