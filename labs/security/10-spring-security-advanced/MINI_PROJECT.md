# Spring Security Advanced - MINI PROJECT

## Project: PolyglotGate — one app, three authentication styles, fully tested

A single Spring Boot app exposing three URL spaces that need genuinely different auth:
a public read-only API, an internal service API that must be fast and stateless, and a
legacy partner API that must support opaque-token introspection. Prove all three coexist
and that no chain bleeds into another.

### Architecture

```
  /public/**    ──▶ Chain A  permitAll + rate limit + strict output encoding
  /internal/**  ──▶ Chain B  JWT local verify (RS256) + SCOPE_* authorities
  /partner/**   ──▶ Chain C  opaque token -> introspection (cached) + client creds
  /legacy/**    ──▶ Chain D  session form login + step-up for admin actions
```

All four chains share a single `AuthenticationManager` and one `AuditDecisionListener`
so logging is not per-chain duplicated logic.

```java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity
class PolyglotGateSecurity {

    @Bean @Order(1)
    SecurityFilterChain publicApi(HttpSecurity http) throws Exception {
        return http.securityMatcher("/public/**")
            .csrf(AbstractHttpConfigurer::disable)
            .authorizeHttpRequests(a -> a.anyRequest().permitAll())
            .addFilterBefore(new RateLimitFilter(100, Duration.ofMinutes(1)),
                             UsernamePasswordAuthenticationFilter.class)
            .build();
    }

    @Bean @Order(2)
    SecurityFilterChain internalApi(HttpSecurity http) throws Exception {
        return http.securityMatcher("/internal/**")
            .csrf(AbstractHttpConfigurer::disable)
            .sessionManagement(s -> s.sessionCreationPolicy(STATELESS))
            .authorizeHttpRequests(a -> a
                .requestMatchers("/internal/inventory/**").hasAuthority("SCOPE_inventory.read")
                .requestMatchers("/internal/inventory/**").hasAuthority("SCOPE_inventory.write")
                .anyRequest().denyAll())
            .oauth2ResourceServer(o -> o.jwt(j -> j
                .jwtAuthenticationConverter(scopesToAuthorities())))
            .build();
    }

    @Bean @Order(3)
    SecurityFilterChain partnerApi(HttpSecurity http) throws Exception {
        return http.securityMatcher("/partner/**")
            .csrf(AbstractHttpConfigurer::disable)
            .sessionManagement(s -> s.sessionCreationPolicy(STATELESS))
            .authorizeHttpRequests(a -> a.anyRequest().hasAuthority("SCOPE_partner.read"))
            // Opaque token: server calls the IdP. Cached, with a revocation window trade-off.
            .oauth2ResourceServer(o -> o.opaqueToken(t -> t
                .introspectionUri("https://idp.internal/oauth2/introspect")
                .clientId("gateway").clientSecret(secret)
                .introspectionCache(new CachedIntrospectionResultCache(cache, Duration.ofSeconds(60)))))
            .build();
    }

    @Bean @Order(4)
    SecurityFilterChain legacyAdmin(HttpSecurity http) throws Exception {
        return http.securityMatcher("/legacy/**")
            .formLogin(Customizer.withDefaults())
            .authorizeHttpRequests(a -> a.anyRequest().hasRole("LEGACY_ADMIN"))
            .build();
    }
}
```

The shared `AuthenticationManager` and a custom provider for a legacy credential store:

```java
@Bean
AuthenticationManager authManager(LegacyUserStore users, PasswordEncoder encoder) {
    DaoAuthenticationProvider legacy = new DaoAuthenticationProvider(users);
    legacy.setPasswordEncoder(encoder);
    legacy.setHideUserNotFoundExceptions(true);
    // Compose: try the legacy store, then fall back to the JWT/opaque converters.
    return new ProviderManager(List.of(legacy));
}

@Service
class LegacyUserStore implements UserDetailsService {
    public UserDetails loadUserByUsername(String username) {
        LegacyAccount a = repo.findByLogin(username)
            .orElseThrow(() -> new UsernameNotFoundException("unknown"));
        return org.springframework.security.core.userdetails.User
            .withUsername(a.login())
            .password(a.bcryptHash())                        // rehashed at migration time
            .authorities("ROLE_LEGACY_ADMIN", "ROLE_AUDITOR")
            .build();
    }
}
```

Method security with a custom, type-safe permission evaluator (SpEL kept readable):

```java
@Component
class ScopeEvaluator {
    boolean hasScope(Authentication auth, String required) {
        return auth.getAuthorities().stream()
            .anyMatch(a -> a.getAuthority().equals("SCOPE_" + required));
    }
}

@Service @Transactional
class InventoryService {
    @PreAuthorize("@scopeEvaluator.hasScope(authentication, 'inventory.write')")
    public void adjust(String sku, int delta) { repo.findBySku(sku).ifPresent(i -> i.adjust(delta)); }

    // Restrict a method by the caller's own tenant claim, not a static role.
    @PreAuthorize("@scopeEvaluator.hasScope(authentication, 'inventory.read') and " +
                  "T(java.util.Objects).equals(#tenantId, authentication.claims.get('tenant'))")
    public StockLevel level(String tenantId, String sku) { return repo.level(tenantId, sku); }
}
```

### Test It

```java
@Test void chainsDoNotBleed() throws Exception {
    // internal rules must not apply to /partner, and vice versa.
    mockMvc.perform(get("/partner/orders")).andExpect(status().isUnauthorized());
    mockMvc.perform(get("/internal/inventory/x").with(jwt().authorities(
            new SimpleGrantedAuthority("SCOPE_partner.read"))))
           .andExpect(status().isForbidden());
}

@Test void opaqueTokenPathWorks() {
    mockMvc.perform(get("/partner/orders").with(opaqueToken().token("valid-abc")))
           .andExpect(status().isOk());
}

@Test void methodSecurityUsesClaimComparison() {
    assertThrows(AccessDeniedException.class, () -> inventory.level("tenant-B", "SKU1")); // caller is tenant-A
}

@Test void unknownRoleOnLegacyIsRejected() {
    mockMvc.perform(get("/legacy/audit").with(user("bob").roles("USER")))
           .andExpect(status().isForbidden());
}
```

## Deliverables

- [ ] Four `SecurityFilterChain` beans with explicit `@Order` and `securityMatcher`
- [ ] Shared `AuthenticationManager` composed across providers
- [ ] Custom `UserDetailsService` adapter for a legacy credential table
- [ ] Opaque-token introspection chain with a documented cache/window trade-off
- [ ] Custom `ScopeEvaluator` used via `@PreAuthorize` with claim comparisons
- [ ] Tests proving chain isolation (JWT token rejected on the opaque path and vice versa)
- [ ] Benchmark comparing per-request cost with and without method security
- [ ] README documenting each chain's auth model and failure behaviour
