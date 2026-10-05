# Network Security Deep - REAL WORLD PROJECT

## Project: Bastion — platform-wide network segmentation and transport security with measured assurance

400 services across three clouds, two data centres, and 3,000 corporate laptops, connected
by a flat internal network. Any compromised workload can reach anything: the production
databases, the secret store, the certificate authority, the CI runners, and every other
tenant. This programme introduces layered segmentation and transport security, and — the
part that matters — proves the controls work by continuously attacking them.

### Architecture

```
  Corporate (3,000 laptops)         Cloud VPC                    Data centre
  ┌──────────────────────┐          ┌─────────────┐            ┌──────────────┐
  │ ZTNA broker          │          │ 400 services│            │ 60 legacy VMs│
  │ identity + posture   │          │ across 3 AZ │            │ (migration)  │
  └──────────┬───────────┘          └──────┬──────┘            └──────┬───────┘
             │ mTLS                      │ mTLS (sidecar)             │ mTLS
             └──────────────┬────────────┴─────────────┬─────────────┘
                            ▼                          ▼
  ┌──────────────────────────────────────────────────────────────────┐
  │ SEGMENTATION, layered (each bounds a different mistake):          │
  │  L4: NetworkPolicy default-deny east-west (VPC / NSG)            │
  │  L7: mesh authorization - which identity may call which path      │
  │  App: service-level policy engine (in the service)                │
  │  Calc: blast-radius graph with quarterly attack verification     │
  └──────────────────────────────────────────────────────────────────┐
  ┌──────────────────────────────────────────────────────────────────┐
  │ CONTROL PLANE (the crown jewels, separately segmented):           │
  │  CA (HSM key)  │  secret store  │  CI runners  │  monitoring    │
  │  No workload may reach the CA. A compromise that reaches the CA   │
  │  can mint identity for everything: this is the top rule.          │
  └──────────────────────────────────────────────────────────────────┘
  ┌──────────────────────────────────────────────────────────────────┐
  │ ASSURANCE (continuous, not annual):                              │
  │  - daily lateral-movement probe from a randomly chosen service    │
  │  - certificate lifecycle monitoring with rotation automation       │
  │  - segmentation policy diff alerts on unexpected widening         │
  │  - quarterly red-team engagement, findings tracked to closure     │
  └──────────────────────────────────────────────────────────────────┘
```

### Implementation

Segmentation as a policy compiler, so intent is code and drift is detectable:

```java
/**
 * Policies are compiled from a declarative spec into platform objects. The benefit is
 * DIFFABILITY: an unexpected widening of a policy is a diff against version control,
 * which is exactly the signal a review process needs and that a dashboard of "current
 * rules" cannot give you.
 */
@Component
class SegmentationPolicyCompiler {

    /** Declarative spec: tiers, allowed flows, and an explicit owner per flow. */
    record ZoneSpec(String zone, Set<String> selectors, Tier tier, String owner) {}
    record FlowSpec(String from, String to, Set<Integer> ports, String rationale, String ticket) {}

    List<NetworkPolicy> compile(Spec spec) {
        var policies = new ArrayList<NetworkPolicy>();
        for (FlowSpec flow : spec.flows()) {
            // A flow with no rationale is a review rejection, not a warning. Undocumented
            // network access is the single largest contributor to unjustified blast radius.
            if (flow.rationale() == null || flow.rationale().isBlank())
                throw new PolicyException("flow " + flow.from() + "->" + flow.to() + " has no rationale");
            policies.add(networkPolicy()
                    .from(podSelector(spec.zone(flow.from())))
                    .to(podSelector(spec.zone(flow.to())))
                    .ports(flow.ports())
                    .withDescription(flow.rationale() + " [" + flow.ticket() + "]"));
        }
        // Default-deny is expressed explicitly as a deny-all, so it is visible in diffs
        // and cannot be silently removed by someone editing a later rule.
        policies.add(networkPolicy().denyAll().withDescription("default deny east-west"));
        return policies;
    }

    /** Drift detection: compare the live platform state against the compiled spec. */
    @Scheduled(fixedDelay = 60_000)
    void detectDrift() {
        var desired = compile(specRepository.current());
        var live = platform.networkPolicies().list();
        var widened = diff(live, desired).stream()
                .filter(Change::isWidening)        // a NARROWING is safe; a WIDENING is the alarm
                .toList();
        if (!widened.isEmpty()) {
            siem.emit("SEGMENTATION_POLICY_WIDENED", widened);
            // Alert loudly. An unexplained widening is either an attacker or an engineer
            // at 11pm who did not realise what they opened.
            incident.page("network policy widened without a reviewed change", widened);
        }
    }
}
```

The exception registry, because a default-deny policy without exceptions is a policy that
gets abandoned:

```java
/**
 * Exceptions are the real governance surface. Each one is a ticket, an owner, a
 * compensating control, and an EXPIRY DATE. The critical property: expiry is enforced by
 * the system, not by a reviewer's memory. A control that depends on someone remembering
 * is a control that decays.
 */
record NetworkException(String id, String from, String to, int port, String ticket,
                        String owner, String compensatingControl, Instant expiresAt,
                        String justification) {
    boolean isActive() { return Instant.now().isBefore(expiresAt); }
    long daysRemaining() { return Duration.between(Instant.now(), expiresAt).toDays(); }
}

@Component
class ExceptionLifecycle {
    @Scheduled(fixedDelay = 300_000)
    void processExpirations() {
        registry.all().stream()
                .filter(NetworkException::isActive).filter(e -> e.daysRemaining() <= 7)
                .forEach(e -> notify.ownerBeforeExpiry(e));   // 7-day warning, not a surprise removal

        registry.all().stream()
                .filter(e -> !e.isActive())
                .forEach(e -> {
                    platform.networkPolicies().delete(e.compiledPolicyId());
                    audit.exceptionRemoved(e.id(), e.owner(), "expired");
                    // The removal is a change with a consequence, so it is announced. An
                    // expiry that breaks a service at 2am should never be a surprise.
                    serviceOwners(e.to()).forEach(o -> notify.removedByExpiry(o, e));
                });
    }

    /** Every exception is re-justified or removed on a schedule. A 12-month-old exception
     *  nobody has re-examined is evidence the default-deny is being worked around. */
    @Scheduled(cron = "0 0 4 1 * *")
    void annualRejustification() {
        registry.all().stream()
                .filter(e -> e.expiresAt().isBefore(Instant.now().plus(Duration.ofDays(90))))
                .forEach(e -> backlog.requireRejustification(e));
    }
}
```

Continuous lateral-movement verification — the part that turns policy into evidence:

```java
/**
 * A segmentation policy is a hypothesis about what an attacker cannot do. This job tests
 * the hypothesis daily by ACTUALLY TRYING, from a randomly chosen service, using a
 * throwaway credential. If a probe succeeds, the policy is wrong, regardless of what the
 * YAML says.
 */
@Component
class LateralMovementProbe {
    @Scheduled(cron = "0 */15 * * * *")
    void probeFromRandomWorkload() {
        var origin = randomServiceWeightedByCriticality();
        var results = reachabilityMatrix()
                .from(origin)
                .withProbeCredential(probeCredentialStore.issueEphemeralFor(origin))
                .attemptAll(targetInventory.allServicesAndDataStores())
                .execute();

        results.succeeded().forEach(target -> {
            if (policyStore.isDeclared(origin, target)) return;   // expected reachability
            // SUCCESS on an UNDECLARED path. This is the alert that matters: it means the
            // policy does not match reality, and reality is what an attacker uses.
            siem.emit("UNDECLARED_LATERAL_REACHABILITY", origin, target, evidence(results, target));
            incident.page("undeclared lateral reachability detected", origin, target);
        });
        audit.probeRun(origin, results, Duration.ofSeconds(6));
    }

    /** Full-attack simulation, quarterly: full credential access, execution, and privilege
     *  escalation attempts - the only way to know the segmented network holds under a
     *  realistic adversary rather than a single connectivity check. */
    @Scheduled(cron = "0 0 2 1 1,4,7,10 *")
    void quarterlyAdversarySimulation() {
        var report = adversarySim.run(entryPoint: internetFacingService(), objective: "reach production database");
        report.findings().forEach(f -> backlog.create("RED_TEAM", f.severity(), f.summary(), ownerOf(f.target())));
    }
}
```

Transport security at scale, with certificate lifecycle automated so expiry is a non-event:

```java
@Component
class FleetCertificateManager {
    private static final Duration WORKLOAD_TTL = Duration.ofHours(24);
    private static final Duration SERVER_TTL = Duration.ofDays(30);

    /**
     * The design choice that removes an entire incident class: workload certificates last
     * 24 HOURS, with keys generated EPHEMERALLY in the sidecar and never written to disk.
     * Consequences:
     *  - no long-lived service credential exists anywhere to steal
     *  - a stolen key expires on its own within a day, with no revocation ceremony
     *  - identity is bound to a pod lifetime, not to a file on a filesystem
     * The trade-off: the control plane issues ~400x more certificates. That is a
     * capacity decision, made deliberately, and it is why the CA is horizontally scaled.
     */
    @Scheduled(fixedDelay = 6 * 3600_000L)
    void rotateFleet() {
        for (var workload : workloadsNeedingRotation(WORKLOAD_TTL.dividedBy(2))) {
            var keyPair = ephemeralKeyGenerator.generateEc("P-256");   // in memory only
            var cert = ca.issue(workload.identity(), WORKLOAD_TTL, keyPair.request());
            workload.install(cert, keyPair);
            metrics.counter("fleet.cert.rotated");
        }
    }

    /** Expiry is monitored as a first-class SLO, because "zero expiry incidents" is
     *  a claim that must be measured rather than asserted. */
    @Slo(target = 0, window = 90)
    void certificateExpiryIncidents() { incidentCounter.for("CERT_EXPIRED"); }
}
```

### Non-functional requirements

- **Blast radius**: reduce reachable service pairs from the flat-network maximum
  (`N(N-1)`, ≈160,000 for 400 services) to under 3 per service — a >99% reduction.
  Measured, not estimated, and reported as a graph metric.
- **Continuous verification**: lateral-movement probe every 15 minutes from a rotating
  service; any undeclared reachability pages immediately. Zero tolerance for silent drift.
- **CA protection**: zero workloads may reach the CA. Verified by probe, and the CA lives
  in its own trust zone with no inbound path from the service estate.
- **Certificate lifecycle**: zero expiry incidents over 12 months; 24h workload certs with
  ephemeral keys; 30d server certs with the no-gap six-step rotation; revocation effective
  globally within 60 seconds.
- **Exception governance**: every exception owned, justified, and expiring. Exception count
  trending to zero; any exception older than 12 months blocks a release.
- **Laptop access**: ZTNA broker replacing full VPN access; a compromised laptop reaches
  only published applications on an allow-list, not a network segment.
- **Data tier isolation**: no app-tier workload may reach a database directly except
  through the owning service. Enforced at L3 and re-verified by probe.
- **Performance**: mTLS adds under 1.5 ms p99 per call with connection reuse; edge
  capacity sized for 400 services' connection count.
- **Compliance**: evidence of encrypted transport, certificate inventory, access reviews,
  and continuous control testing exported for the annual audit — with the coverage
  statement that says explicitly which controls are unverified.
- **Honest reporting**: a quarterly report of what is tested, what is assumed, and what is
  known not to be covered. A programme that claims complete coverage is not measuring.

### Sourced field notes (fetched Oct 2026 — verify before citing)
- Kubernetes Network Policies implement the default-deny-by-explicit-allow segmentation
  that this programme compiles from a declarative spec, and are enforced independently of
  the L7 mesh policy.
  https://kubernetes.io/docs/concepts/services-networking/network-policies/
- OWASP Transport Layer Security Cheat Sheet documents the mutual-TLS pattern, the
  certificate lifecycle practices, and the operational requirements implemented here.
  https://cheatsheetseries.owasp.org/cheatsheets/Transport_Layer_Security_Cheat_Sheet.html

## Deliverables

- [x] Declarative segmentation spec compiled to platform policies, with diff-based drift alerting
- [x] Blast-radius graph with reachable-pair counts as the reported security metric
- [x] Exception registry with owner, compensating control, enforced expiry, and auto-removal
- [x] Continuous lateral-movement probing every 15 minutes with paging on undeclared paths
- [x] 24-hour workload certificates with ephemeral in-memory keys and no on-disk material
- [x] Six-step no-gap rotation for server certificates, measured for convergence
- [x] Revocation effective globally within 60 seconds, including cache invalidation
- [x] CA in an isolated trust zone with no inbound path from the service estate
- [x] Quarterly control-effectiveness report naming tested, assumed, and uncovered controls
