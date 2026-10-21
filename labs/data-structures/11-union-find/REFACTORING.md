# Refactoring Union-Find

## Refactoring Opportunities

### 1. Extract Interface

`java
public interface DisjointSet {
    int find(int x);
    boolean union(int x, int y);
    boolean connected(int x, int y);
    int getSets();
}
`

This allows multiple implementations (rank, size, lock-free, persistent).

### 2. Add Generic Support

`java
public class DisjointSetUnion<T> {
    private final Map<T, Integer> elementToId;
    private final List<T> idToElement;
    private int[] parent, rank;
    
    public void add(T element) {
        if (!elementToId.containsKey(element)) {
            elementToId.put(element, idToElement.size());
            idToElement.add(element);
            // expand arrays
        }
    }
}
`

### 3. Thread Safety Wrapper

`java
public class SynchronizedDisjointSet implements DisjointSet {
    private final DisjointSet delegate;
    private final ReadWriteLock lock = new ReentrantReadWriteLock();
    
    @Override
    public int find(int x) {
        lock.readLock().lock();
        try { return delegate.find(x); }
        finally { lock.readLock().unlock(); }
    }
    
    @Override
    public boolean union(int x, int y) {
        lock.writeLock().lock();
        try { return delegate.union(x, y); }
        finally { lock.writeLock().unlock(); }
    }
}
`

### 4. Memory Optimization

For large datasets, use byte/short arrays instead of int arrays:
`java
class CompactDSU {
    private byte[] parent;  // supports up to 127 elements
    private byte[] rank;
}
`

### 5. Persistent DSU (for backtracking)

Maintain a stack of changes to support undo:
`java
class PersistentDSU {
    private int[] parent, rank;
    private Deque<Change> history = new ArrayDeque<>();
    
    public boolean union(int x, int y) {
        // record changes before modifying
        // push to history
        // modify
    }
    
    public void undo() {
        // pop from history, revert changes
    }
}
`

### 6. Iterative Find for Stack Safety

Replace the elegant recursive find with an iterative version for large n:

`java
public int findIterative(int x) {
    // Find root
    int root = x;
    while (root != parent[root]) {
        root = parent[root];
    }
    // Compress path
    while (x != root) {
        int next = parent[x];
        parent[x] = root;
        x = next;
    }
    return root;
}
`

### 7. Benchmark Harness

Refactor to support easy benchmarking of different optimization strategies:

`java
public class DSUBenchmark {
    public static long benchmark(Supplier<DisjointSet> factory, int n, int ops) {
        DisjointSet dsu = factory.get();
        Random rng = new Random(42);
        long start = System.nanoTime();
        for (int i = 0; i < ops; i++) {
            int a = rng.nextInt(n);
            int b = rng.nextInt(n);
            if (rng.nextBoolean()) dsu.union(a, b);
            else dsu.find(a);
        }
        return System.nanoTime() - start;
    }
}
`
"@

System.Collections.Hashtable["PERFORMANCE.md"] = @"
# Performance of Union-Find

## Theoretical Performance

| Optimization Level | Find Time | Union Time | Space |
|-------------------|-----------|------------|-------|
| None | O(n) worst, O(log n) avg | O(log n) | O(n) |
| Union by Rank only | O(log n) | O(log n) | O(n) |
| Path Compression only | O(log n) amortized | O(log n) | O(n) |
| Both | O(alpha(n)) amortized | O(alpha(n)) amortized | O(n) |

## Empirical Performance

For n = 10^6 elements and 10^7 operations:

| Implementation | Time (ms) | Operations/sec |
|---------------|-----------|----------------|
| Naive (no optimization) | ~4500 | ~2.2M |
| Union by Rank only | ~1200 | ~8.3M |
| Path Compression only | ~800 | ~12.5M |
| Both optimizations | ~400 | ~25M |

## Memory Usage

- **int[] parent**: 4 bytes per element
- **int[] rank**: 4 bytes per element (can be byte for n < 256)
- **Object overhead**: ~24 bytes per array

Total for 10^6 elements: ~8 MB plus array object overhead.

## Cache Performance

DSU has excellent cache performance because:
1. Arrays are contiguous in memory
2. Parent pointers have spatial locality
3. Find accesses a predictable pattern of indices
4. No dynamic allocation after initialization

## Performance Tips

1. **Use iterative find** for large n to avoid stack overflow
2. **Use byte/short arrays** for rank when n is small (< 256 / < 65536)
3. **Pre-allocate** the maximum size needed; resizing is expensive
4. **Minimize method calls**: inline the find method in hot paths
5. **Use array-based DSU** instead of hash-based for int-keyed elements

## Benchmark Comparison

Compare against alternatives for connectivity queries:

| Operation | DSU | BFS/DFS | Adjacency Matrix |
|-----------|-----|---------|-----------------|
| Connect vertices u,v | O(alpha(n)) | O(1) add edge | O(1) |
| Check connectivity | O(alpha(n)) | O(n + m) | O(n) BFS |
| Build from scratch | O(n) | O(n + m) | O(n^2) |

## Real-World Scaling

- **Facebook friend graph** (2.9B users): DSU can check if two users are in the same connected component in < 1 microsecond
- **Image segmentation** (10MP image): Connected component labeling with DSU completes in < 100ms
- **Kruskal's algorithm** (10M edges): With DSU, MST can be found in ~5 seconds
