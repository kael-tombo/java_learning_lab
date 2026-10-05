# CORS & Headers - REAL WORLD PROJECT

## Project: CommerceEdge — a multi-tenant storefront API serving many registered front ends

One commerce platform, many consumers: a first-party SPA, a partner portal, two legacy
checkout pages on legacy origins, a mobile webview, and a marketplace widget embedded in
third-party sites. Every new marketing domain becomes a CORS request. Meanwhile an
Akamai/CloudFront edge terminates TLS and sets some headers itself.

### Architecture

```
  app.shop.example           (first-party SPA, cookie session)
  partner.example.com        (B2B portal, Bearer token)
  checkout-v1.example.com    (legacy, still session + iframe)  -> needs migration
  m.shop.example.com         (webview, none)
  <third-party marketplace>  (widget embed, must be tightest)

        ▼ all reach the edge
  ┌──────────────────────────────────────────────────────┐
  │ CDN / WAF: TLS 1.2+, HSTS, WAF rules, bot management │
  │  -> CORS decided at EDGE from signed config           │
  └────────────────────────┬─────────────────────────────┘
                           ▼
             ┌─────────────────────────────┐
             │ Commerce API (Spring Boot)  │
             │  CorsFilter from same config│
             │  duplicate headers stripped │
             └─────────────────────────────┘
                           ▼
             Origin registry in Postgres, changed only via
             an audited admin flow -> signed edge config push
```

### Implementation

The allow-list is data, not code, because it changes weekly. A signed config is pushed to
the edge and reloaded by the app without a deploy:

```java
@Component
class DynamicCorsPolicy implements CorsConfigurationSource {
    private final OriginRegistry registry;     // Postgres, admin-audited
    private final AtomicReference<CorsConfiguration> current = new AtomicReference<>();
    private final MeterRegistry metrics;

    public DynamicCorsPolicy(OriginRegistry r, MeterRegistry m) {
        this.registry = r; this.metrics = m;
        reload();
    }

    @Scheduled(fixedDelay = 30_000)
    void reload() {
        var cfg = new CorsConfiguration();
        cfg.setAllowedOrigins(registry.activeOrigins());                 // exact strings
        cfg.setAllowedMethods(List.of("GET","POST","PUT","PATCH","DELETE","OPTIONS"));
        cfg.setAllowedHeaders(List.of("Authorization","Content-Type","X-Request-Id"));
        cfg.setExposedHeaders(List.of("X-Request-Id"));
        cfg.setAllowCredentials(true);
        cfg.setMaxAge(Duration.ofMinutes(30));
        current.set(cfg);
    }

    @Override public CorsConfiguration getCorsConfiguration(HttpServletRequest req) {
        CorsConfiguration cfg = current.get();
        // Per-origin tightening: the third-party embed never gets credentials.
        String origin = req.getHeader("Origin");
        if (origin != null && registry.isUntrustedEmbed(origin)) cfg.setAllowCredentials(false);
        if (origin != null) metrics.counter("cors.origin.requests", "origin", origin).increment();
        return cfg;
    }
}
```

Header ownership is explicit, so app and edge never emit conflicting values. The edge is
authoritative for transport-level headers; the app owns CSP because only it knows the page:

```java
@Bean
SecurityFilterChain chain(HttpSecurity http) throws Exception {
    return http
        .cors(cors -> cors.configurationSource(dynamicCorsPolicy))
        .headers(h -> h
            // The EDGE sets HSTS and nosniff. Emitting them again here risks a
            // duplicate-header mismatch where the browser takes the weaker value.
            .httpStrictTransportSecurity(StrictHttpFirewallHeaderWriter::disable)
            .contentTypeOptions(Customizer.withDefaults())
            .frameOptions(FrameOptionsConfig::disable)   // edge sends frame-ancestors instead
            .referrerPolicy(rp -> rp.policy(ReferrerPolicy.STRICT_ORIGIN_WHEN_CROSS_ORIGIN)))
        .addFilterAfter(new StripDuplicateSecurityHeaders(), HeaderWriterFilter.class)
        .build();
}

/** One owner per header. Removes app duplicates so the edge value cannot be weakened. */
class StripDuplicateSecurityHeaders extends OncePerRequestFilter {
    private static final List<String> EDGE_OWNED =
        List.of("Strict-Transport-Security", "X-Content-Type-Options", "Content-Security-Policy");

    @Override protected void doFilterInternal(HttpServletRequest req, HttpServletResponse res, FilterChain c) {
        EDGE_OWNED.forEach(h -> res.setHeader(h, null));   // null removes
        chain: c.doFilter(req, res);
    }
}
```

Per-surface CSP, since one policy cannot serve an embedded widget and an admin console:

```java
Map<String, String> cspBySurface() {
    return Map.of(
      "storefront", "default-src 'self'; script-src 'self' 'nonce-{n}'; " +
                     "connect-src 'self' https://payments.example; frame-ancestors 'none'",
      "embed",      "default-src 'self'; script-src 'self' https://cdn.widgets.example; " +
                     "connect-src 'self'; frame-ancestors https://marketplaces.example " +
                     "https://partner.example",            // only these may embed us
      "admin",      "default-src 'none'; form-action 'self'; frame-ancestors 'none'");
}
```

### Non-functional requirements

- **Config change SLA**: a new legitimate storefront domain goes live in under 15 minutes
  via the audited registry, with no application deploy.
- **Change safety**: origin additions require two-person approval; removals take effect
  within 30 s (and immediately on the next config push).
- **Regression safety**: automated browser test per registered origin, run in CI, asserting
  ACAO exactness — an origin typo fails the build rather than production.
- **Observability**: CORS decision metrics per origin (allowed/denied), plus alerting on
  any single origin generating more than 5% of requests (possible scraping/abuse).
- **Migration**: `checkout-v1` is removed from the allow-list after its frame-ancestors
  issue is resolved; a dated entry in the runbook prevents indefinite exception creep.

### Sourced field notes (fetched Oct 2026 — verify before citing)
- MDN's CORS documentation describes the preflight mechanism and, critically, that CORS is
  a browser-enforced read restriction rather than a server-side access control.
  https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS
- OWASP Secure Headers Project lists recommended headers (CSP, HSTS, X-Content-Type-Options,
  Referrer-Policy, Permissions-Policy) and their purposes, matching the table above.
  https://owasp.org/www-project-secure-headers/

## Deliverables

- [x] Data-driven, signed origin registry with two-person approval for changes
- [x] Dynamic CORS config reloaded without redeploy, exact-match only
- [x] Per-surface CSP: storefront, embed, admin (embed constrained by `frame-ancestors`)
- [x] Untrusted-embed handling that withholds credentials
- [x] Single-ownership model for every security header across edge and app
- [x] CI browser tests asserting ACAO exactness for each registered origin
- [x] Metrics and alerting on per-origin request share
- [x] Exception expiry runbook for legacy origins
