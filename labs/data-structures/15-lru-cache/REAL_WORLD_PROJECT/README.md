# Real-World Project: LRU Cache

## Scenario

A service caches rendered product pages (HTML fragments) keyed by
`productId + locale`. Memory is bounded, so old entries must be evicted.
Traffic is skewed: a small set of products accounts for most hits.

## What you build

- An `LruCache<String, byte[]>` sized to fit a memory budget
- A fronting servlet-style handler that returns cached fragments or renders
  and caches on miss
- Metrics: hits, misses, evictions, current size

## Why LRU fits

- Recency correlates with reuse: hot products stay, cold ones leave
- O(1) eviction keeps latency stable under a size cap
- Where LRU loses: scanning a full catalog once will evict everything — a
  LFU or segmented LRU may be better; measure with a realistic trace

## Success criteria

- Hit rate measured on a skewed trace
- Memory bounded by capacity at all times
- A simulated catalog scan shows the recency-vs-frequency trade-off clearly

## Run with

```bash
javac -d out $(find src -name '*.java')
java -cp out Main
```
