# CODE DEEP DIVE: Production Caching & Redis Patterns
## Lab 12 | Production Engineering Academy

---

## Pattern 1: Cache Breakdown Protection via Distributed Mutex Rebuild

```java
package com.learning.production.lab12;

import org.springframework.data.redis.core.StringRedisTemplate;

import java.time.Duration;
import java.util.concurrent.ThreadLocalRandom;
import java.util.concurrent.TimeUnit;
import java.util.function.Supplier;

public class StampedeSafeCacheService {
    private final StringRedisTemplate redisTemplate;

    public StampedeSafeCacheService(StringRedisTemplate redisTemplate) {
        this.redisTemplate = redisTemplate;
    }

    /**
     * Fetches value from Redis. If expired, acquires a distributed lock so ONLY ONE thread
     * queries the database, while other concurrent callers wait or receive stale data.
     */
    public String getWithStampedeProtection(
            String key,
            Duration baseTtl,
            Supplier<String> dbFallbackSupplier) {

        String value = redisTemplate.opsForValue().get(key);
        if (value != null) {
            return value;
        }

        String lockKey = "lock:rebuild:" + key;
        // Attempt to acquire lock for 5 seconds
        Boolean acquired = redisTemplate.opsForValue().setIfAbsent(lockKey, "locked", Duration.ofSeconds(5));

        if (Boolean.TRUE.equals(acquired)) {
            try {
                // Double check if another thread populated the cache while acquiring lock
                value = redisTemplate.opsForValue().get(key);
                if (value != null) {
                    return value;
                }

                // Execute expensive database query
                value = dbFallbackSupplier.get();

                if (value != null) {
                    // Apply TTL with random Jitter to prevent Cache Avalanche
                    long jitterSeconds = ThreadLocalRandom.current().nextLong(0, baseTtl.toSeconds() / 5);
                    Duration finalTtl = baseTtl.plusSeconds(jitterSeconds);
                    redisTemplate.opsForValue().set(key, value, finalTtl);
                } else {
                    // Prevent Cache Penetration: Cache null marker for 60 seconds
                    redisTemplate.opsForValue().set(key, "@@NULL@@", Duration.ofSeconds(60));
                }
                return "@@NULL@@".equals(value) ? null : value;
            } finally {
                redisTemplate.delete(lockKey); // Release lock
            }
        } else {
            // Another thread is rebuilding the cache. Sleep briefly and retry from cache
            try {
                Thread.sleep(50);
            } catch (InterruptedException ignored) {}

            value = redisTemplate.opsForValue().get(key);
            if ("@@NULL@@".equals(value)) return null;
            if (value != null) return value;

            // If still empty after waiting, execute fallback directly
            return dbFallbackSupplier.get();
        }
    }
}
```

---

## Pattern 2: Two-Level Near-Cache (Caffeine L1 + Redis L2) with Pub/Sub Invalidation

```java
package com.learning.production.lab12;

import com.github.benmanes.caffeine.cache.Cache;
import com.github.benmanes.caffeine.cache.Caffeine;
import org.springframework.data.redis.connection.Message;
import org.springframework.data.redis.connection.MessageListener;
import org.springframework.data.redis.core.StringRedisTemplate;

import java.time.Duration;

public class TwoTierCacheManager implements MessageListener {
    private final Cache<String, String> localCaffeine;
    private final StringRedisTemplate redisTemplate;
    private static final String INVALIDATION_CHANNEL = "cache:invalidation:channel";

    public TwoTierCacheManager(StringRedisTemplate redisTemplate) {
        this.redisTemplate = redisTemplate;
        this.localCaffeine = Caffeine.newBuilder()
                .maximumSize(50_000)
                .expireAfterWrite(Duration.ofMinutes(5))
                .recordStats()
                .build();
    }

    public String get(String key) {
        // Step 1: Check L1 local heap (nanoseconds)
        String localVal = localCaffeine.getIfPresent(key);
        if (localVal != null) {
            return localVal;
        }

        // Step 2: Check L2 distributed Redis (milliseconds)
        String redisVal = redisTemplate.opsForValue().get(key);
        if (redisVal != null) {
            localCaffeine.put(key, redisVal);
            return redisVal;
        }

        return null;
    }

    public void putAndPublish(String key, String value, Duration ttl) {
        // Write to Redis
        redisTemplate.opsForValue().set(key, value, ttl);
        // Put in local Caffeine
        localCaffeine.put(key, value);
        // Broadcast invalidation message so all other application pods evict their local L1
        redisTemplate.convertAndSend(INVALIDATION_CHANNEL, key);
    }

    @Override
    public void onMessage(Message message, byte[] pattern) {
        String evictedKey = new String(message.getBody());
        localCaffeine.invalidate(evictedKey);
    }
}
```
