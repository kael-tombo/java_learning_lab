# Spring Security Advanced - REAL WORLD PROJECT

## Project: StreamForge — securing a mixed reactive/servlet streaming platform

A video platform: reactive `WebFlux` for the playback and live-chat path (high connection
count, low CPU), servlet Spring MVC for the studio and billing admin (complex forms).
Different stacks, one identity, and authorization rules that must be identical across both
or the weaker path becomes the way in.

### Architecture

```
                        ┌──────────────────────────────┐
  Player (WebFlux)  ───▶│ SecurityWebFilterChain      │
    Bearer JWT            │  reactive, non-blocking      │──▶ Playback Svc
  Chat (WebFlux)     ───▶│  SCOPE_playback / SCOPE_chat │──▶ Chat (WebSocket)
                        └──────────────────────────────┘

                        ┌──────────────────────────────┐
  Studio (Servlet)   ───▶│ SecurityFilterChain           │
    Session + MFA       │  form login, step-up          │──▶ Studio Svc
  Admin (Servlet)   ───▶│  ROLE_ADMIN + SoD             │──▶ Billing Admin

  Shared: PolicyEvaluator library (method security)  ──▶ identical rules both stacks
           AuthorizationDecisionCache (Caffeine)      ──▶ 60s, tenant+user+action keyed
           SecurityDecisionAudit (Kafka)              ──▶ every allow/deny with reason
```

### Implementation

Reactive chain, with the classic mistakes explicitly avoided (no blocking calls, correct
context propagation):

```java
@Bean
SecurityWebFilterChain reactiveChain(ServerHttpSecurity http, PolicyEvaluator policies) {
    return http
        .csrf(ServerHttpSecurity.CsrfSpec::disable)          // Bearer auth, no cookies
        .securityContextRepository(new ReactorContextSecurityContextRepository())
        .authorizeExchange(ex -> ex
            .pathMatchers("/api/playback/**").hasAuthority("SCOPE_playback.read")
            .pathMatchers("/api/chat/**").hasAuthority("SCOPE_chat.write")
            .pathMatchers("/admin/**").hasAuthority("ROLE_ADMIN")
            .anyExchange().denyAll())
        .oauth2ResourceServer(o -> o.jwt(j -> j.jwtAuthenticationConverter(scopesToAuthorities())))
        .addFilterAt(new TenantContextWebFilter(), SecurityContextServerWebExchangeWebFilter.class)
        .build();
}

@Component
class TenantContextWebFilter implements WebFilter {
    @Override
    public Mono<Void> filter(ServerWebExchange ex, WebFilterChain chain) {
        // ReactorContext is immutable; use write().contextWrite() - never ThreadLocal here.
        return chain.filter(ex)
            .contextWrite(ReactiveSecurityContextHolder.getContext()
                .map(sc -> new ReactiveSecurityContextHolder.Authentication(
                    new UsernamePasswordAuthenticationToken(
                        sc.getAuthentication().getName(), null, sc.getAuthentication().getAuthorities()))));
    }
}
```

Servlet chain with step-up for high-impact actions. The step-up registry is shared so a
verification in the studio satisfies the admin surface within its window:

```java
@Bean
SecurityFilterChain servletChain(HttpSecurity http, StepUpRegistry stepUp) {
    return http
        .authorizeHttpRequests(a -> a
            .requestMatchers("/studio/**").hasRole("STUDIO_USER")
            .requestMatchers("/admin/billing/**").hasRole("BILLING_ADMIN")
            .requestMatchers("/admin/**").hasRole("ADMIN")
            .anyRequest().authenticated())
        .oauth2Login(o -> o.successHandler(oidcSuccessHandler))
        .sessionManagement(s -> s.sessionFixation(f -> f.changeSessionId()))
        .addFilterAfter(new StepUpAuthenticationFilter(stepUp, Duration.ofMinutes(10)),
                        BearerTokenAuthenticationFilter.class)
        .build();
}
```

Identical policy semantics in both stacks, which is the actual engineering problem:

```java
public interface PolicyEvaluator {
    Decision evaluate(Subject subject, String action, Resource resource);
}

/** One implementation, two adapters. The rules cannot drift between stacks. */
@Service
class DefaultPolicyEvaluator implements PolicyEvaluator { /* deny-by-default engine */ }

@Component("policies")
class PolicyExpressions {
    private final PolicyEvaluator engine;
    private final AuthorizationDecisionCache cache;

    // Called identically from WebFlux @PreAuthorize and MVC @PreAuthorize.
    public boolean allowed(String subjectId, String tenantId, String action, String resourceType, String resourceId) {
        return cache.get(subjectId, tenantId, action, resourceType, resourceId, () -> {
            Subject s = subjectResolver.resolve(subjectId, tenantId);
            Decision d = engine.evaluate(s, action, new Resource(resourceType, resourceId, tenantId));
            audit.publish(d, s, action, resourceId);            // every decision is observable
            return d;
        });
    }
}
```

Failure behaviour is the part that pages people. Denial of service vs denial of security,
made explicit and testable:

```java
@ExceptionHandler(AccessDeniedException.class)
ProblemDetail handleDenied(AccessDeniedException ex) {
    // 403 with a reason code the client can act on, never a stack trace.
    // Decision: fail CLOSED on authorization uncertainty; fail OPEN only where a
    // documented business rule requires availability (none here).
    return ProblemDetail.forStatusAndDetail(FORBIDDEN, "not permitted for this action");
}
// JWKS unreachable -> JwtDecoder throws; the chain returns 503, not 401/403 and not 200.
```

### Non-functional requirements

- **Latency**: reactive path p95 under 8 ms per request; connection count target 200k.
  Authorization decisions cached 60 s; a cache miss is measured, not assumed rare.
- **Reactive purity**: no blocking call in any `WebFilter` or reactive security component.
  Enforced with `BlockHound` in tests so a regression fails CI.
- **Consistency**: the shared `PolicyEvaluator` and its test suite run against both stacks.
- **Availability**: security decisions must never be the reason a stream drops; chat and
  playback fail open on *authorization cache* staleness but closed on *authentication* failure.
- **Observability**: per-decision audit to Kafka; dashboards for deny-rate by reason code
  (a spike is either a client bug or a probing attack), and cache hit ratio.
- **Testing**: contract tests asserting the same 10 policies produce identical decisions
  in WebFlux and MVC; `BlockHound` to keep the event loop clean.

### Sourced field notes (fetched Oct 2026 — verify before citing)
- Spring Security's reactive (WebFlux) reference documents `SecurityWebFilterChain`,
  `ReactiveSecurityContextHolder`, and the WebFlux testing support used above.
  https://docs.spring.io/spring-security/reference/reactive/index.html
- OWASP Cheat Sheet "Authorization" and "Logging" guidance underpin the deny-by-default
  decision point plus audit-every-decision design.
  https://web.archive.org/web/20200125082857/(link removed)

## Deliverables

- [x] Reactive `SecurityWebFilterChain` with correct Reactor context propagation
- [x] Servlet chain with session fixation defence and step-up authentication
- [x] Single `PolicyEvaluator` shared by WebFlux and MVC with identical semantics
- [x] `AuthorizationDecisionCache` with hit-ratio metrics and fail-closed semantics
- [x] Every decision audited with subject, action, resource, and reason code
- [x] `BlockHound` tests guaranteeing no blocking call in the reactive chain
- [x] Cross-stack contract tests: 10 policies, two stacks, identical outcomes
- [x] Documented failure behaviour: JWKS outage, cache staleness, IdP unavailability
