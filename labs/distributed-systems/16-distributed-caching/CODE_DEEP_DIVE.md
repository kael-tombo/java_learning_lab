# Code Deep Dive — Distributed Caching

## 1. CacheClient Interface

`java
public interface CacheClient {
    Optional<V> get(K key);
    void put(K key, V value, Duration ttl);
    boolean delete(K key);
    boolean exists(K key);
}
`

## 2. RedisClusterClient Implementation

- Uses Jedis or Lettuce for Redis Cluster connectivity
- Hash slot-based key distribution
- Automatic failover and topology discovery
- Pipelining for batch operations

## 3. MemcachedClient Implementation

- Uses spymemcached or xmemcached library
- Consistent hashing for key distribution
- Binary protocol for efficiency
- Connection pooling

## 4. CacheAsideStrategy Implementation

`
get(key):
  value = cache.get(key)
  if value == null:
    value = db.query(key)
    cache.put(key, value, ttl)
  return value
`

## 5. WriteBehindCache Implementation

- Queue writes in ConcurrentHashMap buffer
- Background thread flushes buffer periodically
- Configurable batch size and interval
- Retry on failure with exponential backoff
