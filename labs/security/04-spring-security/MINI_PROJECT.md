# Spring Security - MINI PROJECT

## Project: GuardDesk — build a security filter chain from scratch and prove it holds

A Spring Boot 3 / Java 21 service protecting a support-desk API. Start with no starter
auto-config magic you did not write, and add behaviour one filter at a time with a test per step.

### Architecture

```
Request ─▶ SecurityFilterChain
            1. DisableFrameOptions / headers
            2. CsrfFilter            (lab 07) ─┐
            3. RequestCacheAware     │
            4. SecurityContextHolder  │ sets Authentication
            5. BearerTokenAuthenticationFilter (JWT, lab 03)
            6. AnonymousAuthenticationFilter
            7. ExceptionTranslationFilter ─▶ 401 vs 403 decision point
            8. AuthorizationFilter ─▶ AuthorizationManager (request matchers)
         ▼
      Controller ─▶ @PreAuthorize method security (belt and braces)
```

### Implementation

```java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity                 // activates @PreAuthorize on services
class GuardDeskSecurity {

    @Bean
    SecurityFilterChain api(HttpSecurity http) throws Exception {
        return http
            .securityMatcher("/api/**")                 // scope this chain explicitly
            .csrf(csrf -> csrf.csrfTokenRepository(CookieCsrfTokenRepository.withHttpOnlyFalse()))
            .cors(Customizer.withDefaults())
            .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(a -> a
                .requestMatchers(HttpMethod.GET,  "/api/tickets/**").hasRole("AGENT")
                .requestMatchers(HttpMethod.POST, "/api/tickets/**").hasRole("AGENT")
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated())
            .oauth2ResourceServer(o -> o.jwt(Customizer.withDefaults()))
            .headers(h -> h.frameOptions(deny())          // lab 08
                         .contentTypeOptions(Customizer.withDefaults()))
            .exceptionHandling(e -> e.authenticationEntryPoint(
                    (req, res, ex) -> { res.setStatus(401); res.setContentType("application/json");
                                        res.getWriter().write("{\"error\":\"unauthenticated\"}"); }))
            .build();
    }

    @Bean
    SecurityFilterChain actuatorChain(HttpSecurity http) throws Exception {
        return http
            .securityMatcher("/actuator/**")             // second, disjoint chain
            .authorizeHttpRequests(a -> a
                .requestMatchers("/actuator/health").permitAll()
                .anyRequest().hasRole("OPS"))
            .httpBasic(Customizer.withDefaults())
            .build();
    }

    @Bean
    AuditFilter auditFilter(AuditSink sink) {
        return new AuditFilter(sink);                     // registered via addFilterBefore
    }
}
```

Method-level enforcement closes the gap left by URL rules (self-invocation, internal calls):

```java
@Service
class TicketService {
    @PreAuthorize("hasRole('AGENT')")
    @Transactional
    Ticket assign(String ticketId, String agent) {
        return repo.findById(ticketId).map(t -> { t.setAssignee(agent); return repo.save(t); })
                   .orElseThrow(() -> new TicketNotFound(ticketId));
    }

    // Ownership check that a static role cannot express: row-level ABAC.
    @PreAuthorize("hasRole('AGENT') and @ticketGuard.mayAccess(authentication.name, #ticketId)")
    Ticket escalate(String ticketId, String severity) { return repo.findById(ticketId).orElseThrow(); }
}
```

A custom filter registered correctly — order is the whole game:

```java
public class AuditFilter extends OncePerRequestFilter {
    private final AuditSink sink;
    @Override protected void doFilterInternal(HttpServletRequest req, HttpServletResponse res, FilterChain c) {
        long t0 = System.nanoTime();
        try { c.doFilter(req, res); }
        finally { sink.record(req.getMethod(), req.getRequestURI(), res.getStatus(), (System.nanoTime()-t0)/1e6); }
    }
}
// in the chain: http.addFilterBefore(auditFilter, AuthorizationFilter.class);
```

### Test It

```java
@Test void anonymousGetOnTicketIs401() {
    mockMvc.perform(get("/api/tickets/9"))
           .andExpect(status().isUnauthorized());
}
@Test void agentCannotReachAdmin() {
    mockMvc.perform(get("/api/admin/users").with(jwt().authorities(new SimpleGrantedAuthority("ROLE_AGENT"))))
           .andExpect(status().isForbidden());          // authenticated, not authorized
}
@Test void actuatorChainIsIsolated() {
    mockMvc.perform(get("/actuator/env")).andExpect(status().isUnauthorized());
    mockMvc.perform(get("/api/tickets").with(jwt())).andExpect(status().isForbidden());
}
@Test void methodSecurityBlocksOwnershipViolation() {
    assertThrows(AccessDeniedException.class, () -> ticketService.escalate("t-999", "HIGH"));
}
```

## Deliverables

- [ ] Dump the resolved filter chain at startup and save it in the README
- [ ] Two disjoint `SecurityFilterChain` beans with `securityMatcher` scoping
- [ ] Stateless API chain (JWT) plus a session/basic chain for admin tooling
- [ ] `@EnableMethodSecurity` with `@PreAuthorize` on service methods
- [ ] Row-level ownership guard (`@ticketGuard`) for ABAC-style checks
- [ ] Custom `OncePerRequestFilter` for audit, registered at the right position
- [ ] Tests asserting 401 vs 403 semantics, chain isolation, and method security
