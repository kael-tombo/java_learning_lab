# Benchmark: LRU Cache

## Benchmark Scenarios

1. **Correctness baseline**: verify get/put/evict against expected recency order
2. **Throughput**: ops/sec under random key access
3. **Recency-order overhead**: get/put with move-to-front vs without (raw HashMap)
4. **Capacity pressure**: eviction rate as key universe exceeds capacity
5. **Hit rate**: fraction of gets served, on a realistic trace

## Metrics

- Time per get/put (ns)
- Operations per second
- Evictions per 1k ops
- Hit rate on a hot-skew trace (Zipf)
- Heap usage of the node-per-entry list

## Run with

```bash
javac -d out $(find src -name '*.java')
java -cp out Benchmark
```
