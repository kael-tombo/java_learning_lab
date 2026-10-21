# Math Foundation

## Persistence Overhead

Each update creates O(log n) new nodes. With m updates:
- Total nodes created: O(m log n)
- Space: O(n + m log n) with structural sharing

## Comparison

| Structure | Ephemeral Space | Persistent Space | Overhead |
|-----------|----------------|-----------------|----------|
| List | O(n) | O(m) | O(m) nodes |
| BST | O(n) | O(m log n) | O(log n) per op |
| Hash Map | O(n) | O(m log n) | O(log n) per op |

## Amortized Analysis

In persistent structures, each operation creates nodes that are never reclaimed (no GC for old versions). However, structural sharing ensures the total memory is O(n + m log n), which is acceptable for most applications.
