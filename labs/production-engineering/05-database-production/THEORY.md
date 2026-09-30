# THEORY: Database Performance & Connection Pools
## Lab 05 | Production Engineering Academy

---

## 1. Connection Pool Architecture

### 1.1 Why Connection Pools Matter

Creating a database connection is expensive:
- TCP handshake: 1-3ms
- TLS negotiation: 5-10ms
- DB authentication: 5-20ms
- Total: **10-35ms per new connection**

At 1,000 req/s, if each creates a new connection: **10-35 seconds** of pure connection overhead per second. That's 100% of your latency budget gone.

**Connection pool reuses established connections → overhead drops to ~0.1ms**

### 1.2 HikariCP — The Production Standard

HikariCP is the fastest Java connection pool (used by Spring Boot by default).

```
HikariCP Pool Architecture:

Requests → getConnection() → Pool has available connection?
                              YES → return it immediately (~0.1ms)
                              NO  → wait up to connectionTimeout
                                    If timeout: BorrowTimeoutException (not OOM!)
                                    If connection available: return it

After use → connection.close() → NOT really closed!
                                 Connection returned to pool
                                 (reset statement, autocommit state)

Every maxLifetime (30 min) → Replace connection (prevents stale/zombie connections)
```

### 1.3 Production HikariCP Configuration

```yaml
spring:
  datasource:
    hikari:
      # Pool sizing
      maximum-pool-size: 20      # Rarely > 20; DB limits connections
      minimum-idle: 5            # Keep 5 warm connections always

      # Timeouts (ALL must be set — no defaults are safe)
      connection-timeout: 3000   # Max wait for a connection from pool: 3s
                                 # If exceeded: HikariPool-1 - Connection is not available
      idle-timeout: 600000       # Remove idle connections after 10min
      max-lifetime: 1800000      # Replace connections every 30min (prevents stale)
      validation-timeout: 1000   # Max time to validate connection: 1s

      # Diagnostics
      leak-detection-threshold: 5000  # Log if connection held > 5s (possible leak)
      pool-name: payment-db-pool      # Meaningful name for metrics

      # Connection validation (PostgreSQL)
      connection-test-query: SELECT 1  # Validate connection before use
      # OR: use isValid() (faster, driver-native)
```

### 1.4 Pool Sizing Formula

```
Pool size = Tn × (Cm - 1) + 1

Tn = number of threads
Cm = max concurrent connections per thread

Practical guide:
- PostgreSQL (recommended max concurrent): 100
- MySQL: ~150
- Oracle: depends on license

For API service with 50 threads, each potentially holding 1 DB connection:
Pool size = 50 threads × 1 = 50 connections MAX (but usually 10-20 is enough)

WARNING: pool too large = DB overloaded (exceeds its optimal concurrent queries)
         pool too small = threads queue waiting = latency spike
```

---

## 2. SQL Performance

### 2.1 The N+1 Problem — Most Common ORM Bug

```java
// BROKEN — N+1 queries
List<Order> orders = orderRepository.findAll();  // 1 query: SELECT * FROM orders
for (Order order : orders) {
    System.out.println(order.getCustomer().getName());  // N queries: SELECT * FROM customer WHERE id=?
}
// 1 order list + 500 customer queries = 501 SQL queries!

// FIXED — JOIN FETCH (eager load in one query)
@Query("SELECT o FROM Order o JOIN FETCH o.customer WHERE o.status = :status")
List<Order> findByStatusWithCustomer(@Param("status") String status);
// 1 query: SELECT o.*, c.* FROM orders o JOIN customers c ON o.customer_id = c.id

// FIXED — @EntityGraph (alternative, no custom JPQL)
@EntityGraph(attributePaths = {"customer", "customer.address"})
List<Order> findAll();
```

### 2.2 Query Execution Plans

```sql
-- PostgreSQL: understand what the DB is actually doing
EXPLAIN ANALYZE SELECT * FROM orders WHERE customer_id = 123 AND status = 'PENDING';

-- Output:
Index Scan using orders_customer_idx on orders  (cost=0.43..8.45 rows=1 width=312)
                                                (actual time=0.082..0.084 rows=1 loops=1)
  Index Cond: (customer_id = 123)
  Filter: (status = 'PENDING')
  Rows Removed by Filter: 3
Planning Time: 0.5 ms
Execution Time: 0.1 ms   ← Good!

-- BAD: look for "Seq Scan" on large tables
Seq Scan on orders  (cost=0.00..125000.00 rows=5000000 width=312)
                   (actual time=0.001..4523.000 rows=5000000 loops=1)
-- Sequential scan of 5M rows = 4.5 seconds! Add an index.
```

### 2.3 Index Design

```sql
-- Single column (most common)
CREATE INDEX idx_orders_customer_id ON orders (customer_id);

-- Composite index — order matters! Most selective first
CREATE INDEX idx_orders_customer_status ON orders (customer_id, status);
-- This supports: WHERE customer_id=? AND status=?
-- This supports: WHERE customer_id=?  (prefix match)
-- This does NOT support: WHERE status=?  (no prefix)

-- Partial index — smaller, faster for common queries
CREATE INDEX idx_orders_pending ON orders (created_at)
WHERE status = 'PENDING';  -- Only indexes pending orders

-- Covering index — query satisfied entirely from index (no table access)
CREATE INDEX idx_orders_covering ON orders (customer_id)
INCLUDE (order_total, status, created_at);  -- PostgreSQL 11+
```

---

## 3. Transaction Management

### 3.1 Isolation Levels

```sql
-- READ UNCOMMITTED: sees uncommitted data (dirty reads) — almost never use
-- READ COMMITTED (default Postgres): sees committed data; non-repeatable reads possible
-- REPEATABLE READ: snapshot of data at start of transaction
-- SERIALIZABLE: full isolation; transactions appear to run one-at-a-time (slowest)
```

```java
// Spring: @Transactional isolation
@Transactional(isolation = Isolation.READ_COMMITTED)  // Default, usually correct
@Transactional(isolation = Isolation.SERIALIZABLE)    // Financial accuracy required
@Transactional(isolation = Isolation.REPEATABLE_READ) // Snapshot consistency needed
```

### 3.2 Transaction Anti-Patterns

```java
// ANTI-PATTERN 1: Transaction too broad — slow, holds locks
@Transactional  // Transaction spans HTTP call! DB lock held during HTTP
public void processOrder(OrderRequest req) {
    Order order = orderRepo.save(new Order(req));
    paymentResult = paymentGateway.charge(req.getPayment());  // HTTP call inside TX!
    order.setPaymentId(paymentResult.getId());
    orderRepo.save(order);
}

// FIXED: Minimal transaction scope
public void processOrder(OrderRequest req) {
    String orderId = createOrderRecord(req);         // TX 1: fast DB write
    PaymentResult payment = paymentGateway.charge(); // HTTP outside TX
    updateOrderWithPayment(orderId, payment);         // TX 2: fast DB update
}

// ANTI-PATTERN 2: Lost update — optimistic lock
public void incrementCounter(String id) {
    Counter c = counterRepo.findById(id).get();  // Read: 5
    c.setValue(c.getValue() + 1);               // Compute: 6
    counterRepo.save(c);                         // Write: 6 (may overwrite concurrent write!)
}

// FIXED: Optimistic locking with @Version
@Entity
public class Counter {
    @Version Long version;  // JPA increments on save; throws OptimisticLockException if conflict
    Integer value;
}
// OR: atomic SQL update
counterRepo.incrementById(id);  // UPDATE counters SET value=value+1 WHERE id=?
```

### 3.3 Long-Running Transactions — The Silent Killer

```
Problem timeline:
  T=0:   Transaction starts
  T=0:   Lock acquired on row R
  T=50ms: HTTP call to external API (holding lock!)
  T=200ms: HTTP call returns
  T=200ms: Transaction commits, lock released

During T=0 to T=200ms:
  - All other transactions wanting row R are BLOCKED
  - Connection held in pool for 200ms (reduces pool availability)
  - If HTTP call hangs (500ms, 5s, forever): lock held forever
  → Cascading failure: all requests pile up waiting for the lock
```

---

## 4. Read Replicas & CQRS

```java
// Configure Spring Data with read replica routing
@Configuration
public class DataSourceConfig {
    
    @Bean
    @Primary
    public DataSource routingDataSource(
            @Qualifier("primary") DataSource primary,
            @Qualifier("replica") DataSource replica) {
        return new AbstractRoutingDataSource() {
            @Override
            protected Object determineCurrentLookupKey() {
                // Route read-only transactions to replica
                return TransactionSynchronizationManager.isCurrentTransactionReadOnly()
                    ? "replica" : "primary";
            }
        };
    }
}

// Usage: read-only transactions → replica
@Transactional(readOnly = true)  // Routes to replica automatically
public List<Order> findOrders(String customerId) {
    return orderRepository.findByCustomerId(customerId);
}

@Transactional  // Routes to primary
public Order createOrder(CreateOrderRequest req) {
    return orderRepository.save(new Order(req));
}
```
