# CORS & Headers - MINI PROJECT

## Project: DualOrigin — an API, an SPA, and a partner portal that must coexist

Serve one API from two legitimate browser origins (the SPA and the partner portal) plus
reject a hostile origin, and ship a full set of security headers. A second service on
another port reproduces the real cross-origin conditions.

### Architecture

```
  https://app.localhost:3000 (SPA)  ──preflight──▶  API :8080
  https://portal.partner.com       ──preflight──▶      /api/**
  https://evil.example            ──preflight──▶      (must fail: no ACAO)

  Simple GET  (no preflight)  ────────────────────▶  ACAO: https://app.localhost:3000
  Credentialed POST (cookies)  ───────────────────▶  exact origin + ACAC:true (no *)

  Response also carries: Strict-Transport-Security, Content-Security-Policy,
  X-Content-Type-Options: nosniff, Referrer-Policy, frame-ancestors via CSP
```

### Implementation

```java
@Configuration
class CorsConfig {

    @Bean
    CorsConfigurationSource corsConfigurationSource() {
        // Exact-match allow-list. Never endsWith()/contains() - "https://evil-app.localhost"
        // and "https://myapp.localhost.attacker.com" both defeat substring matching.
        Set<String> allowed = Set.of("https://app.localhost:3000", "https://portal.partner.com");
        CorsConfiguration cfg = new CorsConfiguration();
        cfg.setAllowedOrigins(allowed);                 // list, not "*" - we send credentials
        cfg.setAllowedMethods(List.of("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"));
        cfg.setAllowedHeaders(List.of("Authorization", "Content-Type", "X-Request-Id", "Idempotency-Key"));
        cfg.setExposedHeaders(List.of("X-Request-Id", "RateLimit-Remaining"));  // readable by JS
        cfg.setAllowCredentials(true);                  // forbids a wildcard origin
        cfg.setMaxAge(Duration.ofHours(1));             // cache preflight, reduces OPTIONS load

        UrlBasedCorsConfigurationSource src = new UrlBasedCorsConfigurationSource();
        src.registerCorsConfiguration("/api/**", cfg);
        return src;
    }
}
```

Explicit CORS handling for the non-Spring path (a JAX-RS endpoint or a filter), plus the
header block:

```java
@Bean
SecurityFilterChain chain(HttpSecurity http) throws Exception {
    return http
        .cors(cors -> cors.configurationSource(corsConfigurationSource()))
        .headers(headers -> headers
            // 1. HSTS: after max-age, browsers refuse http:// -> prevents SSL stripping
            .httpStrictTransportSecurity(hsts -> hsts
                .includeSubDomains(true).maxAgeInSeconds(31_536_000).preload(true))
            // 2. MIME sniffing: stop the browser guessing text/html for a .json body
            .contentTypeOptions(Customizer.withDefaults())     // => X-Content-Type-Options: nosniff
            // 3. Clickjacking: frame-ancestors is the CSP-native, modern replacement
            .frameOptions(frame -> frame.deny())
            // 4. Referrer leakage: only the origin, never the path/query
            .referrerPolicy(rp -> rp.policy(ReferrerPolicy.NO_REFERRER))
            .permissionsPolicyHeader(p -> p.policy("geolocation=(), camera=(), microphone=()"))
            .cacheControl(Customizer.withDefaults()))
        .authorizeHttpRequests(a -> a.anyRequest().authenticated())
        .build();
}
// Clickjacking note: X-Frame-Options: DENY (header) and frame-ancestors 'none' (CSP) are
// both sent. Modern guidance prefers CSP; the header remains as legacy-browser support.
```

### Test It

```java
@Test void allowedOriginGetsAcaoAndCredentials() throws Exception {
    mockMvc.perform(options("/api/orders").header(HttpHeaders.ORIGIN, "https://app.localhost:3000")
                   .header(HttpHeaders.ACCESS_CONTROL_REQUEST_METHOD, "POST")
                   .header(HttpHeaders.ACCESS_CONTROL_REQUEST_HEADERS, "content-type"))
           .andExpect(status().isOk())
           .andExpect(header().string(ACAO, "https://app.localhost:3000"))   // exact, not "*"
           .andExpect(header().string(ACAC, "true"));
}

@Test void hostileOriginGetsNoAcao() throws Exception {
    mockMvc.perform(options("/api/orders").header(HttpHeaders.ORIGIN, "https://evil.example"))
           .andExpect(status().isForbidden())
           .andExpect(header().doesNotExist(ACAO));
}

@Test void suffixLookalikeIsRejected() throws Exception {
    mockMvc.perform(get("/api/orders").header(HttpHeaders.ORIGIN, "https://app.localhost.evil.com"))
           .andExpect(header().doesNotExist(ACAO));
}

@Test void securityHeadersArePresent() throws Exception {
    mockMvc.perform(get("/api/orders").header(ORIGIN, "https://app.localhost:3000"))
           .andExpect(header().string("Strict-Transport-Security",
                   Matchers.containsString("max-age=31536000")))
           .andExpect(header().string("X-Content-Type-Options", "nosniff"))
           .andExpect(header().string("Referrer-Policy", "no-referrer"));
}
```

### Deliverables

- [ ] Exact-match origin allow-list for two legitimate origins
- [ ] Preflight handling with method/header allow-lists and a cached `Max-Age`
- [ ] Credentialed-request support without ever using a wildcard origin
- [ ] HSTS, `nosniff`, `frame-ancestors`/`X-Frame-Options`, `Referrer-Policy`, Permissions-Policy
- [ ] `exposedHeaders` so the SPA can read correlation and rate-limit headers
- [ ] Tests: allowed origin, hostile origin, suffix-lookalike origin, header presence
- [ ] A devtools walkthrough in the README with the actual preflight exchange
- [ ] Table mapping every header to the attack it mitigates
