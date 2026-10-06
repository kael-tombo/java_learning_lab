# Lab 09: Security Engineering in Production — Mini Project

## Project: `HardenLab` — Break a Vulnerable Spring Boot Service, Then Fix Every Finding

**Time**: 12–16 hours | **Difficulty**: Advanced | **Stack**: Java 21, Spring Boot 3, Spring Security 6, OAuth2 Resource Server (mock IdP), Testcontainers, OWASP ZAP, Semgrep, Trivy, Syft (SBOM)

You are handed `vuln-orders-api`, a Spring Boot service with realistic and deliberate production-style security holes. Break it, enumerate every finding with tooling, fix each one, and prove the fix with an automated test.

---

## Part 1 — The service

A Spring Boot 3 order/invoice service with:
- `POST /api/orders`, `GET /api/orders/{id}`, `GET /api/orders?page=&size=&sort=`
- `GET /internal/metrics/raw` (prometheus scrape endpoint, unauthenticated)
- `GET /internal/reindex` (should be service-only)
- `GET /actuator/**`
- H2 in-memory DB (easy to attack) with JPA + a hand-written native query for the list endpoint
- Logback pattern layout printing the whole request

`docker-compose.yml` provides a `wiremock` IdP that mints tokens on demand so you can test claim validation without a real IdP.

---

## Part 2 — Baseline enumeration

### 2.1 Static analysis

```bash
# Dependency vulnerabilities + SBOM
trivy fs --scanners vuln,secret,misconfig --format table .
syft . -o cyclonedx-json > sbom.json

# Custom rules for the things Semgrep misses by default
semgrep --config=p/java --config=p/spring --config=p/security-audit .
```

Write a small ruleset for the lab's specific patterns:

```yaml
# .semgrep/java-security.yml
rules:
  - id: raw-sql-concatenation
    patterns:
      - pattern-either:
          - pattern: $Q.createQuery("..." + $X + "...")
          - pattern: $S.createStatement("..." + $X + "...")
    message: "String-concatenated SQL. Use a bound parameter or a whitelist-mapped identifier."
    severity: ERROR

  - id: trust-all-tls
    patterns:
      - pattern: new X509TrustManager[] { ... return null; ... }
    message: "Trust-all TrustManager: TLS without peer authentication."
    severity: ERROR

  - id: unbounded-page-size
    pattern: Pageable.ofSize($N)
    message: "Server-side page size must be clamped."

  - id: log-with-request-body
    patterns:
      - pattern: $LOG.info("...", $REQ.getBody())
    message: "Request body may contain PII or credentials."
    severity: WARNING
```

**Deliverable**: `FINDINGS_BASELINE.md` — every finding with file:line, tool, severity, and exploitability notes. Expect 20+.

### 2.2 Dynamic scan

```bash
zap-baseline.py -t http://localhost:8080 -r zap-report.html
zap-baseline.py -t http://localhost:8080 -r zap-active.html -a          # active scan
```

**Deliverable**: append the ZAP findings, with a note on which are false positives and why.

---

## Part 3 — Break it (manual exploitation, authorized, local only)

Demonstrate each class by hand with `curl`, and record the evidence.

### 3.1 JWT validation failures

Have Wiremock mint tokens with configurable defects:

```bash
# 1. Wrong audience (token minted for another service)
curl -H "Authorization: Bearer $TOKEN_WRONG_AUD" http://localhost:8080/api/orders/1
# 2. Wrong issuer
curl -H "Authorization: Bearer $TOKEN_WRONG_ISS" http://localhost:8080/api/orders/1
# 3. Expired
curl -H "Authorization: Bearer $TOKEN_EXPIRED" http://localhost:8080/api/orders/1
# 4. alg: none (unsigned)
curl -H "Authorization: Bearer $TOKEN_ALG_NONE" http://localhost:8080/api/orders/1
# 5. Valid but insufficient scope
curl -H "Authorization: Bearer $TOKEN_READONLY" -X POST http://localhost:8080/api/orders -d '{...}'
```

Record: which requests returned 200 before the fix.

### 3.2 SQL injection via sort

```bash
curl -H "Authorization: Bearer $TOKEN_VALID" \
  'http://localhost:8080/api/orders?sort=id;SELECT+password+FROM+users--'
curl -H "Authorization: Bearer $TOKEN_VALID" \
  'http://localhost:8080/api/orders?size=1000000'     # DoS + bulk exfiltration
```

### 3.3 Actuator exposure

```bash
curl http://localhost:8080/actuator/env | jq '.propertySources[].properties | keys'
curl http://localhost:8080/actuator/heapdump -o heap.bin && strings heap.bin | grep -i password | head
curl -X POST http://localhost:8080/actuator/loggers/ROOT -H 'Content-Type: application/json' \
  -d '{"configuredLevel":"DEBUG"}'
```

### 3.4 Unauthenticated internal endpoints

```bash
curl http://localhost:8080/internal/reindex     # destructive: wipes + rebuilds
```

### 3.5 Mass assignment and IDOR

```bash
# IDOR: fetch another tenant's order by guessing the id
curl -H "Authorization: Bearer $TOKEN_TENANT_A" http://localhost:8080/api/orders/2   # belongs to tenant B
# Mass assignment: set a field the client should not control
curl -X POST -H "Authorization: Bearer $TOKEN_VALID" -H 'Content-Type: application/json' \
  -d '{"sku":"X","qty":1,"totalAmount":0.01,"status":"APPROVED"}' http://localhost:8080/api/orders
```

**Deliverable**: `EXPLOIT_LOG.md` — each attempt, the exact request, the response status/body, and a one-line severity note. This document is what makes the fix PRs reviewable.

---

## Part 4 — Fix it

### 4.1 Identity: validate everything

```java
@Bean
JwtDecoder jwtDecoder(OAuth2ResourceServerProperties props) {
    NimbusJwtDecoder decoder = NimbusJwtDecoder
        .withIssuerLocation(props.getJwt().getIssuerUri())
        .jwsAlgorithm(SignatureAlgorithm.RS256)        // PINNED — never trust the header
        .build();
    decoder.setJwtValidator(JwtValidators.createDefaultWithIssuer(props.getJwt().getIssuerUri()));
    return decoder;
}
```

Convert scopes → authorities so `@PreAuthorize` works on scopes:

```java
@Bean
JwtAuthenticationConverter converter() {
    JwtGrantedAuthoritiesConverter gac = new JwtGrantedAuthoritiesConverter();
    gac.setAuthorityPrefix("SCOPE_");
    gac.setAuthoritiesClaimName("scope");            // or "scp" for some IdPs
    return new JwtAuthenticationConverter() {{ setJwtGrantedAuthoritiesConverter(gac); }};
}
```

### 4.2 Authorization: default deny, explicit grant

```java
@Configuration
@EnableMethodSecurity                       // without this, @PreAuthorize is silently ignored
class SecurityConfig {

    @Bean
    SecurityFilterChain chain(HttpSecurity http) throws Exception {
        return http
            .csrf(AbstractHttpConfigurer::disable)   // stateless bearer API only
            .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(a -> a
                .requestMatchers("/api/**").authenticated()
                .requestMatchers("/internal/**").hasAuthority("SCOPE_internal")
                .requestMatchers("/actuator/health/**").permitAll()
                .requestMatchers("/actuator/prometheus").hasAuthority("SCOPE_metrics")
                .anyRequest().denyAll())             // deny is the default
            .oauth2ResourceServer(o -> o.jwt(Customizer.withDefaults()))
            .headers(h -> h
                .contentSecurityPolicy(csp -> csp.policyDirectives(
                    "default-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'"))
                .frameOptions(f -> f.deny())
                .httpStrictTransportSecurity(hsts -> hsts
                    .includeSubDomains(true).maxAgeInSeconds(31_536_000)))
            .build();
    }
}
```

Method-level, per-operation:

```java
@PreAuthorize("hasAuthority('SCOPE_orders:read')")
@GetMapping("/api/orders/{id}") ...

@PreAuthorize("hasAuthority('SCOPE_orders:write')")
@PostMapping("/api/orders") ...

// tenant isolation in the query itself, not in a post-filter
@Query("select o from Order o where o.id = :id and o.tenantId = :tenant")
Optional<Order> findVisible(@Param("id") UUID id, @Param("tenant") String tenant);
```

### 4.3 Injection and limits

```java
@GetMapping("/api/orders")
public Page<OrderDto> list(@RequestParam(defaultValue = "0") @Max(10_000) int page,
                           @RequestParam(defaultValue = "20") @Max(100) int size,   // clamped
                           @RequestParam(defaultValue = "createdAt") String sort) {
    Sort s = Sort.by(WHITELIST.getOrDefault(sort, Sort.by(DESC, "createdAt")));    // allow-list
    return repo.findAll(PageRequest.of(page, size, s)).map(OrderDto::from);
}
private static final Map<String, Sort> WHITELIST = Map.of(
        "createdAt", Sort.by(DESC, "created_at"),
        "total",     Sort.by(DESC, "total_amount"));
```

Jackson hardening (kills polymorphic-deserialization RCE):

```java
@Bean
Jackson2ObjectMapperBuilderCustomizer jackson() {
    return b -> b.postConfigurer(mapper ->
        mapper.activateDefaultTyping(mapper.getPolymorphicTypeValidator(),
            ObjectMapper.DefaultTyping.NON_FINAL, JsonTypeInfo.As.PROPERTY));
}
```

With an explicit validator rather than `LaissezFaireSubTypeValidator`:

```java
mapper.setPolymorphicTypeValidator(BasicPolymorphicTypeValidator.builder()
    .allowIfSubType("com.company.orders.dto.")
    .build());
```

### 4.4 Actuator lockdown

```yaml
management:
  server:
    port: 9090
    address: 127.0.0.1
  endpoints:
    web:
      exposure:
        include: health,info,prometheus,metrics
  endpoint:
    health:
      probes:
        enabled: true
      show-details: never
```

Network policy so 9090 is reachable only from the monitoring namespace.

### 4.5 Logging, secrets, hardening

```xml
<appender name="JSON" class="ch.qos.logback.core.ConsoleAppender">
  <encoder class="net.logstash.logback.encoder.LogstashEncoder">
    <fieldNames>
      <timestamp>timestamp</timestamp>
      <level>level</level>
      <logger>logger</logger>
      <thread>thread</thread>
      <message>message</message>
      <stackTrace>stack_trace</stackTrace>
      <args/>              <!-- drop the raw MDC/args payload entirely -->
    </fieldNames>
  </encoder>
</appender>
```

Scrubbing filter that drops known-sensitive keys even if something slips through:

```java
public class SensitiveDataFilter extends TurboFilter {
    private static final Pattern SENSITIVE =
        Pattern.compile("(?i)\"(password|secret|token|authorization|cookie|card_?number|ssn)\"\\s*:\\s*\"[^\"]*\"");
    @Override public boolean accept(Marker marker, Logger logger, Level level, String format, Object[] params, Throwable t) {
        return !SENSITIVE.matcher(format == null ? "" : format).find();
    }
}
```

Secrets as mounted files, not env vars:

```yaml
volumes:
- name: db-creds
  secret:
    secretName: orders-db-creds        # synced by an external-secrets operator from Vault
items: [{ key: password, path: db.password }]
volumeMounts:
- { name: db-creds, mountPath: /run/secrets, readOnly: true }
```

```yaml
spring:
  datasource:
    password: file:/run/secrets/db.password   # resolved at startup, never in the process env
```

---

## Part 5 — Prove it with tests that fail when the fix is removed

```java
@SpringBootTest
@AutoConfigureMockMvc
class SecurityRegressionTest {

    @Test void rejectsWrongAudience() throws Exception {
        mockMvc.perform(get("/api/orders/1").header("Authorization", "Bearer " + tokens.wrongAudience()))
            .andExpect(status().isUnauthorized());
    }

    @Test void rejectsAlgNone() throws Exception {
        // A token signed with alg:none but a well-formed structure.
        mockMvc.perform(get("/api/orders/1").header("Authorization", "Bearer " + tokens.unsigned()))
            .andExpect(status().isUnauthorized());
    }

    @Test void requiresWriteScopeForPost() throws Exception {
        mockMvc.perform(post("/api/orders").header("Authorization", "Bearer " + tokens.readOnly())
                        .contentType(MediaType.APPLICATION_JSON).content("{}"))
            .andExpect(status().isForbidden());          // 403, not 401: authenticated but unauthorized
    }

    @Test void hidesAnotherTenantsOrder() throws Exception {
        mockMvc.perform(get("/api/orders/999").header("Authorization", "Bearer " + tokens.tenantA()))
            .andExpect(status().isNotFound());          // 404 not 403: do not confirm existence
    }

    @Test void clampsPageSize() throws Exception {
        mockMvc.perform(get("/api/orders?size=1000000").header("Authorization", "Bearer " + tokens.full()))
            .andExpect(status().is4xxClientError())
            .andExpect(jsonPath("$.page.size").value(lessThanOrEqualTo(100)));
    }

    @Test void sortIsAllowListed() throws Exception {
        // With the allow-list, the injected sort clause is ignored rather than executed.
        mockMvc.perform(get("/api/orders?sort=id;drop%20table%20users").header("Authorization", "Bearer " + tokens.full()))
            .andExpect(status().isOk());
        assertThat(jdbc.queryForObject("select count(*) from users", Integer.class)).isPositive();
    }

    @Test void actuatorIsLockedDown() throws Exception {
        mockMvc.perform(get("/actuator/env")).andExpect(status().isNotFound());
        mockMvc.perform(get("/actuator/heapdump")).andExpect(status().isNotFound());
        mockMvc.perform(post("/actuator/loggers/ROOT").content("{}")).andExpect(status().isNotFound());
    }

    @Test void internalEndpointRequiresServiceScope() throws Exception {
        mockMvc.perform(post("/internal/reindex")).andExpect(status().isUnauthorized());
        mockMvc.perform(post("/internal/reindex").header("Authorization", "Bearer " + tokens.user()))
            .andExpect(status().isForbidden());
    }

    @ParameterizedTest
    @ValueSource(strings = {"/api/orders", "/internal/metrics/raw", "/actuator/env"})
    void securityHeadersPresent(String path) throws Exception {
        mockMvc.perform(get(path))
            .andExpect(header().string("X-Content-Type-Options", "nosniff"))
            .andExpect(header().string("Strict-Transport-Security", containsString("31536000")))
            .andExpect(header().exists("Content-Security-Policy"));
    }
}
```

**Acceptance**: re-introduce each defect one at a time (remove `@EnableMethodSecurity`, restore the concatenated query, widen the actuator exposure) and show exactly one test fails each time. That is what proves the tests have teeth.

---

## Part 6 — The CI gate

```yaml
# .github/workflows/security.yml
security:
  steps:
    - uses: actions/checkout@v4
    - run: trivy fs --scanners vuln,secret,misconfig --exit-code 1 --severity HIGH,CRITICAL .
    - run: semgrep ci --config=p/java --config=p/spring --error --sarif-output=semgrep.sarif
    - run: syft . -o cyclonedx-json > sbom.json && trivy sbom sbom.json --exit-code 1 --severity HIGH,CRITICAL .
    - name: Authorization coverage check
      run: ./ci/check-authz-coverage.sh          # fails if any @RestController path lacks a matcher or @PreAuthorize
    - name: No trust-all TLS
      run: |
        ! grep -rn --include=*.java -E 'X509TrustManager|NoopHostnameVerifier|ALLOW_ALL_HOSTNAME_VERIFIER|TrustAllCerts' src/
    - name: No secrets
      run: ! grep -rnE '(password|secret|token|api[_-]?key)\s*[:=]\s*["'"'"'][^"'"'"']{8,}' src/ --include=*.java
    - run: ./mvnw -q verify                       # includes the SecurityRegressionTest suite
```

`check-authz-coverage.sh`:

```bash
#!/usr/bin/env bash
# Every @RequestMapping path must appear in a security matcher or carry an authorization annotation.
set -euo pipefail
fail=0
for f in $(grep -rl '@RestController\|@Controller' src/main/java); do
  paths=$(grep -oP '@(Get|Post|Put|Delete|Patch|Request)Mapping\(([^)]*)\)?' "$f" || true)
  for p in $paths; do
    if ! grep -qE "requestMatchers\(" src/main/java --include=*Config.java; then :; fi
    if ! grep -q '@PreAuthorize' "$f"; then
      echo "FAIL: $f has a mapped endpoint but no @PreAuthorize and no verified matcher"; fail=1
    fi
  done
done
exit $fail
```

**Acceptance**: open a PR that (a) adds an endpoint without authorization, (b) reintroduces a concatenated query, (c) adds a hardcoded password. All three fail the pipeline with a specific message.

---

## Part 7 — Supply-chain drill

1. Generate an SBOM: `syft . -o cyclonedx-json > sbom.json`.
2. Pick a real advisory affecting one of your dependencies.
3. Answer: which of our artifacts and which images contain it? How long did that take?

**Deliverable**: `SBOM_DRILL.md` with the advisory, the query, the affected-artifact list, and the wall-clock minutes. Then patch and re-verify.

---

## Acceptance Criteria

- [ ] `FINDINGS_BASELINE.md` has 20+ findings from at least three tools, ranked, each with exploitability notes.
- [ ] `EXPLOIT_LOG.md` shows real 200s for at least 5 vulnerability classes before the fix.
- [ ] All `SecurityRegressionTest` cases pass after the fix, and each fails when its defect is re-introduced.
- [ ] Actuator exposes only `health,info,prometheus,metrics` on a separate, network-restricted port; `env`/`heapdump`/`loggers` return 404.
- [ ] No secret is reachable from `/proc/<pid>/environ`, and secrets come from a mounted file.
- [ ] Logs contain no token, password, or PII field — proven by grepping a captured 10k-request log sample.
- [ ] The CI gate blocks all three deliberately vulnerable PRs.
- [ ] `SBOM_DRILL.md` answers an advisory-to-fleet question in under 5 minutes.

---

## Stretch

- Add property-based tests (jqwik) generating random request shapes to hunt for the injection/DoS paths you did not enumerate.
- Add a `NetworkPolicy` + separate management port and verify reachability from inside and outside the cluster.
- Implement step-up authentication: a low-value scope requires a fresh `auth_time` in the token.
- Add an OPA/Rego policy check for "no endpoint may return a field containing PII without a declared classification."
