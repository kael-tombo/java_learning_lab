# CODE DEEP DIVE: API Design for Scale & Resilience
## Lab 10 | Production Engineering Academy

---

## Pattern 1: Production Keyset Cursor Pagination Implementation

```java
package com.learning.production.lab10;

import org.springframework.jdbc.core.namedparam.MapSqlParameterSource;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;

import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.Base64;
import java.util.List;

public class KeysetProductRepository {
    private final NamedParameterJdbcTemplate jdbcTemplate;

    public KeysetProductRepository(NamedParameterJdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    public record Product(long id, String name, double price, Instant createdAt) {}

    public record Cursor(Instant createdAt, long id) {
        public String encode() {
            String raw = createdAt.toEpochMilli() + ":" + id;
            return Base64.getUrlEncoder().encodeToString(raw.getBytes(StandardCharsets.UTF_8));
        }

        public static Cursor decode(String encoded) {
            if (encoded == null || encoded.isBlank()) return null;
            String raw = new String(Base64.getUrlDecoder().decode(encoded), StandardCharsets.UTF_8);
            String[] parts = raw.split(":");
            return new Cursor(Instant.ofEpochMilli(Long.parseLong(parts[0])), Long.parseLong(parts[1]));
        }
    }

    public record PageResult<T>(List<T> items, String nextCursor, boolean hasMore) {}

    /**
     * Executes $O(\log N)$ cursor pagination query using composite index (created_at DESC, id DESC).
     */
    public PageResult<Product> fetchPage(String cursorToken, int pageSize) {
        Cursor cursor = Cursor.decode(cursorToken);
        StringBuilder sql = new StringBuilder(
                "SELECT id, name, price, created_at FROM products "
        );

        MapSqlParameterSource params = new MapSqlParameterSource();
        // Fetch pageSize + 1 to know if there is a next page without running an expensive COUNT(*)
        params.addValue("limit", pageSize + 1);

        if (cursor != null) {
            sql.append("WHERE (created_at, id) < (:createdAt, :id) ");
            params.addValue("createdAt", cursor.createdAt());
            params.addValue("id", cursor.id());
        }

        sql.append("ORDER BY created_at DESC, id DESC LIMIT :limit");

        List<Product> products = jdbcTemplate.query(sql.toString(), params, (rs, rowNum) -> new Product(
                rs.getLong("id"),
                rs.getString("name"),
                rs.getDouble("price"),
                rs.getTimestamp("created_at").toInstant()
        ));

        boolean hasMore = products.size() > pageSize;
        if (hasMore) {
            products.remove(products.size() - 1); // Remove the extra probe item
        }

        String nextCursor = null;
        if (!products.isEmpty() && hasMore) {
            Product last = products.get(products.size() - 1);
            nextCursor = new Cursor(last.createdAt(), last.id()).encode();
        }

        return new PageResult<>(products, nextCursor, hasMore);
    }
}
```

---

## Pattern 2: Atomic Redis Token Bucket Rate Limiter (Lua Script)

```java
package com.learning.production.lab10;

import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.data.redis.core.script.DefaultRedisScript;

import java.time.Instant;
import java.util.Collections;
import java.util.List;

public class RedisTokenBucketRateLimiter {
    private final StringRedisTemplate redisTemplate;
    private final DefaultRedisScript<Long> rateLimitScript;

    // Production atomic Token Bucket Lua script
    private static final String LUA_SCRIPT = """
        local key = KEYS[1]
        local capacity = tonumber(ARGV[1])
        local refill_rate = tonumber(ARGV[2]) -- tokens per millisecond
        local now = tonumber(ARGV[3])
        local requested = tonumber(ARGV[4])

        local data = redis.call('HMGET', key, 'tokens', 'last_updated')
        local tokens = tonumber(data[1])
        local last_updated = tonumber(data[2])

        if not tokens then
            tokens = capacity
            last_updated = now
        else
            local elapsed = math.max(0, now - last_updated)
            tokens = math.min(capacity, tokens + (elapsed * refill_rate))
            last_updated = now
        end

        if tokens >= requested then
            tokens = tokens - requested
            redis.call('HMSET', key, 'tokens', tokens, 'last_updated', last_updated)
            redis.call('EXPIRE', key, 3600)
            return 1 -- Allowed
        else
            redis.call('HMSET', key, 'tokens', tokens, 'last_updated', last_updated)
            return 0 -- Throttled
        end
    """;

    public RedisTokenBucketRateLimiter(StringRedisTemplate redisTemplate) {
        this.redisTemplate = redisTemplate;
        this.rateLimitScript = new DefaultRedisScript<>(LUA_SCRIPT, Long.class);
    }

    public boolean tryAcquire(String clientId, int capacity, double tokensPerSecond) {
        String key = "ratelimit:" + clientId;
        double refillRatePerMs = tokensPerSecond / 1000.0;
        long now = Instant.now().toEpochMilli();

        Long result = redisTemplate.execute(
                rateLimitScript,
                Collections.singletonList(key),
                String.valueOf(capacity),
                String.valueOf(refillRatePerMs),
                String.valueOf(now),
                "1"
        );

        return result != null && result == 1L;
    }
}
```
