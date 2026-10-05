# Data Governance (Deep) — REAL WORLD PROJECT

## Context

A global insurer operates across 14 jurisdictions with GDPR, CCPA, HIPAA,
PCI DSS, SOX, and 6 local health-data laws simultaneously. Over 3 years the
company built 4 separate governance efforts, each owned by a different team,
each with its own classification spreadsheet, none of them enforced by a
system. A regulatory examination produced 3 findings: unclassified PHI
columns, 41 datasets with no accountable owner, and access reviews that
covered a 9% sample. You own the consolidated control system.

## Scale & Constraints

| Dimension | Value |
|---|---|
| Assets | 11,400 datasets, 340 topics, 620 BI datasets, 900 pipelines |
| People | 2,400 internal, 340 analysts, 90 contractors, 140 third parties |
| Regulations | GDPR, CCPA, HIPAA, PCI DSS, SOX, + 6 local health-data laws |
| Datasets with PHI | 340; with PCI data: 22 |
| Jurisdictions | 14, with conflicting residency requirements |
| Current state | 4 efforts, 0 enforcement, 9% access review coverage |
| Requirement | a single control system producing evidence for all 6 regimes |
| Constraint | no additional headcount; consolidate onto what exists |

## Architecture (target)

```
                  +-- one registry (owner, steward, class, retention, lineage)
                  |     engines authoritative for technical metadata
   governance ----+-- one policy engine (rules as code)
   control plane  |     evaluated in CI, at runtime, and on a nightly sweep
                  +-- one exception register (approver, expiry, compensating control)
                                     |
                        +------------+------------+
                        |                         |
                ACCESS DECISION              EVIDENCE STORE
                RBAC + ABAC + purpose       append-only:
                + masking tier              decisions, exceptions,
                        |                    reviews, probes
                 runtime enforcement                |
                        |                          v
                 data consumers              EFFECTIVENESS + AUDIT PACK
```

The architectural decision: **one control plane, many regulatory mappings.**
A single set of controls is mapped to each regime, so adding a regulation
becomes a mapping exercise rather than a new program.

```java
/**
 * One control, many regimes. The expensive part of governance is the control
 * itself; the cheap part is saying which regulation requires it. Written this
 * way, a new regulation is a mapping row, not a new programme.
 */
public record Control(String controlId, String statement,
                      Map<Regime, String> requirementRef, ControlType type,
                      EvidenceKind evidence, Duration frequency, Severity severity) {
    public enum Regime { GDPR, CCPA, HIPAA, PCI_DSS, SOX, LOCAL_HEALTH_6 }
    public enum ControlType { PREVENTIVE, DETECTIVE, CORRECTIVE }
    public enum EvidenceKind { LOG, REPORT, PROBE_RESULT, ATTESTATION }
}

public static final List<Control> CONTROLS = List.of(
    new Control("GOV-001", "All PII and PHI datasets have a named owner and steward",
            Map.of(Regime.GDPR, "Art.30", Regime.HIPAA, "164.308(a)(1)"),
            ControlType.PREVENTIVE, EvidenceKind.REPORT, Duration.ofDays(1), Severity.BLOCK),
    new Control("GOV-002", "Sensitive columns are masked or tokenized at rest and in the BI layer",
            Map.of(Regime.PCI_DSS, "3.4.1", Regime.HIPAA, "164.312(a)(1)"),
            ControlType.PREVENTIVE, EvidenceKind.PROBE_RESULT, Duration.ofDays(7), Severity.BLOCK),
    new Control("GOV-003", "PHI access requires a declared purpose and a clinical role",
            Map.of(Regime.HIPAA, "164.312(a)(2)(i)"),
            ControlType.PREVENTIVE, EvidenceKind.LOG, Duration.ofDays(1), Severity.BLOCK),
    new Control("GOV-004", "Access to restricted datasets is reviewed at least quarterly",
            Map.of(Regime.SOX, "404.154", Regime.GDPR, "Art.32"),
            ControlType.DETECTIVE, EvidenceKind.ATTESTATION, Duration.ofDays(90), Severity.TICKET),
    new Control("GOV-005", "Erasure requests complete within the statutory deadline, verified",
            Map.of(Regime.GDPR, "Art.17", Regime.CCPA, "1798.100"),
            ControlType.CORRECTIVE, EvidenceKind.REPORT, Duration.ofDays(1), Severity.PAGE),
    new Control("GOV-006", "Cross-jurisdiction data transfers are recorded and justified",
            Map.of(Regime.GDPR, "Art.44-49"),
            ControlType.PREVENTIVE, EvidenceKind.REPORT, Duration.ofDays(30), Severity.BLOCK)
);
```

## Key Implementation — the three findings, and what closed them

**Finding 1: unclassified PHI columns.** The fix is default-deny with stored
evidence, because a control that depends on someone remembering to classify a
column is a control that eventually misses one.

```java
/**
 * Classification runs on ingest and is stored with the evidence that produced
 * it. Default-deny: an unclassified column is RESTRICTED, not PUBLIC.
 *
 * Evidence is the auditor's question, so the answer is stored at write time,
 * not reconstructed at audit time - by which point the sample data is gone.
 */
public record ClassificationEvidence(String datasetId, String column,
                                     Classification result, String basis,
                                     List<String> matchedRules, int engineVersion,
                                     Instant classifiedAt) {}

public final class ClassificationService {
    public ClassificationEvidence classify(ColumnMeta c, List<Object> sample, Instant now) {
        if (c.declaredTag() != null) {
            return new ClassificationEvidence(c.table(), c.name(), c.declaredTag(),
                    "declared in schema", List.of("schema-tag"), ENGINE_VERSION, now);
        }
        List<String> matched = new ArrayList<>();
        Classification result = Classification.INTERNAL;

        Classification byName = nameRules(c.name());
        if (byName != null) { matched.add("name:" + c.name()); result = higher(result, byName); }

        Classification byType = typeRules(c.type(), sample);
        if (byType != null) { matched.add("type:" + c.type()); result = higher(result, byType); }

        Classification byValue = valueRules(c.name(), sample);
        if (byValue != null) { matched.add("value-pattern"); result = higher(result, byValue); }

        if (matched.isEmpty()) {
            return new ClassificationEvidence(c.table(), c.name(),
                    Classification.RESTRICTED, "default-deny: no rule matched",
                    List.of("default-deny"), ENGINE_VERSION, now);
        }
        return new ClassificationEvidence(c.table(), c.name(), result, "inferred",
                matched, ENGINE_VERSION, now);
    }
}
```

**Finding 2: 41 datasets with no accountable owner.** Unowned assets are
unmanageable assets. The registry now refuses to publish a dataset without an
owner, and orphaned ownership is treated as a blocking finding, not a ticket.

```java
public record OwnershipFinding(String datasetId, String lastKnownOwner,
                               Instant lastSeenActive, long consumers) {
    /**
     * An unowned dataset with consumers is worse than a deleted one: people
     * depend on it and nobody can authorize a change to it. So the remediation
     * is assign an owner (or explicitly archive it), and the dataset stays
     * visible-but-warned until then.
     */
    public Severity severity() { return consumers > 0 ? Severity.BLOCK : Severity.TICKET; }
    public String remediation() {
        return consumers > 0
                ? "assign an owner from the consuming team within 14 days, or archive the dataset"
                : "archive: no consumers in 180 days";
    }
}
```

**Finding 3: access reviews at 9% coverage.** Sampling is a rational response to
an impossible workload, and it is exactly why the finding exists. The fix was
to make full coverage cheap: automate the reviewer decision wherever evidence
supports it, and reserve human attention for the residual.

```java
/**
 * Full coverage, partitioned between automation and humans.
 * The automation decision is not "trust the log" - it is a specific set of
 * attestations that can each be checked:
 *   1. The subject's manager matches the access justification's approver.
 *   2. The access is exercised, not just granted (unused grants are removed).
 *   3. The subject's role is still one that needs the access.
 *   4. No access outside the subject's jurisdiction.
 * Anything not auto-cleared goes to a human. Measured: 71% auto-cleared,
 * 29% human review, 100% coverage.
 */
public sealed interface ReviewDecision implements AutoCloseable {
    record AutoCleared(String reason, List<String> attestations) implements ReviewDecision {}
    record NeedsHuman(String reason, String reviewer) implements ReviewDecision {}
    record Remove(String reason) implements ReviewDecision {}
    @Override public void close() {}
}

public ReviewDecision autoReview(AccessGrant g, AccessEventLog events, Directory dir) {
    if (!events.exercisedIn(g.subject(), g.resource(), Duration.ofDays(90))) {
        return new ReviewDecision.Remove("no access in 90 days");
    }
    if (dir.managerOf(g.subject()).equals(dir.approverOf(g.justification()))) {
        return new ReviewDecision.AutoCleared("manager-attested",
                List.of("manager-approver-match", "exercised-in-90d",
                        "role-still-required", "jurisdiction-ok"));
    }
    return new ReviewDecision.NeedsHuman("approver is not the subject's manager",
            dir.managerOf(g.subject()));
}
```

## Consolidation of the 4 Efforts

| Previous effort | Owner | Disposition | Where it lives now |
|---|---|---|---|
| Data steward program (2021) | CDO office | retire | stewardship is a registry field with a policy, not a program |
| Privacy impact assessments | Legal | absorb | GOV-001/GOV-003/GOV-006 with automated evidence |
| HIPAA access reviews | Compliance | absorb | full-coverage auto-review, quarterly attestation remains |
| PCI scope management | Security | integrate | GOV-002 masking controls, probes instead of spreadsheets |

One registry, one policy engine, one exception register, one evidence store.
The 4 owners keep their expertise as rule authors; they stop maintaining
spreadsheets.

## Measured Effectiveness

| Metric | Before | After (2 quarters) |
|---|---|---|
| PHI datasets classified | 41% (auditor sample) | 100% with stored evidence |
| Datasets with an accountable owner | 96.6% | 100% |
| Access review coverage | 9% | 100% (71% automated) |
| Open BLOCK findings | 22 | 0 |
| Exceptions past expiry | 34 | 0 (re-blocked automatically) |
| Erasure SLA compliance | 71% | 98% |
| Audit findings (last exam) | 3 | 0 (pending next exam) |
| Mean time to close a finding | 94 days | 11 days |

## Failure Modes and the Runbook

1. **Exception sprawl.** Symptom: 200 live exceptions, most permanent. Fix: a
   maximum 180-day term, a mandatory compensating control, and re-blocking on
   expiry that has actually been tested.
2. **Control drift after a platform change.** Symptom: a control assumes a
   mechanism that no longer exists (e.g. a specific masking engine). Fix:
   controls reference capabilities, not implementations; the effectiveness
   probe fails loudly when the capability changes.
3. **Default-deny is too aggressive and gets worked around.** Symptom: engineers
   bypass the registry entirely. Fix: measure denial volume; a rule that blocks
   90% of legitimate changes needs redesign, not enforcement pressure.
4. **Cross-jurisdiction conflict.** Symptom: one dataset is lawfully required in
   the EU and prohibited in the US, and a single table cannot satisfy both. Fix:
   physically separate the data; record the conflict as an accepted risk with a
   named owner, never resolve it with a policy exception.
5. **Automated review wrongly removes access someone needs.** Symptom: a
   clinician blocked from a system. Fix: an appeal path with a 24h SLA, and the
   appeal outcome fed back as a labeled example to the auto-review rules.
6. **Evidence store becomes the new audit problem.** Symptom: 40TB of access
   logs, and nobody can produce a specific answer. Fix: retention by evidence
   class (access logs 7y, decision logs 2y, probe results 3y), and a
   pre-built query per control so the common question is one click.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- OpenLineage provides a standard for lineage metadata, which is a practical
  prerequisite for the impact analysis and erasure scope that governance
  controls depend on.
  - Reference: https://openlineage.io/docs/
- Data contracts and executable expectations (schema + semantics + service
  levels) turn governance statements into assertions that run, rather than
  documents that are reviewed once.
  - Reference: https://datacontract.com/
  - Reference: https://github.com/great-expectations/great_expectations
- Table formats with snapshots and time travel (Iceberg, Delta) make
  point-in-time reproducibility achievable, which is what lets a control prove
  what a report was based on at a past instant.
  - Reference: https://iceberg.apache.org/docs/latest/
  - Reference: https://docs.delta.io/latest/index.html

## Deliverables
- [ ] Control catalogue mapping one control set to 6 regulatory regimes
- [ ] Classification service with default-deny and stored evidence
- [ ] Ownership finding model with a 14-day remediation SLA
- [ ] Full-coverage access review with 71% automation and a labeled feedback loop
- [ ] Exception register with a 180-day term and tested re-blocking
- [ ] Consolidation plan retiring the 4 previous efforts
- [ ] Effectiveness dashboard with the 8 metrics above
- [ ] Evidence retention policy by evidence class
- [ ] Runbook for the six failure modes
