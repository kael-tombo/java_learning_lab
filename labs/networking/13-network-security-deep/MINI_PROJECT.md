# Network Security Deep - MINI PROJECT

## Project: Aegis — an mTLS service with an automated certificate lifecycle and measured segmentation

Three services, mutual TLS everywhere, an issuing authority with automatic rotation, and
a segmentation policy you verify by actually attempting lateral movement.

### Architecture

```
  client-svc ──mTLS──▶ orders-svc ──mTLS──▶ payments-svc
        │                    │                      │
        │              ┌─────┴──────┐               │
        │              │ CA (issuing)│               │
        │              │ - issues    │               │
        │              │ - rotates   │               │
        │              │ - revokes   │               │
        │              └─────────────┘               │
        ▼                    ▼                      ▼
  ┌──────────────────────────────────────────────────────┐
  │ Verification service: tests every claim we make       │
  │  - certificate chain validates                        │
  │  - expired/hostname-mismatch/wrong-identity rejected   │
  │  - lateral movement from a compromised svc is BLOCKED │
  └──────────────────────────────────────────────────────┘

  Segmentation (default deny east-west):
    client-svc   → orders-svc:8443, payments-svc: DENIED (no policy)
    orders-svc   → payments-svc:8443, payments-db:5432
    payments-svc → payments-db:5432 only
```

### Implementation

The verification service — the most valuable part of the project, because it converts
assumptions into tests:

```java
/**
 * Every security claim this project makes has a test here. A control that has never been
 * attacked is a control of unknown effect, and the most common failure in network security
 * is a policy that reads correctly and does not apply.
 */
class SecurityVerificationSuite {

    @Test void allServiceCertificatesAreIssuedByOurCa() {
        for (ServiceIdentity id : registry.allServices()) {
            var chain = certificateStore.chainOf(id);
            assertThat(pkix.validate(chain)).as("chain for %s", id).isTrue();
            assertThat(chain.issuer()).isEqualTo(CERTIFICATE_AUTHORITY.subject());
        }
    }

    @Test void everyServiceCertificateIsWithinExpiryBudget() {
        // A 14-day threshold, so the alert fires while there is still time to fix it
        // through the normal renewal path, not in a 2am emergency rotation.
        for (ServiceIdentity id : registry.allServices()) {
            var expiry = certificateStore.notAfterOf(id);
            assertThat(Duration.between(clock.instant(), expiry))
                    .as("%s expires in %s", id, expiry)
                    .isGreaterThan(Duration.ofDays(14));
        }
    }

    @Test void selfSignedCertificateIsRejected() {
        var rogue = selfSignedCertificateFor("orders-svc.internal");
        assertThrows(SSLHandshakeException.class, () -> callAs(rogue, "payments-svc.internal", "/charge"));
    }

    @Test void certificateFromADifferentCaIsRejected() {
        var foreign = otherTestCa().issueFor("orders-svc.internal");
        assertThrows(SSLHandshakeException.class, () -> callAs(foreign, "payments-svc.internal", "/charge"));
    }

    @Test void expiredCertificateIsRejectedWithAUsefulMessage() {
        var expired = ca.issueFor("orders-svc.internal", validity: Duration.ofSeconds(-60));
        var error = assertThrows(SSLHandshakeException.class,
                () -> callAs(expired, "payments-svc.internal", "/charge"));
        // An operator reading a generic "handshake failed" at 3am learns nothing.
        assertThat(error.getMessage()).contains("expired");
    }

    @Test void certificateWithWrongSanIsRejected() {
        var wrongName = ca.issueFor("some-other-host.internal");
        assertThrows(SSLHandshakeException.class, () -> callAs(wrongName, "payments-svc.internal", "/charge"));
    }

    @Test void validCertificateButWrongIdentityIsRejected() {
        // The distinction PKIX cannot make: a legitimately issued certificate for a
        // service that is not permitted to call this endpoint.
        var reportingCert = ca.issueClient("reporting-svc", Duration.ofHours(1));
        assertThrows(NotAuthorizedException.class,
                () -> payments.authorize(reportingCert, "/charge"));
    }

    // *** THE MOST IMPORTANT TEST IN THE PROJECT ***
    @Test void compromisedServiceCannotReachAnythingOutsideItsDeclaredDependencies() {
        // Simulate FULL compromise of orders-svc: it has the process, the memory, the
        // keys, and the network position. The only question is what it can still reach.
        var reachable = lateralMovementProbe.from("orders-svc")
                .withFullyCompromisedCredentials()
                .attemptAllKnownTargets();

        assertThat(reachable.succeeded()).containsExactlyInAnyOrder(
                "payments-svc:8443", "payments-db:5432");
        // Every one of these MUST fail. Named explicitly, so adding a new reachable
        // target is a test failure rather than an unnoticed expansion of blast radius.
        assertThat(reachable.succeeded()).doesNotContain(
                "payments-db-admin:5432", "reporting-svc:8443", "kms:8200",
                "vault:8200", "consul:8500", "elasticsearch:9200");
    }

    @Test void compromisedServiceCannotReachTheCertificateAuthority() {
        // A compromise that reaches the CA can mint identity for anything. This is the
        // single most valuable segmentation rule in the estate.
        assertThat(lateralMovementProbe.from("orders-svc").attempt("ca:8443").succeeded()).isFalse();
    }

    @Test void certificateAuthorityCannotInitiateCallsToDataTier() {
        // Direction matters: the CA needs to READ certs, not connect to databases.
        assertThat(lateralMovementProbe.from("ca").attempt("payments-db:5432").succeeded()).isFalse();
    }

    @Test void rotationLeavesNoWindowOfFailedCalls() {
        // The overlap property: new cert installed, old still valid, then old removed.
        var before = successfulCallsTo("payments-svc");
        lifecycle.rotateAll();
        // Every instant during rotation must have at least one valid cert. Verified by
        // running a call loop in a background thread across the rotation.
        assertThat(callsDuringRotation.failed()).isZero();
        assertThat(successfulCallsTo("payments-svc")).isEqualTo(before);
    }

    @Test void revokedCertificateIsRejectedImmediately() {
        var cert = ca.issueClient("orders-svc", Duration.ofHours(1));
        assertThat(callAs(cert, "payments-svc.internal", "/charge").statusCode()).isEqualTo(200);
        ca.revokeForIncident("orders-svc", "suspected key compromise");   // a test incident
        // 24h TTL is the normal protection; revocation is the exception path and must
        // take effect immediately, not at the next expiry.
        assertThat(callAs(cert, "payments-svc.internal", "/charge")).isRejected();
    }
}
```

The certificate lifecycle with a documented rotation sequence:

```java
@Component
class CertificateLifecycle {
    private static final Duration SERVER_CERT_LIFETIME = Duration.ofDays(30);
    private static final Duration WORKLOAD_CERT_LIFETIME = Duration.ofHours(24);
    private static final Duration OVERLAP = Duration.ofDays(7);

    /**
     * Rotation sequence that has no failure window. The order is the whole design:
     *   1. Generate the new key and certificate.
     *   2. PUBLISH the new cert in the trust bundle, KEEPING the old one.
     *   3. Wait for every peer to observe the updated bundle (measured, not assumed).
     *   4. Switch to signing with the new cert.
     *   5. Wait for the maximum lifetime of connections still using the old cert.
     *   6. Remove the old cert from the bundle.
     * Doing 4 before 2, or 6 before 4, is how a rotation causes an outage.
     */
    void rotate(String serviceId) {
        var newCert = ca.issueFor(serviceId, SERVER_CERT_LIFETIME);
        trustBundle.publishBoth(serviceId, newCert, currentCertOf(serviceId));   // 2
        awaitPeerBundleConvergence(serviceId, newCert.serialNumber());          // 3
        keystore.installAsActive(serviceId, newCert);                            // 4
        sleep(SERVER_CERT_LIFETIME);                                            // 5
        trustBundle.retainOnly(serviceId, newCert);                              // 6
        audit.rotationCompleted(serviceId, newCert.serialNumber());
    }

    @Scheduled(fixedDelay = 12 * 3600_000L)
    void renewWorkloadCertsBeforeHalfLife() {
        for (var id : workloadIdentities()) {
            var cert = currentCertOf(id);
            if (Instant.now().isAfter(cert.notAfter().minus(WORKLOAD_CERT_LIFETIME.dividedBy(2))))
                rotateWorkload(id);
        }
    }
}
```

Segmentation expressed so its effect is measurable rather than asserted:

```java
/**
 * The useful reframing of segmentation: it is a REDUCTION in the number of reachable
 * service pairs. Each policy removes edges from a graph. Blast radius is a function of
 * that graph's connectivity, so the policy's value is the edges removed - which is
 * countable, and therefore testable and reportable.
 */
record SegmentationGraph(Set<Edge> edges) {
    /** Reachable targets from a compromised node, given full control of that node. */
    Set<String> blastRadiusFrom(String compromisedService) {
        var reached = new HashSet<String>();
        var frontier = new ArrayDeque<String>();
        frontier.add(compromisedService);
        while (!frontier.isEmpty()) {
            String node = frontier.poll();
            for (var edge : edges)
                if (edge.from().equals(node) && reached.add(edge.to()))
                    frontier.add(edge.to());
        }
        reached.remove(compromisedService);
        return reached;
    }

    /** The number a board understands: with N services, the flat network has N*(N-1)
     *  reachable pairs. Segmentation's job is to drive that number down. */
    int reachablePairs() {
        int pairs = 0;
        for (String svc : services())
            pairs += blastRadiusFrom(svc).size();
        return pairs;
    }
}

// With 200 services: flat = 200 * 199 = 39,800 pairs. After segmentation, if each service
// may reach only 3 others: 200 * 3 = 600 pairs, a 98.5% reduction. That number is the
// business case for segmentation, and it is checkable in a review.
```

### Test It

```java
@Test void threatModelCoversEveryTrustBoundary() {
    var model = threatModel.load("orders-svc");
    // Every boundary the architecture diagram shows must appear in the threat model.
    // A boundary nobody modelled is a boundary nobody is defending.
    assertThat(model.boundaries()).containsAll("gateway->orders", "orders->payments", "orders->db");
    for (var b : model.boundaries())
        assertThat(model.threatsFor(b)).as("no threats modelled for boundary %s", b).isNotEmpty();
}

@Test void certificateExpiryAlertFiresBeforeTheEmergencyWindow() {
    clock.advance(Duration.ofDays(16));            // 14 days before a 30-day cert
    monitoring.runCertificateSweep();
    assertThat(alerts.raised()).anyMatch(a -> a.name().equals("CERT_EXPIRING_SOON")
            && a.subject().equals("orders-svc"));
}

@Test void rotationIsIdempotentUnderRetry() {
    // A failed rotation retried must not end up with two "current" certs.
    lifecycle.rotate("orders-svc");
    lifecycle.rotate("orders-svc");
    assertThat(trustBundle.currentFor("orders-svc")).isNotEqualTo(trustBundle.retiredFor("orders-svc"));
    assertThat(trustBundle.retainedFor("orders-svc")).hasSize(1);   // collapsed, not duplicated
}
```

## Deliverables

- [ ] Threat model per service with boundaries, threats, and a stated out-of-scope list
- [ ] Verification suite testing every security claim, including the compromise scenario
- [ ] Lateral-movement probe that attempts access to every known target from a compromised service
- [ ] Certificate lifecycle with the six-step no-gap rotation sequence
- [ ] 14-day expiry alerting and immediate revocation for incidents
- [ ] Segmentation represented as a graph, with reachable-pair counts before and after
- [ ] Tests: untrusted CA, expired, wrong SAN, wrong identity, lateral movement, rotation
- [ ] A control-effectiveness report stating what is tested and what is NOT
