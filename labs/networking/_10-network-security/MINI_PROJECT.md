# Network Security - MINI PROJECT

## Project: SecureLink — mTLS service-to-service calls with a real certificate lifecycle

Two services that only accept each other over mutual TLS, backed by a small certificate
authority. Includes deliberate failure cases: wrong issuer, expired cert, hostname mismatch,
and a rotated certificate still trusted during the overlap window.

### Architecture

```
  orders-svc ──mTLS──▶ payments-svc
     │                     │
     │  both present a     │
     │  client certificate │
     │  issued by our CA   │
     ▼                     ▼
  ┌──────────────┐   ┌──────────────┐
  │ Client       │   │ Server       │
  │ KeyStore:    │   │ KeyStore:    │
  │  client cert │   │  server cert │
  │  + client key│   │  + CA trust  │
  └──────────────┘   │ TrustStore:  │
                     │  CA only     │
                     └──────────────┘

  CA (issuing)
    - issues server + client certs with SANs
    - enforces key usage: digitalSignature for TLS, NOT keyEncipherment on modern certs
    - short-lived client certs (24h) with automatic renewal
    - revocation via a CRL endpoint

  Network segmentation (see segmentation policy below): default deny east-west.
```

### Implementation

A minimal issuing CA, so certificate semantics are understood rather than delegated:

```java
@Component
class CertificateAuthority {
    private final KeyPair caKeyPair;      // offline-capable, protected key
    private final X500Name caSubject = new X500Name("CN=Internal Lab CA, O=Lab, C=NL");

    /** Server cert with SANs. CN alone is deprecated: hostname verification uses SAN. */
    X509Certificate issueServer(String hostname, List<String> altNames, Duration validity) {
        var builder = baseCertBuilder(caSubject, "SHA256withECDSA", validity);
        // SANs MUST include the exact hostname the client will dial. A CN-only cert
        // works in old code and fails hostname verification in everything modern.
        var sanBuilder = new GeneralName[] {
                new GeneralName(GeneralName.dNSName, hostname),
                altNames.stream().map(n -> (GeneralName) new GeneralName(GeneralName.dNSName, n))
                        .toArray(GeneralName[]::new)
        };
        builder.addExtension(Extension.subjectAlternativeName, false, new GeneralNames(sanBuilder));
        // Key usage: digitalSignature is what TLS 1.3 needs. keyEncipherment is a legacy
        // RSA key-transport usage that modern TLS does not use.
        builder.addExtension(Extension.keyUsage, true, new KeyUsage(KeyUsage.digitalSignature));
        // Extended key usage: serverAuth only, so the cert cannot be reused as a client cert.
        builder.addExtension(Extension.extendedKeyUsage, false, new ExtendedKeyUsage(KeyPurposeId.id_kp_serverAuth));
        return sign(builder.build(csrPublicKey, caKeyPair.getPrivate()));
    }

    X509Certificate issueClient(String serviceName, Duration validity) {
        var builder = baseCertBuilder(caSubject, "SHA256withECDSA", validity);
        // A client cert identifies a WORKLOAD, not a person, so the SAN is a URI SPIFFE ID.
        // Reusing a person's identity here would conflate user auth with workload auth.
        builder.addExtension(Extension.subjectAlternativeName, false, new GeneralNames(
                new GeneralName(GeneralName.uniformResourceIdentifier, "spiffe://lab.internal/ns/prod/sa/" + serviceName)));
        builder.addExtension(Extension.extendedKeyUsage, false,
                new ExtendedKeyUsage(KeyPurposeId.id_kp_clientAuth));
        return sign(builder.build(publicKey, caKeyPair.getPrivate()));
    }
}
```

The mutual TLS client with hostname verification that actually verifies:

```java
@Component
class MutualTlsClient {
    private final SSLContext sslContext;

    MutualTlsClient(CertificateAuthority ca) {
        var kmf = KeyManagerFactory.getInstance(KeyManagerFactory.getDefaultAlgorithm());
        kmf.init(clientKeyStore(), "changeit".toCharArray());       // our client cert + key
        var tmf = TrustManagerFactory.getInstance(TrustManagerFactory.getDefaultAlgorithm());
        tmf.init(caTrustStore());                                   // trust the CA, not the leaf

        var ctx = SSLContext.getInstance("TLSv1.3");
        ctx.init(kmf.getKeyManagers(), tmf.getTrustManagers(), SecureRandom.getInstanceStrong());
        this.sslContext = ctx;
    }

    HttpResponse<String> call(String service, String path) throws IOException {
        var client = HttpClient.newBuilder().sslContext(sslContext)
            .connectTimeout(Duration.ofSeconds(5))
            .version(HttpClient.Version.HTTP_2)      // ALPN negotiates h2 over TLS 1.3
            .build();
        var request = HttpRequest.newBuilder(URI.create("https://" + service + path))
            .header("Content-Type", "application/json")
            .build();
        return client.send(request, HttpResponse.BodyHandlers.ofString());
    }
}
```

Certificate validation on the server, where the trust decision is actually made:

```java
@Component
class ClientCertificateValidator {
    /**
     * PKIX validation is the baseline: chain to a trusted root, check validity dates, check
     * key usage, check revocation. PKIX does NOT check that the certificate is the one you
     * expect for this peer - that is authorisation, and it needs its own step.
     */
    void validate(X509Certificate clientCert) {
        try {
            certPathValidator.validate(new CertPathBuilder()
                    .addCertificate(clientCert)
                    .build());   // uses trust anchors from the trustStore, revocation enabled
        } catch (CertPathValidatorException e) {
            throw new UntrustedClientException("client certificate failed PKIX validation: " + e.getMessage());
        }
        // Now the authorisation check PKIX cannot do: is this SPECIFIC identity allowed
        // to call THIS endpoint? A valid certificate is not an authorisation decision.
        var spiffeId = spiffeIdFrom(clientCert);
        if (!allowedIdentities.forPath(currentPath()).contains(spiffeId))
            throw new NotAuthorizedException("identity " + spiffeId + " not permitted on " + currentPath());
    }
}
```

The certificate lifecycle, which is the operational part people omit:

```java
@Component
class CertificateLifecycle {
    private static final Duration CLIENT_CERT_LIFETIME = Duration.ofHours(24);

    /**
     * Short-lived client certificates remove a whole class of incident: a leaked client
     * key is useful for at most 24 hours, with no revocation ceremony needed. The renewal
     * runs at HALF the lifetime so a failure is recoverable before expiry.
     */
    @Scheduled(fixedDelay = 12 * 3600_000L, initialDelay = 60_000)
    void rotateClientCertificate() {
        var current = currentClientCert();
        if (Instant.now().isAfter(current.notAfter().minus(CLIENT_CERT_LIFETIME.dividedBy(2)))) {
            var renewed = ca.issueClient(serviceName(), CLIENT_CERT_LIFETIME);
            keystore.replace(renewed, ca.signWith(renewed));     // atomic swap of the key entry
            metrics.counter("mtls.cert.rotated");
            audit.certificateRotated(renewed.serialNumber(), renewed.notAfter());
        }
    }

    /**
     * Emergency revocation. If a client key is suspected compromised, the 24-hour window
     * is too long, so the CA publishes a CRL and the affected identity is blocked by
     * the authorization list immediately - two independent controls.
     */
    void revokeForIncident(String spiffeId, String reason) {
        ca.revoke(spiffeId, reason);
        authorizationLists.block(spiffeId);
        audit.emergencyRevocation(spiffeId, reason);
    }
}
```

Network segmentation, default deny east-west, expressed and testable:

```java
/**
 * Segmentation is a CONTAINMENT control: it bounds how far a compromise travels. It is not
 * an access control (that is mTLS plus authorization above) - it is what stops a service
 * that is fully compromised from reaching everything else.
 */
record NetworkPolicy(
    String fromZone, Set<String> fromSelectors,
    String toZone, Set<String> toSelectors,
    Set<Integer> allowedPorts,
    String protocol,
    String rationale) {

    /** Default deny is implicit: a flow not matched by any policy is dropped. */
    static final List<NetworkPolicy> POLICIES = List.of(
        new NetworkPolicy("gateway", Set.of("app=gateway"), "orders", Set.of("app=orders"),
                Set.of(8443), "TCP", "edge to orders only"),
        new NetworkPolicy("orders", Set.of("app=orders"), "payments", Set.of("app=payments"),
                Set.of(8443), "TCP", "orders may call payments"),
        new NetworkPolicy("orders", Set.of("app=orders"), "database", Set.of("app=postgres"),
                Set.of(5432), "TCP", "orders reaches exactly one database"),
        // Deliberately absent: orders -> payments-database. If orders needs it, that is an
        // architecture conversation, not a firewall rule to be quietly added at 2am.
        new NetworkPolicy("monitoring", Set.of("app=prometheus"), "*", Set.of("*"),
                Set.of(9100, 8080), "TCP", "scraping only, no database access")
    );

    static List<NetworkPolicy> flowsFrom(String zone, String selector) {
        return POLICIES.stream()
                .filter(p -> p.fromZone().equals(zone) && p.fromSelectors().contains(selector))
                .toList();
    }
}
```

### Test It

```java
@Test void validMutualTlsCallSucceeds() throws Exception {
    var response = client.call("payments.lab.internal", "/v1/charge");
    assertThat(response.statusCode()).isEqualTo(200);
    assertThat(response.sslSession().getProtocol()).isEqualTo("TLSv1.3");
    assertThat(response.sslSession().getPeerPrincipal().getName()).contains("payments.lab.internal");
}

@Test void callFromUntrustedClientIsRejected() throws Exception {
    var rogueContext = contextWithSelfSignedClientCert();   // not issued by our CA
    assertThrows(SSLHandshakeException.class,
        () -> sendWith(rogueContext, "https://payments.lab.internal/v1/charge"));
}

@Test void expiredCertificateIsRejected() throws Exception {
    var expired = ca.issueServer("payments.lab.internal", List.of(), Duration.ofSeconds(-1));
    assertThrows(SSLHandshakeException.class, () -> connectUsing(expired));
    // The error the operator sees must be actionable, not "handshake failure".
    assertThat(server.lastHandshakeError()).contains("certificate expired");
}

@Test void hostnameMismatchIsRejected() throws Exception {
    var wrongHost = ca.issueServer("other.internal", List.of(), Duration.ofDays(30));
    assertThrows(SSLHandshakeException.class, () -> connectDialing("payments.lab.internal", wrongHost));
}

@Test void validCertificateButWrongIdentityIsRejected() {
    // A legitimate cert from a service that is not allowed on this path. PKIX passes;
    // authorisation must fail. This is the distinction PKIX does not cover.
    ca.issueClient("reporting-svc", Duration.ofHours(1));
    assertThrows(NotAuthorizedException.class, () -> validator.validate(reportingCert, "/v1/charge"));
}

@Test void rotationKeepsExistingConnectionsWorking() throws Exception {
    // Overlap: the new cert is installed BEFORE the old one is removed, so no window exists
    // in which a peer trusts neither.
    lifecycle.rotateClientCertificate();
    assertThat(client.call("payments.lab.internal", "/v1/charge").statusCode()).isEqualTo(200);
}

@Test void lateralMovementIsBlockedBySegmentation() {
    // orders has NO policy reaching the payments database. Even a full compromise of orders
    // cannot open this path, which is the entire point of segmentation.
    var reachableFromOrders = NetworkPolicy.flowsFrom("orders", "app=orders");
    assertThat(reachableFromOrders).extracting(NetworkPolicy::toZone).doesNotContain("payments-db");
}
```

## Deliverables

- [ ] Issuing CA with SAN-based server and client certificates and correct key usage
- [ ] TLS 1.3 mutual handshake with hostname verification and ALPN
- [ ] PKIX validation plus a separate authorisation step for identity-to-path mapping
- [ ] Certificate rotation at half the lifetime, with an atomic keystore swap
- [ ] Emergency revocation via CRL plus an authorisation block, as two independent controls
- [ ] Default-deny segmentation policy with a documented rationale per flow
- [ ] Tests: untrusted client, expired cert, hostname mismatch, wrong identity, lateral movement
- [ ] A certificate inventory with expiry monitoring and an alert threshold of 14 days
