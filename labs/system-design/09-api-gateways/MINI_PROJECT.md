# API Gateways - MINI PROJECT

## Project: A Four-Layer Gateway You Can Attack

**Time**: 12-16 hours

**Goal**: Build a gateway with edge, auth, routing, and aggregation layers —
then write the attacks against it and verify each defence.

### Architecture

```
Client
  │  (Authorization: JWT, X-User-Id: attacker-controlled, X-Internal-Call: true)
  ▼
┌─ EDGE ─────────────────────────────────────────────┐
│ TLS (stubbed), body size limit, header allowlist,    │
│ request ID, trace context init, path normalisation  │
└──────────────────────────────────────────────────────┘
  ▼
┌─ AUTH ─────────────────────────────────────────────┐
│ JWT verify: alg pin, signature, exp, iss, aud;       │
│ JWKS cache with refresh-on-unknown-kid; scope check │
└──────────────────────────────────────────────────────┘
  ▼
┌─ ROUTE ────────────────────────────────────────────┐
│ longest-prefix match, prefix strip, discovery,      │
│ deadline propagation, rate limit, circuit breaker   │
└──────────────────────────────────────────────────────┘
  ▼
┌─ AGGREGATE (optional) ─────────────────────────────┐
│ parallel fan-out, per-field timeout + criticality,   │
│ bounded aggregate deadline, null fallback           │
└──────────────────────────────────────────────────────┘
  ▼
Mock services: users, orders, payments, recommendations
```

### Step 1: Route Table and Routing (2 h)

Implement `RouteTable` from `CODE_DEEP_DIVE.md` with:

```
GET  /users/{userId}                 -> users    (strip)
GET  /users/search                   -> user-search (higher priority)
GET  /orders/{orderId}               -> orders   (strip /orders)
POST /payments                       -> payments
GET  /dashboard/*                    -> dashboard (aggregation route)
```

Required tests:
- Specificity beats order: `GET /users/search` must reach `user-search`.
- `POST /payments` must NOT match a `GET /payments` route.
- Atomic reload: build a new table and swap; assert concurrent requests never
  observe a partial table.
- **Path traversal**: `GET /users/../admin` must be rejected or normalised,
  never routed. This is a real and common gateway hole.

### Step 2: JWT Verification (2 h)

Implement `JwtVerifier` with a fake JWKS issuer.

Required tests (each a real attack):

| Attack | Expected |
|--------|----------|
| `alg: none` | rejected |
| RS256 token verified with HS256 using the public key as secret | rejected |
| Valid signature, expired `exp` | rejected |
| Valid signature, wrong `iss` | rejected |
| Valid signature, wrong `aud` | rejected |
| Valid signature, unknown `kid` | triggers refresh, then accepted |
| Tampered payload (signature unchanged) | rejected |

**JWKS rotation drill**: rotate the issuer's key mid-run with a 6-hour cache
TTL. Assert every request continues to succeed because of refresh-on-unknown-kid.
This is the drill that proves rotation is not a scheduled outage.

### Step 3: Header Sanitisation (1 h — the security centrepiece)

Implement `HeaderSanitiser`. Then run these and assert they fail:

1. `X-User-Id: admin` with a valid low-privilege token -> must NOT become admin.
2. `X-Tenant-Id: victim-corp` -> must be replaced by the token's tenant.
3. `X-Internal-Call: true` reaching an admin-only route -> must be stripped, so
   the route is unauthorised.
4. `Connection: keep-alive`, `Transfer-Encoding: chunked` -> dropped.

Write the test where the mock service asserts the identity it received equals
the identity in the token. That assertion is the actual guarantee.

### Step 4: Deadlines, Timeouts, and Breakers (2 h)

Implement `DeadlineContext` and a breaker. Required tests:

- Client timeout 1,000 ms, gateway budget 50 ms -> downstream timeout is 950 ms.
- **Deadline across three hops**: total work must never exceed 1,000 ms.
  Assert by summing the time each simulated service slept.
- A service that sleeps 3 s must be cut off, and the gateway must return before
  the client gives up.
- Breaker: 50% errors over 20 s -> OPEN -> fast fail with `Retry-After`.
- **A slow-but-not-failing dependency (no errors, 3 s latency)**: the breaker
  must NOT open, and you must demonstrate that a **concurrency limit** is what
  actually protects the gateway. This is the lesson from Exercise 4.

### Step 5: BFF Aggregation with Partial Failure (2 h)

Implement `BffAggregator`. Test the `GET /dashboard` route with `profile` and
`orders` critical, `recommendations` optional.

Required scenarios:

| Scenario | Expected |
|----------|----------|
| All healthy | 200, all fields |
| Recommendations times out (400 ms budget, service sleeps 1.5 s) | 200, `recommendations: null` + errorCode |
| Orders (critical) fails | 502 |
| All three slow | 200 or 502 within the 2 s aggregate deadline, never hanging |
| One field is slow but the others are fast | 200 quickly, slow field nulled |

Assert the total response time in each case. The scenario that must be fastest
is the one where only the non-critical field is slow — that is the entire point
of per-field policy.

### Step 6: Rate Limiting (1 h)

Implement a token-bucket limiter keyed on **tenant**, with a local tier.

- Global limit 1,000 rps, 4 instances -> local `ceil(1000/4) * 1.2 = 300`.
- Drive 5,000 rps from one tenant. Assert it cannot exceed its share while other
  tenants still get through.
- **Store down**: assert the degraded mode falls back to the local limit rather
  than allowing unbounded traffic or denying everything.
- Assert the response is `429` with `Retry-After` and the rate-limit headers.

### Step 7: Observability That Does Not Mislead (1 h)

Emit metrics for:
- Per-route rate, errors, and duration (RED).
- Per-downstream-service latency and error rate.
- Per-stage latency (edge / auth / route / aggregate).
- Breaker state per service; rate-limit rejections; JWT verification failures
  by reason.

**Required:** deliberately break one mock service (add 2 s latency) and verify
the per-service breakdown identifies it while the gateway aggregate shows only a
modest rise. Then add a fourth metric labelled with a raw path and watch the
series count explode — then fix it and record the before/after counts. That
contrast is the deliverable.

### Step 8: Load Test (1 h)

Drive 5,000 rps for 60 s. Report:

| Metric | Value |
|--------|-------|
| p50 / p95 / p99 end-to-end | |
| p95 per stage | |
| Per-route throughput and errors | |
| Rate-limit rejections | |
| Downstream connections held | |

**Checkpoint:** p95 must be within the budget from `MATH_FOUNDATION.md`. If it
is not, find which stage exceeded and fix that stage.

### Deliverables

1. Route table with specificity, atomic reload, and traversal rejection.
2. JWT verifier passing all seven attack tests plus the rotation drill.
3. Header sanitiser with four attack tests and the downstream identity
   assertion.
4. Deadline propagation proving total work stays under the client deadline.
5. Breaker plus concurrency limit, with the slow-but-not-failing demonstration.
6. BFF with per-field policy across all five scenarios.
7. Rate limiter with the noisy-tenant and store-down tests.
8. Per-route/per-service metrics with the deliberate-breakage detection and the
   cardinality before/after.
9. Load test table checked against the latency budget.

### Stretch

- Add request/response transformation (REST in, gRPC out) with a version
  translation layer, and measure the transformation cost per request.
- Add a second gateway tier: mobile BFF vs. partner-facing gateway, with
  different auth, limits, and timeouts — and document why one deployment would
  have served both badly.