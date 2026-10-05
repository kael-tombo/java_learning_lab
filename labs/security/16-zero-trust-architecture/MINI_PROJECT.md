# Zero Trust Architecture - MINI PROJECT

## Project: TrustFence — three services that trust nothing implicitly

Build a small estate: an API gateway, an orders service, and a database-access proxy.
Every call is authenticated with mTLS, authorized by policy, and permitted only by explicit
network policy. Then demonstrate that compromising one service does not yield lateral movement.

### Architecture

```
   Untrusted client
        │  (no network position is trusted; identity is)
        ▼
   ┌────────────┐  mTLS + policy  ┌──────────────┐  mTLS + policy  ┌──────────┐
   │  Gateway   │─────────────────▶│ Orders Svc   │─────────────────▶│ DB Proxy │
   │ (no trust  │                 │ (no trust to │                 │ (only    │
   │  to its    │                 │  anything    │                 │  DB      │
   │  network)  │                 │  by default) │                 │  access) │
   └────────────┘                 └──────────────┘                 └──────────┘
        ▲                                ▲                              ▲
   identity: user JWT              identity: SPIFFE-style          identity: mTLS
   + device posture               workload cert (short TTL)        + k8s policy

   Default deny: orders Svc can ONLY reach DB Proxy. It has NO route to payments Svc.
```

### Implementation

Workload identity with short-lived certificates, verified by the receiving side:

```java
@Component
class MutualTlsConfig {
    /** Certs come from the platform's workload identity API, not from a mounted PEM on disk. */
    @Bean
    SslContext outboundSslContext() {
        return SslContextBuilder.forClient()
            .sslProvider(JdkSslProvider.builder().build())
            .keyManager(new WorkloadKeyManager(workloadIdentityClient))   // presents spiffe://…
            .trustManager(new PlatformTrustManager(platformRootCas()))
            .build();
    }

    @Bean
    SslContext inboundSslContext() {
        return SslContextBuilder.forServer(workloadIdentityClient.currentCertChain(),
                                           workloadIdentityClient.currentPrivateKey())
            // Require and verify the client certificate: mutual TLS, not just server TLS.
            .clientAuth(ClientAuth.REQUIRE)
            .trustManager(new PlatformTrustManager(platformRootCas()))
            .build();
    }
}
```

Policy as code, evaluated per request rather than at connection time:

```java
@Component
class PerRequestPolicyEnforcer {
    /**
     * The point of zero trust: authorization is evaluated for THIS request from identity +
     * posture, not inferred from "which network did it arrive on".
     */
    @PostConstruct
    void loadPolicy() {
        engine.load(Rego.text().query("""
            package authz
            default decision := {"allow": false, "reason": "default deny"}

            decision := {"allow": true, "reason": "workload may call its declared dependencies"}
              if {
                input.subject.spiffe_id == "spiffe://example/ns/payments/sa/orders"
                input.method == "POST"
                startswith(input.path, "/v1/orders")
                input.request.posture.compliant == true      # device/workload posture gate
                input.subject.issued_at + token.lifetime > time.now_ns()   # cert still fresh
              }

            decision := {"allow": false, "reason": "stale identity"}
              if { time.now_ns() - input.subject.issued_at > 900 * 1000000000 }
            """));
    }

    Decision authorize(HttpRequest req, VerifiedIdentity subject, Posture posture) {
        Decision d = engine.eval(Map.of(
                "method", req.method(), "path", req.path(),
                "subject", subject.toMap(), "request", Map.of("posture", posture.toMap())));
        if (!d.allowed()) audit.deny(subject, req, d.reason());   // deny is a first-class signal
        return d;
    }
}
```

Micro-segmentation: the orders service simply has no route to anything except the proxy.
This is the control that contains a compromise, independent of application bugs:

```java
@Component
class OutboundEgressGuard {
    /** Applied to every outbound call. The service physically cannot reach other services. */
    void verify(URI target) {
        if (!policyRegistry.isDeclaredDependency(target)) {
            throw new EgressDeniedException(target, "not a declared dependency of this workload");
        }
    }
}
// In Kubernetes, the same guarantee comes from NetworkPolicy egress rules that name only
// the DB proxy's pod selector - the gateway and payments services are unreachable.
```

Device/workload posture feeding the decision, so risk is continuous rather than assumed:

```java
@Service
class PostureService {
    /** Signals here are workload-flavoured: image digest signed?, patched?, network exposure? */
    Posture assess(WorkloadId id) {
        boolean signedImage   = registry.isSignedBy(imageOf(id));
        boolean noCriticalCves = cveGate.isClean(imageOf(id));
        boolean notExposed    = !networkPolicy.hasIngressRule(id);
        return new Posture(signedImage && noCriticalCves && notExposed,
                           "image=%s,cves=%s,ingress=%s", signedImage, noCriticalCves, notExposed);
    }
}
```

### Test It

```java
@Test void noClientCertificateIsRejected() {
    // Server presents only its own cert; the client is anonymous and must be refused.
    assertThrows(SSLException.class, () -> connectWithoutClientCert());
}

@Test void unrelatedWorkloadIdentityIsRejected() {
    // A valid cert from a DIFFERENT service is still refused: identity must match the policy.
    var res = callAs("spiffe://example/ns/search/sa/indexer", "GET", "/v1/orders");
    assertThat(res.status()).isEqualTo(403);
    assertThat(res.body()).contains("default deny");
}

@Test void compromisedServiceCannotReachPaymentService() {
    // Simulate full compromise of orders: it still has no network route to payments.
    assertThrows(ConnectException.class, () -> callFromCompromisedOrders("https://payments/v1/charge"));
}

@Test void expiredIdentityIsDenied() {
    // Cert older than the freshness window: denied even though the signature is valid.
    var res = callWithStaleIdentity("spiffe://example/ns/payments/sa/orders", ageSeconds: 1200);
    assertThat(res.status()).isEqualTo(403);
    assertThat(res.body()).contains("stale identity");
}
```

## Deliverables

- [ ] mTLS in both directions with workload identity and platform trust roots
- [ ] Per-request policy evaluation (Rego or equivalent) with default deny
- [ ] SPIFFE-style identity, short TTL, and an explicit freshness check in policy
- [ ] Egress guard plus NetworkPolicy proving no lateral route to unrelated services
- [ ] Posture service gating access on image signature, CVE state, and exposure
- [ ] Deny-path audit logging for every policy decision
- [ ] Tests: missing cert, wrong identity, no lateral route, stale identity
- [ ] Trust-boundary diagram of the mini-estate in the README
