# API Gateways - MINI PROJECT

## Project: GateHouse — a routing gateway with auth, rate limiting, and composition

Build a gateway that routes by path, enforces JWT auth, rate limits per client, and
aggregates three backend services into one product page response. Measure the cost of
every filter you add.

### Architecture

```
  Client ──▶ GateHouse
             │
             ├─ 1. Auth filter        verify JWT, extract client identity + scopes
             ├─ 2. Rate limit filter  per-client token bucket, 429 + Retry-After
             ├─ 3. Route filter       /api/catalog/* -> catalog-svc
             │                        /api/orders/*  -> orders-svc
             ├─ 4. Response cache     short TTL for idempotent GETs
             └─ 5. Audit filter       log client, route, status, latency
                     │
        ┌────────────┼─────────────┬──────────────┐
        ▼            ▼             ▼              ▼
   catalog-svc   orders-svc    inventory-svc   pricing-svc

  Composition endpoint (one client call instead of four):
    GET /api/catalog/cards/{sku}
        -> fetch catalog + inventory + pricing + review-count in PARALLEL
        -> merge into one ProductCard
        -> explicit partial-failure semantics
```

### Implementation

The gateway filter chain, with order documented because order is a correctness property:

```java
@Configuration
class GatewayRoutes {
    @Bean
    RouteLocator customRoutes(RouteLocatorBuilder builder) {
        return builder.routes()
            // Composition lives in its own route so it can have its own timeouts, its own
            // rate limit, and its own failure policy - not the default of everything else.
            .route("product-card", r -> r.path("/api/catalog/cards/{sku}")
                .filters(f -> f.filter(authFilter())
                             .filter(rateLimiterFilter("catalog-cards", perSecond(50), burst(100)))
                             .filter(auditFilter())
                             .filter(requestTimeout(Duration.ofMillis(800)))
                             .filter(circuitBreaker("cards", 40))
                             .uri("lb://catalog-svc"))
            .route("catalog", r -> r.path("/api/catalog/**")
                .filters(f -> f.filter(authFilter())
                             .filter(rateLimiterFilter("catalog", perSecond(500), burst(1000)))
                             .filter(auditFilter())
                             .uri("lb://catalog-svc"))
            .build();
    }
}
```

Per-client rate limiting, which is the requirement people get wrong:

```java
@Component
class TokenBucketRateLimiter extends AbstractRateLimiter<RateLimiter> {
    private final Map<String, RateLimiter> limiters = new ConcurrentHashMap<>();

    private RateLimiter limiterFor(String id) {
        // Per client, not global. A global bucket means one noisy tenant starves everyone,
        // which is both a fairness bug and a trivially exploitable denial of service.
        return limiters.computeIfAbsent(id, k -> RateLimiter.create(rate));
    }

    @Override
    protected Mono<Response> isAllowed(String id) {
        RateLimiter limiter = limiterFor(id);
        if (limiter.tryAcquire(1)) {
            return Mono.just(Response.create().build());
        }
        long retryAfter = Duration.ofNanos((long) (limiter.reserve(1).waitTimeNanos())).toSeconds() + 1;
        return Mono.just(Response.create()
                .status(HttpStatus.TOO_MANY_REQUESTS)
                // Tell the client when to come back. A 429 without Retry-After forces
                // clients into blind retry loops, which is how a rate limit becomes an outage.
                .header("Retry-After", String.valueOf(retryAfter))
                .header("X-RateLimit-Limit", String.valueOf(rate))
                .header("X-RateLimit-Remaining", "0")
                .body(BodyInserters.fromValue(problemJson("rate_limit_exceeded",
                        "limit " + rate + "/s, retry in " + retryAfter + "s"))));
    }

    // Bound the map: without eviction, one request per spoofed client id is a memory leak.
    @Scheduled(fixedDelay = 60_000)
    void evictIdle() {
        limiters.entrySet().removeIf(e -> e.getValue().tryAcquire(1) && e.getValue().tryAcquire(1));
    }
}
```

Composition with explicit, per-dependency failure semantics — the decision that matters:

```java
@Component
class ProductCardComposer {
    /**
     * Aggregation failure semantics must be chosen per field, not per request. A page that
     * is 90% useful and 10% wrong is far better than a 500, PROVIDED the missing part is
     * clearly marked. So: required fields fail fast; optional fields degrade with a
     * sentinel the client can detect. Never silently omit - a missing price that looks
     * like a free product is a business incident.
     */
    Mono<ProductCard> compose(String sku, String clientId) {
        Mono<Product>       product    = catalogClient.get(sku);            // required
        Mono<Stock>         stock      = inventoryClient.get(sku);          // required
        Mono<Price>         price      = pricingClient.get(sku);            // required - fail fast
        Mono<List<Review>>  reviews    = reviewClient.forProduct(sku);      // optional
        Mono<ReviewStats>   stats      = reviewClient.stats(sku);           // optional

        // All calls start together. A sequential chain here is the single biggest
        // aggregation mistake: latency becomes the SUM of all dependencies.
        return Mono.zip(product, stock, price, reviews.defaultIfEmpty(List.of()), stats.defaultIfEmpty(REVIEW_STATS_UNKNOWN))
            .map(t -> new ProductCard(
                    t.getT1().name(), price, stock.available(),
                    t.getT4().averageRating(), t.getT4().count(),
                    reviewsRecovered(t.getT3(), sku),
                    degradedFields(sku, t.getT3(), t.getT5())))
            // requiredFailed: 503 (dependency down) rather than 500 (we are broken)
            .onErrorMap(e -> e instanceof DependencyException de
                    ? new UpstreamUnavailableException(de.dependency(), de) : e);
    }

    private List<Review> reviewsRecovered(List<Review> reviews, String sku) {
        if (reviews == null) {                       // the .onErrorResume case
            degraded.set(sku, "reviews");
            metrics.counter("gateway.degraded", "field", "reviews");
            return List.of();                        // empty, with a degraded marker
        }
        return reviews;
    }
}
```

Circuit breaker per dependency, with the right failure threshold semantics:

```java
@Bean
CircuitBreaker catalogBreaker() {
    return CircuitBreaker.of("catalog-svc",
        CircuitBreakerConfig.custom()
            .failureRateThreshold(0.5)        // open if 50% of calls fail
            .slowCallRateThreshold(0.8)       // or 80% exceed the slow-call duration
            .slowCallDurationThreshold(Duration.ofMillis(400))
            .minimumNumberOfCalls(20)         // never trip on a small sample: this is the
            .waitDurationInOpenState(Duration.ofSeconds(15))  // difference between a real
            .permittedNumberOfCallsInHalfOpenState(5)         // breaker and a random outage
            .slidingWindowSize(50)
            .build());
}
```

Latency cost measurement, so each filter can justify its place:

```java
@Bean
LatencyAttributionFilter latencyAttribution() {
    // Per-filter timing, recorded as a header and as a metric. When the gateway adds 12ms,
    // the team must be able to say WHICH filter is responsible.
    return (exchange, chain) -> {
        var timings = new ConcurrentHashMap<String, Long>();
        exchange.getAttributes().put("filterTimings", timings);
        return chain.filter(exchange).doFinally(signal -> {
            timings.forEach((filter, ns) -> metrics.timer("gateway.filter.latency",
                    "filter", filter, "route", routeName(exchange)).record(ns, NANOSECONDS));
        });
    };
}
```

### Test It

```java
@Test void routesByPathAndPreservesThePathSuffix() {
    mockMvc.perform(get("/api/catalog/products/p-123"))
           .andExpect(status().isOk())
           .andExpect(jsonPath("$.id").value("p-123"));
}

@Test void rateLimitIsPerClientNotGlobal() {
    for (int i = 0; i < 100; i++)
        mockMvc.perform(get("/api/catalog/x").header("Authorization", "Bearer " + tokenFor("client-A")));
    // client-B is unaffected by client-A exhausting its budget
    mockMvc.perform(get("/api/catalog/x").header("Authorization", "Bearer " + tokenFor("client-B")))
           .andExpect(status().isOk());
}

@Test void throttledResponseIncludesRetryAfter() {
    var res = exhaustLimit("client-A");
    assertThat(res.getStatus()).isEqualTo(429);
    assertThat(res.getHeader("Retry-After")).isNotNull();
    assertThat(res.getHeader("X-RateLimit-Remaining")).isEqualTo("0");
}

@Test void compositionRunsDependenciesInParallel() {
    // Wall-clock must be close to the SLOWEST dependency, not the sum.
    var wall = timeToCompose(product_300ms, inventory_300ms, pricing_300ms);
    assertThat(wall).isLessThan(600);       // sequential would be ~900
}

@Test void requiredDependencyFailsFastWith503() {
    mockPricing.down();
    mockMvc.perform(get("/api/catalog/cards/p-1"))
           .andExpect(status().isServiceUnavailable())
           .andExpect(jsonPath("$.detail").value(containsString("pricing")));
}

@Test void optionalDependencyDegradesWithoutFailing() {
    mockReviews.down();
    var res = mockMvc.perform(get("/api/catalog/cards/p-1"))
                     .andExpect(status().isOk())
                     .andExpect(jsonPath("$.reviews").isEmpty())
                     .andExpect(jsonPath("$.degradedFields").value(containsString("reviews")));
    // A missing price would be a business incident; a missing review list is not.
    assertThat(res.getContentAsString()).contains("\"degradedFields\"");
}

@Test void breakerOpensAfterSustainedFailureAndRecovers() {
    mockPricing.down();
    repeat(30, () -> get("/api/catalog/cards/p-1"));      // trips
    assertThat(breaker("pricing").state()).isEqualTo(OPEN);
    mockPricing.up();
    Thread.sleep(15_500);
    assertThat(breaker("pricing").state()).isEqualTo(HALF_OPEN);
    repeat(6, () -> get("/api/catalog/cards/p-1"));
    assertThat(breaker("pricing").state()).isEqualTo(CLOSED);
}
```

## Deliverables

- [ ] Config-driven routing with per-route filters, timeouts, and rate limits
- [ ] Documented filter order: auth, then rate limit, then route work, then audit
- [ ] Per-client token bucket with `Retry-After` and `X-RateLimit-*` headers
- [ ] Idle-bucket eviction so the limiter map cannot grow unbounded
- [ ] Composition endpoint fetching dependencies in parallel, with a timing test
- [ ] Per-field failure semantics: required fails fast, optional degrades with a marker
- [ ] Circuit breaker per dependency with a minimum call count and half-open probing
- [ ] Per-filter latency attribution reported as metrics
- [ ] Tests: routing, per-client isolation, parallel composition, degradation, breaker recovery
