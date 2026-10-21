# Distributed Caching (Duplicate Lab) - Interview Preparation

> Key interview questions about distributed caching strategies.

---

## Core Interview Questions

### Q1: What is a cache stampede and how to prevent it?
**Answer**: Cache stampede (thundering herd): many requests miss cache simultaneously due to key expiry, all hitting backend. Prevention: probabilistic early expiration (set TTL shorter, recompute early), mutex lock around cache regeneration ("hold the lock while regenerating"), background refresh jobs, stale-while-revalidate.

### Q2: How does Redis Cluster handle partitioning?
**Answer**: Redis Cluster uses hash slots (16384 total). Each node responsible for subset of slots. Hashed CRC16(key) % 16384 determines slot. Clients use MOVED/ASK redirects. No gossip (Redis Cluster uses its own protocol). Supports automatic failover via replication groups.

### Q3: What is "write-behind" caching and its risks?
**Answer**: Write to cache immediately, async write to database. Risk: cache failure before database write = data loss. Mitigation: write to persistent write-ahead log before acknowledging cache write, use durable cache (Redis AOF), batch writes to database.

### Q4: How does content delivery network (CDN) caching work?
**Answer**: Edge servers cache content close to users. Cache hierarchy: edge -> regional -> origin. Cache-control headers determine TTL. Invalidation via API or versioned URLs. Origin shield protects origin from edge misses. Push vs pull CDN: pull (cache-on-request) vs push (pre-seed content).

### Q5: What is "cache aside" vs "read through" pattern?
**Answer**: Cache aside (lazy loading): application checks cache, on miss loads from DB, populates cache. Application manages cache. Read through: cache library automatically loads from DB on miss (look-aside). Cache aside gives more control; read through is simpler for the application.

## Company-Specific Focus

| Company | Caching Focus |
|---------|--------------|
| Meta | "TAO cache-first architecture for social graph" |
| Amazon | "DAX cache for DynamoDB" |
| Google | "Memcache infrastructure at Google" |
| Netflix | "EVCache for Netflix microservices" |

## LeetCode Connections

| Problem | # | Caching Concept |
|---------|---|----------------|
| LRU Cache | 146 | Eviction policy |
| LFU Cache | 460 | Frequency-based eviction |
| Max Frequency Stack | 895 | Access frequency |
| Design Hit Counter | 362 | Sliding window cache |
| Design Browser History | 1472 | Cache prefetching |

## System Design Connections

- **Design a CDN**: Edge caching, invalidation, origin shield
- **Design a Session Store**: TTL-based cache with persistence
- **Design a Rate Limiter**: Sliding window cache counters
- **Design a Global Feed Cache**: Pre-computed feeds

> **Key Insight**: Caching is often the solution to scalability. Always discuss cache consistency, invalidation, and stampede prevention in system design.