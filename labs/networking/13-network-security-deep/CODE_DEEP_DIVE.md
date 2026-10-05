# Network Security Deep - CODE DEEP DIVE

## 1. SAN parsing — the bug that makes a "valid" certificate useless

```java
/**
 * Getting the identity out of a certificate is deceptively fiddly, and the common
 * shortcut (reading the CN) produces a service that works with old clients and fails
 * everywhere modern, with a confusing "hostname mismatch".
 */
final class SubjectAlternativeNames {
    static Set<String> dnsNames(X509Certificate cert) {
        // Java 8+ has a typed accessor. Using it avoids parsing the DER by hand, which is
        // where hand-rolled implementations pick up malformed-string errors.
        return cert.getSubjectAlternativeNames().stream()
                .filter(entry -> entry.get(0) == 2)          // 2 = dNSName
                .map(entry -> (String) entry.get(1))
                .collect(toCollection(TreeSet::new));
    }

    /**
     * SAN matching is NOT a string equality check. Three rules, each a real bug source:
     *   1. Wildcards match exactly ONE label, and only in the leftmost position:
     *      *.example.com matches a.example.com but NOT a.b.example.com.
     *   2. Wildcards do not match within a label: *b.example.com must not match ab.example.com.
     *   3. Partial wildcards are forbidden: b*.example.com is invalid.
     */
    static boolean matches(String hostname, Set<String> sans) {
        if (sans.contains(hostname)) return true;             // exact match, the common case
        for (String pattern : sans) {
            int star = pattern.indexOf('*');
            if (star < 0) continue;
            if (pattern.indexOf('*', star + 1) >= 0) return false;   // multiple wildcards: invalid
            if (star != 0) return false;                              // not leftmost: invalid

            String suffix = pattern.substring(1);                   // ".example.com"
            if (!hostname.endsWith(suffix)) continue;
            String leftmostLabel = hostname.substring(0, hostname.length() - suffix.length());
            if (leftmostLabel.isEmpty() || leftmostLabel.contains(".")) continue;  // one label only
            // The "b*" case is caught here: *b.example.com would leave leftmostLabel
            // ending in 'b' and matching a host where the wildcard consumed part of a
            // label. Explicitly reject a pattern whose suffix starts mid-label.
            if (pattern.length() > 1 && Character.isLetterOrDigit(pattern.charAt(1)))
                continue;
            return true;
        }
        return false;
    }
}
```

## 2. The key schedule — why TLS 1.3's transcript binding is the security property

```java
/**
 * TLS 1.3 derives all keys from one secret with HKDF-Expand-Label over the transcript
 * hash. The important property is not the derivation itself but that EVERY handshake
 * message is folded into the transcript before keys are derived. A message altered,
 * removed, or reordered changes the transcript, changes the keys, and the Finished MAC
 * fails. This is what makes a downgrade attack detectable rather than silent.
 */
final class KeySchedule {
    static final class Secrets {
        final byte[] earlySecret;      // zero-length PSK or the PSK itself
        final byte[] handshakeSecret;  // ECDHE, only known after ServerHello
        final byte[] masterSecret;     // 0-RTT exporter / later traffic
    }

    static Secrets derive(byte[] psk, byte[] ecDhe, byte[] transcriptSoFar) {
        byte[] earlySecret   = hkdfExtract(zeroSalt(), psk);
        // The ECDHE secret is mixed in BEFORE deriving handshake keys, which is what gives
        // forward secrecy: the handshake keys are not a function of the certificate alone.
        byte[] derived       = hkdfExpandLabel(earlySecret, "derived", emptyHash(), Hash.length);
        byte[] handshakeSecret = hkdfExtract(derived, ecDhe);
        byte[] hsTraffic     = hkdfExpandLabel(handshakeSecret, "s hs traffic",
                                               sha256(transcriptSoFar), 2 * Hash.length);
        // ... master secret similarly, over the transcript through server Finished
        return new Secrets(earlySecret, handshakeSecret, /* master */);
    }

    /** Finished is a MAC over the transcript INCLUDING itself-ward data, bound to the
     *  derived traffic key. Compare in constant time: a timing-variable compare on a MAC
     *  is a real, if narrow, attack surface. */
    static boolean verifyFinished(byte[] expectedMac, byte[] receivedMac) {
        return MessageDigest.isEqual(expectedMac, receivedMac);
    }
}
```

## 3. Certificate chain validation — the four things that actually fail

```java
final class ChainValidator {
    void validate(X509Certificate leaf, Set<TrustAnchor> anchors) {
        // 1. PATH CONSTRUCTION: the leaf must chain to a trust anchor. Using a
        //    CertPathBuilder (not a hand-rolled loop) is what handles cross-signed
        //    intermediates, alternate chains, and AKI/SKI matching correctly.
        var path = new CertPathBuilder().addCertificate(leaf)
                .addCertStore(anchorStore(anchors))
                .build();

        // 2. VALIDITY DATES. Two separate issues here: a clock skew tolerance, and the
        //    not-yet-valid case, which is common right after a CA issues a cert in a
        //    different timezone. PKIX has a built-in skew allowance; the custom path
        //    validator below must not remove it by accident.
        PKIXParameters params = new PKIXParameters(anchorStore(anchors));
        params.setRevocationEnabled(true);
        params.setDate(new Date());                    // "now" at validation time

        new CertPathValidator().validate(path, params);
    }

    /**
     * 3. KEY USAGE / EXTENDED KEY USAGE. A certificate valid for serverAuth only will
     *    correctly be rejected when presented as a client certificate, but only if the
     *    validator checks EKU. A permissive validator accepts it, and then a workload
     *    certificate can impersonate a server.
     */
    void checkExtendedKeyUsage(X509Certificate cert, String requiredEku) {
        List<String> eku = cert.getExtendedKeyUsage();
        if (eku == null || eku.isEmpty()) return;      // absent = unconstrained
        if (!eku.contains(requiredEku)) throw new EkuViolationException(requiredEku);
    }

    /**
     * 4. REVOCATION. Two mechanisms with very different characteristics:
     *    - CRL: a signed list, periodically published. Stale between publications, so
     *      revocation is only effective within the CRL's validity window.
     *    - OCSP: per-certificate, near-real-time, but an extra network round trip to a
     *      third party on the hot path, and it fails when the responder is down.
     * Most production systems use OCSP stapling or a soft-fail policy. The key decision
     * is made explicitly and recorded, not inherited by accident.
     */
    void checkRevocation(X509Certificate leaf) {
        var status = ocspClient.check(leaf, issuerCert(leaf));
        switch (status) {
            case GOOD -> { }
            case REVOKED -> throw new RevokedException(leaf.getSerialNumber());
            case UNKNOWN -> {
                // Soft-fail or hard-fail is a RISK DECISION. For short-lived certificates
                // soft-fail is often correct: the cert expires in hours anyway, and a
                // hard dependency on an OCSP responder is an availability risk.
                audit.log("OCSP_UNKNOWN", leaf.getSerialNumber(), policy.softFailRevocation());
            }
        }
    }
}
```

## 4. Rotation with a verified overlap

```java
/**
 * The six-step rotation from the theory, as code. The two steps people skip are (3) and
 * (5), and both cause outages.
 */
@Component
class RotationService {
    void rotate(String serviceId) {
        var newCert = ca.issue(serviceId, SERVER_TTL);
        var newKey  = ca.keyOf(newCert);

        // (2) Publish new, RETAIN old. Both must be servable during the overlap.
        trustBundle.publishBoth(serviceId, newCert, keystore.current(serviceId));

        // (3) WAIT for peers to actually observe it. Sleeping a fixed interval is the
        //     common shortcut and is wrong whenever a peer is slower than assumed.
        //     Convergence is measured: each peer reports the bundle version it has.
        var targetVersion = trustBundle.versionFor(serviceId);
        await().atMost(PEER_CONVERGENCE_TIMEOUT)
               .pollInterval(Duration.ofSeconds(5))
               .until(() -> peerReports.allPeersAtOrAbove(serviceId, targetVersion));

        // (4) Switch to signing with the new cert. In-flight connections on the old cert
        //     are unaffected, because TLS is per-connection.
        keystore.installAsActive(serviceId, newCert, newKey);

        // (5) WAIT the maximum lifetime of anything using the old cert: a TLS connection
        //     is bound to the certificate presented at handshake time.
        scheduler.schedule(() -> {
            // (6) Only now drop the old cert.
            trustBundle.retainOnly(serviceId, newCert);
            audit.rotationCompleted(serviceId, newCert.getSerialNumber());
        }, SERVER_TTL.toMillis(), MILLISECONDS);
    }
}
```

**A failure mode worth noticing**: if step (3) times out, the correct action is to abort
and keep the old certificate. Proceeding to step (4) without peer convergence is precisely
how a rotation causes an outage — and the code above makes the timeout an exception
before the switch, not after it.

## 5. Network reachability probing — testing the policy, not the YAML

```java
/**
 * A connectivity probe. What makes it trustworthy:
 *  - a real, throwaway credential, so success means "reachable AND permitted", which is
 *    what a policy claims
 *  - every target enumerated from inventory, so a forgotten target is a silent pass
 *  - the probe identity is distinct from the workload's own, so a cached connection or a
 *    host-based firewall allow-rule does not produce a false PASS
 */
@Component
class ReachabilityProbe {
    ProbeResult probe(String fromService, Target target) {
        var identity = probeCredentials.issueEphemeralFor(fromService, ttl: Duration.ofMinutes(10));
        try {
            var client = mtlsClient.forIdentity(identity, target.trustAnchor());
            var response = client.get(target.healthUrl(), timeout(Duration.ofSeconds(2)));

            boolean reached = response.statusCode() > 0;
            boolean permitted = reached && response.statusCode() != 403;
            return new ProbeResult(fromService, target, reached, permitted, response.statusCode());

        } catch (ConnectException | SocketTimeoutException e) {
            // Reached the network stack but not the service: blocked. This is the
            // desired outcome for an undeclared path.
            return ProbeResult.blocked(fromService, target, e.getClass().getSimpleName());

        } catch (SSLException e) {
            // Network path exists but mTLS rejected us. Distinct from "blocked":
            // this is an identity problem, and the fix is different.
            return new ProbeResult(fromService, target, reached = true, permitted = false,
                    reason: "TLS_REJECTED: " + e.getMessage());
        } finally {
            probeCredentials.revoke(identity);      // always revoke, even on success
        }
    }

    /**
     * Distinguishing the three outcomes is what makes the report actionable:
     *   blocked        -> segmentation is working
     *   TLS rejected   -> the path exists; the IDENTITY model is wrong
     *   permitted      -> the path exists and is authorised: a real finding
     * A probe that collapses all three into "failed" cannot be used to improve anything.
     */
    void report(ProbeResult r, SegmentationPolicy policy) {
        if (r.permitted() && !policy.declares(r.from(), r.target()))
            siem.emit("UNDECLARED_REACHABILITY", r, evidence: r.evidence());
        metrics.counter("probe.result", "outcome", r.outcome().name()).increment();
    }
}
```

## 6. The one bug that silently disables the whole programme

```java
/**
 * Identity derived from a HEADER is a critical vulnerability, and it is invisible in the
 * code that depends on it. If authorisation reads the identity from a request header
 * instead of the verified TLS peer, then any workload that can reach the service can
 * claim any identity - and the mesh authorisation is decorative.
 *
 * This test is the cheapest high-value test in the entire lab.
 */
class IdentityBindingTest {
    @Test void identityCannotBeSpoofedByAHeader() {
        // Connect with reporting-svc's valid certificate but claim to be orders-svc.
        var result = callWith(spoofHeader: "X-Service-Identity: orders-svc",
                              certificate: certificateFor("reporting-svc"),
                              path: "/internal/charge");

        assertThat(result.statusCode())
                .as("a spoofed identity header must not grant elevated access")
                .isIn(401, 403);
        // And the server must have recorded the identity as reporting-svc, not orders-svc.
        assertThat(auditLog.lastSubject()).isEqualTo("spiffe://lab/ns/prod/sa/reporting-svc");
    }

    @Test void identityComesFromTheVerifiedPeerCertificate() {
        var auth = (JwtAuthenticationToken) SecurityContextHolder.getContext().getAuthentication();
        assertThat(auth.getName()).isEqualTo(spiffeIdOf(peerCertificateOfCurrentConnection()));
    }
}
```

## 7. Reviewing a segmentation policy: five questions

1. **Is there a default-deny?** Not implied — explicit, and visible in a diff.
2. **Does every flow have a rationale and an owner?** Undocumented flow = unjustified
   blast radius.
3. **Are the exceptions expiring?** And is the expiry enforced by code?
4. **What is the maximum blast radius?** If one service can reach 200 others, that is
   the finding, whatever the average says.
5. **When was the policy last attacked?** A policy that has never been probed is a
   policy of unknown effect.

## Sourced field notes (fetched Oct 2026 - verify before citing)
- RFC 6125 / RFC 2818 define the certificate identity matching rules, including the
  leftmost-single-label wildcard semantics implemented in §1.
  https://www.rfc-editor.org/info/rfc6125/
- RFC 8446 §4.4.1 specifies the TLS 1.3 key schedule, including the transcript-bound
  derivation that the verifier in §2 implements.
  https://www.rfc-editor.org/info/rfc8446/
