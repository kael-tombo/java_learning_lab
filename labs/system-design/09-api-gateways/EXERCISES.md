# API Gateways - Exercises

Twelve exercises, ordered by difficulty. Solutions are provided; attempt each
before reading.

---

## Exercise 1: Longest-Prefix Matching (Easy)

**Goal**: Given the route table below, write a matcher and determine which
service each request reaches.

```
GET /orders/special          -> orders
GET /orders/{orderId}        -> orders
GET /orders/{orderId}/items  -> order-items
GET /orders/search           -> order-search
GET /health                  -> health
```

Which service handles `GET /orders/search`? Which handles
`GET /orders/{orderId}/items`?

<details>
<summary>Solution</summary>

`GET /orders/search` -> **order-search**. Specificity beats registration
order: a literal segment beats a parameter. If you iterate a `LinkedHashMap` in
insertion order and check `/orders/{orderId}` before `/orders/search`, you route
`search` as an order id and the request 404s downstream.

`GET /orders/{orderId}/items` -> **order-items**, and `orderId` = the segment
value. `/orders/special` -> **orders** (parameter match), which is why
`/orders/special` and `/orders/search` need distinct specific routes.
</details>

---

## Exercise 2: Timeout Ordering (Easy)

A client sets a 1,000 ms timeout. The gateway's own budget is 50 ms. The
downstream service's p50 is 400 ms and its p99 is 2,000 ms.

What should the gateway's downstream timeout be? What should the service's
downstream timeout be?

<details>
<summary>Solution</summary>

Gateway -> service: **950 ms** (1000 - 50 for the gateway's own work).

Gateway -> (service's own call to a dependency): **950 - 400 (p50 of its own
dependency) - 20 = ~530 ms**, propagated as an *absolute* deadline.

The key error is propagating a **duration** rather than an absolute deadline: a
950 ms duration at each hop gives a 2,850 ms worst case over three hops, while
the client gave up at 1,000 ms. Propagate `deadline_epoch_ms` and subtract per
hop.
</details>

---

## Exercise 3: Header Stripping (Medium)

Write the sanitiser and answer: if the gateway forwards `X-Tenant-Id`, what is
the attack?

<details>
<summary>Solution</summary>

An attacker sends `X-Tenant-Id: victim-corp` with their own valid token. If the
gateway forwards it and the service prefers the header over the verified claim,
the attacker reads another tenant's data. This is a real breach class.

The gateway must **drop** every inbound identity header and **re-derive** them
from the verified token. Stripping is not optional decoration.
</details>

---

## Exercise 4: Circuit Breaker States (Medium)

A breaker is CLOSED, 30% of requests to service A are timing out, over 20 s.

Walk the state transitions if: (a) errors stop immediately, (b) errors continue
for 5 minutes, (c) traffic drops to 1 rps.

<details>
<summary>Solution</summary>

(a) Errors stop before the minimum-request threshold is met -> stays CLOSED.
The rate alone is not enough; you need minimum volume or a slow trickle never
opens a breaker.

(b) OPEN at threshold. After the open interval -> HALF_OPEN, allow K probes.
Probe succeeds -> CLOSED. Probe fails -> OPEN again, interval may back off.

(c) Traffic drops to 1 rps. With a minimum-request requirement the breaker never
opens — which is correct for protecting *your* resources but wrong for
protecting *latency*, because 1 rps of 3-second requests still feels broken. Use
**concurrency limits alongside breakers**: breakers protect correctness of
state, concurrency limits protect capacity. That is the real answer.
</details>

---

## Exercise 5: Partial Failure Aggregation (Medium)

A BFF composes profile, orders, and recommendations. Profile is critical,
orders is critical, recommendations is optional.

The recommendations service times out at 1,500 ms. Per-field timeout is 400 ms.
The overall client timeout is 800 ms.

What is the response?

<details>
<summary>Solution</summary>

**200** with `recommendations: null` and an `errorCode` on that field.

- The 400 ms per-field timeout fires long before 1,500 ms.
- Recommendations is non-critical, so it degrades to null.
- Profile and orders succeed, so no critical field failed.

The wrong answers: 503 (one non-essential service broke the page), or 200 with
an empty array (which lies — the client cannot distinguish "no
recommendations" from "recommendations unavailable").
</details>

---

## Exercise 6: Tail Latency of Fan-Out (Hard)

Five services, each p50 = 60 ms, each p99 = 400 ms, independent. RTT 20 ms.

Estimate the p99 of the parallel fan-out.

<details>
<summary>Solution</summary>

Single service p99 = 400 ms.
Fan-out: the response is as slow as the slowest of five.
P(all five under 400 ms) = 0.99^5 = 0.951.
So p95 of the fan-out ~= the p99 of a single service, and the **p99 of the
fan-out is far worse** — roughly the 99.6th percentile of the individual
distribution, i.e. ~700-1,500 ms in practice.

Lesson: a 5-service fan-out's p99 is several times a single service's p99, not
equal to it. This is why per-field timeouts and null fallbacks are structural
requirements for aggregation, not polish.
</details>

---

## Exercise 7: Rate Limit Local Derivation (Medium)

Global limit 10,000 rps, 21 gateway instances. Traffic is highly skewed: 40% of
traffic comes from one tenant.

What local limit do you set, and what happens if you set it too high?

<details>
<summary>Solution</summary>

`ceil(10000 / 21) * 1.2 = 572 rps` per instance.

Too high (e.g. 5,000): one instance — or one noisy tenant landing on it — can
consume 50% of the global budget alone, starving every other tenant. The safety
factor exists precisely for this.

Too low (e.g. 250): total capacity is 21 * 250 = 5,250 < 10,000, so the global
limiter becomes the bottleneck and legitimate traffic is throttled even though
the platform has capacity.

Also note: with 40% on one tenant, a *per-tenant* key matters more than the
per-instance arithmetic. Global-per-client limits are useless for fairness.
</details>

---

## Exercise 8: JWKS Key Rotation (Hard)

The identity provider rotates signing keys hourly. Your gateway caches JWKS for
6 hours. During rotation, both keys are valid for a 10-minute overlap.

What happens to requests signed with the new key during the overlap? Design the
failure away.

<details>
<summary>Solution</summary>

A token signed with the new `kid` arrives; the cache has only the old key ->
`unknown kid` -> **401 for up to 6 hours** if you only refresh on TTL expiry.

Fixes, in order:
1. **Refresh on unknown `kid`** (on-demand, single-flight, rate-limited). This
   is the essential fix.
2. TTL must **exceed** the rotation interval (6h > 1h) so steady state never
   misses.
3. Guard the on-demand refresh so 10,000 unknown-kid requests produce **one**
   fetch, not 10,000.
4. Keep serving the cached old key during rotation; do not evict on refresh
   failure.

Without (1), key rotation becomes a scheduled outage — and the incident
playbook for a leaked key ("rotate now") is exactly when you need it.
</details>

---

## Exercise 9: Metrics Cardinality (Medium)

You emit a metric labelled with the raw path. There are 4 million distinct paths
because every order has an id.

Estimate the series count and describe the failure mode.

<details>
<summary>Solution</summary>

4 million distinct label values per metric name. A time-series database handles
maybe 10k-100k *active* series per metric comfortably; 4M exhausts memory, blows
up storage, and typically stalls the whole metrics pipeline.

Failure mode: a single `GET /orders/{id}` metric takes down the metrics
backend, which then takes down alerting for **every** service. One bad label
removes your entire observability system.

Fix: emit route **templates** (`/orders/{id}`), so series count equals route
count (~800). Keep the raw path in logs and traces, where cardinality is
expected and bounded by sampling.
</details>

---

## Exercise 10: Retry Amplification (Hard)

Client retries 3x. Gateway retries 2x. Service retries 3x.
A `POST /payments` times out at the gateway.

How many requests can reach the payment processor? What is the fix?

<details>
<summary>Solution</summary>

`3 * 2 * 3 = 18x`. A single timed-out `POST /payments` can produce **18 charge
requests** — up to 17 duplicates of a real customer charge.

Fixes:
1. Retry at **exactly one layer** (normally the client).
2. Retry **only idempotent methods** (GET, PUT, DELETE) or requests carrying an
   idempotency key.
3. Retry **only connection-level failures** — never on a timeout, because a
   timeout tells you nothing about whether the request was processed.
4. Add jitter. Without jitter, all retries from all layers fire simultaneously
   and you get the amplification *plus* a thundering herd.
</details>

---

## Exercise 11: Gateway Latency Spike (Hard)

Gateway p95 jumps from 120 ms to 900 ms. Overall CPU is 55%. Services are
healthy. What are the five most likely causes, in investigation order?

<details>
<summary>Solution</summary>

1. **JWKS cache miss storm** — an unknown `kid` (rotation) causing a fetch per
   request to the identity provider. Look at: auth-stage latency specifically.
2. **A downstream service degrading** — the gateway's per-service latency
   breakdown will show which one. The aggregate is a symptom.
3. **Circuit breaker half-open probe storms** — many instances probing
   simultaneously.
4. **Config reload** rebuilding the route table or leaking threads.
5. **Connection pool exhaustion** against a downstream — gateway concurrency
   limit hit, requests queueing.

Method: use the gateway's own per-stage and per-downstream metrics before
hypothesising. This is why per-route and per-service breakdown matters — with
only a gateway-level p95, item 2 and 3 are indistinguishable.
</details>

---

## Exercise 12: Design Review (Hard)

"A team proposes putting the `checkAccountBalance` logic in the gateway so all
services get consistent balance checks."

Write the rejection.

<details>
<summary>Solution</summary>

This is a business rule, not a cross-cutting concern. Rejection:

1. **It needs a database read.** The gateway must not touch the database. That
   makes every request's latency depend on the accounts database, including
   requests that do not care about balances.
2. **Blast radius.** A bug or a slow query in the gateway now affects *every*
   request to the platform, not just account operations.
3. **Deploy coupling.** Changing balance logic requires a gateway deploy — the
   release train for all 200 services.
4. **Duplicated truth.** The rule also exists in the accounts service. Now two
   copies can disagree, and only one is authoritative.
5. **Testability.** Gateway business logic is hard to test in isolation and hard
   to reason about in review.

Correct placement: a dedicated `account-balance` service or a synchronised
projection consumed by the services that need it. The gateway's job is to
answer *can this request proceed*, never *is this request correct*.
</details>