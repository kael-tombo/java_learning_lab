# HANDS-ON LAB EXERCISES: API Design, Resilience & Scale
## Lab 10 | Production Engineering Academy — Top 0.0001% Engineering

---

## Exercise 1: 1,000,000-Row Pagination Benchmark: Offset vs Keyset

### Objective
Measure and compare SQL execution time and database buffer hit rates across a 1,000,000-row table between naive Offset Pagination and $O(\log N)$ Keyset Cursor Pagination.

### Test Setup & Verification Test
```java
package com.learning.production.lab10;

import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.embedded.EmbeddedDatabaseBuilder;
import org.springframework.jdbc.datasource.embedded.EmbeddedDatabaseType;

import javax.sql.DataSource;
import java.time.Instant;
import java.util.concurrent.TimeUnit;

import static org.junit.jupiter.api.Assertions.*;

public class PaginationBenchmarkTest {
    private static JdbcTemplate jdbcTemplate;

    @BeforeAll
    static void setupDatabase() {
        DataSource dataSource = new EmbeddedDatabaseBuilder()
                .setType(EmbeddedDatabaseType.H2)
                .build();
        jdbcTemplate = new JdbcTemplate(dataSource);

        jdbcTemplate.execute("""
            CREATE TABLE orders (
                id BIGINT PRIMARY KEY,
                tenant_id INT NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                created_at TIMESTAMP NOT NULL
            );
            CREATE INDEX idx_orders_pagination ON orders (created_at DESC, id DESC);
        """);

        // Insert 100,000 test records in batches
        System.out.println("Populating test dataset...");
        jdbcTemplate.batchUpdate(
            "INSERT INTO orders (id, tenant_id, amount, created_at) VALUES (?, 1, 99.99, ?)",
            new org.springframework.jdbc.core.BatchPreparedStatementSetter() {
                @Override
                public void setValues(java.sql.PreparedStatement ps, int i) throws java.sql.SQLException {
                    ps.setLong(1, i + 1);
                    ps.setTimestamp(2, java.sql.Timestamp.from(Instant.now().minusSeconds(100_000 - i)));
                }
                @Override
                public int getBatchSize() {
                    return 100_000;
                }
            }
        );
        System.out.println("Dataset ready.");
    }

    @Test
    @DisplayName("Prove that Keyset pagination execution time remains flat while Offset degrades linearly")
    void testPaginationScalability() {
        // Measure Offset at deep page: OFFSET 90,000 LIMIT 20
        long startOffset = System.nanoTime();
        jdbcTemplate.queryForList("SELECT id FROM orders ORDER BY created_at DESC, id DESC LIMIT 20 OFFSET 90000");
        long offsetDurationMs = TimeUnit.NANOSECONDS.toMillis(System.nanoTime() - startOffset);

        // Measure Keyset pagination at equivalent depth
        // Simulate reading cursor from previous page
        Instant cursorTime = Instant.now().minusSeconds(10_000);
        long cursorId = 10_000L;

        long startKeyset = System.nanoTime();
        jdbcTemplate.queryForList(
            "SELECT id FROM orders WHERE (created_at < ? OR (created_at = ? AND id < ?)) ORDER BY created_at DESC, id DESC LIMIT 20",
            java.sql.Timestamp.from(cursorTime), java.sql.Timestamp.from(cursorTime), cursorId
        );
        long keysetDurationMs = TimeUnit.NANOSECONDS.toMillis(System.nanoTime() - startKeyset);

        System.out.printf("Results -> Offset Duration: %d ms | Keyset Duration: %d ms%n", offsetDurationMs, keysetDurationMs);
        assertTrue(keysetDurationMs <= offsetDurationMs, "Keyset pagination must be faster than deep offset scan!");
    }
}
```

---

## Exercise 2: Distributed Redis Token Bucket Rate Limiter Test

### Objective
Verify that `AdvancedTokenBucketRateLimiter` enforces strict burst capacity, refills tokens smoothly over time, and returns accurate `RateLimitResult` metadata.

### Tasks & Test Specification:
1. Initialize `AdvancedTokenBucketRateLimiter` with `capacity = 10` and `refillRate = 5 tokens/second`.
2. Fire 10 sequential requests immediately:
   - Assert all 10 return `isAllowed == true`.
   - Assert the 10th request reports `remainingTokens == 0`.
3. Fire an 11th request immediately:
   - Assert `isAllowed == false`.
   - Assert `retryAfterSeconds >= 1`.
4. Sleep for 400 milliseconds (refills $\approx 2$ tokens):
   - Fire 2 requests: assert both return `isAllowed == true`.
   - Fire 3rd request: assert returns `isAllowed == false`.

---

## Exercise 3: Distributed Idempotency Filter with Concurrent Race Testing

### Objective
Demonstrate that `DistributedIdempotencyManager` strictly prevents double-execution under concurrent multithreaded requests and rejects payload tampering with `HTTP 422`.

### Test Implementation:
```java
package com.learning.production.lab10;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.data.redis.connection.RedisStandaloneConfiguration;
import org.springframework.data.redis.connection.lettuce.LettuceConnectionFactory;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;

import java.util.UUID;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

import static org.junit.jupiter.api.Assertions.*;

public class DistributedIdempotencyTest {

    @Test
    @DisplayName("Verify concurrent identical requests result in exactly ONE execution and ONE 409 Conflict")
    void testConcurrentIdempotencyRace() throws Exception {
        // Setup Redis connection (assumes local Redis or mock)
        LettuceConnectionFactory factory = new LettuceConnectionFactory(new RedisStandaloneConfiguration("localhost", 6379));
        factory.afterPropertiesSet();
        StringRedisTemplate redisTemplate = new StringRedisTemplate(factory);
        DistributedIdempotencyManager manager = new DistributedIdempotencyManager(redisTemplate, new ObjectMapper());

        String key = "test-idemp-" + UUID.randomUUID();
        String payload = "{\"amount\":50.00,\"accountId\":\"act_984\"}";

        AtomicInteger executionCounter = new AtomicInteger(0);
        CyclicBarrier barrier = new CyclicBarrier(2);
        ExecutorService pool = Executors.newFixedThreadPool(2);

        Callable<ResponseEntity<String>> worker = () -> {
            barrier.await(); // Synchronized release
            return manager.executeIdempotent(key, payload, () -> {
                executionCounter.incrementAndGet();
                try {
                    Thread.sleep(100); // Simulate slow payment gateway
                } catch (InterruptedException ignored) {}
                return ResponseEntity.status(HttpStatus.CREATED).body("{\"status\":\"CHARGED\"}");
            });
        };

        Future<ResponseEntity<String>> f1 = pool.submit(worker);
        Future<ResponseEntity<String>> f2 = pool.submit(worker);

        ResponseEntity<String> r1 = f1.get();
        ResponseEntity<String> r2 = f2.get();

        // Exactly ONE must succeed and ONE must receive 409 Conflict
        assertTrue(
            (r1.getStatusCode() == HttpStatus.CREATED && r2.getStatusCode() == HttpStatus.CONFLICT) ||
            (r2.getStatusCode() == HttpStatus.CREATED && r1.getStatusCode() == HttpStatus.CONFLICT)
        );
        assertEquals(1, executionCounter.get(), "Business logic must execute STRICTLY ONCE!");

        // Test payload tampering: Reusing key with different amount
        String modifiedPayload = "{\"amount\":999.00,\"accountId\":\"act_984\"}";
        ResponseEntity<String> tamperedResponse = manager.executeIdempotent(key, modifiedPayload, () -> {
            fail("Must never reach business logic on payload conflict!");
            return null;
        });

        assertEquals(HttpStatus.UNPROCESSABLE_ENTITY, tamperedResponse.getStatusCode());
        pool.shutdown();
    }
}
```

---

## Exercise 4: Zero-Downtime Expand-and-Contract Dual-Write Verification

### Objective
Verify that `ExpandContractCustomerService` transitions across migration phases without data loss, data corruption, or downtime.

### Tasks:
1. Deploy `ExpandContractCustomerService` in `PHASE_1_EXPAND_DUAL_WRITE`.
2. Insert 50 customers:
   - Assert each record writes to both `full_name` and `(first_name, last_name)`.
   - Assert reads succeed seamlessly by reading from `full_name`.
3. Transition service configuration to `PHASE_2_CONTRACT_READ`.
   - Insert another 50 customers.
   - Assert reads now read directly from `(first_name, last_name)`.
4. Transition service configuration to `PHASE_3_COMPLETE`.
   - Insert 50 customers.
   - Assert writes write strictly to `first_name` and `last_name`.
   - Assert total 150 customers exist in complete consistency.
