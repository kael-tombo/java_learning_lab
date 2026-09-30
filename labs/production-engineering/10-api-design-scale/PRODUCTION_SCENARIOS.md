# PRODUCTION SCENARIOS: Real-World API Design & Scale Incidents
## Lab 10 | Production Engineering Academy — Top 0.0001% Engineering

---

## Scenario 1: The Scraping Bot & Deep Offset DB Meltdown

### Incident Overview
- **Impact**: Primary PostgreSQL database CPU spiked to 100%; checkout and cart APIs experienced 504 Gateway Timeouts for 42 minutes. Revenue impact: $820,000.
- **Affected System**: Public catalog API `/api/v1/products?page=N&size=50` serving 25,000,000 SKUs.

### Forensic Timeline & Telemetry
```
14:00:00 - Normal operations: DB CPU 18%, P99 API latency 28ms.
14:02:15 - A competitor launches 80 concurrent crawler threads harvesting catalog data.
14:03:00 - Scraper reaches deep pages: page=25000 (offset=1250000).
14:04:30 - PostgreSQL `pg_stat_activity` shows 80 active backends executing:
           `SELECT * FROM products ORDER BY id LIMIT 50 OFFSET 1250000;`
14:05:00 - Average execution time per query jumps from 3ms to 14,800ms.
14:06:00 - PostgreSQL `shared_buffers` hit ratio plunges from 99.8% to 14.2% as deep scans
           force cold disk blocks into memory, flushing out cached order and user data!
14:08:00 - HikariCP connection pools in 50 Spring Boot checkout pods exhaust (connection timeout 30s).
14:15:00 - PagerDuty alerts SRE team. On-call identifies scraping bot IP subnet.
14:22:00 - SRE applies Cloudflare WAF rule blocking queries containing `offset > 1000`.
14:26:00 - DB CPU drops to 22%, HikariCP pools recover. Outage resolved.
```

### Forensic Root Cause
1. **Linear Offset Complexity**:
   To fulfill `OFFSET 1250000 LIMIT 50`, the PostgreSQL storage engine had to physically read 1,250,050 rows, verify transaction visibility via MVCC tuples, sort in memory, and discard 1,250,000 rows.
2. **Buffer Cache Eviction Storm**:
   Continuous reading of cold disk pages evicted the entire working set of active customer checkout queries from RAM.

### Permanent Architectural Safeguards
1. **Keyset Cursor Pagination Standard**:
   Replaced offset pagination with indexed cursor queries:
   ```sql
   SELECT id, name, price, created_at FROM products 
   WHERE (created_at, id) < (:cursor_created_at, :cursor_id) 
   ORDER BY created_at DESC, id DESC LIMIT 50;
   ```
   Execution latency remains constant at $1.8\text{ms}$ even at page 500,000.
2. **Hard Upper Bound on Legacy Offset**:
   Enforced strict gateway validation: any request with `page * size > 1000` is immediately rejected with `HTTP 400 Bad Request: Deep offset not permitted. Use keyset pagination API`.

---

## Scenario 2: The Black Friday Double-Billing Race (Missing In-Flight Idempotency Mutex)

### Incident Overview
- **Impact**: 4,120 customers double-billed during peak flash sale checkout. Customer support inundated with 12,000 tickets; merchant incurred $62,000 in payment processing chargeback fees.
- **Root Cause**: Naive idempotency implementation that cached the result only *after* payment completion, without acquiring an in-flight execution mutex lock.

### Forensic Sequence of Events
```
Timeline:
T0: User clicks "Complete Purchase" on mobile app.
    Mobile app sends: `POST /v1/charges` with `Idempotency-Key: f47ac10b-58cc-4372-a567-0e02b2c3d479`.
T1: Request reaches Pod 1. Backend begins payment processing with Stripe gateway (Latency: 850ms).
T2: At T + 400ms, user experiences mobile UI hesitation and taps "Complete Purchase" a second time.
    Mobile app sends duplicate: `POST /v1/charges` with the SAME `Idempotency-Key`.
T3: Request 2 reaches Pod 2.
    Pod 2 queries Redis: `GET idempotency:f47ac10b-58cc-4372-a567-0e02b2c3d479`.
    Redis returns NULL because Pod 1 has NOT finished processing yet!
T4: Pod 2 believes this is a new transaction and initiates a SECOND payment charge with Stripe!
T5: At T + 850ms, Pod 1 completes charge 1, saves result to Redis, and returns HTTP 201 to user.
T6: At T + 1250ms, Pod 2 completes charge 2, overwrites Redis, and returns HTTP 201.
Result: Customer's credit card was billed TWICE for the identical order!
```

### The Architectural Safeguards
1. **Mandatory In-Flight Lock Acquisition**:
   Before initiating payment processing, the application must execute an atomic Redis lock:
   ```java
   Boolean locked = redisTemplate.opsForValue()
       .setIfAbsent("lock:" + idempotencyKey, "IN_PROGRESS", Duration.ofSeconds(15));
   if (!Boolean.TRUE.equals(locked)) {
       return ResponseEntity.status(HttpStatus.CONFLICT)
           .header("Retry-After", "2")
           .body("{\"error\":\"Transaction currently processing\"}");
   }
   ```
2. **Cryptographic Payload Fingerprint**:
   Added `SHA-256(request_payload)` validation to reject key reuse with modified charge amounts.

---

## Scenario 3: The Mobile App Launch Catastrophe (Violating Postel's Law)

### Incident Overview
- **Impact**: 480,000 iOS app users experienced instantaneous app crashes upon launching the mobile app following a backend microservice deployment.
- **Affected Version**: iOS App v3.2.1 (released 4 months earlier to the Apple App Store).

### Forensic Chronology
1. **The Backend Change**:
   A backend engineering team refactored the `/api/v2/user/profile` endpoint to standardize on camelCase:
   - Changed JSON field: `"user_id": 10492` $\to$ `"userId": "usr_10492"`.
2. **The Mobile Crash**:
   - iOS app v3.2.1 used Swift's `Decodable` with strict key mapping and non-optional `user_id: Int`.
   - When the app received `"userId": "usr_10492"`, the JSON parser threw a fatal `DecodingError.keyNotFound` exception.
   - Because the error was unhandled in the root app coordinator, the iOS runtime killed the app instantly on the splash screen!
3. **The Deployment Dilemma**:
   - Backend teams could not wait for an Apple App Store emergency review (which takes 24–48 hours for review + weeks for user adoption).

### The Mitigation & Permanent Architecture
1. **Emergency Envoy Response Rewriting Filter**:
   Within 15 minutes, SREs deployed an inline Envoy Lua response filter that cloned `"userId"` into `"user_id"`, restoring instant backward compatibility for mobile clients.
2. **Postel's Law Mandate in Backend & Mobile**:
   - All client decoders must configure permissive parsing (ignore unknown fields and provide fallback defaults for missing attributes).
3. **Automated Backward Compatibility Gate in CI/CD**:
   - Implemented OpenAPI diff checking in Github Actions. Any PR that renames, removes, or alters the type of an existing field fails CI automatically.

---

## Scenario 4: Multi-Pod Rate Limiter Bypass & Flash Sale Collapse

### Incident Overview
- **Impact**: Concert ticketing platform collapsed during ticket drop for a stadium tour; 94% of tickets acquired by scalper automated bots.
- **Root Cause**: Rate limiting implemented locally in-memory using Google Guava `RateLimiter` across 60 Kubernetes pods.

### Forensic Telemetry
```
09:59:58 - Ticket drop countdown: 10 seconds.
10:00:00 - Ticket sales open. Inbound traffic surges to 180,000 RPS.
10:00:05 - Scalper botnets with 5,000 rotating IPs launch automated purchases.
10:00:10 - Developers believed each client was limited to 10 requests/second.
           However, the rate limiter was in-memory inside each Spring Boot pod:
           `RateLimiter limiter = RateLimiter.create(10.0);`
10:00:15 - Because traffic was load-balanced across 60 pods, each bot successfully
           executed 60 pods x 10 req/s = 600 requests/second!
10:00:30 - PostgreSQL ticketing database locked with 500 active transactions.
10:01:00 - Inventory exhausted; scalper bots secured 45,000 tickets.
```

### The Architectural Safeguards
1. **Centralized Redis Cluster Token Bucket**:
   Migrated rate limiting to a dedicated Redis Cluster using atomic Lua scripts. Quotas are enforced globally across all 60 pods:
   - Max 10 requests/second globally per authenticated account, regardless of which pod handles the request.
2. **Edge Bot Management (Cloudflare Turnstile & Proof-of-Work)**:
   Integrated cryptographic Proof-of-Work challenges at the CDN edge before allowing requests to reach the API Gateway.
