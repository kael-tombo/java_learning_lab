# Code Deep Dive: Spring Security

## SecurityFilterChain configuration

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    SecurityFilterChain apiChain(HttpSecurity http) throws Exception {
        http
          .csrf(csrf -> csrf.disable())                    // stateless JWT API
          .sessionManagement(s -> s.sessionCreationPolicy(STATELESS))
          .authorizeHttpRequests(auth -> auth
              .requestMatchers("/actuator/health", "/login").permitAll()
              .requestMatchers(HttpMethod.GET, "/public/**").permitAll()
              .requestMatchers("/admin/**").hasRole("ADMIN")
              .anyRequest().authenticated())
          .oauth2ResourceServer(o -> o.jwt(Customizer.withDefaults()));
        return http.build();
    }
}
```

Pitfalls: disabling CSRF is only correct for purely token-authenticated APIs;
a cookie-authenticated admin path silently inherited the same `csrf.disable()`
is the classic regression. `STATELESS` alone does not clear an existing
`JSESSIONID` cookie still being accepted by an older filter.

## Password encoder and verification

```java
@Bean
PasswordEncoder encoder() {
    return new BCryptPasswordEncoder(12);                  // work factor 12
}

boolean verify(String raw, String stored) {
    return encoder().matches(raw, stored);                // constant-time compare
}
```

Pitfall: handwritten MD5 + fixed salt, or `raw.equals(storedHash)` string
compares that leak timing. Both fail review; the encoder bean above is the
supported path.

## Ownership check with method security

```java
@Service
public class OrderService {
    @PreAuthorize("hasRole('ADMIN') or @orderSecurity.isOwner(#orderId)")
    public Order get(Long orderId) { return repo.findById(orderId).orElseThrow(); }
}

@Component("orderSecurity")
public class OrderSecurity {
    public boolean isOwner(Long orderId) {
        var auth = SecurityContextHolder.getContext().getAuthentication();
        return repo.findById(orderId)
                   .map(o -> o.userId().equals(auth.getName()))
                   .orElse(false);
    }
}
```

Pitfall: `@PreAuthorize` on private methods is silently ignored (Spring AOP
only proxies public methods). Also double-fetching the entity (once in the
check, once in the method) races with a delete in between; acceptable at low
risk, document it.

## Parameterized queries — always

```java
// WRONG — injectable
String sql = "SELECT * FROM orders WHERE note LIKE '%" + keyword + "%'";
// RIGHT
List<Order> rows = jdbc.query(
    "SELECT * FROM orders WHERE note LIKE ? ESCAPE '\\'",
    (rs, i) -> map(rs), "%" + escapeLike(keyword) + "%");
```

Pitfall: `LIKE` patterns built from user input need escaping of `%`/`_`;
otherwise users inject wildcards and turn indexes into scans.

## JWT validation essentials

```java
@Bean
JwtDecoder jwtDecoder(@Value("${jwt.issuer}") String issuer,
                      @Value("${jwt.audience}") String audience) {
    NimbusJwtDecoder dec = NimbusJwtDecoder.withJwkSetUri(jwksuri).build();
    dec.setJwtValidator(new DelegatingOAuth2TokenValidator<>(
        JwtValidators.createDefaultWithIssuer(issuer),
        new JwtClaimValidator<List<String>>("aud", a -> a.contains(audience)),
        new JwtTimestampValidator()));
    return dec;
}
```

Pitfalls: accepting tokens with no `aud` check, skipping issuer validation,
and trusting the `alg` header from the token itself rather than pinning
`RS256` on the decoder.

## Security headers and error hygiene

```java
http.headers(h -> h
    .contentSecurityPolicy(csp -> csp.policyDirectives("default-src 'self'"))
    .frameOptions(f -> f.deny())
    .referrerPolicy(r -> r.policy(ORIGIN_WHEN_CROSS_ORIGIN)));
```

Pitfall: Spring Boot's default JSON error includes `trace` in dev profiles;
`application-prod.yml` must set `server.error.include-stacktrace=never` —
otherwise trace details land in customer support tickets.
