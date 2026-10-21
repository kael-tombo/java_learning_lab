# Math Foundations — Distributed Caching

## 1. Cache Hit Ratio

The cache hit ratio follows locality patterns:
- Working set size W, cache size C
- If C >= W: hit ratio approaches 100%
- If C < W: hit ratio = C/W (with random access)

## 2. Latency Impact

Average latency = P(hit) * L(cache) + P(miss) * (L(cache) + L(db))

With L(cache)=1ms, L(db)=10ms, hit=90%:
Average = 0.9 * 1 + 0.1 * 11 = 2ms (vs 10ms without cache)

## 3. Write-Behind Batch Size

Optimal batch size B for write-behind:
B = sqrt(2 * lambda * C / S)
Where lambda = write rate, C = cost per batch, S = cost per item

## 4. Cache Sizing

S = R * T * V
Where S = cache size, R = request rate, T = average TTL, V = average value size

## 5. Redis Cluster Slot Distribution

16384 hash slots distributed across N nodes
Each node responsible for ~16384/N slots
Replicas: typically 1-2 per master
