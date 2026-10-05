# Zero Trust Architecture - REAL WORLD PROJECT

## Project: Perimeterless — retiring the VPN for a 3,000-person engineering organisation

The company has outgrown its VPN. Contractors are on corporate networks to reach internal
Git, artifact repositories, dashboards, and a legacy monolith with no modern auth. Replacing
the VPN wholesale would break everything, so the migration is staged by trust tier.

### Architecture

```
  BEFORE                                  AFTER
  ──────                                  ──────
  VPN concentrator ──> flat 10.0.0.0/8    Broker / access proxy ──> per-app policy
  Anyone on VPN = trusted                 Identity: OIDC (human) + SPIFFE (workload)
  Network ACLs (thousands, stale)         Device posture: managed, patched, EDR healthy
                                         Session: time-bound, re-evaluated on risk change

  Trust tiers
  ────────────
  Tier 0  Public           marketing site, docs            no auth
  Tier 1  Internal         dashboards, runbooks            OIDC + posture
  Tier 2  Engineering      Git, CI, artifact registry      OIDC + posture + device-bound token
  Tier 3  Restricted       prod DB consoles, secrets       OIDC + mTLS/SSH cert + JIT approval
  Tier 4  Legacy monolith  no modern auth                 break-glass only, time-boxed
```

### Implementation

The access proxy evaluates policy per request, with posture as a live input, not a
once-at-login snapshot:

```java
@Service
class AccessDecisionService {
    /**
     * Deny by default. The decision combines: who (OIDC), what device (posture), what
     * resource (tier), and what changed (risk events) - evaluated on every request or on a
     * short TTL, not once at sign-in.
     */
    Decision evaluate(AccessRequest req) {
        Identity id = identityService.verify(req);          // token + signature + audience
        Posture p  = postureService.assess(id.deviceId());  // EDR, patch level, disk encryption

        if (p.isCompromised())          return deny("device reported compromised");
        if (!p.isCompliant())           return deny("posture non-compliant: " + p.failedChecks());
        if (p.lastSeen().isBefore(Instant.now().minus(Duration.ofDays(14))))
                                          return deny("device not seen in 14 days - re-enrol");
        if (riskEngine.hasRecentAnomaly(id, req)) return deny("elevated risk session");
        return policy.allow(id, req.resource(), req.tier());
    }

    /** Continuous evaluation: a posture change revokes access mid-session. */
    @EventListener
    void onDeviceRiskChanged(DeviceRiskEvent e) {
        sessions.forUser(e.userId()).forEach(s -> {
            s.revoked = true;
            audit.security("ACCESS_REVOKED_POSTURE", e.userId(), e.reason());
        });
    }
}
```

Time-boxed, JIT-approved access to the restricted tier replaces standing privilege — the
single change that most reduces blast radius:

```java
@Service
class JustInTimeAccess {
    @Value("${jit.max-duration:PT30M}") Duration maxDuration;
    @Value("${jit.default-duration:PT15M}") Duration defaultDuration;

    @Transactional
    Grant grantAccess(Request req, Requester caller) {
        requireTier3(caller);                                 // approver must themselves be trusted
        Grant g = new Grant(UUID.randomUUID().toString(), caller.userId(), req.target(),
                            Instant.now().plus(Duration.between(Instant.now(), maxDuration)),
                            approvalRequestId(req.approvals));
        grants.save(g);
        siem.emit("JIT_ACCESS_GRANTED", g.id(), caller.userId(), req.target(), g.expiresAt());
        return g;
    }

    @Scheduled(fixedDelay = 60_000)
    void expireGrants() {
        grants.findAllActive().stream()
            .filter(g -> g.expiresAt().isBefore(Instant.now()))
            .forEach(g -> { g.revoked = true; siem.emit("JIT_ACCESS_EXPIRED", g.id(), g.userId()); });
    }
}
```

Workload identity replaces the flat network's implicit trust; the mesh provides mTLS plus
authorization so no service can reach another without a declared dependency:

```java
@Bean
WorkloadIdentityPolicy workloadPolicy() {
    return WorkloadIdentityPolicy.builder()
        .trustDomain(TrustDomain.from("spiffe://example.internal"))
        // SVIDs are short-lived and rotated automatically; no long-lived service token exists.
        .defaultSvidTtl(Duration.ofMinutes(30))
        // Authorization is derived from the SVID's own path, not from a config file,
        // so identity and permission cannot drift apart.
        .authorizationPolicy(pathToService("ns/orders/sa/*"), allow("ns/db-proxy/sa/read"))
        .authorizationPolicy(pathToService("ns/payments/sa/*"), allow("ns/db-proxy/sa/read", "ns/ledger/sa/write"))
        .build();
}
```

### Non-functional requirements

- **Availability**: access availability must not regress during migration. Proxy is
  multi-region, and each tier has a documented rollback path back to the VPN route.
- **Latency**: added latency per proxied request p95 under 25 ms, measured per tier.
- **Migration sequence**: Tier 1 → Tier 2 → Tier 3 → Tier 4. Each tier keeps the VPN
  path as a fallback for a defined window, then the route is deleted, not left dormant.
- **Blast radius**: a compromised contractor laptop is confined to Tier 0/1 resources;
  a compromised service is confined to its declared dependencies. Both are measured in
  quarterly tests, not assumed.
- **Posture enforcement**: unmanaged or unencrypted devices are refused; enforcement
  cannot be disabled by the user, only by security with a logged exception.
- **Session policy**: 8 h max for Tier 1/2, 30 min JIT for Tier 3, phishing-resistant MFA.
- **Observability**: every decision logged with subject, device, posture, tier, decision;
  deny-rate anomalies and posture-driven revocations alert the SOC (labs 19/20).
- **Decommissioning**: the VPN concentrator's address ranges are removed from route
  tables and firewall rules only after traffic analysis shows zero legitimate use.

### Sourced field notes (fetched Oct 2026 — verify before citing)
- NIST SP 800-207 "Zero Trust Architecture" defines the policy decision/enforcement points
  and the core tenets (never trust/always verify, assume breach) implemented by the proxy.
  https://csrc.nist.gov/pubs/sp/800/207/final
- Kubernetes Network Policies are used for workload-level micro-segmentation, the
  default-deny enforcement mechanism behind the declared-dependency model.
  https://kubernetes.io/docs/concepts/services-networking/network-policies/

## Deliverables

- [x] Per-request access decision combining identity, posture, tier, and live risk
- [x] Trust tiers 0–4 with an explicit resource classification per tier
- [x] JIT, time-boxed, dual-approved access replacing standing privilege for Tier 3
- [x] Continuous evaluation revoking sessions on posture change
- [x] Workload identity with short-lived SVIDs and policy derived from identity path
- [x] Staged migration with per-tier rollback and eventual VPN route deletion
- [x] Blast-radius tests run quarterly for both human and workload compromise
- [x] Decision telemetry with deny-anomaly and posture-revocation alerting
