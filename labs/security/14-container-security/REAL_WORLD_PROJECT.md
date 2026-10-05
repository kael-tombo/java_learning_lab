# Container Security - REAL WORLD PROJECT

## Project: PlatformShield — workload security for a 200-node Kubernetes estate

A shared platform hosting 140 services across 40 teams. The container baseline must be
enforced centrally so a team cannot ship a privileged pod, while still letting teams move
fast. This is an adoption problem as much as a technical one.

### Architecture

```
  Developer ──> CI: build, scan, generate SBOM, sign image (Sigstore), push by digest
                                            │
   Admission Controller ────────────────────┤
     1. verify signature (policy engine)
     2. verify SBOM present; CVE gate vs. severity threshold + exception registry
     3. enforce Pod Security "restricted" (namespace labels + VAP)
     4. inject sidecars: seccomp, network policy default-deny, image scanner
     5. reject + explain, or annotate + record
                                            │
                                   Kubernetes cluster
                                            │
  Runtime detection ──> eBPF: exec in container, new privileges, /proc access, egress to
                      new IP, crypto-mining patterns ──> alert ──> SIEM (lab 19)
                                            │
  Kyverno/OPA exception registry: every deviation is a ticket, an owner, an expiry date
```

### Implementation

The admission pipeline in one place, with a deny path that explains itself:

```java
@Component
class WorkloadAdmissionController {
    // deny-by-default, with an explicit, expiring exception registry as the only escape hatch
    public AdmissionResponse review(AdmissionRequest req) {
        List<Violation> violations = new ArrayList<>();
        if (!verifySignature(req.image())) violations.add(new Violation("UNSIGNED_IMAGE",
            "image " + req.image() + " is not signed by our Sigstore identity"));
        if (!sbomStore.has(req.image())) violations.add(new Violation("NO_SBOM", "no SBOM for " + req.image()));
        violations.addAll(cveGate.evaluate(sbomStore.get(req.image())));   // CVEs above threshold
        violations.addAll(podSecurity.validate(req.pod()));                // restricted profile
        violations.addAll(exceptions.lookup(req.image(), req.namespace(), req.team())); // still-violating-but-allowed

        if (violations.stream().anyMatch(v -> v.blocking() && !v.excepted()))
            return AdmissionResponse.deny(violations, "see runbook/security/container-baseline");
        audit.admission(req, violations);
        return AdmissionResponse.allowWithAnnotations(violations);   // record non-blocking findings
    }

    boolean verifySignature(String imageRef) {
        // Identity-based: only our CI pipeline's OIDC identity may push to prod registries.
        return cosign.verify(imageRef, identity: workflowIdentity, issuer: sigstoreIssuer);
    }
}
```

Runtime detection catches what static analysis cannot — the pod that was compliant at
admission and misbehaved at runtime:

```java
@Component
class RuntimeAnomalyDetector {
    // Signals that correlate with container escape and post-compromise activity:
    //   unexpected exec        - a shell in a distroless Java image is anomalous by definition
    //   privilege escalation   - setuid binary execution or capability use not present at admission
    //   filesystem tampering   - writes to the image layer (read-only rootfs should prevent it)
    //   new egress destinations - a Java service talking to an IP outside its NetworkPolicy
    //   image mismatch         - the running image digest differs from the deployed spec
    void onExec(ExecEvent e) {
        if (!e.image().contains("jre") && e.binary().equals("/bin/sh"))
            alert.warn("SHELL_IN_RUNTIME_IMAGE", e.pod(), e.image(), e.user());
        if (e.userId() == 0) alert.critical("ROOT_EXEC_IN_CONTAINER", e.pod(), e.command());
    }

    void onNetworkFlow(Flow f) {
        if (!networkPolicy.allows(f.pod(), f.destination())) 
            alert.critical("POLICY_VIOLATION", f.pod(), f.destination());
        if (firstSeenDestination(f.pod(), f.destinationIp())) 
            metrics.counter("egress.new_destination", "pod", f.pod(), "port", f.port()).increment();
    }
}
```

Enforcement is progressive, because a hard block on day one stops every team:

```java
enum EnforcementMode { AUDIT_ONLY, ENFORCE_WITH_EXCEPTIONS, ENFORCE_STRICT }

@Component
class BaselineRollout {
    // Phase 1 (month 0-1):  AUDIT_ONLY  - report every violation, block nothing, fix nothing yet
    // Phase 2 (month 1-3):  ENFORCE_WITH_EXCEPTIONS - block new violations; existing keep
    //                        working under a ticket with an expiry date
    // Phase 3 (month 3+):   ENFORCE_STRICT - zero exceptions, everyone compliant
    //
    // Per-team opt-in tracks each team to a date, so the platform team never becomes the
    // bottleneck for 40 teams' release schedules.
    Map<String, LocalDate> complianceDeadlines = Map.of(
        "team-payments", LocalDate.now().plusDays(30),
        "team-search",   LocalDate.now().plusDays(60),
        "team-legacy",   LocalDate.now().plusDays(120));
}
```

### Non-functional requirements

- **Coverage**: 100% of production workloads digest-pinned, signed, SBOM-attached, and
  admitted through the controller. Zero workloads running privileged.
- **Adoption**: each of the 40 teams reaches compliance by their own deadline; a shared
  self-service tool generates the compliant manifest rather than teams hand-writing it.
- **Exceptions**: every exception has a ticket, an owner, a compensating control, and an
  expiry date. Expired exceptions are auto-rejected — the system does not forget.
- **Performance**: admission latency budget 200 ms including signature verification,
  with a signature trust cache so warm requests are local.
- **Detection latency**: runtime signals to alert under 60 seconds.
- **Availability**: the controller fails *open* only for explicitly trusted images; a
  controller outage cannot block all deployments, which is why signature verification
  results are cached and re-validated on a short TTL.
- **Supply chain**: ties directly to lab 18 — SLSA build provenance, SBOM per image, and
  dependency scanning all feed this admission gate.

### Sourced field notes (fetched Oct 2026 — verify before citing)
- Kubernetes Pod Security Standards define the `restricted` profile (non-root, capability
  drop, seccomp, no privilege escalation) enforced by the admission policy above.
  https://kubernetes.io/docs/concepts/security/pod-security-standards/
- Kubernetes Network Policies specify how pods are isolated for ingress and egress, the
  default-deny-plus-explicit-allow model used for micro-segmentation here.
  https://kubernetes.io/docs/concepts/services-networking/network-policies/
- OWASP Docker Security Cheat Sheet covers image provenance, base-image selection, and the
  "run as non-root, no added privileges" runtime rules enforced by the admission policy.
  https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html

## Deliverables

- [x] CI pipeline producing SBOM-attested, signed, digest-pinned images
- [x] Admission controller verifying signature, SBOM, CVE gate, and pod security
- [x] Progressive enforcement (audit → enforce with exceptions → strict) per team
- [x] Exception registry with owner, compensating control, and enforced expiry
- [x] Runtime detection for exec, privilege, tampering, and egress anomalies
- [x] Default-deny network policies with named-peer allowances
- [x] Admission latency budget with a signature trust cache
- [x] Self-service manifest generator to remove the platform team as a bottleneck
