# ARCHITECTURE DECISIONS: Enterprise API Design, Evolution & Scale Standards
## Lab 10 | Production Engineering Academy — Top 0.0001% Engineering

---

## ADR-01: Pagination Architecture: Mandating Opaque Keyset Cursors over Offset

### Status: ACCEPTED
**Context & Problem Statement**:
Deep offset pagination (`OFFSET 100000 LIMIT 20`) on transactional tables (Orders, Payments, Audit Logs) causes full B-Tree scans and disk read spikes in PostgreSQL, degrading database performance and causing intermittent timeouts. Furthermore, insertions during pagination cause drifting window duplicate items.

### Decision
1. **Offset Pagination Prohibition**:
   - `OFFSET` queries are strictly prohibited on any dataset with $> 10,000$ rows.
2. **Mandatory Keyset / Cursor Pagination**:
   - All collection queries must paginate using multi-column composite index seekers:
     ```sql
     WHERE (created_at, id) < (:cursor_created_at, :cursor_id)
     ORDER BY created_at DESC, id DESC
     LIMIT :limit
     ```
3. **Opaque Cursors Standard**:
   - Internal table columns must never be exposed raw in query strings. Cursors must be formatted as Base64-URL-safe HMAC-signed JSON envelopes:
     `cursor=eyJjIjoxNzI3NzA5MjAwLCJpZCI6OTQ4MjEwLCJzIjoiZTNiMGNiYTFmIn0`
4. **Enforced Limits**:
   - Default page size: `20`.
   - Hard maximum limit: `100` items per request. Unbounded queries (`SELECT * FROM table` without `LIMIT`) are blocked by API Gateway schema validators.

### Consequences
- **Positive**:
  - P99 pagination latency is constant ($O(\log N)$) regardless of whether querying page 1 or page 50,000.
  - Zero duplicate records from concurrent row insertions.
- **Negative / Trade-offs**:
  - Clients cannot "jump to page 47 directly"; navigation is strictly sequential (`next` / `previous`).

---

## ADR-02: Distributed Rate Limiting: Redis Token Bucket with Edge Offload

### Status: ACCEPTED
**Context & Problem Statement**:
Uncontrolled API scraping and bursty microservice calls exhaust backend connection pools and cause cascade service degradation. In-memory local rate limiters (e.g., Guava RateLimiter) fail across distributed fleets of 100+ pods because state is not shared, allowing clients to send $100\times$ their intended quota by spreading requests across pods.

### Decision
1. **Tiered Rate Limiting Architecture**:
   - **Tier 1 (Edge Protection)**: Cloudflare / Envoy edge rate limiters block brute-force volumetric L7 attacks based on client IP.
   - **Tier 2 (Gateway Tenant Tiers)**: Spring Cloud Gateway / Envoy filters evaluate API keys and JWT claims against a distributed Redis Cluster using atomic Lua Token Bucket scripts.
2. **Standardized Response Headers**:
   Every API response must include standard rate-limiting headers:
   ```http
   RateLimit-Limit: 100
   RateLimit-Remaining: 84
   RateLimit-Reset: 1727709260
   Retry-After: 3
   ```
3. **Throttling Policy**:
   - Exceeded quotas return `HTTP 429 Too Many Requests` with a JSON Problem Details body (RFC 7807) and `Retry-After` header.

### Consequences
- **Positive**:
  - Global quota enforcement across arbitrary number of application pods.
  - Token bucket allows short bursts while preserving steady-state backend throughput.
- **Negative / Trade-offs**:
  - Adds ~0.8ms Redis network round-trip to incoming API requests (mitigated via Redis connection pipelining).

---

## ADR-03: Distributed Idempotency Standard: IETF Header with Conflict Verification

### Status: ACCEPTED
**Context & Problem Statement**:
Transient network disconnects cause clients to retry non-idempotent state mutations (`POST /v1/payments`, `POST /v1/transfers`). Without strict idempotency handling, retried requests double-bill customers or duplicate ledger entries.

### Decision
1. **IETF `Idempotency-Key` Header**:
   - All state-mutating `POST` and `PATCH` endpoints must require the `Idempotency-Key` HTTP header.
2. **State Machine Invariant**:
   - Keys transition through: `IN_PROGRESS (Lock)` $\to$ `COMPLETED (Cached Response)` or `FAILED`.
   - Idempotency records are persisted in Redis with a 24-hour TTL and backed by an SQL `idempotency_keys` table.
3. **Payload Hash Fingerprinting**:
   - When storing an idempotency record, calculate `SHA-256(request_payload + request_path)`.
   - If an existing key is received with a mismatched hash, the server must reject the call immediately with `HTTP 422 Unprocessable Entity` (Payload Hash Conflict).
4. **Concurrent Request Handling**:
   - A concurrent duplicate request arriving while the first is `IN_PROGRESS` returns `HTTP 409 Conflict` with header `Retry-After: 1`.

### Consequences
- **Positive**:
  - Strict guarantee of exactly-once execution semantics across all financial transactions.
- **Negative / Trade-offs**:
  - Requires persistent storage for response payloads and locks.

---

## ADR-04: API Evolution, Wire Formats & Sunset Deprecation Policy (RFC 8594)

### Status: ACCEPTED
**Context & Problem Statement**:
Ad-hoc API changes breaking mobile clients with slow update cycles caused customer support escalations. Inconsistent wire formats (JSON without field validation vs Protobuf without tag reservations) resulted in deserialization crashes.

### Decision
1. **Backward Compatibility Rules**:
   - Never rename or delete an active field.
   - All new fields added to existing APIs must be optional/nullable with safe defaults.
   - Clients must adhere to Postel's Law: ignore unknown fields during deserialization.
2. **Protobuf Evolution Invariants**:
   - Numeric field tags are immutable.
   - Deprecated fields must be declared `reserved <tag>` and `reserved "<name>"`.
3. **Deprecation & Sunset Governance (RFC 8594)**:
   - Deprecated endpoints must return HTTP response headers:
     ```http
     Deprecation: @1735689600
     Sunset: Wed, 30 Jun 2027 00:00:00 GMT
     Link: <https://docs.company.com/api/v2-migration>; rel="sunset"
     ```
   - Minimum sunset grace period is 180 days for public APIs, 90 days for internal microservices.

### Consequences
- **Positive**:
  - Zero-downtime client migrations and zero breaking changes for mobile applications.
