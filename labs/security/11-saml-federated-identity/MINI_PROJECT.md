# SAML 2.0 Federated Identity - MINI PROJECT

## Project: FederationDemo — a Spring Boot SP that trusts a Keycloak IdP

Implement SP-initiated SSO, single logout, and metadata-driven configuration. Add a
signature-wrapping attack test that proves your validator is not fooled.

### Architecture

```
 Browser                SP (your app)                    IdP (Keycloak)
    │  GET /saml2/authenticate/{registrationId}
    ├──────────────────────────▶
    │                           ├─ build AuthnRequest (HTTP-Redirect binding)
    │◀──────────────────────────┤  302 to IdP SSO URL with SAMLRequest
    │  authenticate at IdP
    ├─────────────────────────────────────────────────────▶ IdP
    │◀─────────────────────────────────────────────────────┤  302 with SAMLResponse
    │  POST /login/saml2/sso/{registrationId}              │
    ├──────────────────────────▶
    │                           ├─ 1. validate XML signature over the Response/Assertion
    │                           ├─ 2. validate Conditions: Audience, NotBefore/NotOnOrAfter
    │                           ├─ 3. extract NameID + attributes into a JWT session
    │                           └─ 4. store SecurityContext in session
    ◀──────────────────────────┤  302 to app
    SLO: POST /saml2/logout/{registrationId} ──────────────▶ IdP
```

### Implementation

Spring Security's `OpenSaml4AuthenticationProvider` does the hard XML work; the value you
add is the wiring, the attribute mapping, and the tests:

```java
@Configuration
@EnableWebSecurity
class SamlSpSecurity {

    @Bean
    SecurityFilterChain sp(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(a -> a.anyRequest().authenticated())
            .saml2Login(Customizer.withDefaults())
            .saml2Logout(Customizer.withDefaults())
            .exceptionHandling(e -> e
                .saml2Login(s -> s.authenticationFailureUrl("/login/saml2/failure"))
                // Never redirect an error back to the IdP ACS: the "open redirect" class of
                // bug in SAML implementations starts exactly here.
                .defaultAuthenticationEntryPointFor(new LoginUrlAuthenticationEntryPoint("/saml2/authenticate/keycloak"), matcher));
        return http.build();
    }

    @Bean
    RelyingPartyRegistrationRepository registrations(IdpMetadataService metadata) {
        RelyingPartyRegistration keycloak = RelyingPartyRegistration
            .withRegistrationId("keycloak")
            .assertingPartyMetadata(metadata.fetch("keycloak"))   // live metadata, not a hardcoded cert
            .entityId("{baseUrl}/saml2/service-provider-metadata/{registrationId}")
            .assertionConsumerServiceLocation("{baseUrl}/login/saml2/sso/{registrationId}")
            .signatureCredentials(signingCredential())              // SP request signing
            .build();
        return new InMemoryRelyingPartyRegistrationRepository(keycloak);
    }
}
```

IdP metadata is fetched, parsed, and cached with pinning of the signing certificate by
thumbprint so a rogue metadata document cannot substitute its own key:

```java
@Component
class IdpMetadataService {
    private final Saml2MetadataTransformer transformer = new Saml2MetadataTransformer();
    private final Cache<String, Saml2Metadata> cache = Caffeine.newBuilder()
            .expireAfterWrite(Duration.ofHours(1))
            .expireAfterAccess(Duration.ofMinutes(30))
            .build();

    Saml2Metadata fetch(String idp) {
        return cache.get(idp, this::downloadAndParse);
    }

    private Saml2Metadata downloadAndParse(String idp) {
        URI uri = configuredMetadataUrl(idp);                    // https://idp/realms/x/protocol/saml/descriptor
        HttpResponse<byte[]> res = http.send(HttpRequest.newBuilder(uri).GET().build(),
                                             HttpResponse.BodyHandlers.ofByteArray());
        // SSRF guard: the URL comes from config, not user input, but validate the scheme and
        // block private ranges so a config mistake cannot reach internal metadata endpoints.
        guardPublicUrl(uri);
        Saml2Metadata md = transformer.transform(new ByteArrayResource(res.body()));
        verifyPinnedThumbprint(idp, md);                         // fail if the IdP cert rotated unexpectedly
        return md;
    }
}
```

Mapping SAML attributes into a usable principal, with a fail-closed default:

```java
@Component
class SamlAttributeMapper {
    static final String ROLE_CLAIM = "urn:oid:2.5.4.42";        // givenName, example attribute OIDs

    SamlPrincipal map(Saml2AuthenticatedPrincipal p) {
        Map<String, List<String>> attrs = p.getAttributes();
        String email = first(attrs, "email", "mail", "urn:oid:0.9.2342.19200300.100.1.3");
        if (email == null) throw new BadCredentialsException("IdP provided no email attribute");
        Set<String> roles = new HashSet<>(attrs.getOrDefault("Role", List.of("ROLE_USER")));
        return new SamlPrincipal(p.getName(), email, p.getSessionIndexes(), roles);
    }
}
```

### Test It

```java
@Test void spInitiatedSsoEstablishesSession() {
    mvc.perform(get("/saml2/authenticate/keycloak")).andExpect(3xx().url(startsWith(idpSsoUrl())));
    mvc.perform(post("/login/saml2/sso/keycloak").param("SAMLResponse", base64(capturedResponse)))
       .andExpect(redirectedUrl("/home")).andExpect(request().session().exists());
}

@Test void signatureWrappingIsRejected() {
    // Move the legitimate signature onto a decoy assertion and change the used one.
    String wrapped = signatureWrapAttack(capturedResponse);
    assertThrows(Saml2AuthenticationException.class,
        () -> mvc.perform(post("/login/saml2/sso/keycloak").param("SAMLResponse", base64(wrapped))));
}

@Test void expiredConditionsAreRejected() {
    String expired = withNotOnOrAfterInThePast(capturedResponse);
    assertThrows(Saml2AuthenticationException.class,
        () -> mvc.perform(post("/login/saml2/sso/keycloak").param("SAMLResponse", base64(expired))));
}

@Test void metadataCertRotationBreaksPinning() {
    assertThrows(MetadataTrustException.class, () -> service.fetch("idp-with-unexpected-cert"));
}
```

## Deliverables

- [ ] SP-initiated SSO against Keycloak with `RelyingPartyRegistration`
- [ ] Single logout (SLO) with local session invalidation
- [ ] Metadata-driven IdP config with caching and certificate thumbprint pinning
- [ ] `Saml2AuthenticatedPrincipal` → app principal attribute mapping, fail-closed
- [ ] SSRF guard on the metadata fetch path
- [ ] Tests: successful SSO, signature wrapping, expired conditions, metadata mismatch
- [ ] A captured-response fixture committed for use as a test resource
- [ ] README annotating the SAML response element by element
