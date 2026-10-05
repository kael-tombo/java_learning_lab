# HTTP Protocol - REAL WORLD PROJECT

## Project: GateLine — an HTTP API gateway in front of a fragile legacy upstream

The company has a 12-year-old order system that speaks HTTP/1.0, cannot be modified, and
is deployed behind a CDN. This gateway is the compatibility layer: it terminates modern TLS,
normalises hop-by-hop and framing behaviour, enforces policy, and gives the legacy upstream
a clean, predictable request. Most production HTTP incidents are exactly this problem.

### Architecture

```
  Clients ──HTTPS──▶ CDN/WAF ──▶ GateLine (Spring Cloud Gateway / Netty) ──▶ Legacy Order System
                                    │                       │                  (HTTP/1.0, no TLS)
                                    │                       │
                     ┌──────────────┴────────┐              └─ request/response translation
                     │ Cross-cutting:         │
                     │  - auth (JWT/OAuth2)   │   Normalisation rules applied here:
                     │  - rate limit / quota  │   - strip hop-by-hop headers
                     │  - WAF rule subset     │   - drop Accept-Encoding from upstream
                     │  - request/response log│   - add Host, X-Forwarded-*, Forwarded
                     │  - circuit breaker     │   - strip Server, Date duplicates
                     └───────────────────────┘
```

### Implementation

Header normalisation, which is the gateway's most security-relevant job:

```java
@Component
class HeaderNormalizer implements GlobalFilter, Ordered {
    // Hop-by-hop headers apply to a SINGLE connection, not end to end. A gateway that
    // forwards them can make the next hop mis-frame a message - the request smuggling class.
    private static final Set<String> HOP_BY_HOP = Set.of(
            "connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
            "te", "trailer", "transfer-encoding", "upgrade");

    @Override
    public Mono<Void> filter(ServerHttpRequest req, ServerHttpResponse res) {
        ServerHttpRequest filtered = req.mutate()
            .headers(h -> HOP_BY_HOP.forEach(h::remove))
            .header("X-Forwarded-Proto", tlsScheme(req))
            .header("X-Forwarded-Host", req.getHeaders().getFirst("Host"))
            .header("X-Request-Id", requestId())       // correlation across all hops
            .build();
        // Accept-Encoding negotiation is the gateway's job, not the upstream's. Forwarding the
        // client's header blindly produces responses the gateway cannot correctly cache.
        return chain.filter(filtered);
    }
}
```

Response transformation for an HTTP/1.0 upstream, plus security headers:

```java
@Component
class UpstreamResponseTransformer implements GlobalFilter {
    @Override
    public Mono<Void> filter(ServerWebExchange ex, GatewayFilterChain chain) {
        return chain.filter(ex).transform(res -> {
            HttpHeaders h = res.getHeaders();
            h.remove("Server");                        // do not advertise the upstream stack
            h.set("Strict-Transport-Security", "max-age=31536000; includeSubDomains; preload");
            h.set("X-Content-Type-Options", "nosniff");
            h.set("Content-Security-Policy", "default-src 'none'; frame-ancestors 'none'");
            h.set("Referrer-Policy", "no-referrer");
            // Normalise the legacy error shape into a problem+json the clients can handle uniformly.
            if (res.getStatusCode().isError() && !h.containsKey("Content-Type")) {
                h.set("Content-Type", "application/problem+json");
            }
            return res.writeWith(upstreamBodyResolvingGzip(h));
        });
    }
}
```

Policy enforcement at the edge, where a bad request is cheapest to reject:

```java
@Bean
SecurityFilterChain edge(HttpSecurity http) throws Exception {
    return http
        .csrf(AbstractHttpConfigurer::disable)                    // Bearer/API gateway
        .sessionManagement(s -> s.sessionCreationPolicy(STATELESS))
        .authorizeHttpRequests(a -> a
            .requestMatchers("/actuator/health").permitAll()
            .requestMatchers(HttpMethod.POST, "/orders/**").hasAuthority("SCOPE_orders.write")
            .anyRequest().hasAuthority("SCOPE_orders.read"))
        .oauth2ResourceServer(o -> o.jwt(Customizer.withDefaults()))
        .headers(h -> h.frameOptions(deny())
                     .contentTypeOptions(Customizer.withDefaults()))
        .build();
}

// Body-size and content-type guards: reject before the upstream allocates anything.
@Bean
RouteLocator guardedRoutes(RouteLocatorBuilder b, RequestSizeFilter sizeFilter) {
    return b.route("orders", r -> r.path("/orders/**")
        .filters(f -> f.addRequestHeader("X-Gateway", "gateline")
                     .filter(sizeFilter.max(1_048_576))     // 1 MiB: order payloads are small
                     .filter(contentTypeGuard))
        .uri("http://legacy-order-system.internal"));
}
```

Resilience, because the upstream genuinely cannot be changed:

```java
@Bean
Retry filter() {
    // Retry only idempotent methods. Retrying a POST can double-create an order, which is
    // a data-integrity incident rather than an availability improvement.
    return Retry.backoff(3, Duration.ofMillis(200))
        .filter(t -> t instanceof TimeoutException || t instanceof ConnectException)
        .doOnRetry(signal -> metrics.counter("upstream.retry",
                "method", signal.request().getMethod().name(), "cause", signal.failure().getClass().getSimpleName()).increment())
        .doOnRetry(signal -> log.warn("upstream retry {} attempt={}", signal.request().getPath(), signal.totalRetries()));
}

@Bean
CircuitBreaker breaker() {
    return CircuitBreaker.of("legacy-orders", breakerConfig)
        .fallbackWhen(signal -> {
            metrics.counter("upstream.fallback").increment();
            // 503 with a machine-readable code, not a 200 with an error body.
            return serverResponse(HttpStatus.SERVICE_UNAVAILABLE).body(problem("UPSTREAM_UNAVAILABLE"));
        });
}
```

### Non-functional requirements

- **Latency**: added gateway latency p95 under 8 ms, p99 under 20 ms, measured at the edge.
- **Framing safety**: hop-by-hop headers stripped, `Content-Length`/`Transfer-Encoding`
  conflict rejected, and a smuggling-focused test in CI.
- **Compatibility**: legacy HTTP/1.0 upstream requires no changes; gateway owns TLS 1.2+,
  HTTP/2 to clients, and all modern header hygiene.
- **Resilience**: circuit breaker, timeouts sized below the client's patience, retries only
  on idempotent methods, and a documented degraded mode (read-only, or a 503 contract).
- **Observability**: `X-Request-Id` propagated to the upstream, latency/error metrics split
  by route and status, and upstream-vs-gateway error attribution in dashboards.
- **Security**: JWT verification at the edge, per-client rate limits, request size caps,
  and security headers on every response including errors.
- **Rollout**: shadow mode (compare decisions without enforcing) before blocking traffic,
  so a gateway rule cannot take down production on a Friday.

### Sourced field notes (fetched Oct 2026 — verify before citing)
- RFC 9112 specifies HTTP/1.1 message syntax and framing, including the rule that
  `Transfer-Encoding` overrides `Content-Length` and the `Host` field requirement -
  the basis for the normalisation and smuggling defences above.
  https://www.rfc-editor.org/info/rfc9112/
- MDN HTTP response status documentation is the reference for the status code and
  redirect semantics the gateway normalises for clients.
  https://developer.mozilla.org/en-US/docs/Web/HTTP/Status

## Deliverables

- [x] Hop-by-hop header stripping plus `X-Forwarded-*` and `X-Request-Id` propagation
- [x] Response normalisation: security headers, `Server` removal, problem+json errors
- [x] Edge authentication and authorization with scope-based route rules
- [x] Request size limit and content-type guard before upstream allocation
- [x] Circuit breaker with a machine-readable degraded-mode contract
- [x] Idempotent-only retry with metrics distinguishing retry from failure
- [x] Request-smuggling regression tests in CI
- [x] Shadow-mode rollout process before enforcement
