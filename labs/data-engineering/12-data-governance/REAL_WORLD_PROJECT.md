# Data Governance (Foundations) — REAL WORLD PROJECT

## Context

A multi-national insurer (EU + US, 14 subsidiaries) has completed a
lakehouse migration and now faces a regulatory reality: GDPR erasure requests
take 6 weeks to fulfil because nobody can find every copy of a person's data,
HIPAA requires access logging on 40 PHI tables, and the internal audit found
11 datasets containing card data with no documented control. You own the
governance program, and its first deliverable is evidence, not policy.

## Scale & Constraints

| Dimension | Value |
|---|---|
| Datasets | 3,900 in the lakehouse, 640 in the BI semantic layer |
| Copies of subject data | bronze, silver, gold, 3 BI caches, 2 search indexes, 1 vector store, 6 backups, 2 data exports |
| Regulatory | GDPR (EU), CCPA (US-CA), HIPAA, PCI DSS, SOX, plus 14 local residency rules |
| Erasure SLA | 30 days statutory; internal target 10 days |
| Access | 2,400 internal users, 340 analysts, 90 contractors |
| Constraints | residency forbids moving EU subject data outside the EU region |
| Evidence | annual audit + quarterly internal review + ad-hoc regulator requests |

## Architecture (target)

```
              +-- classification service (auto-tagging on ingest)
              |     PII / PHI / PCI / residency tags, with evidence
              v
        dataset registry (owner, steward, class, retention, location, lineage)
              |
    +---------+---------+-----------+------------+
    |         |         |           |            |
 access    retention  residency   lineage     purpose
 policy    policy     policy      graph       limitation
    |         |         |           |            |
    +---------+---------+-----------+------------+
              |
     policy engine (evaluated on every change, in CI, and nightly)
              |
     evidence store: every decision, exception, and access event, append-only
```

## Key Implementation — the three gaps the audit found

**Gap 1: PII was discovered by an auditor, not by a system.** Classification
now happens on ingest with evidence, and untagged data is treated as
restricted by default.

```java
/**
 * Default-deny is the only stance that survives contact with reality:
 * an unclassified column is treated as the highest sensitivity present in
 * the same row, not as public.
 */
public enum DefaultSensitivity { PUBLIC, INTERNAL, RESTRICTED }

public final class IngestClassifier {
    public Classification classifyColumn(ColumnMeta c, List<Object> sample) {
        Classification explicit = c.tag();
        if (explicit != null) return explicit;
        Classification inferred = heuristics(c, sample);
        return inferred == null ? DefaultSensitivity.RESTRICTED : inferred;
    }

    /** Also emits the evidence, because an auditor asks "how do you know?". */
    public ClassificationEvidence record(String table, ColumnMeta c,
                                         Classification result, String basis) {
        return new ClassificationEvidence(table, c.name(), result, basis,
                Instant.now(), engineVersion());
    }
}
```

**Gap 2: nobody could find the copies.** The lineage graph was partial because
it was only declared for tables someone remembered. Now it is emitted by the
platform, and coverage itself is a policy.

```java
public record LineageCoverage(String table, int declaredEdges, boolean isSource,
                              boolean isSink, Set<String> capturedBy) {
    /** A policy, not a nice-to-have: an un-instrumented table cannot be erased safely. */
    boolean covered() { return isSource() || isSink() || capturedBy.containsAll(upstreamOf()); }
}

public static final class InstrumentedCopy implements Policy {
    public String id() { return "GOV-011"; }
    public void evaluate(List<Dataset> all, List<String> violations) {
        all.stream()
           .filter(d -> d.classification().rank() >= PII.rank())
           .filter(d -> !lineage.capturesAllCopiesOf(d.id()))
           .forEach(d -> violations.add(id() + ": " + d.id()
                   + " is classified " + d.classification()
                   + " but " + lineage.uninstrumentedCopies(d.id()).size()
                   + " copy/copies are not instrumented for erasure"));
    }
}
```

**Gap 3: erasure was a project, not a service.** The fix is a single orchestrated
flow that is idempotent, verifiable, and produces a receipt.

```java
public final class ErasureOrchestrator {
    public Receipt fulfil(ErasureRequest req) {
        Receipt r = inventory.begin(req);                 // idempotent by request id
        for (String copy : inventory.allCopiesOf(req.subject())) {
            r = r.withStep(copy, () -> physicalDelete(copy, req.subject()));
            r = r.withStep(copy + ":cache", () -> cache.purge(req.subject()));
            r = r.withStep(copy + ":search", () -> search.delete(req.subject()));
            r = r.withStep(copy + ":vector", () -> vectorStore.delete(req.subject()));
            r = r.withStep(copy + ":export", () -> exportRegistry.revoke(req.subject()));
        }
        r = r.withStep("backups", () -> backupPurge.schedule(req.subject(), req.deadline()));
        r = r.withStep("residency", () -> residency.assertNoCrossRegionCopies(req.subject()));
        r = r.withStep("verify", () -> verification.run(req.subject(), r.steps()));

        // A receipt with a failed step is not a receipt. Partial erasure is a
        // breach with extra steps, so this must fail loudly.
        if (!r.allStepsSucceeded()) {
            alerts.pageLegal("Erasure " + req.id() + " incomplete: " + r.failedSteps());
            throw new ErasureIncomplete(r);
        }
        return r;
    }
}
```

The verification step is the part auditors ask about: a generated query per
copy, executed, with the row count recorded as zero. Not "we ran the delete."

## Operating Model (a program, not a document)

| Cadence | Activity | Output |
|---|---|---|
| On every change | Policy evaluation in CI | PR blocked or exception recorded |
| Nightly | Full registry policy sweep | Digest to owners, 14-day SLA for violations |
| Weekly | Access review for PHI/PCI | Signed review per dataset |
| Quarterly | Erasure sampling test (3 random subjects) | Proof the erasure flow works |
| Annually | Internal audit pack | Lineage coverage, exceptions, access logs, erasure SLA |

**Exceptions are the real governance artifact.** A policy with no exceptions is
a policy nobody believes; recording who approved what, and when it expires, is
what makes the system auditable.

```java
public record PolicyException(String policyId, String datasetId, String justification,
                              String approvedBy, Instant approvedAt, Instant expiresAt) {
    public boolean active(Instant now) { return now.isBefore(expiresAt); }
    public boolean overdue(Instant now) { return now.isAfter(expiresAt); }
}
```

## Failure Modes and the Runbook

1. **Erasure misses a copy.** Symptom: regulator request finds residual data.
   Fix: the inventory must enumerate copies from the lineage graph, and the
   uninstrumented-copy policy (GOV-011) blocks promoting such a table.
2. **Residency violation.** Symptom: EU subject data lands in a US region via a
   cross-region copy or a vendor export. Fix: residency asserted per copy in
   the erasure flow and continuously in the pipeline, not at export time.
3. **Classification drift.** Symptom: a new column in a PII table is untagged and
   treated as public. Fix: default-deny + quarterly auto-classification sweep
   comparing the inferred label to the declared one.
4. **Owner churn.** Symptom: datasets owned by departed employees, unreachable
   for decisions. Fix: the inactive-owner policy (GOV-003) fails the nightly
   sweep; ownership must be reassigned within 14 days.
5. **Over-permissioned access to PHI.** Symptom: an analyst bulk-exports PHI.
   Fix: column masking, purpose limitation on grants, quarterly access review,
   and export logging with alerting on volume.
6. **Backup purge misses the deadline.** Symptom: erasure SLA breached on backup
   media. Fix: purge scheduled at request time with a deadline far shorter than
   the statutory clock, and a daily check that every scheduled purge ran.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- OpenLineage is an open standard for capturing lineage metadata across data
  tools, which is the practical foundation for impact analysis, governance, and
  knowing where a subject's data lives.
  - Reference: https://openlineage.io/
  - Reference: https://openlineage.io/docs/
- Apache Iceberg and Delta Lake provide snapshot isolation, schema evolution, and
  time travel, which are also what make a table auditable: the exact state of a
  table at any past instant is retrievable.
  - Reference: https://iceberg.apache.org/docs/latest/
  - Reference: https://docs.delta.io/latest/index.html

## Deliverables
- [ ] Registry with auto-classification, default-deny, and stored evidence
- [ ] Lineage coverage policy (GOV-011) and a coverage report
- [ ] Erasure orchestrator across 14 copy types with verification queries
- [ ] Policy set including retention ceiling, inactive owner, residency, access
- [ ] Exception register with approver and expiry
- [ ] Operating calendar (nightly/weekly/quarterly/annual) with owners
- [ ] Runbook for the six failure modes
- [ ] Audit pack template an auditor can follow without follow-up questions
