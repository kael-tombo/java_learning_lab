# Data Governance (Deep) — MINI PROJECT

## Project: Governance Control System

Policy-as-code, classification with evidence, attribute-based access control
with purpose limitation, exception management, and an effectiveness report.

### Scope
- `PolicyEngine`: rules with severity, scope, evaluation context, and a reason.
- `Classifier`: auto-classification with stored evidence; default-deny.
- `AccessDecision`: RBAC + ABAC (purpose, region, license) + masking level.
- `ExceptionRegister`: approved exceptions with approver and expiry.
- `EffectivenessTester`: synthetic probes that verify controls actually work.
- `AuditPack`: assembles evidence for a time window.

### Architecture

```
  data change --> policy engine (CI gate) --pass--> deploy
                        | fail
                        v
                  exception request --> register (approver, expiry)
                        |
  runtime access request --> AccessDecision engine (RBAC + ABAC + masking)
                        |
                        v
                 audit log (who/what/why/decision/policy)
                        |
                 effectiveness probes (do the controls hold?)
```

### Implementation — policy engine

```java
public record PolicyContext(String datasetId, String actor, String purpose,
                            String region, Instant now, Set<String> tags,
                            Classification classification, String environment) {}

public record Finding(String policyId, Severity severity, String message,
                      String remediation, String datasetId) {
    public String toTicket() {
        return policyId + " [" + severity + "] " + datasetId + ": " + message
                + "\nRemediation: " + remediation;
    }
}

public interface Rule {
    String id();
    String title();
    Severity defaultSeverity();
    List<Finding> evaluate(PolicyContext ctx, Registry registry);
}

/**
 * A rule is a pure function of (context, registry). No I/O in a rule: that is
 * what makes the same rule usable in CI, at runtime, and in a scheduled sweep.
 */
public final class PiiNeedsMasking implements Rule {
    public String id() { return "GOV-020"; }
    public String title() { return "PII columns must be masked or tokenized"; }
    public Severity defaultSeverity() { return Severity.BLOCK; }

    public List<Finding> evaluate(PolicyContext ctx, Registry r) {
        if (!isPii(ctx.classification())) return List.of();
        List<String> unmasked = r.columnsOf(ctx.datasetId()).stream()
                .filter(FieldRef::sensitive)
                .filter(f -> !f.masked() && !f.tokenized())
                .map(FieldRef::name).toList();
        return unmasked.isEmpty() ? List.of()
                : List.of(new Finding(id(), defaultSeverity(),
                        "unmasked sensitive columns: " + unmasked,
                        "apply a masking policy or tokenize before publishing",
                        ctx.datasetId()));
    }
}
```

### Access decision: RBAC + ABAC + purpose

```java
public record Subject(String id, Set<String> roles, String department,
                      Set<String> licenses, String region, boolean contractor) {}

public record Resource(String datasetId, Classification classification,
                       Set<String> allowedRegions, String purposeRequired) {}

public record AccessRequest(Subject subject, Resource resource, String purpose,
                            String clientIp, Instant at) {}

public sealed interface AccessDecision permits Allow, Deny, AllowMasked {}

public record Allow(Set<String> columns, String basis, Instant expiresAt) implements AccessDecision {}
public record AllowMasked(Set<String> columns, Map<String,String> masks, String basis)
        implements AccessDecision {}
public record Deny(String reason, String policyId, String appealPath) implements AccessDecision {}

public final class AccessEngine {
    public AccessDecision decide(AccessRequest req) {
        // 1. RBAC: does any role grant access to the resource at all?
        if (!roleGrants(req.subject().roles(), req.resource().datasetId())) {
            return new Deny("no role grants access to " + req.resource().datasetId(),
                    "RBAC-001", "request an exception in the data portal");
        }

        // 2. ABAC: purpose limitation. PHI access requires a declared purpose,
        //    and contractors are excluded regardless of role.
        if (isPhi(req.resource().classification())) {
            if (req.subject().contractor()) {
                return new Deny("contractors cannot access PHI", "ABAC-002",
                        "engage through the vendor SOW process");
            }
            if (req.purpose() == null || req.purpose().isBlank()) {
                return new Deny("PHI access requires a declared purpose",
                        "ABAC-003", "declare a purpose in the data portal");
            }
        }

        // 3. Residency: subject region must cover the data's regions.
        if (!covers(req.subject().region(), req.resource().allowedRegions())) {
            return new Deny("data residency restriction: " + req.resource().allowedRegions(),
                    "ABAC-004", "request a cross-region processing approval");
        }

        // 4. Sensitivity decides the shape of the grant, not whether it exists.
        Set<String> cols = columnsFor(req);
        if (req.resource().classification() == Classification.PHI) {
            return new AllowMasked(cols, masksFor(cols), "PHI access with direct identifiers masked");
        }
        if (isPci(req.resource().classification())) {
            return new AllowMasked(cols, Map.of("card_pan", "****-****-****-1234"),
                    "PCI access: PAN tokenized");
        }
        return new Allow(cols, "role grant", null);
    }
}
```

### Exception register with expiry

```java
public record PolicyException(String id, String policyId, String scope,
                              String justification, String requestedBy,
                              String approvedBy, Instant approvedAt, Instant expiresAt,
                              boolean compensatingControl) {
    public boolean active(Instant now) { return now.isBefore(expiresAt); }
    public boolean overdue(Instant now) { return now.isAfter(expiresAt); }
    public long daysRemaining(Instant now) {
        return Duration.between(now, expiresAt).toDays();
    }
}

public final class ExceptionGate {
    /**
     * An exception that has not been renewed before expiry must re-block. The
     * classic governance failure is an exception approved once in 2021 and
     * never revisited, which is indistinguishable from no control at all.
     */
    public List<Finding> evaluate(List<PolicyException> exceptions,
                                  List<Finding> findings, Instant now) {
        List<Finding> out = new ArrayList<>();
        for (Finding f : findings) {
            PolicyException e = exceptions.stream()
                    .filter(x -> x.policyId().equals(f.policyId()))
                    .filter(x -> x.scope().equals(f.datasetId()))
                    .findFirst().orElse(null);
            if (e == null) {
                out.add(f);
            } else if (e.overdue(now)) {
                out.add(new Finding(f.policyId(), Severity.BLOCK,
                        f.message() + " (exception " + e.id() + " expired "
                                + e.expiresAt() + ")",
                        "renew the exception with a current justification", f.datasetId()));
            } else if (!e.compensatingControl()) {
                out.add(new Finding(f.policyId(), Severity.TICKET,
                        f.message() + " (exception " + e.id() + ", "
                                + e.daysRemaining(now) + " days left, no compensating control)",
                        "document a compensating control before expiry", f.datasetId()));
            }
        }
        return out;
    }
}
```

### Effectiveness testing: verify the controls, do not assert them

```java
public record ControlTest(String controlId, String hypothesis, boolean passed,
                          String evidence, Instant at) {}

public final class EffectivenessTester {
    /**
     * A control is effective only if attempting to violate it fails. These are
     * synthetic probes run on a schedule; they are the difference between
     * "we have a policy" and "we have a working control".
     */
    public List<ControlTest> run(AccessEngine engine, Warehouse warehouse) {
        List<ControlTest> out = new ArrayList<>();
        Subject contractor = new Subject("c1", Set.of("ANALYST"), "vendor",
                Set.of(), "US", true);
        AccessDecision d1 = engine.decide(new AccessRequest(contractor,
                new Resource("phi.patients", Classification.PHI, Set.of("US"), "TREATMENT"),
                "TREATMENT", "10.0.0.1", Instant.now()));
        out.add(new ControlTest("ABAC-002",
                "a contractor with the ANALYST role cannot read PHI",
                d1 instanceof Deny, "decision=" + d1, Instant.now()));

        AccessDecision d2 = engine.decide(new AccessRequest(
                new Subject("a1", Set.of("ANALYST"), "analytics", Set.of(), "EU", false),
                new Resource("phi.patients", Classification.PHI, Set.of("US"), "TREATMENT"),
                "TREATMENT", "10.0.0.2", Instant.now()));
        out.add(new ControlTest("ABAC-004",
                "an EU analyst cannot read US-resident PHI",
                d2 instanceof Deny, "decision=" + d2, Instant.now()));

        // And a positive control: the legitimate path must still work, or the
        // control is just an outage.
        AccessDecision d3 = engine.decide(new AccessRequest(
                new Subject("n1", Set.of("CLINICIAN"), "care", Set.of("TREATMENT"), "US", false),
                new Resource("phi.patients", Classification.PHI, Set.of("US"), "TREATMENT"),
                "TREATMENT", "10.0.0.3", Instant.now()));
        out.add(new ControlTest("ABAC-003",
                "a clinician with a purpose can read PHI with masking",
                d3 instanceof AllowMasked, "decision=" + d3, Instant.now()));
        return out;
    }
}
```

### Audit pack

```java
public record AuditPack(Instant period, String datasetId, List<ControlTest> controls,
                        List<PolicyException> exceptions, List<AccessEvent> accesses,
                        List<Finding> openFindings, double controlPassRate) {
    public boolean auditorReady() {
        return controls.stream().allMatch(ControlTest::passed)
                && openFindings.stream().noneMatch(f -> f.severity() == Severity.BLOCK)
                && exceptions.stream().noneMatch(PolicyException::overdue);
    }
}
```

### Stretch
- Add a segregation-of-duties rule: the dataset owner cannot approve their own exception.
- Add quarterly re-certification that demotes a dataset whose description is stale.
- Add a policy-coverage metric: which rules have no scope and therefore never run.

## Deliverables
- [ ] Policy engine with pure-function rules usable in CI, runtime, and sweeps
- [ ] Access engine with RBAC + ABAC + purpose limitation + masking tiers
- [ ] Exception register with expiry, compensating-control requirement, and re-blocking
- [ ] Effectiveness probes including a positive control
- [ ] Audit pack generator with an `auditorReady` assertion
- [ ] Governance metrics: control pass rate, exception age, open findings by severity
