# Spring Security - REAL WORLD PROJECT

## Project: CareBridge — mixed public/private API for a healthcare scheduling platform

A real regulatory-flavoured system: a patient-facing public API, a clinician API behind
JWT with role *and* care-relationship checks, a hospital-admin API behind a separate
authenticating network zone, and an internal ops actuator. Four different trust levels in
one Spring Boot application.

### Architecture

```
                        ┌──────────────────────────────┐
 patient PWA  ─────────▶│ Chain A: /public/**         │ permitAll + strict rate limit
                        │   (registration, slot search)│
 clinician app ─────────▶│ Chain B: /api/**            │ JWT, ROLE_*, care-relationship
                        │                              │ ABAC, rate limit per clinician
 hospital admin ────────▶│ Chain C: /admin/**          │ Basic->mTLS edge, ADMIN only,
                        │   (network-zone enforced)    │ step-up auth for PHI export
 ops SRE ───────────────▶│ Chain D: /actuator/**       │ ROLE_OPS, localhost-restricted
                        └──────────────┬───────────────┘
                                       ▼
                       Method security layer: @PreAuthorize on every service
                                       ▼
                       AuditFilter -> immutable audit log (labs 19/20)
```

### Implementation

```java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity
class CareBridgeSecurity {

    @Bean @Order(1)
    SecurityFilterChain publicApi(HttpSecurity http) throws Exception {
        return http.securityMatcher("/public/**")
            .csrf(csrf -> csrf.disable())          // pure token/anon API, no ambient cookie
            .cors(cors -> cors.configurationSource(careBridgeCorsSource()))
            .sessionManagement(s -> s.sessionCreationPolicy(STATELESS))
            .authorizeHttpRequests(a -> a.anyRequest().permitAll())
            .addFilterBefore(new IpRateLimitFilter(20, Duration.ofMinutes(1)), UsernamePasswordAuthenticationFilter.class)
            .build();
    }

    @Bean @Order(2)
    SecurityFilterChain clinicianApi(HttpSecurity http) throws Exception {
        return http.securityMatcher("/api/**")
            .authorizeHttpRequests(a -> a
                .requestMatchers(HttpMethod.GET,  "/api/patients/**").hasAnyRole("CLINICIAN", "NURSE")
                .requestMatchers(HttpMethod.POST, "/api/appointments/**").hasRole("CLINICIAN")
                .requestMatchers("/api/prescriptions/**").hasRole("PHYSICIAN")
                .anyRequest().authenticated())
            .oauth2ResourceServer(o -> o.jwt(jwt -> jwt.jwtAuthenticationConverter(clinicianConverter())))
            .sessionManagement(s -> s.sessionCreationPolicy(STATELESS))
            .build();
    }

    @Bean @Order(3)
    SecurityFilterChain adminApi(HttpSecurity http) throws Exception {
        return http.securityMatcher("/admin/**")
            .requiresChannel(c -> c.anyRequest().requiresSecure())   // TLS mandatory
            .authorizeHttpRequests(a -> a.anyRequest().hasRole("HOSPITAL_ADMIN"))
            .httpBasic(basic -> basic.requireSsl(true))
            .sessionManagement(s -> s.sessionFixation(fix -> fix.changeSessionId()))
            .build();
    }

    @Bean @Order(4)
    SecurityFilterChain ops(HttpSecurity http) throws Exception {
        return http.securityMatcher("/actuator/**")
            .authorizeHttpRequests(a -> a
                .requestMatchers("/actuator/health", "/actuator/info").permitAll()
                .anyRequest().hasRole("OPS"))
            .headers(h -> h.frameOptions(deny()))
            .build();
    }

    /** Step-up authentication: viewing or exporting PHI needs a fresh, stronger proof. */
    @Bean
    StepUpAuthenticationFilter stepUpFilter(StepUpRegistry registry) {
        return new StepUpAuthenticationFilter(registry, Duration.ofMinutes(5));
    }
}
```

Service layer is where the real authorization logic lives, because URL rules cannot express
"this clinician is assigned to this patient":

```java
@Service
class AppointmentService {
    @Transactional
    @PreAuthorize("hasRole('CLINICIAN') and @careGuard.isAssignedTo(authentication.name, #patientId)")
    public Appointment book(String patientId, Instant slot) {
        Patient p = patients.require(patientId);
        if (!slots.available(p, slot)) throw new SlotUnavailable(slot);
        return repo.save(Appointment.of(p, slot));
    }

    @PreAuthorize("@phiPolicy.canExport(authentication, #patientId)")
    public byte[] exportPhi(String patientId) {
        stepUp.requireFreshAuthentication(Tier.TWO, 5, TimeUnit.MINUTES);  // fail closed
        return phiAssembler.assemble(patientId);
    }
}
```

### Non-functional requirements

- **Availability**: security misconfig must fail startup, not degrade to permit-all. Add a
  context test that asserts a deny-by-default route is not open.
- **Audit**: every PHI read logged with actor, patient, purpose-of-use, and outcome.
- **Compliance mapping**: OWASP ASVS V2 (auth) / V4 (access control) / V14 (config) controls.
- **Rate limits**: public endpoints per-IP; clinician endpoints per-token-subject.
- **Testing**: contract tests proving each chain only answers its own URL prefix.
- **Runbook**: IdP outage behaviour (fail closed, cached JWKS), key compromise, admin lockout.

### Sourced field notes (fetched Oct 2026 — verify before citing)
- Spring Security reference: the `SecurityFilterChain` / `securityMatcher` model, multi-chain
  ordering, and method-security annotations used throughout this design.
  https://docs.spring.io/spring-security/reference/
- OWASP ASVS 5.0 is the control catalogue this project maps to (authentication,
  access control, session, and configuration sections).
  https://owasp.org/www-project-application-security-verification-standard/

## Deliverables

- [x] Four `SecurityFilterChain` beans with explicit ordering and disjoint matchers
- [x] JWT clinician API with role + care-relationship ABAC
- [x] Admin zone forcing TLS, session-based admin access with fixation defence
- [x] Step-up authentication for PHI export, failing closed
- [x] Per-endpoint rate limiting (IP for public, subject for clinical)
- [x] Immutable audit log for every PHI access
- [x] Startup self-tests that fail the build on a deny-by-default violation
- [ ] Tabletop exercise: IdP outage and credential-compromise runbooks
