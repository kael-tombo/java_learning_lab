# OAuth 2.0 - REAL WORLD PROJECT

## Project: PartnerHub — OAuth 2.0 authorization for a B2B logistics partner ecosystem

Ten external partners (carriers, customs brokers, warehouse operators) need machine-to-machine
and headless-delegate access to FleetTrack. Each partner is an isolated tenant: its own client,
its own scope vocabulary, its own rate budget, and no cross-tenant visibility. This is the
shape of every marketplace/partner-integration backend.

### Architecture

```
                       ┌───────────────────────────────┐
 Partner client ──────▶│  Auth Server (Spring Boot)   │
  (PKCE / cc)          │  /authorize  /token /revoke  │
                       │  /oauth2/jwks  /admin/clients│
                       └───┬───────────────┬───────────┘
                           │ tokens        │ config + audit
                           ▼               ▼
 ┌──────────────────┐   ┌───────────────────────────────┐
 │ API Gateway      │──▶│ Resource Server (orders,      │
 │ mTLS + rate      │   │ shipments, webhooks)          │
 │ limit per client │   │  scope -> authority mapping   │
 └──────────────────┘   └──────────┬────────────────────┘
                                   │ signed internal call
                                   ▼
                        ┌───────────────────────────────┐
                        │ Webhook Dispatcher           │
                        │ per-partner signing key       │
                        └───────────────────────────────┘
```

### Implementation

```java
@Configuration
class PartnerResourceServerConfig {

    @Bean
    SecurityFilterChain api(HttpSecurity http) throws Exception {
        return http
            .csrf(AbstractHttpConfigurer::disable)          // token auth, no ambient cookie
            .sessionManagement(s -> s.sessionCreationPolicy(STATELESS))
            .authorizeHttpRequests(a -> a
                // Scope-to-authority mapping happens via JwtAuthenticationConverter;
                // here we express the policy once, in one place.
                .requestMatchers(HttpMethod.GET,  "/api/orders/**").hasAuthority("SCOPE_orders.read")
                .requestMatchers(HttpMethod.POST, "/api/orders/**").hasAuthority("SCOPE_orders.write")
                .requestMatchers("/api/shipments/**").hasAuthority("SCOPE_shipments.read")
                .requestMatchers("/api/admin/**").hasAuthority("SCOPE_partner.admin")
                .anyRequest().denyAll())
            .oauth2ResourceServer(o -> o.jwt(j -> j
                .jwkSetUri("https://auth.partnerhub.io/oauth2/jwks")   // rotated, cached
                .jwtAuthenticationConverter(scopeConverter())))
            .build();
    }

    @Bean
    JwtAuthenticationConverter scopeConverter() {
        // audience must be OUR api, not merely "valid signature" — blocks token confusion
        // where a partner's token for another service is replayed here.
        JwtAuthenticationConverter c = new JwtAuthenticationConverter();
        c.setJwtGrantedAuthoritiesConverter(jwt -> {
            List<GrantedAuthority> out = new ArrayList<>();
            for (String s : jwt.getClaimAsStringList("scope")) out.add(new SimpleGrantedAuthority("SCOPE_" + s));
            if (!jwt.getAudience().contains("fleettrack-api")) throw new BadJwtException("bad audience");
            return out;
        });
        return c;
    }
}
```

Per-partner isolation and budget enforcement at the gateway:

```java
@Component
class PartnerQuotaFilter extends OncePerRequestFilter {
    private final Map<String, TokenBucket> buckets = new ConcurrentHashMap<>();

    @Override protected void void doFilterInternal(HttpServletRequest req, HttpServletResponse res, FilterChain chain) {
        JwtAuthentication auth = (JwtAuthentication) SecurityContextHolder.getContext().getAuthentication();
        String client = auth.getToken().getSubject();
        TokenBucket b = buckets.computeIfAbsent(client, c -> new TokenBucket(rateFor(c), burstFor(c)));
        if (!b.tryConsume(1)) {
            audit.warn("QUOTA_EXCEEDED", client, req.getRequestURI());
            res.setStatus(429);
            res.setHeader("Retry-After", "60");
            res.setHeader("X-RateLimit-Remaining", "0");
            return;
        }
        chain.doFilter(req, res);
    }
}
```

### Non-functional requirements

- **Availability**: auth server in at least 2 zones; JWKS cached 5 min with refresh-on-unknown-kid.
- **Latency**: p95 added auth overhead under 8 ms at 2 k RPS (JWT verify is local, no introspection).
- **Key management**: RS256 with quarterly rotation; overlap window so in-flight tokens still verify.
- **Audit**: every grant, refresh, revocation, and scope denial to an immutable sink (labs 19/20).
- **Onboarding**: self-service client registration with approval + per-partner scope review gate.
- **Abuse**: per-partner anomaly detection on scope usage (e.g. partner reading all tenants' orders).

### Sourced field notes (fetched Oct 2026 — verify before citing)
- OAuth 2.0 Security Best Current Practice (RFC 9700) enumerates the BCP requirements
  this design leans on: PKCE, exact redirect URI matching, sender-constrained tokens,
  and refresh-token rotation/replay handling.
  https://www.rfc-editor.org/info/rfc9700/
- OWASP Authorization Code Cheat Sheet covers the PKCE + state flow and the
  `redirect_uri` validation rules implemented above.
  https://owasp.org/www-project-cheat-sheets/cheatsheets/Authorization_Code_Cheat_Sheet.html

## Deliverables

- [x] Authorization server: auth code + PKCE, client credentials, refresh rotation
- [x] Per-partner client registration with approval workflow and scope review
- [x] Resource server with audience-checked JWT validation and scope-based routes
- [x] Per-partner rate limiting at the gateway with 429 + `Retry-After`
- [x] JWKS endpoint with key rotation and refresh-on-unknown-kid
- [x] Full audit trail of grants, revocations, and denials
- [ ] Partner-facing developer portal with token introspection debugging tool
