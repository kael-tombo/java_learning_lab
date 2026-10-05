# Authorization & RBAC - MINI PROJECT

## Project: LedgerVault — one permission model enforced at URL, method, and data layers

A multi-tenant expense system. Authorization is currently scattered across controllers as
`if (user.isManager())`. Replace it with a single permission vocabulary, deny by default,
and enforce at three layers so no entry point bypasses the policy.

### Architecture

```
 Entry point            Layer                       Example
 ─────────────────────────────────────────────────────────────────
 HTTP request     ──▶   URL matcher        GET /api/ledger/**  requires LEDGER_READ
 Service method   ──▶   @PreAuthorize      requires LEDGER_APPROVE
 Repository/row   ──▶   Row guard          entry.tenantId == caller.tenantId
 Message consumer ──▶   PolicyService       same checks, no SecurityContext shortcut
```

Default-deny: the guard consults a registry, and *absence* of a rule means denial.

```java
@Component
class PolicyEngine {
    private final Map<String, PermissionRule> rules = new ConcurrentHashMap<>();
    record Subject(String userId, String tenantId, Set<String> roles, Map<String,Object> attrs) {}
    record Resource(String type, String id, String tenantId, String status, String region) {}
    record Decision(boolean allowed, String reason) {}

    /** Fail-closed: an unregistered action is a DENY, never an implicit allow. */
    Decision check(Subject s, String action, Resource r) {
        if (s == null || action == null) return new Decision(false, "missing subject/action");
        // 1. Tenant boundary first - a cross-tenant request fails before any role is considered.
        if (r.tenantId() != null && !r.tenantId().equals(s.tenantId()))
            return new Decision(false, "tenant-isolation");
        PermissionRule rule = rules.get(action);
        if (rule == null) return new Decision(false, "no rule for action " + action);  // deny by default
        return rule.evaluate(s, r);
    }

    void register(PermissionRule r) { rules.put(r.action(), r); }
}
```

Attribute rules capture what roles cannot. Role explosion would otherwise demand roles like
`APPROVER_EU`, `APPROVER_APAC`, `APPROVER_OVER_5000` — combinatorially impossible to maintain:

```java
// RBAC part: coarse role gate.
register(action("LEDGER_APPROVE").requireRole("LEDGER_APPROVER"));
// ABAC part: status, region, and amount conditions the role cannot express.
register(action("LEDGER_VOID")
    .requireRole("LEDGER_APPROVER")
    .require((s, r) -> "POSTED".equals(r.status()),                "only POSTED entries can be voided")
    .require((s, r) -> s.attrs().get("region").equals(r.region()), "approver must cover the region")
    .require((s, r) -> s.attrs().get("clearance") instanceof Integer c && c >= 3, "clearance >= 3"));
```

Service methods use the same engine, so an internal call cannot skip the check:

```java
@Service
class LedgerService {
    @Transactional
    public LedgerEntry approve(String entryId) {
        LedgerEntry e = repo.findById(entryId).orElseThrow();
        var subject = subjectProvider.current();
        // Same engine, same rules, fail-closed on a missing SecurityContext.
        policy.require(subject, "LEDGER_APPROVE", toResource(e));
        return repo.save(e.approve(subject.userId(), Instant.now()));
    }
}

@Component
class PolicyGate {
    void require(Subject s, String action, Resource r) {
        Decision d = engine.check(s, action, r);
        if (!d.allowed()) { audit.deny(s, action, r, d.reason()); throw new AccessDeniedException(action); }
        audit.allow(s, action, r);
    }
}
```

A message consumer has no `SecurityContext`, which is exactly the bug this design prevents:

```java
@Component
class ApprovalRequestConsumer {
    @KafkaListener(topics = "ledger.approval.requested")
    void onMessage(ApprovalRequested msg) {
        // Do NOT assume a caller context exists. Derive the subject from the message identity.
        Subject svc = new Subject("svc-approver", msg.tenantId(), Set.of("LEDGER_APPROVER"),
                                  Map.of("region", msg.region(), "clearance", 4));
        policy.require(svc, "LEDGER_APPROVE", new Resource("LEDGER", msg.entryId(), msg.tenantId(), msg.status(), msg.region()));
        ledger.approveFromWorkflow(msg.entryId(), "svc-approver");
    }
}
```

### Test It

```java
@Test void unknownActionIsDeniedByDefault() {
    assertFalse(engine.check(subject("u1","t1", Set.of("ADMIN")), "DELETE_EVERYTHING", resource).allowed());
}

@Test void crossTenantIsDeniedEvenForAdmin() {
    var s = subject("admin", "tenant-A", Set.of("LEDGER_APPROVER"));
    assertFalse(engine.check(s, "LEDGER_APPROVE", resource("e1", "tenant-B")).allowed());
}

@Test void approvalRequiresRegionMatch() {
    var s = subject("u2", "t1", Set.of("LEDGER_APPROVER"), Map.of("region", "EU", "clearance", 3));
    assertTrue(engine.check(s, "LEDGER_APPROVE", resource("e1","t1","APPROVED","EU")).allowed());
    assertFalse(engine.check(s, "LEDGER_APPROVE", resource("e1","t1","APPROVED","APAC")).allowed());
}

@Test void consumerPathIsAlsoGuarded() {
    assertThrows(AccessDeniedException.class,
        () -> consumer.onMessage(requestWithRegion("APAC")));   // svc subject only covers EU
}
```

## Deliverables

- [ ] `PolicyEngine` with deny-by-default semantics and an explicit rule registry
- [ ] Tenant-boundary check evaluated before any role logic
- [ ] RBAC roles plus ABAC attribute rules (status, region, clearance, amount)
- [ ] `@PreAuthorize` guard calling the same engine at the service layer
- [ ] Message-consumer authorization that derives a subject explicitly
- [ ] Authorization decision audit log (subject, action, resource, reason)
- [ ] Tests: default deny, cross-tenant, attribute mismatch, consumer path
- [ ] A before/after inventory of every authorization check you replaced
