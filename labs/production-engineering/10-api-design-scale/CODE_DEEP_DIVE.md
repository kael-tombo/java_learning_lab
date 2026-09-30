# CODE DEEP DIVE: Production API Design & Scale Patterns
## Lab 10 | Production Engineering Academy — Top 0.0001% Engineering

---

## Pattern 1: Tamper-Proof HMAC Keyset Cursor Pagination

Implements $O(\log N)$ cursor pagination on multi-column composite index `(created_at DESC, id DESC)`. The cursor is serialized, Base64Url-encoded, and signed with HMAC-SHA256 to prevent clients from tampering with timestamps or IDs to breach data isolation.

```java
package com.learning.production.lab10;

import org.springframework.jdbc.core.namedparam.MapSqlParameterSource;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.time.Instant;
import java.util.Base64;
import java.util.List;

public class SecureKeysetProductRepository {
    private final NamedParameterJdbcTemplate jdbcTemplate;
    private final byte[] hmacSecretKey;

    public SecureKeysetProductRepository(NamedParameterJdbcTemplate jdbcTemplate, String secret) {
        this.jdbcTemplate = jdbcTemplate;
        this.hmacSecretKey = secret.getBytes(StandardCharsets.UTF_8);
    }

    public record Product(long id, String name, double price, Instant createdAt) {}

    public record Cursor(Instant createdAt, long id) {
        public String encode(byte[] secret) {
            String payload = createdAt.toEpochMilli() + ":" + id;
            String signature = sign(payload, secret);
            String token = payload + ":" + signature;
            return Base64.getUrlEncoder().withoutPadding().encodeToString(token.getBytes(StandardCharsets.UTF_8));
        }

        public static Cursor decode(String encoded, byte[] secret) {
            if (encoded == null || encoded.isBlank()) return null;
            try {
                String decoded = new String(Base64.getUrlDecoder().decode(encoded), StandardCharsets.UTF_8);
                String[] parts = decoded.split(":");
                if (parts.length != 3) {
                    throw new IllegalArgumentException("Malformed cursor format");
                }
                String payload = parts[0] + ":" + parts[1];
                String expectedSig = sign(payload, secret);
                if (!MessageDigest.isEqual(expectedSig.getBytes(StandardCharsets.UTF_8), parts[2].getBytes(StandardCharsets.UTF_8))) {
                    throw new SecurityException("Tampered cursor signature detected!");
                }
                return new Cursor(Instant.ofEpochMilli(Long.parseLong(parts[0])), Long.parseLong(parts[1]));
            } catch (Exception e) {
                throw new IllegalArgumentException("Invalid pagination cursor: " + e.getMessage(), e);
            }
        }

        private static String sign(String payload, byte[] secret) {
            try {
                Mac mac = Mac.getInstance("HmacSHA256");
                mac.init(new SecretKeySpec(secret, "HmacSHA256"));
                return Base64.getUrlEncoder().withoutPadding().encodeToString(mac.doFinal(payload.getBytes(StandardCharsets.UTF_8)));
            } catch (Exception e) {
                throw new RuntimeException("HMAC computation failed", e);
            }
        }
    }

    public record PageResult<T>(List<T> items, String nextCursor, boolean hasMore) {}

    public PageResult<Product> fetchPage(String cursorToken, int requestedLimit) {
        // Enforce hard upper bound on page size
        int limit = Math.min(Math.max(1, requestedLimit), 100);
        Cursor cursor = Cursor.decode(cursorToken, hmacSecretKey);

        StringBuilder sql = new StringBuilder("SELECT id, name, price, created_at FROM products ");
        MapSqlParameterSource params = new MapSqlParameterSource();
        // Fetch limit + 1 probe row to determine hasMore without running an expensive SELECT COUNT(*)
        params.addValue("limit", limit + 1);

        if (cursor != null) {
            sql.append("WHERE (created_at < :createdAt) OR (created_at = :createdAt AND id < :id) ");
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

        boolean hasMore = products.size() > limit;
        if (hasMore) {
            products.remove(products.size() - 1); // Discard probe item
        }

        String nextCursor = null;
        if (!products.isEmpty() && hasMore) {
            Product last = products.get(products.size() - 1);
            nextCursor = new Cursor(last.createdAt(), last.id()).encode(hmacSecretKey);
        }

        return new PageResult<>(products, nextCursor, hasMore);
    }
}
```

---

## Pattern 2: Atomic Redis Token Bucket with RFC RateLimit Headers

Calculates token replenishment on demand using a single Redis Lua script, returning whether the request was allowed, remaining quota, and time to replenishment.

```java
package com.learning.production.lab10;

import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.data.redis.core.script.DefaultRedisScript;

import java.time.Instant;
import java.util.Collections;
import java.util.List;

public class AdvancedTokenBucketRateLimiter {
    private final StringRedisTemplate redisTemplate;
    private final DefaultRedisScript<List> rateLimitScript;

    private static final String LUA_TOKEN_BUCKET = """
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

        local allowed = 0
        local retry_after_ms = 0

        if tokens >= requested then
            tokens = tokens - requested
            allowed = 1
        else
            allowed = 0
            local needed = requested - tokens
            retry_after_ms = math.ceil(needed / refill_rate)
        end

        redis.call('HMSET', key, 'tokens', tokens, 'last_updated', last_updated)
        redis.call('EXPIRE', key, 3600)

        return { allowed, math.floor(tokens), retry_after_ms }
    """;

    public record RateLimitResult(boolean isAllowed, long remainingTokens, long retryAfterSeconds) {}

    public AdvancedTokenBucketRateLimiter(StringRedisTemplate redisTemplate) {
        this.redisTemplate = redisTemplate;
        this.rateLimitScript = new DefaultRedisScript<>(LUA_TOKEN_BUCKET, List.class);
    }

    public RateLimitResult evaluate(String clientId, int capacity, double tokensPerSecond) {
        String key = "ratelimit:" + clientId;
        double refillRatePerMs = tokensPerSecond / 1000.0;
        long now = Instant.now().toEpochMilli();

        @SuppressWarnings("unchecked")
        List<Long> result = redisTemplate.execute(
                rateLimitScript,
                Collections.singletonList(key),
                String.valueOf(capacity),
                String.valueOf(refillRatePerMs),
                String.valueOf(now),
                "1"
        );

        if (result != null && result.size() >= 3) {
            boolean allowed = result.get(0) == 1L;
            long remaining = result.get(1);
            long retryAfterMs = result.get(2);
            long retryAfterSec = Math.max(1, (retryAfterMs + 999) / 1000);
            return new RateLimitResult(allowed, remaining, retryAfterSec);
        }

        // Fail open if Redis returns unexpected structure
        return new RateLimitResult(true, capacity, 0);
    }
}
```

---

## Pattern 3: Distributed Idempotency Filter with SHA-256 Payload Hash Verification

Ensures exactly-once execution for state-changing HTTP requests. Rejects payload tampering, buffers concurrent identical requests, and replays cached HTTP responses.

```java
package com.learning.production.lab10;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.time.Duration;
import java.util.HexFormat;
import java.util.concurrent.TimeUnit;
import java.util.function.Supplier;

public class DistributedIdempotencyManager {
    private final StringRedisTemplate redisTemplate;
    private final ObjectMapper objectMapper;

    public record CachedResponse(int statusCode, String payloadJson, String payloadHash) {}

    public DistributedIdempotencyManager(StringRedisTemplate redisTemplate, ObjectMapper objectMapper) {
        this.redisTemplate = redisTemplate;
        this.objectMapper = objectMapper;
    }

    public ResponseEntity<String> executeIdempotent(
            String idempotencyKey,
            String requestPayload,
            Supplier<ResponseEntity<String>> businessOperation) {

        if (idempotencyKey == null || idempotencyKey.isBlank()) {
            return businessOperation.get();
        }

        String redisKey = "idempotency:" + idempotencyKey;
        String lockKey = "lock:" + redisKey;
        String currentHash = computeSha256(requestPayload);

        // Step 1: Check if this idempotency key was already completed
        String existingRecord = redisTemplate.opsForValue().get(redisKey);
        if (existingRecord != null) {
            try {
                CachedResponse cached = objectMapper.readValue(existingRecord, CachedResponse.class);
                // Verify payload fingerprint to detect key reuse with conflicting arguments
                if (!MessageDigest.isEqual(cached.payloadHash().getBytes(), currentHash.getBytes())) {
                    return ResponseEntity.status(HttpStatus.UNPROCESSABLE_ENTITY)
                            .body("{\"error\":\"Idempotency key reuse with mismatched payload\"}");
                }
                // Return cached response instantly
                return ResponseEntity.status(cached.statusCode()).body(cached.payloadJson());
            } catch (Exception e) {
                // If deserialization fails, continue to recompute
            }
        }

        // Step 2: Acquire execution mutex lock to prevent concurrent races
        Boolean lockAcquired = redisTemplate.opsForValue()
                .setIfAbsent(lockKey, "IN_PROGRESS", Duration.ofSeconds(15));

        if (!Boolean.TRUE.equals(lockAcquired)) {
            // Concurrent duplicate request is currently executing!
            return ResponseEntity.status(HttpStatus.CONFLICT)
                    .header("Retry-After", "2")
                    .body("{\"error\":\"A request with this Idempotency-Key is currently in progress\"}");
        }

        try {
            // Step 3: Execute actual business operation
            ResponseEntity<String> response = businessOperation.get();

            // Step 4: Persist response payload into idempotency store with 24-hour TTL
            CachedResponse recordToCache = new CachedResponse(
                    response.getStatusCode().value(),
                    response.getBody(),
                    currentHash
            );
            String serialized = objectMapper.writeValueAsString(recordToCache);
            redisTemplate.opsForValue().set(redisKey, serialized, 24, TimeUnit.HOURS);

            return response;
        } catch (Exception e) {
            // In case of business failure, do not cache failure so client can retry with same key
            throw new RuntimeException("Business operation failed: " + e.getMessage(), e);
        } finally {
            redisTemplate.delete(lockKey); // Release lock
        }
    }

    private static String computeSha256(String data) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest(data.getBytes(StandardCharsets.UTF_8));
            return HexFormat.of().formatHex(hash);
        } catch (Exception e) {
            throw new RuntimeException("Hashing failed", e);
        }
    }
}
```

---

## Pattern 4: Zero-Downtime Expand-and-Contract Dual-Write Service Layer

Demonstrates how to safely evolve an entity schema (migrating single `fullName` into `firstName` and `lastName`) across independent rolling deployments without database lockups or client crashes.

```java
package com.learning.production.lab10;

import org.springframework.jdbc.core.namedparam.MapSqlParameterSource;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;

public class ExpandContractCustomerService {
    private final NamedParameterJdbcTemplate jdbcTemplate;
    private final MigrationPhase currentPhase;

    public enum MigrationPhase {
        PHASE_1_EXPAND_DUAL_WRITE,  // Writes to old + new columns; Reads from old
        PHASE_2_CONTRACT_READ,       // Writes to old + new columns; Reads from new
        PHASE_3_COMPLETE             // Writes only to new columns; Reads from new
    }

    public record Customer(long id, String firstName, String lastName) {}

    public ExpandContractCustomerService(NamedParameterJdbcTemplate jdbcTemplate, MigrationPhase phase) {
        this.jdbcTemplate = jdbcTemplate;
        this.currentPhase = phase;
    }

    public void createCustomer(long id, String firstName, String lastName) {
        String legacyFullName = firstName + " " + lastName;

        switch (currentPhase) {
            case PHASE_1_EXPAND_DUAL_WRITE, PHASE_2_CONTRACT_READ -> {
                // Dual-Writing to both schemas simultaneously
                String sql = "INSERT INTO customers (id, full_name, first_name, last_name) " +
                             "VALUES (:id, :fullName, :firstName, :lastName)";
                MapSqlParameterSource params = new MapSqlParameterSource()
                        .addValue("id", id)
                        .addValue("fullName", legacyFullName)
                        .addValue("firstName", firstName)
                        .addValue("lastName", lastName);
                jdbcTemplate.update(sql, params);
            }
            case PHASE_3_COMPLETE -> {
                // Final clean state: writing strictly to new columns
                String sql = "INSERT INTO customers (id, first_name, last_name) " +
                             "VALUES (:id, :firstName, :lastName)";
                MapSqlParameterSource params = new MapSqlParameterSource()
                        .addValue("id", id)
                        .addValue("firstName", firstName)
                        .addValue("lastName", lastName);
                jdbcTemplate.update(sql, params);
            }
        }
    }

    public Customer getCustomer(long id) {
        MapSqlParameterSource params = new MapSqlParameterSource("id", id);

        if (currentPhase == MigrationPhase.PHASE_1_EXPAND_DUAL_WRITE) {
            // Read from old column and split dynamically as fallback
            String sql = "SELECT id, full_name FROM customers WHERE id = :id";
            return jdbcTemplate.queryForObject(sql, params, (rs, rowNum) -> {
                String fullName = rs.getString("full_name");
                String[] parts = fullName.split(" ", 2);
                return new Customer(rs.getLong("id"), parts[0], parts.length > 1 ? parts[1] : "");
            });
        } else {
            // Read from new optimized columns
            String sql = "SELECT id, first_name, last_name FROM customers WHERE id = :id";
            return jdbcTemplate.queryForObject(sql, params, (rs, rowNum) -> new Customer(
                    rs.getLong("id"),
                    rs.getString("first_name"),
                    rs.getString("last_name")
            ));
        }
    }
}
```
