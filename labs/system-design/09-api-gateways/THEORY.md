# API Gateways - Theory

## 1. The Problem

A platform with 200+ services has 200+ places to solve authentication, rate
limiting, TLS termination, logging, and protocol translation. Left to the
services, that is 200 implementations that will disagree with each other — and
the disagreement is the outage.

The gateway centralises cross-cutting concerns so services can contain only
business logic. The cost is a new component in the critical path of every
request, which is a real trade, not a free win.

## 2. What Belongs at the Gateway

**Yes** — concerns that are identical for every service and must be consistent:
- TLS termination
- Authentication (who is calling)
- Coarse-grained authorisation (which service)
- Rate limiting and quotas (per client, per route)
- Request logging and trace context generation
- Protocol translation (REST to gRPC)
- Response shaping (problem details, envelope normalisation)

**No** — concerns that require domain knowledge:
- Business authorisation ("may this user refund *this* order")
- Aggregate validation across a workflow
- Anything requiring a database round trip
- Anything where a gateway bug is a business-logic bug

The rule: **the gateway answers "can this request proceed?", never "is this
request correct?"** The moment the gateway needs domain data to decide, it has
become a service.

## 3. The Four Layers

```
Client
  │
  ▼
┌──────────────────────────────────────────────────────────┐
│ Layer 1: EDGE                                            │
│  TLS termination, DDoS/WAF, IP allowlist, request ID,     │
│  body size limit, header allowlist, trace context init    │
└──────────────────────────────────────────────────────────┘
  │
  ▼
┌──────────────────────────────────────────────────────────┐
│ Layer 2: AUTHENTICATION                                  │
│  Token signature (JWKS), expiry, issuer, audience,        │
│  scope extraction, service-identity for internal calls    │
└──────────────────────────────────────────────────────────┘
  │
  ▼
┌──────────────────────────────────────────────────────────┐
│ Layer 3: ROUTING                                          │
│  Path/host/header matching, version mapping, service      │
│  discovery, load balancing, deadline propagation,         │
│  rate limiting, circuit breaker                           │
└──────────────────────────────────────────────────────────┘
  │
  ▼
┌──────────────────────────────────────────────────────────┐
│ Layer 4: AGGREGATION (optional, BFF)                      │
│  Compose multiple service calls into one response;        │
│  partial-failure policy per field                         │
└──────────────────────────────────────────────────────────┘
  │
  ▼
Services
```

Layer 4 is optional and is the one most often built unnecessarily. It exists for
**fan-out reduction**, not for business logic: a mobile client making 5 calls
round-trip 5 times where a BFF can do it in 1. If clients are browsers and CORS
is not a problem, layer 4 is usually not worth the aggregation failure surface.

## 4. Authentication and Authorisation

Token verification at the gateway:

```
  1. Fetch signing keys from the issuer's JWKS endpoint (cache!)
  2. Verify signature, algorithm, expiry, issuer, audience
  3. Extract subject, scopes, tenant
  4. Attach a normalised identity header for downstream services
```

**The gateway must verify; it must not merely decode.** A gateway that decodes
a JWT and forwards the claims without checking the signature is an
authentication bypass with extra latency.

**Key rotation** is the operational requirement: JWKS keys rotate on a schedule
and after incidents. Cache JWKS with a TTL and refresh on an unknown `kid`.
Fetching JWKS per request adds a dependency to the critical path that can fail
independently of your services — so cache it hard and refresh on demand.

Authorisation stays in services. The gateway checks scope at the route level
("this token may call payments"), not the resource level ("this user may refund
this order").

## 5. Routing

```java
// Route table entry
{ method, pathPattern, hostPattern, serviceName, stripPrefix, timeoutMs, rewrites }
```

Design notes:

- **Longest-prefix matching**, not exact match — routes are hierarchical.
- **Strip vs. preserve prefix.** Decide per service and document it; services
  that assume the prefix was stripped will 404 in production.
- **Path parameters**: `/orders/{orderId}/items/{itemId}` must not be
  confused with a literal segment. Match parameters *before* wildcards.
- **Timeouts are mandatory** and must be *shorter* than the caller's deadline,
  so the gateway returns before the client gives up.
- **Retry only idempotent requests** and only on connection-level failures.
  A gateway that retries a `POST` produces duplicate charges.

**Header hygiene** is the security control teams forget:
- Strip hop-by-hop headers.
- **Remove inbound `X-User-Id`, `X-Tenant-Id`, `X-Internal-Call` before
  routing to a public-facing service.** Otherwise anyone can send
  `X-User-Id: admin` and become admin. This is a real and recurring breach.

## 6. Aggregation (BFF)

Aggregation reduces client round-trips, and it introduces a
**partial-failure** problem you must design for explicitly:

```java
record AggregatedResponse(String profile, String orders, String recommendations)
```
When the recommendations service is down, do you return:
- **200 with `recommendations: null`** — the client renders the page with a
  gap. Usually correct for read paths.
- **503** — a non-essential service takes down the whole page. Almost always
  wrong.
- **Fallback content** — best, when you have it.

So: declare per-field criticality, and set the timeout per field, not per
request. Three sequential 500 ms calls is a 1.5 s endpoint; three parallel calls
with 400 ms timeouts and a null fallback is a 400 ms endpoint that never fails.

## 7. Rate Limiting and Quotas

See lab `11-rate-limiting-design` for the algorithms. At the gateway the
specific concerns are:

- **Key selection**: API key, tenant, user, or IP. Global limits are useless —
  one noisy tenant starves the rest.
- **Route classes**: authentication routes fail closed, public reads fail open.
- **Two-tier**: a local in-process limit plus a global one, with the local limit
  derived as `global / instances * safety factor`.
- **Response contract**: `429` with `Retry-After` and rate-limit headers.

## 8. Circuit Breaking at the Gateway

A gateway without breakers will happily queue requests to a dying service until
it exhausts its own connection pool — converting one service's failure into a
platform-wide one. Breakers belong at the gateway precisely because it is the
choke point where every failure passes.

Breaker per service, with thresholds tuned per dependency: a fragile third party
opens at a lower error rate than an internal service.

## 9. Observability

The gateway is the best place to observe a platform, because it sees 100% of
traffic.

- **Trace context**: generate or continue a trace ID at the edge. Propagate to
  every downstream service. If the gateway does not do this, you lose the
  request's identity the moment a header is dropped.
- **RED metrics** per route: rate, errors, duration. Per route, not per gateway
  aggregate — a gateway-level p99 hides one broken service entirely.
- **Dependency metrics**: per-downstream-service latency and error rate, so you
  can attribute a gateway latency spike to a specific service.
- **Request size distribution**, which is how you find the endpoint that is
  moving gigabytes.

Cardinality discipline: route templates, not raw paths. `/orders/{id}` not
`/orders/918273`. A gateway is the single easiest place to melt a metrics
backend.

## 10. Gateway Anti-Patterns

| Anti-pattern | Consequence |
|--------------|-------------|
| Business logic in the gateway | One deployable holds all business rules |
| Gateway calls the database | Latency and blast radius both become the gateway's |
| No timeouts | One slow service cascades to everything |
| Retrying non-idempotent requests | Duplicate charges, duplicate orders |
| Forwarding inbound identity headers | Authentication bypass |
| Route-based metrics only | Cardinality explosion |
| BFF by default | Aggregation failure surface for no client benefit |
| Per-request JWKS fetch | Auth availability now depends on the issuer |
| Synchronous fan-out without budgets | Tail latency is the sum, not the max |

## 11. Choosing Where to Put It

The gateway is not always right:

- **Internal service-to-service**: prefer mesh (mTLS, retries, telemetry) over
  an edge gateway. The gateway is for the *untrusted edge*.
- **Few services**: a gateway adds a component and a latency hop for little
  benefit.
- **Different consumers**: a mobile BFF and a partner-facing gateway are
  genuinely different products. "One gateway for everyone" ends up serving
  nobody well.

## Summary

The gateway is a **policy enforcement point**, not a business layer. Its job is
to make untrusted traffic safe and routable. Keep domain logic out, make
timeouts mandatory and shorter than the caller's, strip inbound identity
headers, rate limit per tenant rather than globally, and instrument per route.