# CODE DEEP DIVE: Production Caching & Redis Patterns
## Lab 12 | Production Engineering Academy — Top 0.0001% Engineering

---

## Pattern 1: Probabilistic Early Expiration (XFetch / Vattani 2015 Algorithm)

Standard caching serves a key until it expires, causing a stampede (thundering herd) when high-QPS traffic hits a cold cache. The XFetch algorithm computes whether a key should be refreshed **probabilistically prior to expiration**, strictly bounding background refreshes to one thread while serving all concurrent readers instantly.

```java
package com.learning.production.lab12;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.redis.core.StringRedisTemplate;

import java.time.Duration;
import java.time.Instant;
import java.util.concurrent.*;
import java.util.function.Supplier;

/**
 * Implements the optimal probabilistic early refresh algorithm (VLDB 2015).
 * Formula: delta - beta * ln(U) * remaining_ttl > total_ttl
 */
public class ProbabilisticEarlyExpirationCache<T> {
    private static final Logger log = LoggerFactory.getLogger(ProbabilisticEarlyExpirationCache.class);

    private final StringRedisTemplate redisTemplate;
    private final ObjectMapper objectMapper;
    private final Class<T> targetClass;
    private final ExecutorService refreshExecutor;
    private final ConcurrentMap<String, Boolean> inFlightRefreshes = new ConcurrentHashMap<>();

    // Aggressiveness parameter beta (default = 1.0)
    private final double beta;

    public record CacheEnvelope<T>(
            @JsonProperty("data") T data,
            @JsonProperty("deltaMs") long deltaMs,
            @JsonProperty("ttlSeconds") long ttlSeconds,
            @JsonProperty("cachedAtEpochMs") long cachedAtEpochMs
    ) {
        @JsonCreator
        public CacheEnvelope {}
    }

    public ProbabilisticEarlyExpirationCache(
            StringRedisTemplate redisTemplate,
            ObjectMapper objectMapper,
            Class<T> targetClass,
            double beta) {
        this.redisTemplate = redisTemplate;
        this.objectMapper = objectMapper;
        this.targetClass = targetClass;
        this.beta = beta;
        // Bounded thread pool for asynchronous cache warming
        this.refreshExecutor = new ThreadPoolExecutor(
                4, 16, 60L, TimeUnit.SECONDS,
                new ArrayBlockingQueue<>(500),
                new ThreadFactory() {
                    private int counter = 0;
                    @Override
                    public Thread newThread(Runnable r) {
                        Thread t = new Thread(r, "xfetch-refresh-" + (++counter));
                        t.setDaemon(true);
                        return t;
                    }
                },
                new ThreadPoolExecutor.DiscardPolicy() // If saturated, skip early refresh
        );
    }

    public T get(String key, Duration ttl, Supplier<T> databaseLoader) {
        String rawJson = redisTemplate.opsForValue().get(key);

        if (rawJson == null) {
            // Absolute cache miss: Must load synchronously
            return loadAndCache(key, ttl, databaseLoader);
        }

        try {
            CacheEnvelope<T> envelope = objectMapper.readValue(
                    rawJson,
                    objectMapper.getTypeFactory().constructParametricType(CacheEnvelope.class, targetClass)
            );

            long now = Instant.now().toEpochMilli();
            long remainingTtlMs = (envelope.cachedAtEpochMs() + (envelope.ttlSeconds() * 1000L)) - now;

            // If remaining time is negative, key is logically expired
            if (remainingTtlMs <= 0) {
                return loadAndCache(key, ttl, databaseLoader);
            }

            // XFetch Probabilistic Check:
            // delta - beta * ln(U) * remainingTtl > totalTtl
            double u = ThreadLocalRandom.current().nextDouble(0.0001, 1.0);
            double recomputeScore = envelope.deltaMs() - (beta * Math.log(u) * remainingTtlMs);

            if (recomputeScore > (envelope.ttlSeconds() * 1000.0)) {
                triggerAsyncRefresh(key, ttl, databaseLoader);
            }

            // Return current cached data instantly without waiting for refresh!
            return envelope.data();
        } catch (Exception e) {
            log.warn("Failed to deserialize cached envelope for key: {}. Falling back to DB", key, e);
            return loadAndCache(key, ttl, databaseLoader);
        }
    }

    private void triggerAsyncRefresh(String key, Duration ttl, Supplier<T> databaseLoader) {
        if (inFlightRefreshes.putIfAbsent(key, Boolean.TRUE) == null) {
            refreshExecutor.submit(() -> {
                try {
                    log.debug("XFetch probabilistic trigger fired for key: {}", key);
                    loadAndCache(key, ttl, databaseLoader);
                } catch (Exception e) {
                    log.error("Async XFetch background refresh failed for key: {}", key, e);
                } finally {
                    inFlightRefreshes.remove(key);
                }
            });
        }
    }

    private T loadAndCache(String key, Duration ttl, Supplier<T> databaseLoader) {
        long start = System.nanoTime();
        T value = databaseLoader.get();
        long deltaMs = TimeUnit.NANOSECONDS.toMillis(System.nanoTime() - start);

        if (value != null) {
            try {
                CacheEnvelope<T> envelope = new CacheEnvelope<>(
                        value,
                        Math.max(1, deltaMs),
                        ttl.toSeconds(),
                        Instant.now().toEpochMilli()
                );
                String serialized = objectMapper.writeValueAsString(envelope);
                // Set physical TTL slightly longer than logical TTL to ensure early refresh window
                Duration physicalTtl = ttl.plusMinutes(2);
                redisTemplate.opsForValue().set(key, serialized, physicalTtl);
            } catch (Exception e) {
                log.error("Failed to write to Redis for key: {}", key, e);
            }
        }
        return value;
    }
}
```

---

## Pattern 2: Multi-Tier L1/L2 Cache with Safe Local Invalidation

Combines in-memory JVM heap (Caffeine) for sub-microsecond reads with Redis L2 for distributed consistency. Uses Redis Pub/Sub for cross-pod invalidation, with local instance identity checks to avoid redundant self-invalidation.

```java
package com.learning.production.lab12;

import com.github.benmanes.caffeine.cache.Cache;
import com.github.benmanes.caffeine.cache.Caffeine;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.redis.connection.Message;
import org.springframework.data.redis.connection.MessageListener;
import org.springframework.data.redis.core.StringRedisTemplate;

import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import java.util.function.Supplier;

public class ResilientTwoTierCache implements MessageListener {
    private static final Logger log = LoggerFactory.getLogger(ResilientTwoTierCache.class);

    private final String instanceId = UUID.randomUUID().toString();
    private final Cache<String, String> l1Caffeine;
    private final StringRedisTemplate redisTemplate;
    private static final String INVALIDATION_TOPIC = "cache:bus:invalidation";

    // Observability metrics
    private final Counter l1HitCounter;
    private final Counter l1MissCounter;
    private final Counter l2HitCounter;
    private final Counter l2MissCounter;

    public ResilientTwoTierCache(StringRedisTemplate redisTemplate, MeterRegistry registry) {
        this.redisTemplate = redisTemplate;

        // Bounded JVM Heap L1 Cache with Size and Time Constraints
        this.l1Caffeine = Caffeine.newBuilder()
                .maximumSize(30_000)
                .expireAfterWrite(30, TimeUnit.SECONDS)
                .recordStats()
                .build();

        this.l1HitCounter = registry.counter("cache.tier.requests", "tier", "l1", "result", "hit");
        this.l1MissCounter = registry.counter("cache.tier.requests", "tier", "l1", "result", "miss");
        this.l2HitCounter = registry.counter("cache.tier.requests", "tier", "l2", "result", "hit");
        this.l2MissCounter = registry.counter("cache.tier.requests", "tier", "l2", "result", "miss");
    }

    public String get(String key, Duration l2Ttl, Supplier<String> dbFallback) {
        // Step 1: L1 Check (Nano-second latency)
        String val = l1Caffeine.getIfPresent(key);
        if (val != null) {
            l1HitCounter.increment();
            return "@@NULL@@".equals(val) ? null : val;
        }
        l1MissCounter.increment();

        // Step 2: L2 Redis Check (Milli-second latency)
        try {
            val = redisTemplate.opsForValue().get(key);
            if (val != null) {
                l2HitCounter.increment();
                l1Caffeine.put(key, val);
                return "@@NULL@@".equals(val) ? null : val;
            }
        } catch (Exception e) {
            log.warn("Redis L2 unreachable. Degrading to DB query directly for key: {}", key);
        }
        l2MissCounter.increment();

        // Step 3: L3 Persistent Database Query
        String dbVal = dbFallback.get();
        if (dbVal != null) {
            put(key, dbVal, l2Ttl);
            return dbVal;
        } else {
            // Negative caching to prevent Cache Penetration attacks
            put(key, "@@NULL@@", Duration.ofSeconds(60));
            return null;
        }
    }

    public void put(String key, String value, Duration ttl) {
        try {
            // Write to L2 Redis
            redisTemplate.opsForValue().set(key, value, ttl);
        } catch (Exception e) {
            log.error("Failed to write key {} to Redis L2", key, e);
        }

        // Write to local L1
        l1Caffeine.put(key, value);

        // Broadcast invalidation payload format: "senderInstanceId:key"
        try {
            String message = instanceId + ":" + key;
            redisTemplate.convertAndSend(INVALIDATION_TOPIC, message);
        } catch (Exception e) {
            log.error("Failed to broadcast invalidation for key: {}", key, e);
        }
    }

    public void evict(String key) {
        try {
            redisTemplate.delete(key);
        } catch (Exception e) {
            log.error("Failed to delete key {} from Redis L2", key, e);
        }
        l1Caffeine.invalidate(key);
        redisTemplate.convertAndSend(INVALIDATION_TOPIC, instanceId + ":" + key);
    }

    @Override
    public void onMessage(Message message, byte[] pattern) {
        String payload = new String(message.getBody(), StandardCharsets.UTF_8);
        int colonIdx = payload.indexOf(':');
        if (colonIdx > 0) {
            String senderId = payload.substring(0, colonIdx);
            String targetKey = payload.substring(colonIdx + 1);

            // Skip self-invalidation to prevent unnecessary cache thrashing
            if (!instanceId.equals(senderId)) {
                l1Caffeine.invalidate(targetKey);
                log.trace("Evicted key {} from L1 following remote node invalidation", targetKey);
            }
        }
    }
}
```

---

## Pattern 3: Atomic Distributed Mutex with Safe Token Release (Lua Script)

A classic production flaw occurs when Thread A acquires a lock with a 3-second TTL. If Thread A's database query takes 4 seconds, the lock expires. Thread B acquires the lock. Thread A finishes and executes `redis.delete(lockKey)` — **accidentally releasing Thread B's active lock!**

This pattern enforces unique tokenization and Lua-based atomic verification:

```java
package com.learning.production.lab12;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.data.redis.core.script.DefaultRedisScript;

import java.time.Duration;
import java.util.Collections;
import java.util.UUID;

public class AtomicDistributedLock implements AutoCloseable {
    private static final Logger log = LoggerFactory.getLogger(AtomicDistributedLock.class);

    private final StringRedisTemplate redisTemplate;
    private final String lockKey;
    private final String lockToken;
    private final Duration lockTimeout;
    private boolean acquired = false;

    // Lua script: Releases lock ONLY if the current value matches the caller's unique lockToken
    private static final String UNLOCK_LUA_SCRIPT =
            "if redis.call('get', KEYS[1]) == ARGV[1] then " +
            "    return redis.call('del', KEYS[1]) " +
            "else " +
            "    return 0 " +
            "end";

    private static final DefaultRedisScript<Long> RELEASE_SCRIPT =
            new DefaultRedisScript<>(UNLOCK_LUA_SCRIPT, Long.class);

    public AtomicDistributedLock(StringRedisTemplate redisTemplate, String lockKey, Duration lockTimeout) {
        this.redisTemplate = redisTemplate;
        this.lockKey = "lock:" + lockKey;
        this.lockToken = UUID.randomUUID().toString();
        this.lockTimeout = lockTimeout;
    }

    public boolean tryLock(Duration maxWaitTime) throws InterruptedException {
        long deadline = System.currentTimeMillis() + maxWaitTime.toMillis();
        long retryIntervalMs = 50;

        while (System.currentTimeMillis() < deadline) {
            Boolean success = redisTemplate.opsForValue()
                    .setIfAbsent(lockKey, lockToken, lockTimeout);

            if (Boolean.TRUE.equals(success)) {
                this.acquired = true;
                return true;
            }

            // Sleep with exponential backoff + jitter before retrying
            Thread.sleep(retryIntervalMs);
            retryIntervalMs = Math.min(250, (long)(retryIntervalMs * 1.5));
        }

        return false;
    }

    @Override
    public void close() {
        if (!acquired) {
            return;
        }

        try {
            Long result = redisTemplate.execute(
                    RELEASE_SCRIPT,
                    Collections.singletonList(lockKey),
                    lockToken
            );

            if (result == null || result == 0) {
                log.warn("Lock key {} was either already expired or hijacked by another process!", lockKey);
            }
        } catch (Exception e) {
            log.error("Failed to release lock {}", lockKey, e);
        } finally {
            this.acquired = false;
        }
    }
}
```

---

## Pattern 4: Hot Key Salted Sharding with Replica Offload

For viral keys receiving $> 20,000$ QPS, distributing requests across random salt suffixes balances the load across distinct Redis cluster shards:

```java
package com.learning.production.lab12;

import org.springframework.data.redis.core.StringRedisTemplate;

import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ThreadLocalRandom;

public class SaltedHotKeyManager {
    private final StringRedisTemplate redisTemplate;
    private final int shardCount;

    public SaltedHotKeyManager(StringRedisTemplate redisTemplate, int shardCount) {
        this.redisTemplate = redisTemplate;
        this.shardCount = shardCount;
    }

    /**
     * Reads from a randomly selected salted key instance to distribute traffic across cluster masters.
     */
    public String getHotKey(String baseKey) {
        int randomShard = ThreadLocalRandom.current().nextInt(0, shardCount);
        String saltedKey = baseKey + "#" + randomShard;
        return redisTemplate.opsForValue().get(saltedKey);
    }

    /**
     * Propagates writes to ALL salted sub-keys to keep all shards synchronized.
     */
    public void setHotKey(String baseKey, String value, Duration ttl) {
        // Use pipelining to write to all salted shards in a single network round-trip
        redisTemplate.executePipelined((org.springframework.data.redis.connection.RedisCallback<Object>) connection -> {
            for (int i = 0; i < shardCount; i++) {
                String saltedKey = baseKey + "#" + i;
                byte[] rawKey = saltedKey.getBytes();
                byte[] rawVal = value.getBytes();
                connection.stringCommands().setEx(rawKey, ttl.toSeconds(), rawVal);
            }
            return null;
        });
    }

    /**
     * Evicts all salted instances simultaneously.
     */
    public void evictHotKey(String baseKey) {
        List<String> keys = new ArrayList<>(shardCount);
        for (int i = 0; i < shardCount; i++) {
            keys.add(baseKey + "#" + i);
        }
        redisTemplate.delete(keys);
    }
}
```

---

## Pattern 5: Chunked Pipelining to Prevent Event-Loop Saturation

Querying 5,000 keys with a single `MGET` or sequential loop creates either heavy network overhead or locks the Redis single thread. This pattern executes bounded batch queries with pipelining:

```java
package com.learning.production.lab12;

import org.springframework.dao.DataAccessException;
import org.springframework.data.redis.connection.RedisConnection;
import org.springframework.data.redis.connection.StringRedisConnection;
import org.springframework.data.redis.core.RedisCallback;
import org.springframework.data.redis.core.StringRedisTemplate;

import java.util.*;

public class ChunkedBatchRedisService {
    private final StringRedisTemplate redisTemplate;
    private static final int BATCH_SIZE = 200; // Optimal Redis pipeline batch window

    public ChunkedBatchRedisService(StringRedisTemplate redisTemplate) {
        this.redisTemplate = redisTemplate;
    }

    public Map<String, String> multiGetChunked(List<String> keys) {
        if (keys == null || keys.isEmpty()) {
            return Collections.emptyMap();
        }

        Map<String, String> resultMap = new HashMap<>(keys.size());

        for (int i = 0; i < keys.size(); i += BATCH_SIZE) {
            int end = Math.min(i + BATCH_SIZE, keys.size());
            List<String> batch = keys.subList(i, end);

            List<Object> batchResults = redisTemplate.executePipelined(new RedisCallback<Object>() {
                @Override
                public Object doInRedis(RedisConnection connection) throws DataAccessException {
                    StringRedisConnection stringConnection = (StringRedisConnection) connection;
                    for (String key : batch) {
                        stringConnection.get(key);
                    }
                    return null;
                }
            });

            for (int j = 0; j < batch.size(); j++) {
                Object val = batchResults.get(j);
                if (val != null) {
                    resultMap.put(batch.get(j), val.toString());
                }
            }
        }

        return resultMap;
    }
}
```
