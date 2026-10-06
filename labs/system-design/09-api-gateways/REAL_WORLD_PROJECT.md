# API Gateways - REAL WORLD PROJECT

## Project: Production API Gateway for a 200-Service Platform

**Time**: 3-4 weeks (team of 3)

**Scenario**: You are consolidating 200 services behind a single edge. Each
service currently implements its own authentication, rate limiting, and
logging, and they all disagree. Requirements in tension:

- 12,000 rps peak, 99.99% availability (52 min/month of downtime).
- Two identity providers plus a legacy API-key system for 400 enterprise
  tenants.
- p95 end-to-end under 150 ms; the gateway may add no more than 10 ms.
- Partner APIs need different limits, longer timeouts, and an audit log that
  includes their credentials.
- EU traffic must stay in-region.

### Step 1: Latency Budget, Signed Off Per Route Class

Produce a budget table and get it agreed with the services being fronted. This
is the artefact that stops "the gateway made us slower" arguments later.

```
end_to_end = edge + auth + route + service + shaping

Budget (p95):
  edge      8 ms   (TLS resumption + WAF)
  auth      2 ms   (JWKS cached; p99 15 ms on refresh)
  route     1 ms   (hash lookup + cached discovery)
  service   120 ms (route class dependent)
  shaping   3 ms   (problem details, headers)
  ---------------------
  gateway contribution = 14 ms; gateway total = 14 ms

route classes:
  interactive   service budget  120 ms, gateway deadline 15 ms to service
  batch         service budget 2000 ms, gateway deadline 60 ms to service
  streaming     service budget   30 ms, gateway deadline 12 ms to service
```
**Deliverable:** the budget table, the measured p95 per stage, and the variance
report against it. State any route class that cannot meet its budget rather than
quietly widening it.

### Step 2: Authentication Federation

Four credential types with genuinely different requirements:

| Credential | Used by | Verification |
|-----------|---------|--------------|
| OIDC JWT (IdP A) | first-party web/mobile | JWKS, refresh on unknown kid |
| OIDC JWT (IdP B) | enterprise SSO (400 tenants) | JWKS, separate issuer/audience |
| API key (legacy) | enterprise tenants | hashed lookup + rotation |
| mTLS client cert | service-to-service and some partners | terminated at the edge |

Requirements:
- Key lookup must not require a database round trip per request. Keep a
  credential cache with a bounded TTL and an explicit invalidation path for
  revocation.
- **Revocation** is the hard part: a JWT is valid until it expires. Define
  the maximum token lifetime, and document the revocation latency guarantee
  honestly (usually "up to token TTL").
- Legacy API key rotation without downtime: accept old and new for an overlap
  window, then retire the old one. Instrument the overlap usage so you know when
  it is safe to cut.

**Required tests:** each credential type accepted correctly; each rejected
when malformed; unknown `kid` triggers exactly **one** JWKS fetch under
concurrent load; and identity-provider outage for 5 minutes does not fail
requests (cache serves).

### Step 3: Routing and Service Discovery

- Route table pushed, not fetched: **no runtime dependency on a config
  service**. Rolling changes with a validation step (reject a config that would
  break an existing route).
- Discovery cached with a static fallback table. A discovery outage must not
  stop routing.
- Per-service: connect timeout, total timeout, concurrency limit, breaker
  thresholds. All tuned per dependency, not globally.
- **Header hygiene**: a deny-list of inbound identity headers, enforced by a
  test that runs against every route on every deploy.

**Required:** a config-change drill that pushes a bad config, verifies it is
rejected before propagation, and verifies a good config reload causes no
error spike.

### Step 4: Aggregation for First-Party Mobile Only

Partner APIs get **no** BFF (they call services through the gateway, one route
at a time). Mobile gets a BFF for the home screen.

- Declare per-field criticality. Home screen: profile critical, orders critical,
  recommendations optional.
- Per-field timeouts and a bounded aggregate deadline.
- Measured fan-out cost: 12,000 rps with an average fan-out of 4 means 48,000
  downstream connections. Size pools accordingly with a **concurrency limit per
  downstream**, not a fixed pool.

**Deliverable:** the criticality matrix, per-field timeout table, and the
measured connection budget per downstream service.

### Step 5: Rate Limiting and Quotas (Platform-Wide Policy)

One policy table, signed off by product and security (see
`11-rate-limiting-design` for the algorithms):

| Route class | Key | Algorithm | Limit | Fail mode |
|-------------|-----|-----------|-------|-----------|
| `/auth/*` | user + IP | fixed window | 5/min | **fail closed** |
| Interactive API | API key | token bucket | plan rate | local fallback |
| Batch/export | tenant | sliding window | plan rate | **fail closed** |
| Internal | service ID | concurrency | pool size | local fallback |
| Partner | partner ID | token bucket | contract | **fail closed** |

Two tiers, with the local limit derived as `ceil(global / instances) * 1.2`.
Alerts on partner quota consumption so sales can engage before a customer is
throttled.

### Step 6: Observability and Cardinality Discipline

Metrics, all with **bounded cardinality**:

- Per route template: rate, errors, duration percentiles.
- Per downstream service: rate, errors, duration percentiles, pool utilisation.
- Per stage: edge, auth, route, aggregate.
- Per credential type: auth successes/failures by reason.
- Breaker state, rate-limit rejections, in-flight concurrency.

**Hard requirement:** no metric label may contain a raw path, user id, tenant
id, API key, or request id. Enforce it with an automated cardinality check in
CI: reject any metric whose label cardinality exceeds a threshold at startup.
This is the control that stops one route from taking down the metrics backend.

Trace context generated at the edge and propagated to every downstream call, so
a request's identity survives the whole path.

### Step 7: Failure Drills

1. **Identity provider outage (5 min).** Verify cached JWKS keeps serving, no
   401 storm, and new-tenant onboarding is degraded (documented acceptable).
2. **Downstream service 3 s latency, no errors.** Verify the breaker does *not*
   open, the concurrency limit protects the gateway, and load is shed with
   `503` rather than queued. This is the drill that proves concurrency limits
   are load-bearing.
3. **Service discovery unavailable.** Verify the static fallback keeps routing
   and measure the staleness cost.
4. **Metrics cardinality attack.** Deploy a build that labels a metric with a
   request id. Verify the CI cardinality check rejects it before merge, and
   separately verify what happens when it bypasses CI (document the blast
   radius).
5. **Bad config push.** Verify validation rejects it and the previous config
   continues serving.
6. **Traffic spike 3x.** Verify autoscaling on concurrency and p95 latency (not
   CPU), and that the spike does not cause a retry storm.

### Deliverables

1. Latency budget table, measured per stage, with a variance report.
2. Authentication federation with revocation guarantees and the four test
   groups from Step 2.
3. Pushed config with validation, cached discovery with static fallback, and the
   header-hygiene test suite.
4. Mobile BFF criticality matrix, timeouts, and measured connection budget.
5. Rate-limit policy table with two-tier derivation and quota alerting.
6. Metrics with an **automated cardinality check in CI** and trace propagation.
7. Six drill reports with measured numbers, especially drill 2 (the concurrency
   limit proof) and drill 4 (the cardinality blast radius).
8. Runbooks: key rotation, revocation, bad config rollback, identity provider
   outage, partner quota breach.

### Grading Rubric

| Dimension | Weak | Strong |
|-----------|------|--------|
| Budget | "Added ~5 ms" | Per-stage table measured and agreed with services |
| JWKS | Cached with fixed TTL | Refresh-on-unknown-kid, single-flight, outage drill |
| Revocation | Not addressed | TTL and revocation latency stated honestly |
| BFF | Everywhere | First-party only; criticality matrix; connection budget |
| Limits | Global | Per-route-class table with fail modes and derivation |
| Cardinality | "Be careful" | CI-enforced check plus a documented blast radius |
| Discovery | Cached only | Cached with static fallback, drill-verified |

## Sourced field notes (fetched Oct 2026 — verify before citing)

- RFC 9110 — *HTTP Semantics*: the normative definitions this gateway's
  behaviour is built on — status codes (`401`, `403`, `404`, `429`, `502`,
  `503`), method semantics, `Retry-After`, and hop-by-hop header rules in
  section 7.6.1. Cite sections when arguing for a routing or error contract.
  https://www.rfc-editor.org/rfc/rfc9110.html
- RFC 9111 — *HTTP Caching*: validators (`ETag`, `Last-Modified`),
  `Cache-Control`, and revalidation semantics; the reference for which gateway
  responses are safe to cache and which must always revalidate.
  https://www.rfc-editor.org/rfc/rfc9111.html

Both are stable standards. Re-verify the current standardised `RateLimit-*`
response header field names and formats before shipping them — header naming in
this area has been standardised after much existing blog guidance was written.
Also confirm your CDN or load balancer's actual header-stripping behaviour,
because the identity-header control in Step 3 depends on it.