# Keycloak - MINI PROJECT

## Project: IdentityForge — provision a whole identity estate from code, not clicks

Run Keycloak in Testcontainers, then create the entire company identity setup
(realm, clients, roles, groups, a service account, protocol mappers) through the admin
REST API. Your Java app provisions it, diffs it, and reports drift.

### Architecture

```
        IdentityForge (Java 21 admin client)
                 │  admin REST API, service account token
                 ▼
        ┌──────────────────┐        ┌────────────────────────────┐
        │  Keycloak        │───────▶│  realm: acme               │
        │  (Testcontainer)  │  JWKS  │   client: order-api (conf) │
        └──────────────────┘        │   client: portal  (public) │
                 ▲                  │   roles: ORDER_READ/WRITE  │
                 │                  │   mapper: audience=order-api│
      realm-export.json ───────────└────────────────────────────┘
                 ▼
          DesiredState reconciler -> drift report -> CI exit code
```

### Implementation

```java
public class RealmProvisioner {
    private final String base;
    private final HttpClient http;
    private final String adminToken;

    public void provision() throws Exception {
        if (realmExists(REALM)) return;                       // idempotent
        try (var in = getClass().getResourceAsStream("/realm-desired.json")) {
            http.send(json(HttpRequest.newBuilder(URI.create(base + "/admin/realms"))
                    .header("Authorization", "Bearer " + adminToken)
                    .POST(HttpRequest.BodyPublishers.ofInputStream(() -> in)).build(),
                HttpResponse.BodyHandlers.ofString());
        }
    }

    /** Service account = client credentials identity; roles must be granted explicitly. */
    public void grantServiceAccountRoles(String clientId, String... realmRoles) throws Exception {
        String serviceAccountUserId = lookupServiceAccountUser(clientId);
        for (String role : realmRoles) {
            http.send(json(HttpRequest.newBuilder(
                        URI.create(base + "/admin/realms/" + REALM + "/users/" + serviceAccountUserId
                                 + "/role-mappings/realm"))
                    .POST(HttpRequest.BodyPublishers.ofString(
                            "[{\"id\":\"" + roleId(role) + "\",\"name\":\"" + role + "\"}]")).build()),
                HttpResponse.BodyHandlers.ofString());
        }
    }

    /**
     * Protocol mapper is what makes OUR resource server accept the token.
     * Without an audience, a token minted for another client will fail `aud` validation.
     */
    public void addAudienceMapper(String clientId, String expectedAudience) throws Exception {
        String mapper = """
            {"name":"audience","protocol":"openid-connect","protocolMapper":"oidc-audience-mapper",
             "config":{"included.client.audience":"%s","access.token.claim":"true","id.token.claim":"false"}}"""
            .formatted(expectedAudience);
        http.send(json(HttpRequest.newBuilder(URI.create(
                    base + "/admin/realms/" + REALM + "/clients/" + clientId + "/protocol-mappers/models"))
                .POST(HttpRequest.BodyPublishers.ofString(mapper)).build()),
            HttpResponse.BodyHandlers.ofString());
    }
}
```

The Spring Boot side trusts only the issuer and the JWKS — no shared secrets:

```java
@SpringBootApplication
public class OrderApiApplication { }

@SpringBootApplication
class SecurityBeans {
    @Bean
    JwtDecoder jwtDecoder(@Value("${spring.security.oauth2.resourceserver.jwt.issuer-uri}") String issuer) {
        // Nimbus discovers JWKS from the issuer's discovery document and caches it.
        return JwtDecoders.fromIssuerLocation(issuer);
    }

    @Bean
    SecurityFilterChain chain(HttpSecurity http) throws Exception {
        return http.csrf(AbstractHttpConfigurer::disable)
            .sessionManagement(s -> s.sessionCreationPolicy(STATELESS))
            .authorizeHttpRequests(a -> a
                .requestMatchers("/api/orders/**").hasAuthority("SCOPE_order.read")
                .anyRequest().authenticated())
            .oauth2ResourceServer(o -> o.jwt(jwt -> jwt
                .jwtAuthenticationConverter(new KeycloakJwtAuthenticationConverter())))
            .build();
    }
}
```

### Test It

```java
@Test void realmIsCreatedIdempotently() {
    provisioner.provision(); provisioner.provision();       // second call is a no-op
    assertThat(clientExists("order-api")).isTrue();
}

@Test void driftIsDetected() {
    deleteRoleSilently("ORDER_WRITE");                       // simulate manual edit
    assertThat(provisioner.diffAgainstDesired()).contains("ORDER_WRITE");
}

@Test void serviceAccountGetsNoImplicitRoles() {
    provisioner.grantServiceAccountRoles("order-api", "ORDER_READ");
    try (Keycloak kc = keycloak.start()) {
        String t = kc.clientCredentialsToken("order-api");
        assertThat(claims(t).get("scope")).contains("order.read");
        assertThat(claims(t).get("scope")).doesNotContain("order.write");
    }
}
```

## Deliverables

- [ ] Keycloak in Testcontainers with a programmatic stop/start lifecycle
- [ ] `realm-desired.json` covering realm, clients, roles, groups, mapper
- [ ] Idempotent provisioner: run twice, second run changes nothing
- [ ] Drift detector reporting manual edits, with a non-zero CI exit code
- [ ] Service-account role granting via the admin API
- [ ] Audience protocol mapper so `aud` validation succeeds
- [ ] Spring Boot resource server using `JwtDecoders.fromIssuerLocation`
- [ ] Test asserting a service account gets only its explicitly granted scope
