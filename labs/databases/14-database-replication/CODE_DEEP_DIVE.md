# Code Deep Dive: Database Replication

## Architecture Overview
This deep dive examines the Java implementation patterns used throughout this lab. The code leverages Java 21+ features including records, sealed classes, pattern matching, and virtual threads.

## Core Implementation Patterns

### Pattern 1: Strategy Pattern
All implementations follow a strategy pattern that separates algorithm from orchestration. This interface allows swapping between different implementation strategies cleanly:

`java
public interface Strategy<K, V> {
    V locate(K key);
    Map<V, List<K>> distribute(Collection<K> keys);
    void rebalance(Map<V, Long> capacities);
    double getBalanceFactor();
}
`

### Pattern 2: Thread-Safe State with ReadWriteLock
Routing tables are accessed by multiple threads concurrently:

`java
private final ReentrantReadWriteLock lock = new ReentrantReadWriteLock();

public T getNode(String key) {
    lock.readLock().lock();
    try { return ring.get(hash(key)); }
    finally { lock.readLock().unlock(); }
}

public void addNode(T node) {
    lock.writeLock().lock();
    try { addNodeInternal(node); }
    finally { lock.writeLock().unlock(); }
}
`

### Pattern 3: Builder for Complex Configuration
`java
Manager manager = Manager.builder()
    .withVirtualNodes(150)
    .withRebalanceThreshold(0.3)
    .withMonitoring(true)
    .build();
`

### Pattern 4: Async Result Aggregation with CompletableFuture
Cross-node queries use CompletableFuture for parallel execution:

`java
public CompletableFuture<Result> scatterGather(Query query) {
    List<CompletableFuture<Partial>> futures = nodes.stream()
        .map(n -> CompletableFuture.supplyAsync(() -> execute(n, query)))
        .toList();
    return CompletableFuture.allOf(futures.toArray(new CompletableFuture[0]))
        .thenApply(v -> merge(futures.stream().map(CompletableFuture::join).toList()));
}
`

## Key Classes

### MainRouter.java
Entry point for routing operations. Initializes the routing strategy, manages configuration, and coordinates cross-shard operations.

### HashRing.java
Implements the consistent hash ring with virtual node support. Uses SHA-256 (configurable) and a TreeMap for O(log N) lookups.

### PartitionManager.java
Manages range-based partitions with split/merge support. Uses NavigableMap for efficient lookups.

## Testing Strategy

### Unit Tests
- Each strategy tested in isolation
- Deterministic behavior verification
- Edge cases (empty ring, single node, node failure)

### Integration Tests
- Testcontainers for real database instances
- Multi-node scenario verification
- Consistency guarantee validation

### Performance Tests
- JMH benchmarks for routing operations
- Throughput and latency measurements
- Scalability tests with increasing node count

## Performance Considerations

### Hash Computation
- SHA-256 is cryptographically secure but slow
- For non-security applications, consider MurmurHash3
- Cache hash values where possible

### Memory Usage
- Hash ring state: O(V × N) where V = virtual nodes, N = physical nodes
- For V=150 and N=100: ~15,000 entries, minimal memory footprint
