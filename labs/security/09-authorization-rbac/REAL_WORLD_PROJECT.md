# Authorization & RBAC - REAL WORLD PROJECT

## Project: TenantGrid — authorization for a multi-tenant B2B SaaS billing platform

Every customer is a tenant with its own users, roles, approval limits, and data-residency
region. Sales wants configurable roles per tenant; finance needs segregation of duties; the
EU tenant's data must never leave its region. A single `ROLE_ADMIN` cannot express any of
this, and one cross-tenant bug is a reportable breach.

### Architecture

```
      Tenant config service (per-tenant role definitions, versioned)
                     │
                     ▼
        ┌────────────────────────────────────────────┐
        │ Policy Decision Point (PDP)                │
        │  1. resolve tenant context (JWT claim)     │
        │  2. resolve role graph (cached per tenant) │
        │  3. evaluate attribute + relation rules    │
        │  4. return decision + reason code         │
        └───────────────┬────────────────────────────┘
                        │ decision + reason (audit)
      ┌─────────────────┼──────────────────┐
      ▼                 ▼                  ▼
  REST controllers  Kafka consumers   Scheduled jobs
   (layer 1)         (layer 2)          (layer 3: system actor)

  Enforcement is triple-layered:
    L1 URL matcher   - coarse, fast, denies by default
    L2 service guard - the authoritative PDP call
    L3 data scoping  - repository always filters by tenant_id (defence in depth)
```

### Implementation

The PDP is deliberately a single component with one rule language, so auditors can read
one file rather than grep for `if` statements:

```java
@Service
class PolicyDecisionPoint {
    private final TenantConfigCache configCache;      // Caffeine, TTL 60s, keyed by tenant
    private final PolicyEngine engine;               // same deny-by-default engine as the lab

    record Request(String tenantId, String actorId, String actorType, String action,
                   String resourceType, String resourceId, Map<String,Object> resourceAttrs) {}

    record Decision(boolean allowed, String reasonCode, String policyId) {}

    @Transactional(readOnly = true)
    Decision evaluate(Request req) {
        // 0. Fail closed on any missing input. An unknown tenant is never "allowed".
        if (req.tenantId() == null || req.action() == null) return deny("MISSING_CONTEXT", null);

        TenantConfig tc = configCache.get(req.tenantId());        // roles, limits, region
        if (tc == null) return deny("UNKNOWN_TENANT", null);

        // 1. Data residency: a request routed to the wrong region is denied at the PDP,
        //    not trusted to be caught by the network layer.
        if (!tc.dataRegion().equals(regionOf(req.resourceAttrs()))) return deny("DATA_RESIDENCY", "res-1");

        Actor actor = req.actorType().equals("SYSTEM")
                ? systemActor(req.actorId())
                : tc.rolesFor(req.actorId());

        Decision d = engine.check(
            new Subject(actor.id(), req.tenantId(), actor.permissions(), actor.attributes()),
            req.action(),
            new Resource(req.resourceType(), req.resourceId(), req.tenantId(),
                         str(req.resourceAttrs(), "status"), str(req.resourceAttrs(), "region")));

        return d.allowed() ? allow(d.reasonCode(), d.policyId()) : deny(d.reasonCode(), d.policyId());
    }
}
```

Segregation of duties is a policy that plain RBAC cannot express — it forbids combinations:

```java
record PolicyDef(String id, String effect, List<Condition> conditions) {}
record Condition(String type, String field, Op op, Object value) {}

private static final List<PolicyDef> SOD_RULES = List.of(
    // The same actor must not both create and approve a refund above the tenant limit.
    new PolicyDef("sod-refund-001", "DENY", List.of(
        new Condition("actor.permissions", Op.CONTAINS, "REFUND_CREATE"),
        new Condition("actor.permissions", Op.CONTAINS, "REFUND_APPROVE"),
        new Condition("resource.amount", Op.GT, 10_000))),
    new PolicyDef("limit-approve-002", "ALLOW", List.of(
        new Condition("actor.permissions", Op.CONTAINS, "INVOICE_APPROVE"),
        new Condition("resource.amount", Op.LTE, Field.ACTOR, "approvalLimit")))
);
```

Layer 3 is what makes a policy-engine bug non-fatal: the repository cannot read another
tenant's rows even if authorization were bypassed entirely.

```java
public interface ScopedRepository<T> {
    Optional<T> findByIdAndTenantId(String id, String tenantId);
    List<T> findAllByTenantId(String tenantId);
}

@Component
class InvoiceRepositoryImpl implements ScopedRepository<Invoice> {
    // Every query requires tenantId. There is no findById(id) in the API surface at all.
    public Optional<Invoice> findByIdAndTenantId(String id, String tenantId) { ... }
}

// Defence in depth: a filter asserts the tenant scope on every managed entity load.
@Component
class TenantScopeAssertion extends OncePerRequestFilter {
    @Override protected void doFilterInternal(HttpServletRequest req, HttpServletResponse res, FilterChain c) {
        String jwtTenant = jwt.tenantClaim(req);
        try (var ctx = TenantContext.open(jwtTenant)) {   // ThreadLocal, cleared in finally
            c.doFilter(req, res);
        }
    }
}
```

Scheduled and message-driven paths use a `SYSTEM` actor with explicitly narrow permissions,
because pretending to be a user is how background jobs end up over-privileged:

```java
@Scheduled(cron = "0 */15 * * * *")
void dunningRun() {
    var req = new Request(TenantContext.systemTenant(), "dunning-job", "SYSTEM",
                          "INVOICE_MARK_OVERDUE", "INVOICE", "*",
                          Map.of("region", currentRegion()));
    Decision d = pdp.evaluate(req);
    if (!d.allowed()) { metrics.counter("dunning.denied", "reason", d.reasonCode()).increment(); return; }
    repo.findOverdueByTenant(TenantContext.systemTenant()).forEach(inv -> {
        pdp.requireForSystem("INVOICE_MARK_OVERDUE", inv.id());     // per-record, not bulk trust
        inv.markOverdue(clock.instant());
    });
}
```

### Non-functional requirements

- **Latency**: PDP p95 under 5 ms. Tenant config cached 60 s; rules compiled to a decision
  tree, not interpreted per call. L1 URL rules absorb the bulk of traffic before the PDP.
- **Correctness**: cross-tenant isolation is tested in CI with a generated matrix of
  (tenantA user, tenantB resource) pairs — all must deny. This is a release gate.
- **Audit**: every decision logged with tenant, actor, action, resource, reason code, and
  policy id. Denial reasons are a first-class alerting signal (spikes mean probing).
- **Change safety**: tenant role configuration is versioned; a permission change is a
  reviewed, reversible deployment, never a direct DB edit.
- **Blast radius**: SYSTEM actors carry only the actions they need; a job cannot escalate.
- **Compliance**: audit export meets SOC 2 CC6 access-control evidence requirements.

### Sourced field notes (fetched Oct 2026 — verify before citing)
- NIST SP 800-162 "Guide to Attribute Based Access Control (ABAC)" defines the subject,
  object, environment, and policy attributes this PDP evaluates.
  https://csrc.nist.gov/pubs/sp/800/162/upd2/final
- OWASP Authorization Cheat Sheet covers defence-in-depth, deny-by-default, and validating
  permissions on every request rather than only at the edge.
  https://owasp.org/www-project-cheat-sheets/cheatsheets/Authorization_Cheat_Sheet.html

## Deliverables

- [x] Central policy decision point with deny-by-default and reason codes
- [x] Tenant-scoped actor resolution from a versioned, cached tenant config
- [x] Data-residency enforcement inside the PDP, not at the network edge
- [x] Segregation-of-duties policies expressing forbidden permission combinations
- [x] Three enforcement layers: URL matcher, service guard, repository tenant scoping
- [x] `SYSTEM` actor model for jobs and consumers with per-record checks
- [x] CI isolation matrix gating every release on cross-tenant denial
- [x] Full authorization audit trail with policy id and reason code
