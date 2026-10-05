# API Gateways - REAL WORLD PROJECT

## Project: MerchantHub — a public API gateway for 40,000 merchants and 15 partner integrations

The company sells payments, invoicing, and payouts through an API. Partners integrate
directly; there is no client app team to hide integration complexity behind. The gateway
is the product surface, so it must be predictable, well-documented, and boring.

### Architecture

```
  Partners (15)          Public clients (browser/mobile)        Internal services
        │                        │                                   │
        └────────────────────────┴────────────────┬──────────────────┘
                                                 ▼
  ┌───────────────── MerchantHub Edge ────────────────────────────────┐
  │  DNS/WAF │ TLS 1.3 │ request signing │ per-partner quota          │
  │  routes: /v2/payments /v2/payouts /v2/invoices /v2/refunds       │
  │  per-route: timeout, breaker, retry policy, rate limit, idempotency│
  └──────────────────────────┬────────────────────────────────────────┘
                             ▼
   payments-svc   payouts-svc   ledger-svc   invoice-svc   compliance-svc
        │              │             │             │              │
        └──────────────┴─────────────┴─────────────┴──────────────┘
              Postgres (separate schemas) + Kafka outbox
```

### Implementation

Per-partner configuration as data, since onboarding is weekly and quotas differ:

```java
@Service
class PartnerPolicyRegistry {
    // A partner's contract is: plan tier, allowed routes, rate/burst limits, monthly
    // volume cap, whether idempotency is mandatory, and IP allowlist. All of it data,
    // changeable by a support-approved workflow, versioned and auditable.
    record PartnerPolicy(String partnerId, PlanTier tier, Set<String> allowedRoutes,
                         int ratePerSecond, int burst, long monthlyCap,
                         boolean idempotencyRequired, Set<String> allowedCidrs,
                         Instant effectiveFrom, long version) {}

    RoutePolicy policyFor(String partnerId, String route) {
        var p = registry.require(partnerId);
        // Route-level authorisation, not just partner-level. A partner entitled to payments
        // must not thereby gain payouts, even though both are under the same API key.
        if (!p.allowedRoutes().contains(route))
            throw new RouteNotEntitledException(partnerId, route);
        return RoutePolicy.of(route, p);
    }
}
```

Idempotency enforced at the gateway for money-moving routes, because retrying a payment
is a financial incident:

```java
@Component
class IdempotencyGate implements GlobalFilter, Ordered {
    @Override public Mono<Void> filter(ServerWebExchange ex, GatewayFilterChain chain) {
        String route = routeOf(ex);
        if (!IDEMPOTENT_REQUIRED_ROUTES.contains(route)) return chain.filter(ex);
        String key = ex.getRequest().getHeaders().getFirst("Idempotency-Key");
        if (key == null)
            // Fail closed. Rejecting is far cheaper than discovering a double charge.
            return problem(ex, HttpStatus.BAD_REQUEST, "idempotency_key_required");
        // Bind the key to the request body fingerprint: the same key with a different body
        // is a client bug that would otherwise silently return the wrong original result.
        return idempotencyStore.reserve(key, sha256(bodyOf(ex)))
            .flatMap(reservation -> {
                if (reservation.isReplay())
                    return cachedOrConflict(ex, reservation);   // 200 replay, or 409 on body mismatch
                ex.getAttributes().put(IDEMPOTENCY_KEY, key);
                return chain.filter(ex).doOnSuccess(v -> idempotencyStore.commit(key, statusOf(ex)))
                                     .doOnError(e -> idempotencyStore.release(key));
            });
    }

    @Override public int getOrder() { return -100; }   // before routing, so replays never reach the service
}
```

Circuit breakers and timeouts configured per route, based on each dependency's real
latency profile rather than one global default:

```java
@Bean
RouteLocator perRouteResilience(RouteLocatorBuilder b) {
    return b.routes()
        .route("payments", r -> r.path("/v2/payments/**")
            .filters(f -> f
                // payments-svc p99 is 220ms; the client budget is 1500ms, so 1200ms leaves
                // room for one retry without breaching the client's own timeout.
                .filter(requestTimeout(Duration.ofMillis(1200)))
                .filter(circuitBreaker("payments-svc", 50))
                // Retrying a create is only safe BECAUSE idempotency is enforced above.
                .filter(retryOn(DEADLINE_EXCEEDED, UNAVAILABLE, maxAttempts(2), perTry(400)))
                .uri("lb://payments-svc"))
        .route("payouts", r -> r.path("/v2/payouts/**")
            .filters(f -> f
                .filter(requestTimeout(Duration.ofMillis(3000)))   // bank rails are slow
                .filter(circuitBreaker("payouts-svc", 30))
                .filter(retryOn(UNAVAILABLE, maxAttempts(3), perTry(1000)))  // backoff between attempts
                .uri("lb://payouts-svc"))
        .build();
}
```

Publishing to partners, where breaking a partner is a commercial event:

```java
/**
 * Change management for a public API. The gateway makes versioning cheap: a new version is
 * a new route set, and v1 stays alive until a measured sunset, not a hopeful date.
 */
class ApiVersionLifecycle {
    void deprecate(String version) {
        versions.markDeprecated(version, Instant.now(),
                deprecationHeaders(version));   // Deprecation, Sunset, Link to migration guide
        // Per-partner usage is already tracked, so the sunset is a conversation about
        // specific partners' data, not a guess.
        support.notifyPartnersOnVersion(version, usageReport(version));
    }

    void retire(String version) {
        requireAllPartnersMigrated(version);    // hard precondition, cannot be bypassed
        routes.disable(version);
        audit.versionRetired(version, approver(), evidenceOfMigration());
    }
}
```

Sandbox parity, because partner integration failures are expensive to debug:

```java
@Configuration
class SandboxRouting {
    // Sandbox runs the SAME gateway, SAME filters, SAME policies shape, with fake
    // adapters behind the service interfaces. Partners can test failure modes
    // (429, 409, 503) that production will never let them produce on demand.
    @Bean
    RouteLocator sandboxRoutes(RouteLocatorBuilder b, SandboxFactory sandbox) {
        return b.route("sandbox", r -> r.path("/sandbox/v2/**")
            .filters(f -> f.filter(authFilter()).filter(rateLimiterFilter("sandbox", perSecond(5), burst(10)))
                             .filter(sandboxEnforceFailureSemantics()))   // can inject 429/409/503
            .uri(sandbox.baseUrl()));
    }
}
```

### Non-functional requirements

- **Availability**: 99.95% edge availability. The gateway is deployed multi-region with
  active/active and health-based failover of the whole edge, not just the backend.
- **Latency**: gateway overhead p50 under 6 ms, p99 under 20 ms. Measured per filter, and
  any filter exceeding 3 ms at p99 must justify itself in review.
- **Idempotency**: mandatory on all money-moving routes, with body-fingerprint binding and
  a 24-hour key retention. Tested by replaying a real partner request.
- **Quotas**: per-partner rate, burst, and monthly cap, with `RateLimit-*` headers on every
  response, and a documented escalation path for a partner hitting a legitimate ceiling.
- **Change safety**: shadow-mode rollout for new gateway rules — compare decisions without
  enforcing — then a percentage ramp with an automatic rollback trigger on error rate.
- **Security**: request signing with nonce and clock-skew window, IP allowlist per partner,
  WAF rules at the edge, and partner-facing IP rotation runbook.
- **Observability**: per-route, per-partner latency and error rate; quota utilisation;
  idempotency replay rate (a spike means a partner has a retry bug); breaker state changes;
  and a partner-facing status page fed by the same signals.
- **DX**: OpenAPI per version, a sandbox with injectable failure modes, runnable examples,
  and a self-service partner console for keys, quotas, and usage.

### Sourced field notes (fetched Oct 2026 — verify before citing)
- MDN HTTP rate limiting/429 guidance and the `Retry-After` header define the response
  contract partners need in order to back off correctly instead of retry-looping.
  https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/429
- Spring Cloud Gateway documentation describes the route and filter model, including
  per-route circuit breakers, retries, and request-size limits used above.
  https://docs.spring.io/spring-cloud-gateway/reference/

## Deliverables

- [x] Per-partner, per-route policy registry with entitlement checks and versioning
- [x] Gateway-enforced idempotency with request-body fingerprint binding and 409 on mismatch
- [x] Per-route timeouts, breakers, and retry policies justified by measured dependency latency
- [x] Multi-region active/active edge with health-based failover
- [x] API version lifecycle with measured per-partner sunset and a hard migration precondition
- [x] Sandbox parity including injectable 429/409/503 for partner testing
- [x] Shadow-mode rollout and automatic rollback triggers for gateway rule changes
- [x] Partner-facing status page, usage console, and OpenAPI docs per version
