# PRODUCTION READINESS CHECKLIST: API Design, Resilience & Scale
## Lab 10 | Go-Live Quality Gate | Production Engineering Academy — Top 0.0001% Engineering

---

## 1. Pagination & Query Bounds Quality Gate

- [ ] **Zero Unbounded Queries Policy**:
  - Every collection endpoint mandates a `limit` parameter with a default of $20$ and a hard ceiling of $\le 100$.
  - Endpoints returning raw `List<Entity>` without pagination are strictly prohibited.
- [ ] **Keyset Cursor Pagination Enforced on Large Tables**:
  - Any dataset projected to exceed $10,000$ rows uses keyset cursor pagination.
  - Query execution verified via `EXPLAIN (ANALYZE, BUFFERS)` to prove an **Index Only Scan** or **Bitmap Index Scan** with $O(\log N)$ seeks.
- [ ] **Composite Index Alignment**:
  - Database composite index matches exact query sorting order:
    ```sql
    CREATE INDEX idx_orders_pagination ON orders (tenant_id, created_at DESC, id DESC);
    ```
- [ ] **Tamper-Proof Opaque Cursors**:
  - Cursors exposed to clients are Base64-URL-encoded and signed with HMAC-SHA256. Raw SQL column names and primary keys are completely hidden.
- [ ] **Elimination of Deep `COUNT(*)`**:
  - Paginated responses omit global table counts on datasets $> 50,000$ rows. The presence of a next page is determined via a `limit + 1` probe row.

---

## 2. Distributed Rate Limiting & Abuse Prevention

- [ ] **Multi-Tier Rate Limiting Configured**:
  - **L7 Edge**: Cloudflare / AWS WAF blocks IP-based volumetric floods.
  - **API Gateway**: Redis-backed Token Bucket / Sliding Window Counter rate limiters evaluate authenticated API keys and user IDs.
- [ ] **Standardized RFC Response Headers**:
  - All responses include standard rate limit headers:
    - `RateLimit-Limit`: Maximum permitted request quota.
    - `RateLimit-Remaining`: Remaining request count in active window.
    - `RateLimit-Reset`: Epoch timestamp when quota resets.
- [ ] **HTTP 429 Status with RFC 7807 Problem Details**:
  - Throttled requests receive `HTTP 429 Too Many Requests` accompanied by a `Retry-After: <seconds>` header.
- [ ] **Request Payload Size Hard Capped**:
  - Maximum body size configured on Gateway and Spring Boot (`spring.servlet.multipart.max-request-size = 10MB` for uploads, `1MB` for standard JSON).

---

## 3. Distributed Idempotency & Financial Safety

- [ ] **Mandatory `Idempotency-Key` Header**:
  - All non-idempotent state mutations (`POST /v1/payments`, `POST /v1/orders`, `PATCH /v1/wallets`) enforce the `Idempotency-Key` HTTP header.
- [ ] **Cryptographic Hash Fingerprinting**:
  - Request body and path are hashed with `SHA-256`.
  - Reusing an existing key with a modified payload returns `HTTP 422 Unprocessable Entity`.
- [ ] **In-Flight Lock Protection**:
  - A distributed mutex (`SET lock:key "IN_PROGRESS" NX PX 15000`) prevents concurrent identical requests from double-executing.
  - Concurrent requests receive `HTTP 409 Conflict` with `Retry-After: 1`.
- [ ] **Response Caching Duration**:
  - Idempotency response records are retained in Redis for at least 24 hours.

---

## 4. Contract Evolution & Backward Compatibility

- [ ] **Adherence to Postel's Law**:
  - Deserializers configured to ignore unknown fields:
    ```java
    objectMapper.configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);
    ```
- [ ] **Protobuf Tag Immutability & `reserved` Declarations**:
  - CI pipeline includes a Protobuf linter (e.g. `buf breaking`) asserting no field numbers have been changed or reused.
  - Removed fields are explicitly marked `reserved`.
- [ ] **Deprecation & Sunset Governance (RFC 8594)**:
  - Deprecated endpoints return:
    - `Deprecation: @<epoch_timestamp>`
    - `Sunset: <HTTP-date>`
    - `Link: <url>; rel="sunset"`
  - Minimum deprecation period: 180 days for public APIs, 90 days for internal APIs.

---

## 5. API Observability, Metrics & SLI Thresholds

| Metric | Prometheus Query | Warning Threshold | Critical Page Threshold |
|---|---|---|---|
| **P99 API Latency** | `histogram_quantile(0.99, rate(http_server_requests_seconds_bucket[1m]))` | $> 250\text{ms}$ | $> 1,000\text{ms}$ |
| **HTTP 5xx Server Error Rate** | `sum(rate(http_server_requests_seconds_count{status=~"5.."}[1m])) / sum(rate(http_server_requests_seconds_count[1m]))` | $> 0.5\%$ | $> 2.0\%$ |
| **Rate Limit Throttling (429 Rate)** | `sum(rate(http_server_requests_seconds_count{status="429"}[1m])) / sum(rate(http_server_requests_seconds_count[1m]))` | $> 5.0\%$ | $> 20.0\%$ |
| **Idempotency Conflict (409/422 Rate)** | `sum(rate(http_server_requests_seconds_count{status=~"409|422"}[1m]))` | $> 10/\text{min}$ | $> 100/\text{min}$ |
| **Keyset Cursor Decode Failures** | `rate(api_cursor_decode_errors_total[5m])` | $> 0.1\%$ | $> 1.0\%$ |
