# ANTI-PATTERNS: Database Performance & Connection Management
## Lab 05 | Production Engineering Academy

---

## Anti-Pattern 1: Oversizing Database Connection Pools

### The Mistake
Setting `maximumPoolSize: 100` across 50 container pods against a single database instance with 16 vCPUs ($50 \times 100 = 5,000$ connections).

### Why It Fails
1. PostgreSQL processes each connection as an independent operating system process (`postgres` backend).
2. 5,000 processes competing for 16 CPU cores leads to catastrophic OS context switching.
3. Disk I/O elevator algorithms and buffer pool latches become bottlenecked.
4. Total query throughput plummets from 30,000 TPS to 2,000 TPS while latency skyrockets from 2ms to 2,000ms.

### The Correct Production Fix
Keep application pool sizes small ($10 - 20$ connections per pod). Use an intermediate proxy pooler like **PgBouncer** or AWS RDS Proxy between applications and the database.

---

## Anti-Pattern 2: `spring.jpa.open-in-view=true` (OSIV)

### The Mistake
Leaving Spring Boot's default `open-in-view: true` enabled in production.

### Why It Fails
1. Open-Session-In-View binds a Hibernate Session and an underlying JDBC connection to the thread for the **entire duration of the HTTP request**, including controller serialization and template rendering.
2. If Jackson JSON serialization is slow or the client reads the HTTP stream slowly, the database connection remains locked and unavailable to other threads.
3. Leads to silent connection pool exhaustion under modest traffic.

### The Correct Production Fix
Always set in `application.yml`:
```yaml
spring:
  jpa:
    open-in-view: false
```
Fetch all required data within `@Transactional` service methods before returning to the web layer.

---

## Anti-Pattern 3: Massive Bulk Operations Using JPA `.saveAll()`

### The Mistake
Inserting 100,000 records using Spring Data JPA `repository.saveAll(entities)`.

### Why It Fails
1. Default JPA identity generation (`GenerationType.IDENTITY`) disables JDBC batching because Hibernate must execute an `INSERT` immediately to obtain the generated primary key value.
2. 100,000 inserts execute as 100,000 individual round trips to the database.
3. If each network round trip takes 1ms, the batch takes $100,000 \times 1\text{ms} = 100\text{ seconds}$!

### The Correct Production Fix
1. Use `GenerationType.SEQUENCE` with `allocationSize: 50`.
2. Or use Spring `JdbcTemplate.batchUpdate()` or PostgreSQL `COPY` command, completing 100,000 records in $< 300\text{ms}$.
