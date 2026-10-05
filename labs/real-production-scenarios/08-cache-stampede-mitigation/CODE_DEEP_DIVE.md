# CODE DEEP DIVE — Lab 08: Stampede Runbook

## 1. Detect Hot Key + Cliff
```bash
redis-cli -h prod-redis INFO stats | grep -E "keyspace_hits|keyspace_misses|expired_keys"
redis-cli SLOWLOG GET 10
kubectl logs -l app=catalog --tail=500 | grep -oE "product:[0-9]+" | sort | uniq -c | sort -rn | head
# log snippet:
# Cache MISS product:88412 (hitRatio 0.41, misses/s 6120, dbPool 198/200)
# HikariPool - Connection is not available, request timed out after 30000ms
```

## 2. Singleflight (Java)
```java
ConcurrentHashMap<String, CompletableFuture<Product>> inflight = new ConcurrentHashMap<>();
Product get(String id) {
  Product stale = cache.getIfPresent(id);
  try {
    return inflight.computeIfAbsent(id, k ->
      CompletableFuture.supplyAsync(() -> db.load(k), loaderPool))
      .get(2, TimeUnit.SECONDS);
  } catch (Exception e) {
    metrics.counter("cache.fallback.stale").increment();
    if (stale != null) return stale;
    throw new ServiceUnavailableException("warming", e);
  } finally { inflight.remove(id); }
}
```

## 3. Jittered TTL + SWR (Caffeine/Redis)
```java
Caffeine.newBuilder().refreshAfterWrite(4, TimeUnit.MINUTES).maximumSize(50_000).build(this::load);
long ttl = (long)(300 * (1 + ThreadLocalRandom.current().nextDouble(-0.15, 0.15)));
redis.setex("product:"+id, ttl, json);
```

## 4. Fill Throttle + Negative Cache
```java
Semaphore fillGuard = new Semaphore(10);
if (!fillGuard.tryAcquire()) { return staleOr429(); }
try { /* load + cache, include nulls 45s */ } finally { fillGuard.release(); }
```

## 5. Hot-Key Split Read
```bash
for i in $(seq 1 8); do redis-cli GET "product:88412#$i" > /dev/null & done
```

## 6. Hit-Rate Alert
```promql
sum(rate(cache_hits[2m])) / (sum(rate(cache_hits[2m]))+sum(rate(cache_misses[2m]))) < 0.85
```

## 7. Anti-Patterns
- `FLUSHDB` in incident — guarantees second stampede.
- Fixed 300s TTL fleet-wide + synchronized deploys = periodic cliff.
