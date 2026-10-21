# Performance of LRU Cache

## Empirical Benchmarks

| Operation | HashMap + DLL | LinkedHashMap |
|-----------|---------------|---------------|
| get (cache hit) | ~50ns | ~50ns |
| put (new) | ~80ns | ~100ns |
| put (update) | ~60ns | ~70ns |
| eviction | ~40ns | ~90ns |

## When to Use Each Implementation

- **HashMap + DLL**: Maximum performance, more code
- **LinkedHashMap**: Simpler, slightly slower
- **ConcurrentLRU**: Thread-safe, good for web servers
- **LFU**: When access frequency matters more than recency
