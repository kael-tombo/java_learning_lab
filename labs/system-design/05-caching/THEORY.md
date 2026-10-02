# Caching Strategies - THEORY

## Overview

Caching reduces latency, decreases load, and improves scalability. This lab covers caching patterns, strategies, and implementation in distributed systems.

## 1. Cache Patterns

### Cache-Aside (Lazy Loading)
```java
public String getUser(String userId) {
    // Check cache first
    String cached = cache.get(userId);
    if (cached != null) {
        return cached;
    }
    
    // Load from database
    String user = db.findUser(userId);
    
    // Store in cache
    cache.put(userId, user);
    
    return user;
}
```
**Pros**: Easy, only cache what's needed
**Cons**: Cache miss causes latency

### Read-Through
```java
public String getUser(String userId) {
    return cache.getOrCompute(userId, () -> db.findUser(userId));
}
```
**Pros**: Transparent caching
**Cons**: Cache stores everything

### Write-Through
```java
public void saveUser(String userId, String user) {
    db.saveUser(userId, user);
    cache.put(userId, user);
}
```
**Pros**: Cache always current
**Cons**: Write latency higher

### Write-Behind (Write-Back)
```java
public void saveUser(String userId, String user) {
    cache.put(userId, user);
    asyncQueue.offer(new WriteOperation(userId, user));
}

@Scheduled
public void flushWrites() {
    while (!asyncQueue.isEmpty()) {
        WriteOperation op = asyncQueue.poll();
        db.saveUser(op.getUserId(), op.getUser());
    }
}
```
**Pros**: Fast writes
**Cons**: Risk of data loss

## 2. Cache Invalidation

### Time-Based
```yaml
# TTL-based expiration
cache:
  user-profile: 300s    # 5 minutes
  session: 1800s        # 30 minutes
  config: 3600s         # 1 hour
```

### Event-Based
```java
@EventListener
public void onUserUpdate(UserUpdatedEvent event) {
    cache.invalidate("user:" + event.getUserId());
    // Publish to other cache nodes
    pubsub.publish("user-updated", event.getUserId());
}
```

### Version-Based
```java
public class VersionedCache {
    private final Map<String, VersionedValue> cache = new ConcurrentHashMap<>();
    
    public void put(String key, Object value) {
        cache.put(key, new VersionedValue(value, version++));
    }
    
    public boolean isStale(String key, long clientVersion) {
        return cache.get(key).version > clientVersion;
    }
}
```

## 3. Distributed Caching

### Redis Cluster
```yaml
# Consistent hashing for distribution
cluster:
  nodes: 6
  shards: 3
  replication: 1
  hash_slots: 16384
```

### Memcached
```java
public class MemcachedClient {
    private final MemcachedClient client;
    
    public String get(String key) {
        return client.get(key);
    }
    
    public void set(String key, String value, int ttl) {
        client.set(key, ttl, value);
    }
    
    public void delete(String key) {
        client.delete(key);
    }
}
```

## 4. Cache Warming

```java
@Service
public class CacheWarmingService {
    @PostConstruct
    public void warmCache() {
        // Load hot data on startup
        List<String> hotUsers = userService.getHotUserIds();
        hotUsers.parallelStream().forEach(id -> {
            User user = db.findUser(id);
            cache.put("user:" + id, user);
        });
    }
    
    @Scheduled(cron = "0 0 3 * * ?")
    public void scheduledWarm() {
        // Refresh every night
        warmCache();
    }
}
```

## 5. Cache Strategies by Scenario

| Scenario | Strategy | TTL | Notes |
|----------|----------|-----|-------|
| User Profile | Cache-aside | 5-15min | High read, low write |
| Product Catalog | Read-through | 1-24h | Large, stable data |
| Session | Write-through | 30min | Critical data |
| Config | Write-behind | 1h-1d | Rarely changes |
| Rate Limits | Write-behind | 1min | High volume |

## Summary

1. **Choose pattern**: Cache-aside for most, write-through for critical
2. **Invalidate properly**: TTL, events, or version-based
3. **Distribute**: Consistent hashing, Redis cluster
4. **Warm**: Preload hot data on startup
5. **Monitor**: Hit rate, latency, memory usage

## Sourced field notes (fetched Oct 2026 — verify before citing)

- Design of a Modern Cache (Benjamin Manes, HighScalability, 25 Jan 2016) — https://highscalability.com/design-of-a-modern-cache/ — Window-TinyLFU admission filter (Count-Min Sketch frequency check) plus Segmented LRU retention beats plain LRU on database/search traces — consider Caffeine-style policies before assuming the lab's default LRU is near-optimal.
- Design of a Modern Cache (Benjamin Manes, HighScalability, 25 Jan 2016) — https://highscalability.com/design-of-a-modern-cache/ — Prefer fixed-duration TTLs organized on O(1) write-order/access-order queues with lazy expiry during maintenance, which backs the lab's TTL-per-scenario table (e.g. user-profile 300s, session 1800s) and its scavenger/scheduled-refresh notes.
- Design of a Modern Cache (Benjamin Manes, HighScalability, 25 Jan 2016) — https://highscalability.com/design-of-a-modern-cache/ — Scale concurrent access with buffered async replay (striped ring buffers for reads, MPSC queue for writes) so reads scale linearly with CPUs — relevant when the lab's Redis-cluster/consistent-hashing section meets hot-key contention.