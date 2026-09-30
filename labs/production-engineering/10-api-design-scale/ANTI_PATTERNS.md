# ANTI-PATTERNS: API Design, Resilience & Scale
## Lab 10 | Production Engineering Academy — Top 0.0001% Engineering

---

## Anti-Pattern 1: Deep Offset Pagination on Large Tables

### The Mistake
Exposing `?page=N&size=50` or executing SQL queries with `OFFSET N`:
```sql
SELECT * FROM orders WHERE tenant_id = 42 ORDER BY created_at DESC LIMIT 50 OFFSET 250000;
```

### Why It Fails
1. **Linear Time Complexity $O(N + K)$**: The database engine cannot calculate the disk offset of row 250,000 without physically scanning, parsing MVCC visibility, and sorting the preceding 250,000 rows.
2. **Buffer Cache Poisoning**: Crawlers and scraping bots querying deep pages force gigabytes of cold table blocks into PostgreSQL / MySQL buffer pools, evicting the hot working set of active queries.
3. **The Drifting Window Bug**: If an order is inserted while a customer paginates from page 1 to page 2, all rows shift down. The customer sees the 50th item duplicated on page 2.

### The Correct Production Fix
Use **Keyset / Cursor-Based Pagination** anchored to an indexed composite key:
```sql
SELECT * FROM orders 
WHERE tenant_id = 42 AND (created_at, id) < (:cursor_created_at, :cursor_id)
ORDER BY created_at DESC, id DESC 
LIMIT 50;
```
Latency remains constant ($< 2\text{ms}$) regardless of whether the query reads page 1 or page 50,000.

---

## Anti-Pattern 2: Returning Unbounded Collections (The Heap Killer)

### The Mistake
Exposing REST collection endpoints without default limits or hard upper bounds:
```java
@GetMapping("/users/{id}/transactions")
public List<TransactionDto> getTransactions(@PathVariable Long id) {
    // Unbounded repository query!
    return transactionRepository.findByUserId(id); 
}
```

### Why It Fails
1. For standard consumer accounts with 20 transactions, the endpoint functions normally.
2. When an enterprise merchant or automated test account with 400,000 transactions invokes the endpoint:
   - Hibernate instantiates 400,000 entity objects on the JVM heap.
   - Jackson attempts to serialize a 250MB continuous JSON string.
   - Eden and Tenured generations exhaust within seconds, triggering consecutive Stop-The-World Full GC pauses and terminating the pod via Linux OOMKiller.

### The Correct Production Fix
Always mandate pagination parameters with hard upper bounds enforced at controller validation:
```java
@GetMapping("/users/{id}/transactions")
public PageResponse<TransactionDto> getTransactions(
        @PathVariable Long id,
        @RequestParam(defaultValue = "20") @Min(1) @Max(100) int limit,
        @RequestParam(required = false) String cursor) {
    return transactionService.getPagedTransactions(id, limit, cursor);
}
```

---

## Anti-Pattern 3: In-Memory Local Rate Limiting Across Multi-Pod Fleets

### The Mistake
Using an in-process local rate limiter (e.g. Google Guava `RateLimiter` or Resilience4j `RateLimiter`) inside each application pod:
```java
// Inside Spring Controller
private final RateLimiter limiter = RateLimiter.create(100.0); // 100 req/sec

@PostMapping("/checkout")
public ResponseEntity<?> checkout(...) {
    if (!limiter.tryAcquire()) {
        return ResponseEntity.status(429).build();
    }
    // ...
}
```

### Why It Fails
1. The rate limit state is isolated inside each individual JVM heap.
2. In a production cluster running 60 Kubernetes pods behind a round-robin load balancer, an attacker or abusive client can distribute requests evenly across all 60 pods.
3. The client successfully executes **$60 \times 100 = 6,000$ requests/second** before receiving a single HTTP 429 response!

### The Correct Production Fix
Enforce rate limiting centrally at the **API Gateway** or via a shared **Redis Cluster** using atomic Lua Token Bucket or Sliding Window scripts:
```java
boolean allowed = redisRateLimiter.tryAcquire(clientId, 100, 100.0);
```

---

## Anti-Pattern 4: Idempotency Keys Without Payload Fingerprint Validation

### The Mistake
Accepting an `Idempotency-Key` header and replaying the cached response without verifying whether the request payload matches the original invocation:
```java
// VULNERABLE IMPLEMENTATION:
String cachedResponse = redis.get("idempotency:" + idempotencyKey);
if (cachedResponse != null) {
    return ResponseEntity.ok(cachedResponse); // Blind replay!
}
```

### Why It Fails
1. **Security & Financial Disaster**:
   - Client sends: `POST /v1/transfers {"amount": 10.00, "to": "Alice"}` with key `K1`. The transfer succeeds.
   - Due to a client bug or malicious parameter tampering, the client sends: `POST /v1/transfers {"amount": 10000.00, "to": "Bob"}` with the SAME key `K1`.
   - The vulnerable server inspects key `K1`, sees it was already processed, and returns `HTTP 200 {"status": "SUCCESS"}`!
   - Bob believes he was sent $10,000, while Alice was the only recipient of $10!

### The Correct Production Fix
Compute and store a cryptographic digest (`SHA-256`) of the request path and payload alongside the idempotency record. If an existing key arrives with a conflicting hash, immediately reject the call with **HTTP 422 Unprocessable Entity**:
```java
if (!MessageDigest.isEqual(cachedRecord.payloadHash(), currentRequestHash)) {
    return ResponseEntity.status(HttpStatus.UNPROCESSABLE_ENTITY)
            .body("{\"error\":\"Idempotency key reuse with mismatched payload\"}");
}
```

---

## Anti-Pattern 5: Breaking Schema Evolution & Violating Postel's Law

### The Mistake
Renaming a JSON field or changing a primitive type in an active API without supporting backward compatibility:
```json
// Old API response (v1):
{"user_id": 10482, "status": "ACTIVE"}

// Developer deploys "cleaner" response:
{"userId": "usr_10482", "status": 1}
```

### Why It Fails
1. Mobile applications (iOS/Android) cannot force instant customer updates; millions of users run app versions built 6 to 18 months ago.
2. Older JSON deserializers expect an integer `user_id` and fail with `JsonParseException` or `UnrecognizedPropertyException`.
3. Upstream microservice pipelines crash instantly upon deployment.

### The Correct Production Fix
1. **Adhere to Postel's Law**: Always configure deserializers to ignore unknown fields:
   `@JsonIgnoreProperties(ignoreUnknown = true)`.
2. **Follow the Expand and Contract Pattern**:
   Add new fields alongside old fields (`userId` and `user_id`), dual-write for a multi-month deprecation period, track usage via API Gateway metrics, and provide `Sunset` headers (RFC 8594) before final removal.

---

## Anti-Pattern 6: Missing Distributed Mutex on In-Flight Idempotent Requests

### The Mistake
Creating the idempotency record only *after* the business database transaction completes:
```java
// VULNERABLE CODE:
if (isAlreadyProcessed(idempotencyKey)) {
    return getCachedResponse(idempotencyKey);
}
// Execute payment... (Takes 800ms)
paymentService.chargeCustomer(order);
// Save idempotency record...
saveIdempotencyRecord(idempotencyKey, response);
```

### Why It Fails
If a client fires two identical requests concurrently at $t = 0\text{ms}$ (due to double-clicking, frontend retry race, or mobile network split):
1. Both Thread A and Thread B check `isAlreadyProcessed(idempotencyKey)` simultaneously.
2. Both receive `false`.
3. Both threads execute `paymentService.chargeCustomer(order)`.
4. **The customer is double-billed** before either thread can write the completed idempotency record!

### The Correct Production Fix
Acquire an atomic distributed lock or insert an `IN_PROGRESS` state record in Redis/DB **before** initiating the business transaction:
```java
Boolean acquired = redis.opsForValue().setIfAbsent("lock:" + idempotencyKey, "IN_PROGRESS", 15s);
if (!acquired) {
    return ResponseEntity.status(HttpStatus.CONFLICT)
            .header("Retry-After", "2")
            .body("{\"error\":\"Request with this Idempotency-Key is currently in progress\"}");
}
```

---

## Anti-Pattern 7: Exposing Sequential Auto-Increment Database IDs

### The Mistake
Exposing raw primary keys in public REST endpoints:
`GET /api/v1/orders/18420`

### Why It Fails
1. **Business Intelligence Leak (The German Tank Problem)**:
   Competitors can place one order on Monday (`id = 18420`) and one order on Friday (`id = 21920`). They immediately know your platform processes exactly 3,500 orders/week and can calculate total gross merchandise value.
2. **Insecure Direct Object Reference (IDOR)**:
   Attackers easily script sequential enumeration attacks (`for id in range(1, 1000000): fetch(id)`), discovering security vulnerabilities in authorization filters.

### The Correct Production Fix
Expose globally unique, non-sequential, cryptographically unguessable identifiers:
- **UUIDv7**: Time-ordered 128-bit UUIDs (preserves B-Tree index sequential write performance while preventing enumeration).
- **NanoID / Hashids**: Compact URL-safe identifiers (e.g. `ord_8jF2kL9m`).

---

## Anti-Pattern 8: Protobuf Tag Number Reuse and Missing `reserved` Declarations

### The Mistake
Deleting a deprecated Protobuf field and subsequently assigning its numerical tag to a new field:
```protobuf
// V1 Schema:
message Transaction {
    int64 id = 1;
    double deprecated_fee = 2; // Tag 2 deprecated and removed in V2
}

// V2 Schema (DANGEROUS):
message Transaction {
    int64 id = 1;
    string merchant_name = 2;  // REUSED TAG 2 FOR A STRING!
}
```

### Why It Fails
1. Protobuf wire protocol transmits only numeric tags, not field names.
2. When a service running V2 reads a historical binary record serialized with V1:
   - Tag 2 contains an 8-byte floating point IEEE-754 number (`deprecated_fee`).
   - V2 attempts to deserialize those raw float bytes as a UTF-8 `string`!
3. The parser throws a fatal deserialization exception or corrupts business data with unprintable garbage characters.

### The Correct Production Fix
Whenever removing a field from a Protobuf definition, **always reserve both the tag number and the field name**:
```protobuf
message Transaction {
    reserved 2;
    reserved "deprecated_fee";
    
    int64 id = 1;
    string merchant_name = 3; // Assigned clean, unused tag 3
}
```
The Protobuf compiler will permanently reject any attempt to reuse tag 2.
