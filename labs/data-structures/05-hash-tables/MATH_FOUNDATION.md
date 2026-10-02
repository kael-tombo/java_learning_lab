# Mathematical Foundation — Hash Table (Design HashMap)

## 1. Hash Table Abstract Data Type

A **hash table** maps keys to values using a hash function to compute array indices.

### Core Operations
| Operation | Average | Worst Case |
|-----------|---------|------------|
| `put(key, value)` | O(1) | O(n) |
| `get(key)` | O(1) | O(n) |
| `remove(key)` | O(1) | O(n) |
| `contains(key)` | O(1) | O(n) |
| `size()` | O(1) | O(1) |

---

## 2. Hash Function Design

### Requirements
1. **Deterministic**: Same key → same hash
2. **Uniform distribution**: Keys spread evenly across buckets
3. **Fast computation**: O(1) time
4. **Avalanche effect**: Small key change → large hash change

### Java's Integer.hashCode()
```java
public static int hashCode(int value) {
    return value;
}
```

### Supplemental Hash (Power-of-2 Tables)
```java
static int hash(int key) {
    int h = key.hashCode();  // or Integer.hashCode(key)
    h ^= (h >>> 16);         // mix high 16 bits into low 16 bits
    return h & (capacity - 1);  // modulo power of 2
}
```

### Why XOR-Shift?
With power-of-2 capacity, index = `hash & (capacity - 1)` uses only low bits.
- If keys differ only in high bits, they collide.
- XOR-shift mixes high bits into low bits.
- `h >>> 16` shifts high 16 bits to low position.
- `h ^ (h >>> 16)` combines them.

### Alternative: Multiplicative Hashing
```java
// Knuth's multiplicative hash
static int hash(int key) {
    return (key * 0x9e3779b9) >>> (32 - log2(capacity));
}
```
Golden ratio `0x9e3779b9` = 2654435769 = ⌊2³²/φ⌋.

---

## 3. Collision Resolution

### Separate Chaining (Used in Solution)

**Structure**: Array of linked lists.
```
buckets[0] → Entry → Entry → null
buckets[1] → null
buckets[2] → Entry → null
...
```

**Operations**:
- `put`: Hash to bucket, traverse list, update or prepend.
- `get`: Hash to bucket, traverse list, return value or -1.
- `remove`: Hash to bucket, traverse, relink pointers.

**Complexity**:
- Average chain length = load factor α = n / m
- **Time**: O(1 + α) average, O(n) worst case
- **Space**: O(n + m) for entries + bucket array

### Open Addressing (Alternative)

**Structure**: Single array, probing sequence on collision.
```
[Key1][Key2][ ][Key3][ ][Key4]...
```

**Probing Methods**:
1. **Linear**: `h(k, i) = (h(k) + i) % m` — clustering
2. **Quadratic**: `h(k, i) = (h(k) + c₁i + c₂i²) % m` — secondary clustering
3. **Double Hashing**: `h(k, i) = (h₁(k) + i × h₂(k)) % m` — best distribution

**Deletion**: Mark as "deleted" (tombstone), not empty.

---

## 4. Load Factor and Resizing

### Load Factor Definition
```
α = n / m
```
where n = number of entries, m = bucket count (capacity).

### Trade-off
| Low α (e.g., 0.5) | High α (e.g., 0.9) |
|-------------------|-------------------|
| Fewer collisions | Less memory |
| Faster operations | More collisions |
| More empty space | Slower operations |

### Default 0.75 Analysis
- Expected chain length = 0.75
- Probability of chain length ≥ k: P(X ≥ k) ≈ e^(-α) × α^k / k!
- For α=0.75: P(≥3) ≈ 0.04, P(≥5) ≈ 0.001
- Memory overhead: ~33% empty buckets

### Resize Algorithm
```java
void resize() {
    Entry[] oldBuckets = buckets;
    buckets = new Entry[oldBuckets.length * 2];
    size = 0;
    
    for (Entry head : oldBuckets) {
        Entry curr = head;
        while (curr != null) {
            put(curr.key, curr.value);  // rehash with new capacity
            curr = curr.next;
        }
    }
}
```

### Amortized Analysis of Resize
- Capacity sequence: 16, 32, 64, 128, ...
- Total entries rehashed after n inserts: n + n/2 + n/4 + ... < 2n
- **Amortized O(1) per put**

---

## 5. Mathematical Analysis of Separate Chaining

### Expected Chain Length
For n keys, m buckets, uniform hash:
- **Expected length of any chain**: α = n/m
- **Expected search time (unsuccessful)**: 1 + α
- **Expected search time (successful)**: 1 + α/2

### Variance
- Chain lengths follow Binomial(n, 1/m) ≈ Poisson(α)
- Variance = α
- Standard deviation = √α

### Maximum Chain Length
For m buckets, n = αm keys:
```
E[max chain] ≈ log m / log log m  (for α = O(1))
```
With α = 0.75, m = 1024: max chain ≈ 4-5 with high probability.

### Java 8 Treeify Optimization
When chain length > 8 (TREEIFY_THRESHOLD):
- Convert linked list to red-black tree
- Search becomes O(log n) worst case
- Revert to list when length < 6 (UNTREEIFY_THRESHOLD)

---

## 6. Universal Hashing (Theoretical)

### Definition
A family of hash functions H is **universal** if for any distinct keys x ≠ y:
```
Pr[h(x) = h(y)] ≤ 1/m  for h chosen uniformly from H
```

### Construction (Carter-Wegman)
```
h_{a,b}(x) = ((a × x + b) mod p) mod m
```
where p is prime > max key, a ∈ [1, p-1], b ∈ [0, p-1].

**Guarantee**: Expected chain length ≤ 1 + α for any input set.

### Why Not Used in Practice?
- Random a,b per table — not deterministic
- Fixed hash functions with good mixing (like XOR-shift) work well empirically
- Java's HashMap uses fixed supplemental hash

---

## 7. Space Complexity Analysis

### Separate Chaining
```
Total space = m × pointer_size + n × (key_size + value_size + pointer_size)
            = O(m + n)
```
Typical overhead: ~8 bytes per entry (next pointer) + bucket array.

### Open Addressing
```
Total space = m × (key_size + value_size + status_byte)
            = O(m)
```
Better cache locality, no pointer overhead. But m must be larger (α < 0.7).

### Java HashMap (Typical)
- Default capacity: 16
- Max capacity: 1 << 30
- Entry: key(4/8) + value(4/8) + next(4/8) + hash(4) = 24-32 bytes
- 1M entries ≈ 32-64 MB + bucket array

---

## 8. Perfect Hashing (Static Sets)

For static key set (no inserts/deletes):
- **Two-level hashing**: O(1) worst-case lookup
- First level: m buckets
- Second level: Each bucket has its own hash table sized to k² (k = bucket size)
- Total space: O(n)
- Lookup: 2 hash computations + 1 array access

---

## 9. Comparison: Hash Table vs Balanced BST

| Aspect | Hash Table | Red-Black Tree (TreeMap) |
|--------|------------|-------------------------|
| Search | O(1) avg | O(log n) worst |
| Insert | O(1) avg | O(log n) worst |
| Delete | O(1) avg | O(log n) worst |
| Order | None | Sorted |
| Range query | O(n) | O(log n + k) |
| Memory | Higher | Lower (no empty buckets) |
| Worst case | O(n) | O(log n) |

---

## 10. Applications and Patterns

### Frequency Counting
```java
Map<Integer, Integer> freq = new HashMap<>();
for (int x : arr) freq.merge(x, 1, Integer::sum);
```

### Grouping
```java
Map<String, List<String>> groups = new HashMap<>();
for (String s : arr) groups.computeIfAbsent(key(s), k -> new ArrayList<>()).add(s);
```

### Two Sum / Pair Problems
```java
// O(n) time, O(n) space
Map<Integer, Integer> map = new HashMap<>();
for (int i = 0; i < n; i++) {
    if (map.containsKey(target - nums[i])) return new int[]{map.get(target - nums[i]), i};
    map.put(nums[i], i);
}
```

### Caching (LRU)
- HashMap: key → Node (O(1) lookup)
- Doubly Linked List: LRU order (O(1) move/remove)
- Combined: O(1) get/put

### Distributed Systems
- Consistent Hashing: Minimize reshuffling on node add/remove
- Virtual Nodes: Balance load across heterogeneous nodes

---

## 11. Summary: Complexity Guarantees

| Operation | Separate Chaining | Open Addressing | Java HashMap |
|-----------|-------------------|-----------------|--------------|
| put (avg) | O(1) | O(1/(1-α)) | O(1) |
| put (worst) | O(n) | O(n) | O(n)* |
| get (avg) | O(1) | O(1/(1-α)) | O(1) |
| get (worst) | O(n) | O(n) | O(log n)* |
| Space | O(n+m) | O(m) | O(n+m) |

*Java 8+ treeifies long chains → O(log n) worst case for get

**Key Insight**: Hash tables trade worst-case guarantees for average-case speed. With good hash function and load factor management, O(1) average is achieved in practice.