# Why LRU Cache Exists

## The Caching Problem

Applications need to store frequently accessed data in memory for fast retrieval. Without caching, every request would hit the database. Caching reduces latency by 10-100x, but memory is limited—so we need an eviction policy.

## Why LRU?

The LRU policy is based on the principle of locality of reference: recently accessed data is likely to be accessed again. This makes LRU effective for most real-world workloads.

## Why Not Use Other Policies?

- **FIFO**: May evict frequently used items
- **LFU**: Complex to implement, vulnerable to access pattern shifts
- **Random**: No guarantees on cache behavior
- **LRU**: Simple, effective, efficient
