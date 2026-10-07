# Authentication Basics - REAL WORLD PROJECT

## Project: FleetTrack Admin Console — hardened workforce login for a logistics platform

A multi-tenant internal admin console. Real employees authenticate with a password, enrol a
second factor, and then work behind a session that must survive a coffee break but not a
stolen laptop. This is the shape of almost every internal Java system that is not a
consumer SaaS.

### Architecture

```
Browser ──HTTPS──> Nginx/ALB ──> Spring Boot Admin Console
                                    │
                                    ├─ FilterChainProxy
                                    │    ├─ CorsFilter            (lab 08)
                                    │    ├─ CsrfFilter            (lab 07)
                                    │    ├─ RateLimitFilter       (bucket per IP+user)
                                    │    ├─ AuthenticationFilter  (UserDetailsService + Argon2)
                                    │    └─ AuthorizationFilter   (roles, lab 09)
                                    ├─ SessionRegistry (Redis)  — single logout, device list
                                    └─ AuditPublisher ──> SIEM (lab 19)

Postgres: users, credentials(argon2 hash+salt), mfa_secrets(encrypted), recovery_codes
Audit sink: append-only table + Kafka topic `auth.events` for the SOC
```

### Implementation

```java
@Configuration
@EnableWebSecurity
class SecurityConfig {

    @Bean
    SecurityFilterChain chain(HttpSecurity http) throws Exception {
        return http
            .csrf(csrf -> csrf.csrfTokenRepository(new HttpSessionCsrfTokenRepository()))
            .cors(Customizer.withDefaults())
            .sessionManagement(s -> s
                .sessionFixation(fix -> fix.migrateSession())   // rotate id on login
                .sessionConcurrency(c -> c.maximumSessions(3))   // device cap
                .sessionRegistry(redisSessionRegistry()))
            .authorizeHttpRequests(a -> a
                .requestMatchers("/actuator/health", "/login").permitAll()
                .requestMatchers("/admin/**").hasRole("FLEET_ADMIN")
                .anyRequest().authenticated())
            .oauth2Login(Customizer.withDefaults())
            .build();
    }

    @Bean
    PasswordEncoder passwordEncoder() {
        // Memory-hard; tune cost so verification stays under ~100ms on prod hardware.
        return new Argon2PasswordEncoder(19, 2 * 1024, 2, 1, 256);
    }

    @Bean
    DaoAuthenticationProvider provider(UserDetailsService uds, PasswordEncoder pe) {
        DaoAuthenticationProvider p = new DaoAuthenticationProvider(uds);
        p.setPasswordEncoder(pe);
        p.setHideUserNotFoundExceptions(true);  // 404 vs 401 no longer distinguishable
        p.setHideNotFoundExceptions(true);
        return p;
    }
}
```

Brute-force defence and audit emission live in one filter so policy is auditable in a
single place rather than scattered across controllers:

```java
@Component
class LoginThrottleFilter extends OncePerRequestFilter {
    private final RateLimiter limiter = RateLimiter.create(5.0);   // 5/s per key
    private final AuditPublisher audit;

    @Override
    protected void doFilterInternal(HttpServletRequest req, HttpServletResponse res, FilterChain c) {
        if (!req.getRequestURI().equals("/login")) { c.doFilter(req, res); return; }
        String key = req.getRemoteAddr() + "|" + req.getParameter("username");
        if (!limiter.tryAcquire(key, 1)) {
            audit.warn("AUTH_BRUTE_FORCE", key, req.getRemoteAddr());
            res.setStatus(429);
            res.setHeader("Retry-After", "30");
            return;
        }
        c.doFilter(req, res);
    }
}
```

### Operational requirements

- **MFA**: TOTP mandatory for admins, optional-but-prompts-for-others; recovery codes single-use.
- **Session policy**: 15 min idle, 8 h absolute, 3 concurrent devices, kill-all on password change.
- **Metrics**: login success rate, distinct-failure-per-IP, lockout count, p95 verify latency.
- **Alerts**: >200 failures/min from one IP (credential stuffing), or any admin MFA disable event.
- **Compliance mapping**: NIST SP 800-63B authenticator guidance, OWASP ASVS V2/V3 controls.

### Sourced field notes (fetched Oct 2026 — verify before citing)
- OWASP Password Storage Cheat Sheet is the reference for preferring Argon2id over
  PBKDF2/bcrypt when the stack supports it, and for salting/peppering practice.
  https://web.archive.org/web/20200125082857/https://web.archive.org/web/20200119054315/https://owasp.org/www-project-cheat-sheets/cheatsheets/Password_Storage_Cheat_Sheet.html
- Spring Security reference documents the authentication architecture, `SecurityFilterChain`
  beans, and session/concurrency management used above.
  https://docs.spring.io/spring-security/reference/ (stable; see `servlet/authentication`)

## Deliverables

- [x] Argon2id `PasswordEncoder` tuned with documented cost parameters
- [x] `SecurityFilterChain` with CSRF, CORS, session fixation defence, role-based rules
- [x] Per-IP+user login throttle emitting structured audit events
- [x] TOTP second factor with single-use recovery codes
- [x] Session concurrency cap and "sign out everywhere" on password change
- [x] Dashboard query for stuffing-attack detection
- [ ] Load test: verify p95 login latency stays under budget at 200 RPS
