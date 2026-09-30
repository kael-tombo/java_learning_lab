# THEORY: API Design for Scale, Resilience & Evolution
## Lab 10 | Production Engineering Academy — Top 0.0001% Engineering

---

## 1. Deep Mechanics of Pagination: Offset vs Keyset vs Opaque Cursors

### 1.1 The Mathematical Breakdown of Offset Pagination (`OFFSET N`)
Consider a database table `orders` with $10,000,000$ rows:
```sql
SELECT * FROM orders ORDER BY created_at DESC, id DESC LIMIT 20 OFFSET 5000000;
```

#### Why Offset Fails at Scale ($O(N + K)$ Time Complexity):
1. **The Engine Pipeline**: The SQL engine cannot magically calculate the physical disk offset of row 5,000,000 because rows vary in byte length due to variable-width columns (`VARCHAR`, `TEXT`, `JSONB`) and MVCC visibility flags.
2. **The Execution Plan**:
   - The database traverses the B-Tree index to find the start.
   - It reads and verifies MVCC visibility for **all 5,000,020 rows**.
   - It buffers them in memory or creates a disk temporary file for sorting.
   - It discards the first 5,000,000 rows.
   - It returns the remaining 20 rows.
3. **Hardware Impact**:
   - Page 1 (`OFFSET 0`): Latency $\approx 1.2\text{ms}$.
   - Page 50,000 (`OFFSET 1000000`): Latency $\approx 850\text{ms}$.
   - Page 250,000 (`OFFSET 5000000`): Latency $\approx 4,800\text{ms}$ ($4.8\text{s}$), exhausting database buffer pools and saturating disk IOPS.

#### The Drifting Window Anomaly:
Offset pagination assumes an immutable data stream. If a new row is inserted while a user is paginating:
```
Page 1 returned rows [1..20].
Row 0 is inserted at the top.
Page 2 requests OFFSET 20 LIMIT 20.
Row 20 shifts to position 21!
Result: User sees Row 20 TWICE (duplicate data bug).
```
Conversely, if an order is deleted, rows shift up, and the user skips a record entirely.

---

### 1.2 Keyset (Cursor-Based) Pagination ($O(\log N + K)$ Complexity)
Instead of specifying a relative distance from the beginning, keyset pagination anchors queries to the indexed values of the last record received by the client:

```sql
SELECT * FROM orders 
WHERE (created_at, id) < (:last_created_at, :last_id)
ORDER BY created_at DESC, id DESC 
LIMIT 20;
```

#### Why Keyset Excels:
1. **B-Tree Direct Seek ($O(\log N)$)**:
   The database navigates the multi-column composite B-Tree index `(created_at DESC, id DESC)` in $\sim 4$ page reads, lands directly on `(:last_created_at, :last_id)`, and scans exactly the next 20 adjacent leaf nodes.
2. **Performance Invariant**:
   - Page 1: $1.2\text{ms}$.
   - Page 250,000: $1.2\text{ms}$.
   - Latency is strictly independent of table size $N$.
3. **Zero Window Drift**:
   New insertions at the head of the table do not alter the cursor point. The user never sees duplicate or missing records.

---

### 1.3 Opaque Cursors & Security Tokens
Exposing raw database columns (`created_at`, `id`) in API URLs leaks internal database schemas and primary key distributions, enabling scraping and enumeration attacks.

**Production Standard**: Encode cursors as encrypted, signed, or Base64-URL-safe opaque strings:
```
GET /v1/orders?cursor=eyJjcmVhdGVkX2F0IjoxNzI3NzA5MjAwLCJpZCI6OTQ4MjEwfQ%3D%3D
```
- **Structure**:
  `Base64UrlEncode(JSON.stringify({ created_at: 1727709200, id: 948210, sig: HMAC_SHA256(data, secret) }))`
- **Tamper Resistance**: The HMAC signature prevents clients from forging cursors to access arbitrary database partitions.

---

## 2. Distributed Rate Limiting: Algorithms, Math & Trade-Offs

Rate limiting protects downstream services from saturation, enforces API monetization tiers, and defends against DDoS / brute-force attacks.

```
Incoming Request Stream ──► [ Rate Limiter Engine ] ──┬──► Allowed (Forward to API)
                                                      └──► 429 Too Many Requests
```

### 2.1 Algorithm Comparison Matrix

| Algorithm | Memory Overhead | Burst Handling | Boundary Spike Vulnerability | Implementation Complexity |
|---|---|---|---|---|
| **Fixed Window Counter** | $O(1)$ per client | Poor (No burst control) | **Severe (2x quota spike)** | Low |
| **Sliding Window Log** | $O(\text{Requests})$ (High) | Precise | Zero | Medium (Memory heavy) |
| **Sliding Window Counter** | $O(1)$ per client | Good (Smooth approximation) | Minimal ($< 0.5\%$) | Medium |
| **Token Bucket** | $O(1)$ per client | Excellent (Tunable burst) | Zero | Low/Medium (Redis Lua) |
| **Leaky Bucket** | $O(1)$ per client | None (Strict constant outflow)| Zero | Medium (Queueing required) |
| **GCRA (Generic Cell Rate)**| $O(1)$ per client | Precise (Virtual finish time) | Zero | Advanced (Redis Lua) |

---

### 2.2 The Fixed Window Boundary Vulnerability
In Fixed Window, time is divided into static 1-minute blocks (e.g. `[12:00, 12:01)`). Limit = 100 requests/min.
```
12:00:00                       12:00:59   12:01:00                       12:01:59
   │                              │          │                              │
   │                              ▲          ▲                              │
   │                              │          │                              │
   └──────────────────────────────┴──────────┴──────────────────────────────┘
                        100 requests       100 requests
                        in 1 second        in 1 second
```
- An attacker sends 100 requests at `12:00:59` and 100 requests at `12:01:00`.
- Both batches pass the limiter because they fall into separate static windows.
- **The Vulnerability**: 200 requests hit the system in a 2-second interval, doubling the intended maximum capacity!

---

### 2.3 The Sliding Window Counter Approximation
To prevent boundary spikes without the unbounded memory usage of Sliding Window Log, the **Sliding Window Counter** estimates traffic by interpolating between the current window and previous window:

$$\text{Estimated Count} = \text{Count}_{\text{current}} + \text{Count}_{\text{previous}} \times \left(1 - \frac{t_{\text{elapsed}}}{\text{Window Size}}\right)$$

> **Example**: Window = 60s. Limit = 100 req.
> - Previous window count: 80 requests.
> - Current window count: 30 requests.
> - Current elapsed time: 18 seconds ($18/60 = 0.30$).
> - Estimated count: $30 + 80 \times (1 - 0.30) = 30 + 56 = 86$ requests.
> - Since $86 < 100$, the request is permitted.

---

### 2.4 Token Bucket via Redis Atomic Lua
Token bucket allows bursts up to bucket capacity $B$ while refilling continuously at rate $R$ tokens/second. In distributed systems, tokens are recalculated on-demand rather than running a background tick thread:

$$\text{Tokens}_{\text{new}} = \min(B, \text{Tokens}_{\text{old}} + (\text{now} - t_{\text{last}}) \times R)$$

```lua
-- Redis Atomic Token Bucket Script
local key = KEYS[1]
local capacity = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
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
end

if tokens >= requested then
    tokens = tokens - requested
    redis.call('HMSET', key, 'tokens', tokens, 'last_updated', now)
    redis.call('EXPIRE', key, math.ceil(capacity / refill_rate) * 2)
    return {1, math.floor(tokens)}
else
    redis.call('HMSET', key, 'tokens', tokens, 'last_updated', now)
    return {0, math.floor(tokens)}
end
```

---

## 3. Idempotency & Distributed Deduplication

In distributed networks, network failures are indistinguishable from slow responses. A client sending `POST /v1/payments` may encounter a TCP timeout. If the client retries, the server must guarantee that the customer is charged **strictly once**.

### 3.1 The IETF Idempotency-Key Standard
Clients transmit a unique UUIDv4 token in the HTTP header:
```http
POST /v1/charges HTTP/1.1
Host: api.stripe.com
Idempotency-Key: 9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d
Content-Type: application/json

{"amount": 5000, "currency": "usd"}
```

---

### 3.2 Idempotency State Machine & Execution Flow

```
                      [ Client POST with Idempotency-Key ]
                                       │
                                       ▼
                     [ Check Redis/DB Idempotency Record ]
                                       │
            ┌──────────────────────────┼──────────────────────────┐
            ▼                          ▼                          ▼
      [ Record MISS ]         [ State: IN_PROGRESS ]     [ State: COMPLETED ]
            │                          │                          │
   [ Acquire Mutex Lock ]      [ Concurrent Race! ]     [ Verify Request Hash ]
            │                  Wait 50ms & Retry,                 │
            ▼                  or return 409 Conflict    ┌────────┴────────┐
   [ Insert IN_PROGRESS ]                                ▼                 ▼
            │                                      [ Hash Matches ]   [ Hash Mismatch ]
            ▼                                      Return Cached      Return 422
   [ Execute Business DB Tx ]                      Response Payload   Unprocessable Entity
            │                                      (HTTP 200/201)     (Payload Conflict)
            ▼
   [ Update to COMPLETED ]
   [ Cache HTTP Response Payload ]
            │
            ▼
   [ Return HTTP 200/201 ]
```

#### Safe Payload Hashing:
If a client sends an existing `Idempotency-Key` with a **different payload** (e.g. changed amount from $50 to $500), the server must **reject the request immediately with HTTP 422 Unprocessable Entity** to prevent fraudulent parameter hijacking.

---

## 4. API Evolution & Compatibility Invariants

### 4.1 Postel's Law (The Robustness Principle)
> *"Be conservative in what you send, be liberal in what you accept."* — Jon Postel (RFC 760)

1. **Consumers Must Ignore Unknown Fields**:
   When reading JSON or Protobuf payloads, client deserializers must silently ignore unrecognized keys rather than failing with `UnrecognizedPropertyException`.
   - In Jackson: `@JsonIgnoreProperties(ignoreUnknown = true)`
2. **Producers Must Not Remove or Re-purpose Fields**:
   Fields once published are permanent invariants.

---

### 4.2 Protobuf Wire-Level Invariants

Protocol Buffers encodes messages into binary TLV (Tag-Length-Value) streams:
```
Field Tag = (field_number << 3) | wire_type
```

#### The Golden Rules of Protobuf Compatibility:
1. **Never Change Field Numbers (Tags)**: The field name is never sent over the wire; only the numeric tag is transmitted. Changing tag `2` to `3` breaks all existing serialized payloads.
2. **Never Change Field Types**: Changing `int32` to `string` corrupts binary decoding.
3. **Deprecation Invariant (`reserved`)**:
   When removing a field, mark its tag and name as reserved:
   ```protobuf
   message UserProfile {
       reserved 3, 7, 12 to 15;
       reserved "fax_number", "ssn_hash";
       
       string id = 1;
       string email = 2;
   }
   ```
   This prevents future developers from accidentally assigning tag `3` to a new field, which would cause old stored binary records to deserialize into the new field!

---

### 4.3 Zero-Downtime Database & API Migration: Expand and Contract

When modifying a schema (e.g. renaming column `customer_name` to `first_name` and `last_name`):

```
Phase 1: EXPAND
  - Database: Add nullable columns `first_name` and `last_name`.
  - Application: Writes to BOTH old and new columns (Dual-Writing). Reads from old column.

Phase 2: BACKFILL
  - Execute background migration script to populate `first_name` and `last_name` for historical rows.

Phase 3: CONTRACT READ
  - Application: Switch all read queries to `first_name` and `last_name`.
  - Application: Continue dual-writing.

Phase 4: CONTRACT WRITE
  - Application: Stop writing to `customer_name`.

Phase 5: CLEANUP
  - Database: Drop column `customer_name` after 30 days.
```
Every phase is independently deployable and roll-back safe.
