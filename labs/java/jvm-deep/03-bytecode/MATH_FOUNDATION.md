# MATH_FOUNDATION — Bytecode Serialization

## 1. Space Complexity Analysis

For an N-node tree where each node has value + child count + children:

| Component | Bytes per node |
|-----------|----------------|
| Value (int32) | 4 bytes |
| Child count (int32) | 4 bytes |
| **Subtotal per node** | **8 bytes** |
| **Total for N nodes** | **8N bytes** |

### Comparison: Binary vs JSON

| Format | Bytes per node (est.) | Overhead |
|---------|----------------------|----------|
| Binary (this lab) | 8 + children | Minimal |
| JSON (pretty) | ~50-100+ | Braces, quotes, commas |
| JSON (compact) | ~30-50 | Braces, quotes, commas |

**Space savings**: 3-6x smaller than compact JSON, 5-10x vs pretty JSON.

---

## 2. Variable-Length Encoding (LEB128)

For values that are typically small, fixed 4-byte ints waste space.

### LEB128 Encoding

```
Value  | Binary          | LEB128 bytes
-------|-----------------|-------------
0      | 0000 0000       | 0x00
127    | 0111 1111       | 0x7F
128    | 1000 0000       | 0x80 0x01
300    | 1 0010 1100     | 0xAC 0x02
16383  | 11 1111 1111    | 0xFF 0x7F
16384  | 1 0000 0000 0000| 0x80 0x80 0x01
```

### Space Savings Analysis

For values uniformly distributed in [0, 1000]:
- Fixed 4-byte: 4 bytes/value
- LEB128: ~1.5 bytes average (most values < 128)
- **Savings: ~60%**

---

## 3. Tree Size Formulas

### N-ary Tree Properties

Let:
- N = total nodes
- b = average branching factor
- h = height

Then:
- **Nodes at depth d**: b^d
- **Total nodes**: N = (b^(h+1) - 1) / (b - 1)  (for b > 1)
- **Height**: h = log_b(N(b-1) + 1) - 1

### Serialization Size Formula

```
Total bytes = N * 8 + overhead
```

Where overhead includes:
- Root marker (if any): 0-4 bytes
- Alignment/padding: 0-3 bytes

---

## 4. Information Theory Bounds

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

## 5. Stream Processing Complexity

### Streaming Bounds

| Operation | Time | Space (aux) |
|-----------|------|-------------|
| Serialize | O(N) | O(h) recursion stack |
| Deserialize | O(N) | O(h) recursion stack |
| Iterative deserialize | O(N) | O(h) explicit stack |

### Lower Bounds

Any tree serialization must:
- Visit each node: Ω(N) time
- Store structure: Ω(N) bits
- Output bytes: Ω(N) I/O

---

## 5. Bit-Level Packing

For maximum density, consider bit-packing multiple fields:

```
[nodeType: 2 bits][hasChildren: 1 bit][value: 29 bits]
```

Saves 1 byte/node for trees with small values. Use when N > 10⁶.

---

## 6. Compression Bounds

For trees with repetitive structure:

| Technique | Savings |
|-----------|---------|
| gzip on binary | 30-50% |
| Delta encoding (parent delta) | 20-40% |
| Dictionary (shared subtrees) | 50-80% |
| Combined (delta + gzip) | 60-80% |

---

## 7. Complexity Summary

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