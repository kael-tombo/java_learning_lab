# INTERVIEW QUESTIONS: Database Performance & Connection Pools
## Lab 05 | Senior / Staff / Principal Level

---

## Senior Level (5+ Years)

### Q1: Why does increasing the database connection pool size beyond a certain threshold degrade system throughput rather than improve it?
**Answer**:
A database engine is constrained by hardware resources: CPU cores, disk I/O channels, and memory bus. When thousands of connections execute queries simultaneously against a 16-core CPU:
1. The OS kernel spends massive CPU cycles context-switching between thousands of processes or threads instead of executing query instructions.
2. Contention on database internal locks (buffer pool latches, row locks, WAL locks) increases exponentially.
3. Disk read heads or SSD queue depth saturate, leading to severe latency inflation.
According to queuing theory (Little's Law and Amdahl's Law), optimal throughput occurs when active query threads roughly match $(2 \times \text{CPU cores}) + \text{spindle count}$. Beyond this point, throughput drops while latency skyrockets.

### Q2: How does `spring.jpa.open-in-view=true` cause subtle production outages?
**Answer**:
OSIV holds an open database connection across the entire lifecycle of an HTTP request. If the controller spends time serializing a large JSON payload, streaming data to a slow client over cellular network, or calling another microservice, the database connection sits completely idle yet checked out. Under high traffic, this exhausts connection pools rapidly even when total SQL query execution time is only a few milliseconds.

---

## Staff / Principal Level (8+ Years)

### Q3: Contrast Optimistic Locking vs Pessimistic Locking in high-concurrency systems. When does each fail?
**Answer**:
- **Optimistic Locking** (`@Version`): Does not acquire database locks on read. On update: `UPDATE table SET val=?, version=version+1 WHERE id=? AND version=?`. If version changed, throws `OptimisticLockException`.
  - *When to use*: Low-to-moderate contention. High read-to-write ratio.
  - *Failure mode*: Under heavy write contention (e.g. ticket booking or flash sales), 95%+ of updates fail and must retry, wasting massive CPU and network round-trips.
- **Pessimistic Locking** (`SELECT ... FOR UPDATE`): Directly acquires exclusive row lock at the database level.
  - *When to use*: High contention where conflict is guaranteed.
  - *Failure mode*: Holding locks for extended duration causes thread serialization and deadlocks if multiple rows are locked in inconsistent orders.

### Q4: Design a zero-downtime database migration strategy for renaming a column in a 500-million row table with 20,000 TPS.
**Answer**:
Direct `ALTER TABLE RENAME COLUMN` locks the table metadata, blocking reads and writes, and instantly breaks older application versions running in the fleet.
**Zero-Downtime Multi-Phase Pattern**:
1. **Phase 1 (Add New Column)**: Add new column as nullable (`ALTER TABLE orders ADD COLUMN customer_uuid UUID`). Fast metadata-only change.
2. **Phase 2 (Dual-Writing)**: Deploy application version that writes to BOTH old and new columns, but reads from old column.
3. **Phase 3 (Backfill)**: Run an asynchronous background batch migration script copying data from old column to new column in small batches (e.g. 1,000 rows with 50ms pause) to avoid lock contention and replication lag.
4. **Phase 4 (Read New Column)**: Deploy application version that reads from new column and writes to both.
5. **Phase 5 (Stop Dual-Writing)**: Deploy application version that only writes to new column.
6. **Phase 6 (Drop Old Column)**: Drop old column safely in off-peak hours.
