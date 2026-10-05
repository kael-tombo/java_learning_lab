# Network Security - REAL WORLD PROJECT

## Project: MeshShield — service-to-service encryption and segmentation for a 200-service platform

Every service call crosses the network unencrypted and unverified today: plain HTTP inside
the cluster, and a flat network where any compromised pod can reach any other. The target
is mutual TLS everywhere with an automated certificate lifecycle, and default-deny
segmentation that bounds a compromise.

### Architecture

```
  ┌──────────── control plane (holds the CA key, tightly controlled) ─────────────┐
  │  Certificate Authority (intermediate, HSM-backed key)                        │
  │  issues: workload certs (24h, auto-renewed), server certs (30d, rotated)     │
  │  publishes: CRL on revocation, OCSP responder, an audit log per issuance      │
  └────────────────────────────────┬────────────────────────────────────────────┘
                                 │ issues
  ┌──────────────────────────────┴─────────────────────────────────────────────┐
  │ Service mesh sidecars: 200 services x 2 = 400 sidecars                      │
  │  - workload identity certificate fetched at startup (never stored on disk)  │
  │  - mTLS to every outbound call, identity asserted from the cert, not a header│
  │  - inbound: verify chain, check SAN matches the requested service            │
  │  - authorization: explicit per-route policy, default deny                    │
  └──────────────────────────────┬─────────────────────────────────────────────┘
                                 │ all east-west traffic encrypted + verified
  ┌──────────────────────────────┴─────────────────────────────────────────────┐
  │ Data plane policies (layered, and they are different controls):             │
  │  - L3/L4: NetworkPolicy default-deny east-west                             │
  │  - L7: mesh authorization (which identity may call which path)              │
  │  - Application: authorization in the service (lab 09's policy engine)        │
  │  Each layer limits a different kind of mistake. Removing one is acceptable    │
  │  with a compensating control; removing all three is not.                     │
  └────────────────────────────────────────────────────────────────────────────┘
```

### Implementation

Control-plane CA with strict key protection, because this component is the crown jewels:

```java
@Service
class IssuingAuthority {
    // The CA signing key never leaves the HSM, and this service is the only thing that
    // can ask it to sign. A compromised control plane is worse than a compromised
    // workload: it can mint identity for anything.
    void issueWorkloadCertificate(WorkloadId id) {
        var csr = workloadRuntime.generateCsr(id);   // ephemeral key, generated in the sidecar
        var cert = hsm.sign(csr, issuer: intermediateIssuer, notAfter: now().plus(WORKLOAD_TTL));
        // Audit EVERY issuance. A service mesh creates a lot of certificates; an
        // unlogged one is an unattributable identity.
        auditLog.issued(id, cert.serialNumber(), cert.notAfter(), workloadRuntime.podUid());
        revocationRegistry.register(cert.serialNumber(), id, WORKLOAD_TTL);
        return cert;
    }

    /** Revocation must be fast for compromised workloads, even though certs are short-lived. */
    void revokeCompromised(WorkloadId id, String reason) {
        revocationRegistry.revokeByIdentity(id, reason);      // immediate block
        hsm.revokeIntermediateIfNeeded(id, reason);           // escalate only if warranted
        // Force re-issuance everywhere the old cert was trusted: a revocation alone is
        // useless if a sidecar keeps serving the cached certificate for its TTL.
        meshControlPlane.invalidateCachedCertificates(id);
    }
}
```

Sidecar identity, where ephemeral keys are the reason revocation is tractable:

```java
/**
 * Design decision: the workload private key is generated EPHEMERALLY in the sidecar at
 * startup and never written to disk. Consequences:
 *  - No key material to steal from the filesystem or a backup.
 *  - A restarted pod has a new identity, so a leaked key is bound to one pod lifetime.
 *  - Rotation is a sidecar restart or a re-issue, not a file operation.
 */
class SidecarIdentityProvider {
    private volatile KeyPair current;

    @PostConstruct
    void obtainIdentity() {
        var keyPair = keyGenerator.generateEc("P-256");       // generated in memory, not read from disk
        var csr = pki.buildCsr(keyPair, spiffeIdOf(thisPod()));
        current = new KeyPairAndCert(pkiObtainCertificate(csr), keyPair);
        secretsWatcher.deleteOnExit();                        // belt and braces: no persistence
    }

    @Scheduled(fixedDelay = 12 * 3600_000L)
    void renewBeforeHalfLife() {
        if (Instant.now().isAfter(current.cert().notAfter().minus(WORKLOAD_TTL.dividedBy(2)))) {
            var keyPair = keyGenerator.generateEc("P-256");   // NEW key, not a renewed cert
            current = new KeyPairAndCert(pkiObtainCertificate(pki.buildCsr(keyPair, spiffeIdOf(thisPod()))), keyPair);
            // Atomic swap: in-flight calls finish on the old cert, new calls use the new one.
        }
    }
}
```

Inbound verification with identity-based authorization, which is distinct from PKIX:

```java
/**
 * Inbound mTLS. Two separate decisions, and conflating them is the classic error:
 *   1. Is this certificate trustworthy?  -> PKIX chain + validity + revocation
 *   2. May this identity call THIS path? -> authorization policy, default deny
 * A valid certificate only answers (1). Any service can then call any path, which is
 * the flat-network problem restated with better crypto.
 */
class InboundAuthorizer {
    void authorize(String peerSpiffeId, String path, String method) {
        var policy = policyStore.forPath(path, method);
        if (policy.denies(peerSpiffeId)) { audit.deny(peerSpiffeId, path, "explicit deny"); throw forbidden(); }
        if (!policy.allows(peerSpiffeId)) {                 // default deny on no match
            audit.deny(peerSpiffeId, path, "no matching allow");
            // This alert is worth having: a service calling an unexpected path is either a
            // bug or reconnaissance, and both are visible only if you log the denies.
            metrics.counter("mesh.deny", "caller", callerOf(peerSpiffeId), "path", pathPattern(path)).increment();
            throw forbidden();
        }
        audit.allow(peerSpiffeId, path);
    }
}
```

Layered segmentation, with the exceptions tracked as first-class objects:

```java
/**
 * Default-deny east-west. The exception registry is the whole governance story: every
 * exception is a ticket, an owner, a compensating control, and an expiry. Undated
 * exceptions are how a default-deny network decays back to a flat network within a year.
 */
record SegmentationException(String from, String to, int port, String ticket, String owner,
                             String compensatingControl, Instant expiresAt) {
    boolean isActive() { return expiresAt.isAfter(Instant.now()); }
}

class SegmentationController {
    @Scheduled(fixedDelay = 30_000)
    void reconcile() {
        var desired = policyCompiler.compile();             // desired NetworkPolicies from the policy store
        var existing = networkPolicyClient.list();
        applyDiffs(desired, existing);
        // Expired exceptions are removed AUTOMATICALLY. The system does not remember to
        // clean up, because that is exactly when it would fail to.
        expiredExceptions().forEach(e -> {
            networkPolicyClient.delete(e);
            audit.exceptionExpired(e.ticket(), e.owner());
            incident.notify("network exception expired and was removed", e);
        });
    }

    @Test void noPolicyPermitsCrossingTheDataTierBoundaryFromAppTier() {
        var appTier = networkPolicyClient.list().stream()
            .filter(p -> p.selectors().anyMatch(s -> s.startsWith("tier=app")))
            .filter(p -> p.ingress().stream().anyMatch(i -> i.from().anyMatch(f -> f.startsWith("tier=data"))))
            .toList();
        // Apps must reach data services through the service layer, not directly to the store.
        assertThat(appTier).isEmpty();
    }
}
```

Outbound identity propagation, ensuring a header cannot claim an identity the cert does not:

```java
class OutboundCallContext {
    /**
     * When a service calls another service, the caller identity is carried in the TLS
     * certificate, NOT in a header. A header is trivially spoofable by any workload; the
     * certificate is bound to the connection's private key. If a header-based identity is
     * accepted anywhere, mesh authorization is bypassed entirely.
     */
    OutboundCallContext forTarget(String serviceName) {
        var target = serviceRegistry.require(serviceName);
        var policy = policyStore.forCallerToTarget(currentSpiffeId(), target.spiffeId());
        if (!policy.allows(currentPath(), method())) {
            audit.deny(currentSpiffeId(), serviceName, "outbound policy");
            throw forbidden();     // fail at the call site, not at the callee
        }
        return new OutboundCallContext(target, Deadline.after(2, SECONDS), traceHeaders());
        // traceHeaders carries trace context ONLY. No identity, no role, no tenant claims.
    }
}
```

### Non-functional requirements

- **Coverage**: mTLS on 100% of east-west service calls. Any plaintext service-to-service
  call is an alert, not a metric to watch slowly decline.
- **Authentication overhead**: p99 under 1.5 ms added per call, measured on both the
  establish path (cached connections) and the new-connection path. Connection reuse is
  required or this cost dominates.
- **Certificate lifecycle**: workload certs 24h with auto-renew at half-life; server certs
  30d rotated automatically; CA key in an HSM; issuance fully audited. Zero expiry
  incidents — the single most important operational metric in this project.
- **Compromise containment**: a compromised pod can reach only its declared dependencies.
  Verified quarterly by a test that actually attempts lateral movement from a compromised
  workload, because a policy that has never been attacked is a policy of unknown effect.
- **Revocation**: compromised identity blocked within 60 seconds across all sidecars,
  including cache invalidation, not merely CRL publication.
- **Segmentation governance**: exception count trending to zero, every exception owned with
  an expiry, auto-removal on expiry, and a monthly review of the exception register.
- **Observability**: mTLS failure rate by reason, certificate issuance and expiry metrics,
  mesh deny rate by caller and path, and lateral-movement test results as a standing report.
- **Rollout**: per-service opt-in with a shadow mode that reports "this call would have
  failed" for two weeks before enforcement, so policy errors surface as data first.
- **Compliance**: evidence of encrypted transport, certificate inventory, and access
  review exported for the annual audit.

### Sourced field notes (fetched Oct 2026 — verify before citing)
- Kubernetes Network Policies implement default-deny-by-explicit-allow segmentation, the
  L3/L4 layer of this design, and are enforced independently of the mesh's L7 policy.
  https://kubernetes.io/docs/concepts/services-networking/network-policies/
- OWASP Transport Layer Security Cheat Sheet documents TLS configuration, certificate
  management, and the mutual-TLS pattern used for service-to-service authentication.
  https://cheatsheetseries.owasp.org/cheatsheets/Transport_Layer_Security_Cheat_Sheet.html

## Deliverables

- [x] HSM-backed issuing authority with full issuance auditing and fast revocation
- [x] Ephemeral workload keys generated per sidecar, never persisted to disk
- [x] Inbound mTLS separating PKIX trust from identity-based per-path authorization
- [x] Default-deny east-west segmentation with an owned, expiring exception registry
- [x] Automatic exception expiry with an incident notification, not silent cleanup
- [x] Identity carried by certificate only, with a test proving header spoofing fails
- [x] Shadow-mode rollout reporting would-be denials before enforcement
- [x] Quarterly lateral-movement test from a simulated compromised workload
- [x] Certificate inventory, expiry alerting, and a zero-expiry-incident target
