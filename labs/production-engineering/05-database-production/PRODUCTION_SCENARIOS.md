# PRODUCTION SCENARIOS: Database Performance & Connection Pools
## Lab 05 | Production Engineering Academy

---

## Scenario 1: The Black Friday Connection Pool Starvation

### Context
High-traffic retail website running on Spring Boot 3 + PostgreSQL with HikariCP. 30 application pods, each configured with `maximumPoolSize: 50`. Total potential connections = 1,500. PostgreSQL instance had `max_connections = 400`.

### The Disaster
- As traffic ramped up to 25,000 req/s, developers thought: "Latency is increasing, let's increase HikariCP connection pool size from 10 to 50 so threads don't wait for connections!"
- When traffic spiked, all 30 pods attempted to scale their pools to 50.
- Total connection requests exceeded PostgreSQL `max_connections = 400`. PostgreSQL started throwing `FATAL: remaining connection slots are reserved for non-replication superuser connections`.
- Inside PostgreSQL, 400 concurrent active query backend processes engaged in intense context switching and disk buffer lock contention on 16 vCPUs. Disk I/O skyrocketed to 100%, causing query execution times to jump from 4ms to 1,200ms.
- Pods spent all their time waiting on connections (`ConnectionTimeoutException: Connection is not available, request timed out after 30000ms`), causing total application outage.

### The Mathematical Reality of Connection Pools
PostgreSQL author formula for optimal pool size:
$$\text{pool size} = (\text{core\_count} \times 2) + \text{effective\_spindle\_count}$$
On a 16-core database server with fast NVMe SSD:
$$\text{Optimal total active connections} = (16 \times 2) + 1 = 33\text{ connections!}$$
Having 400 connections degraded throughput by 90% due to CPU context switching and lock thrashing.

### The Fix
1. Reduced HikariCP pool size from 50 down to **10 connections per pod**.
2. Placed **PgBouncer** connection pooler in transaction pooling mode in front of PostgreSQL, multiplexing 500 client connections onto 32 physical PostgreSQL server connections.
3. Database CPU dropped from 100% to 32%, p99 query latency dropped from 1,200ms to 6ms.

---

## Scenario 2: The "HTTP Inside Transaction" Connection Leak

### Context
Order fulfillment service processing customer purchases:

```java
@Transactional
public void processOrder(OrderRequest request) {
    Order order = orderRepository.save(new Order(request)); // Acquired DB connection
    
    // FATAL MISTAKE: Calling slow 3rd-party fraud API inside active DB transaction
    FraudCheckResult result = fraudDetectionClient.checkFraud(order.getUserId()); 
    
    order.setFraudScore(result.score());
    orderRepository.save(order);
}
```

### The Failure Mode
The fraud detection partner experienced a slow degradation where responses took 4.5 seconds.
- Every thread in the service grabbed a database connection on line 1.
- The thread then held the database connection idle while waiting 4.5 seconds for the HTTP call.
- The HikariCP connection pool was completely depleted in 15 seconds, starving all other read and write queries across the entire application.

### The Architect's Rule
**NEVER execute network I/O, external REST/gRPC calls, or heavy asynchronous waits inside a database transaction.**
Transactions must only contain in-memory CPU transformations and database queries.
