# INTERVIEW QUESTIONS: API Design for Scale, Resilience & Evolution
## Lab 10 | Senior / Staff / Principal & Chief Architect Level — Top 0.0001% Engineering

---

## Senior Level (5+ Years Experience)

### Q1: Why is cursor/keyset pagination $O(\log N)$ while offset pagination is $O(N)$? How do you implement keyset pagination on non-unique columns?
**Answer**:
1. **The Physics of Offset Pagination**:
   When running `SELECT * FROM orders ORDER BY created_at DESC LIMIT 20 OFFSET 500000;`, the database cannot jump to byte offset 500,000 because rows have variable length. It must scan 500,020 rows in B-Tree order, evaluate MVCC row visibility, discard the first 500,000 in memory, and return 20. The latency scales linearly with offset depth ($O(N + K)$), eventually resulting in query timeouts and buffer pool thrashing.
2. **The Physics of Keyset Pagination**:
   Keyset pagination queries:
   `WHERE (created_at, id) < (:cursor_created_at, :cursor_id) ORDER BY created_at DESC, id DESC LIMIT 20;`
   The database navigates the composite index B-Tree from root to leaf in $O(\log N)$ time, lands directly on the cursor tuple, and reads exactly 20 adjacent leaf records ($O(\log N + K)$).
3. **Handling Non-Unique Columns**:
   If you paginate solely on `created_at` (`WHERE created_at < :cursor_ts`), multiple rows sharing the identical millisecond timestamp will cause missing records or infinite pagination loops.
   - **Production Requirement**: A **tie-breaker column** (typically the primary key `id`) must be appended to create a strictly monotonic composite key `(created_at DESC, id DESC)`.

---

### Q2: Compare Fixed Window, Sliding Window Log, Sliding Window Counter, and Token Bucket. When would you choose one over another?
**Answer**:
1. **Fixed Window Counter**:
   - Resets count every static interval (e.g. 100 req per minute block `[12:00, 12:01)`).
   - *Vulnerability*: **Boundary burst spike**. An attacker sends 100 req at 12:00:59 and 100 req at 12:01:00. Both pass, generating 200 requests in 2 seconds ($2\times$ quota spike).
2. **Sliding Window Log**:
   - Stores timestamps of every request in a Redis Sorted Set (`ZSET`).
   - *Advantage*: Absolute mathematical accuracy; zero boundary spike.
   - *Disadvantage*: Memory complexity is $O(\text{Requests})$. For 100,000 users making 1,000 req/min, Redis memory explodes to gigabytes.
3. **Sliding Window Counter (Approximation)**:
   - Interpolates current window count with weighted previous window count:
     $$\text{Estimated} = \text{Count}_{\text{curr}} + \text{Count}_{\text{prev}} \times (1 - t_{\text{elapsed}}/\text{Window})$$
   - *Advantage*: $O(1)$ memory per client; bounds boundary spikes to $< 0.5\%$. Ideal for standard gateway rate limiting.
4. **Token Bucket**:
   - Bucket holds up to capacity $C$ tokens; refills at rate $R$ tokens/second.
   - *Advantage*: Allows controlled bursts up to $C$ while guaranteeing long-term traffic never exceeds $R$. Handled in Redis with $O(1)$ space using atomic Lua scripts. Ideal for REST APIs and third-party developer integrations.

---

### Q3: Walk through the complete design of an idempotent payment API endpoint.
**Answer**:
A client calls `POST /v1/charges` with header `Idempotency-Key: <UUIDv4>`.
1. **Deduplication Store**: Redis Cluster backed by an SQL `idempotency_keys` table.
2. **Payload Fingerprinting**: Compute `SHA-256(request_body + path)`.
3. **State Machine Transitions**:
   - **Step 1 (Check & Lock)**: Attempt atomic insert of state `IN_PROGRESS` with a 15-second lock timeout:
     `SET lock:idempotency:<key> "IN_PROGRESS" NX PX 15000`
   - **Step 2 (Existing Record Check)**:
     - If record exists with state `COMPLETED`: Verify request hash matches. If matched, return the cached HTTP status code and response body immediately (replay). If hash differs, return `HTTP 422 Unprocessable Entity` (Key reuse with payload conflict).
     - If record exists with state `IN_PROGRESS`: Another thread is currently processing this transaction. Return `HTTP 409 Conflict` with `Retry-After: 1`.
   - **Step 3 (Execute Transaction)**:
     - Run payment processing within a database transaction.
   - **Step 4 (Save Response & Complete)**:
     - Write HTTP response (e.g. `201 Created`, payload, hash) to Redis with a 24-hour TTL and release the lock.
   - **Step 5 (Error Handling)**:
     - If business transaction throws an unexpected runtime exception, delete the lock so the client can retry immediately with the same key.

---

## Staff Level (8+ Years Experience)

### Q4: Design a globally distributed rate-limiting architecture supporting 1,000,000 requests/sec across 4 continental regions with sub-millisecond overhead.
**Answer**:
A centralized Redis cluster in a single region causes cross-region network latency penalties ($80 - 150\text{ms}$ round-trip), unacceptable for an inline rate-limiting proxy.

**Decentralized Multi-Region Architecture**:
1. **Local Redis Clusters per Region**:
   - Each cloud region (us-east, eu-central, ap-southeast, sa-east) runs an independent local Redis Cluster.
   - Inbound requests check only their local regional Redis instance over VPC peering ($< 0.5\text{ms}$ latency).
2. **Asymmetric Quota Partitioning**:
   - A central coordinator (or background orchestrator) allocates fractions of the global client quota to each region based on historical traffic distributions:
     - US: 50% ($500\text{k}$ req/sec), EU: 30%, AP: 15%, SA: 5%.
   - Each local Redis enforces its fractional quota independently.
3. **Dynamic Rebalancing Loop (Asynchronous Heartbeat)**:
   - Every 2 seconds, regional proxies publish consumption telemetry to a Kafka topic or via a lightweight Gossip protocol.
   - If a regional traffic spike occurs in Europe (e.g. Europe consumes 95% of its allocation while US consumes only 10%), the coordinator dynamically shifts unallocated quota to Europe within 2 seconds.
4. **Local Batching / Token Reservations**:
   - API Gateways buffer token acquisitions locally using in-memory token buckets, fetching tokens from Redis in batches of 50 or 100 to reduce Redis QPS by $98\%$.
5. **Fail-Open Policy**:
   - If local Redis encounters network failure or cluster partition, the rate limiter **fails OPEN**, logging an alert while prioritizing customer uptime over strict rate enforcement.

---

### Q5: How do you execute a zero-downtime database and API schema migration using the Expand and Contract pattern?
**Answer**:
Consider splitting table column `address TEXT` into `street, city, zip, country`:

1. **Phase 1: Expand (Non-Breaking Addition)**:
   - Add new nullable columns to database schema: `street`, `city`, `zip`, `country`.
   - Add new optional fields to API payload definitions.
   - Deploy Application Version A: **Dual-Writing**.
     - All incoming writes write to BOTH old column `address` and new structured columns.
     - All reads continue reading from old column `address`.
2. **Phase 2: Backfill Historical Data**:
   - Execute an asynchronous, chunked background migration job to parse and backfill all historical rows where new columns are `NULL`.
   - Run verification scripts to assert $100\%$ data parity.
3. **Phase 3: Contract Reads**:
   - Deploy Application Version B: Switch all read queries to use the new structured columns.
   - Continue dual-writing to guarantee rollback safety.
4. **Phase 4: Contract Writes**:
   - Deploy Application Version C: Cease writing to old column `address`.
5. **Phase 5: Cleanup**:
   - After a bake period (e.g. 30 days), drop old column `address` from the database.

---

### Q6: What security vulnerabilities emerge when an API accepts idempotency keys without cryptographic payload hashing?
**Answer**:
If an API stores only `Idempotency-Key -> Response` without hashing the request payload:
1. **Parameter Tampering / Accounting Fraud**:
   - An attacker submits: `POST /v1/transfers {"amount": 5.00, "recipient": "Eve"}` with `Idempotency-Key: abc-123`.
   - Attacker repeats the call with a modified payload: `POST /v1/transfers {"amount": 50000.00, "recipient": "Eve"}` reusing `Idempotency-Key: abc-123`.
   - The server matches key `abc-123`, skips the transfer, and replays `HTTP 200 {"status": "SUCCESS"}`.
   - If a frontend or downstream microservice consumes that response, it records a $50,000 transfer as completed!
2. **Accidental Client Key Collisions**:
   - Two distinct client operations inadvertently generate the same UUIDv4 or hardcoded string. Operation B receives Operation A's private response payload (PII / token data leak).
3. **The Architectural Mandate**:
   - Calculate `SHA-256(request_body + request_path)`.
   - Store the hash with the idempotency record.
   - Reject any reuse with mismatched hash using **HTTP 422 Unprocessable Entity**.

---

## Principal / Chief Architect Level (Top 0.0001%)

### Q7: Compare wire-format performance and architecture across JSON, Protobuf, FlatBuffers, and Cap'n Proto. When should an enterprise use each?
**Answer**:
1. **JSON (Text-Based, Schema-Optional)**:
   - *Wire Encoding*: UTF-8 text characters with field names repeated in every payload.
   - *Serialization Overhead*: High CPU cost parsing strings, numbers, brackets, and allocating intermediate string objects.
   - *Best For*: Public REST APIs, browser-facing web applications, human readability.
2. **Protocol Buffers (Binary, Schema-Enforced)**:
   - *Wire Encoding*: Binary Tag-Length-Value (TLV) stream with Varint encoding.
   - *Serialization Overhead*: Compact byte size ($3-5\times$ smaller than JSON); fast parsing; requires schema compilation (`.proto`).
   - *Best For*: Internal microservice RPCs (gRPC), event streams (Kafka), cross-language backend communication.
3. **FlatBuffers & Cap'n Proto (Zero-Copy Binary)**:
   - *Wire Encoding*: In-memory binary representation matches wire representation. Data is aligned on memory offsets with internal pointer offsets.
   - *Serialization Overhead*: **Virtually zero serialization/deserialization CPU cost**. Accessing a field reads raw bytes directly from the network buffer without allocating JVM objects on the heap!
   - *Best For*: Ultra-low-latency financial trading systems, real-time gaming, edge IoT sensors, and high-frequency messaging pipelines.

---

### Q8: Design an enterprise API Gateway architecture capable of handling 500,000 concurrent WebSocket and HTTP/2 connections with zero-downtime route reconfiguration.
**Answer**:
1. **Data Plane vs Control Plane Separation**:
   - **Data Plane**: High-performance C++ / Rust proxy (e.g. **Envoy Proxy**) running as a Kubernetes DaemonSet or Deployment.
   - **Control Plane**: Centralized configuration management engine implementing the **Dynamic Discovery Service (xDS v3 API)** over gRPC.
2. **Zero-Downtime Dynamic Reconfiguration**:
   - Routes, clusters, TLS certificates, and rate limits are updated via **Route Discovery Service (RDS)** and **Cluster Discovery Service (CDS)**.
   - When routing rules change, Envoy receives an asynchronous xDS gRPC push and applies the new routing table in memory atomically without restarting processes or dropping active TCP/WebSocket connections.
3. **Connection Concurrency & Resource Budgeting**:
   - Non-blocking event-driven architecture using Linux `epoll` / `io_uring` with 1 worker thread per CPU core.
   - Kernel TCP tuning:
     ```conf
     net.core.somaxconn = 65535
     net.ipv4.tcp_max_syn_backlog = 65535
     net.ipv4.ip_local_port_range = 1024 65535
     ```
   - Connection buffer pooling to limit memory footprint to $< 32\text{KB}$ per idle connection.
4. **Context Propagation & Resilience Filters**:
   - Inject W3C Trace Context (`traceparent`, `tracestate`) headers automatically.
   - Built-in circuit breaking (outlier detection based on consecutive 5xx errors) and local token bucket rate limiting.
