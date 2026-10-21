# Interview Questions: Bloom Filter Variants

## LeetCode Problem Map
| Problem | Difficulty | Company Signal | Pattern |
|---------|-----------|----------------|---------|
| LC 705 Design HashSet | Easy | Google, Amazon, Microsoft | Hint: Bloom-like array |

Note: Bloom filters have few direct LC problems but are a popular system design topic at FAANG.

## NeetCode Reference
Not covered as a standalone problem in NeetCode 150. Relevant to system design interviews.

## Company-Specific Questions
### Google
- Design a Bloom filter for Chrome's malicious URL checker
- How would you implement a counting Bloom filter for cache admission?
- Compare Bloom filters vs Cuckoo filters vs XOR filters for different use cases
- Design a distributed Bloom filter for Google Search index deduplication
- How does Bigtable use Bloom filters to reduce disk reads?

### Microsoft
- How does Bing use Bloom filters for page deduplication?
- Design a spell-checker using Bloom filters
- Explain the trade-offs: standard Bloom vs counting vs cuckoo filter
- How would you implement a Bloom filter in a distributed system?

### Meta
- Design a Bloom filter for detecting duplicate Facebook posts
- How would you use a Bloom filter for friend recommendation deduplication?
- Counting Bloom filter for content frequency estimation
- Design a system for spam detection using Bloom filters

### Amazon
- How does DynamoDB use Bloom filters for partition lookup?
- Design a product cache using Bloom filters for hot vs cold detection
- Counting Bloom filter for inventory item frequency tracking
- How would you use a Bloom filter in a distributed key-value store?

### Apple
- Memory-efficient Bloom filter for iOS app (Safari fraud detection)
- How would you implement a Bloom filter on Apple Watch?
- Design a privacy-preserving contact tracing system using Bloom filters
- Cuckoo filter for low false-positive rate on resource-constrained devices

### Oracle
- How does Oracle use Bloom filters in query execution (bloom pruning)?
- Design a Bloom filter for distributed database partition pruning
- Explain Oracle's bloom filter optimization in parallel joins
- How would you implement a counting Bloom filter for data warehouse aggregation?

## Real Production Scenarios
- Scenario 1: CDN cache deduplication - using a Bloom filter to avoid caching duplicate content in a CDN edge node, reducing storage costs by 30% while tolerating a 1% false-positive rate
- Scenario 2: Database query acceleration - implementing Bloom filter indexes to prune partitions in a distributed query engine (e.g., Presto/Trino) reducing scan by 80%
- Scenario 3: Web crawler deduplication - debugging a Bloom filter that misses a significant fraction of already-seen URLs due to insufficient hash functions, causing duplicate page processing

## Interview Tips
- Standard Bloom: O(k) hash functions, false-positive rate = (1 - e^(-kn/m))^k; no false negatives
- Counting Bloom: 4-bit counters for deletion support; Cuckoo filter: O(1) lookup with deletion
- Optimal hash count: k = (m/n) * ln(2); optimal m: m = -n * ln(p) / (ln(2))^2
- Common edge cases: filter full (all bits set), hash collision, non-uniform hash distribution

## Java-Specific Considerations
- `java.util.BitSet` for standard Bloom filter bit array; `long[]` for manual bit operations
- Hash functions: `MurmurHash3` (via Guava's `Hashing.murmur3_128()`) is preferred
- Multiple hash functions: compute two independent hashes (h1, h2) then `hi = h1 + i * h2`
- Counting Bloom: `byte[]` counters (max 15 with 4-bit counters) or `short[]` (max 65535)
- Cuckoo filter: `long[]` fingerprints; use `HashMap<Long, List<Integer>>` for bucket storage
- Pitfall: using `hashCode()` which can return negative values; always `Math.abs(hash) % m`
- Pitfall: not considering serialization of Bloom filters for distributed systems
- Guava's `BloomFilter<T>` is production-ready: `BloomFilter.create(Funnels.stringFunnel(), expectedInsertions, fpp)`
