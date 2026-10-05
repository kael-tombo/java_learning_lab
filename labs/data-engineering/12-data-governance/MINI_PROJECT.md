# Data Governance (Foundations) — MINI PROJECT

## Project: Governance Kernel — Registry, Lineage, Policy, Deletion

A working governance layer: a dataset registry with ownership and
classification, a lineage graph, a policy-as-code evaluator, and a deletion
flow that produces evidence.

### Scope
- Registry: `Dataset(id, owner, steward, classification, retention, tags, location)`.
- Classification: PII/PHI/PCI detectors driven by column name, type, and sample values.
- Lineage: DAG built from declared edges, with impact and root-cause queries.
- Policy: rules (e.g. "PII dataset must have a steward", "raw retention <= 400d")
  evaluated in code, failing with an actionable message.
- Deletion: subject-based erasure across all datasets with an evidence receipt.

### Architecture

```
   sources -> staging -> curated -> marts -> dashboards
        |         |          |         |          |
        +---------+----------+---------+----------+
                          |
                 [Registry: id, owner, class, retention, location]
                          |
                 [Lineage DAG: nodes=datasets, edges=transformations]
                          |
                 [Policy engine: rule set evaluated per dataset]
                          |
                 [Erasure service: find all nodes containing a subject,
                  rewrite, purge, emit immutable evidence]
```

### Implementation

```java
public enum Classification {
    PUBLIC,        // no restriction
    INTERNAL,      // company data, no external sharing
    CONFIDENTIAL,  // commercially sensitive
    PII,           // directly or indirectly identifying a person
    PHI,           // health information (HIPAA)
    PCI            // cardholder data (PCI DSS)
}

public record Dataset(String id, String owner, String steward,
                      Classification classification, Duration retention,
                      Set<String> columns, String location, boolean containsRawPii) {
    public Dataset {
        Objects.requireNonNull(owner, "every dataset needs an owner: " + id);
        if (retention.isNegative() || retention.isZero()) {
            throw new IllegalArgumentException("retention must be positive: " + id);
        }
    }
}
```

### Automatic classification from evidence

```java
public final class Classifier {
    /** Name heuristics alone miss plenty; combine name, type, and value shape. */
    private static final Map<Pattern, Classification> BY_NAME = Map.of(
            Pattern.compile(".*(ssn|social.?security|national.?id).*", CASE_INSENSITIVE), PII),
            Pattern.compile(".*(email|e_mail|phone|mobile|address|postcode|zip).*", CASE_INSENSITIVE), PII),
            Pattern.compile(".*(dob|date.?of.?birth).*", CASE_INSENSITIVE), PII),
            Pattern.compile(".*(diagnosis|icd|patient|hospital|blood|prescription).*", CASE_INSENSITIVE), PHI),
            Pattern.compile(".*(card_?(pan|number)|cvv|cvc|track).*", CASE_INSENSITIVE), PCI));

    public Classification classify(Column c, List<Object> sampleValues) {
        Classification byName = BY_NAME.entrySet().stream()
                .filter(e -> e.getKey().matcher(c.name()).matches())
                .map(Map.Entry::getValue)
                .findFirst().orElse(Classification.INTERNAL);

        Classification byValue = looksLikePiiByValue(c, sampleValues);
        return higher(byName, byValue);
    }

    /** Free-text columns holding an SSN pattern are PII even if the name is `notes`. */
    private Classification looksLikePiiByValue(Column c, List<Object> values) {
        if (c.type() != ColumnType.STRING) return Classification.INTERNAL;
        return values.stream().filter(Objects::nonNull).map(String::valueOf)
                .anyMatch(v -> SSN.matcher(v).matches() || EMAIL.matcher(v).matches())
                ? Classification.PII : Classification.INTERNAL;
    }

    static Classification higher(Classification a, Classification b) {
        return rank(a) >= rank(b) ? a : b;
    }
    private static int rank(Classification c) {
        return switch (c) {
            case PUBLIC -> 0; case INTERNAL -> 1; case CONFIDENTIAL -> 2;
            case PII -> 3; case PHI -> 4; case PCI -> 5;
        };
    }
}
```

### Lineage graph

```java
public final class LineageGraph {
    private final Map<String, Set<String>> downstream = new HashMap<>();  // dataset -> derived
    private final Map<String, Set<String>> upstream = new HashMap<>();

    public void addEdge(String from, String to) {
        downstream.computeIfAbsent(from, k -> new LinkedHashSet<>()).add(to);
        upstream.computeIfAbsent(to, k -> new LinkedHashSet<>()).add(from);
    }

    /** Blast radius: if `dataset` is wrong or deleted, what is affected? */
    public Set<String> impact(String dataset) {
        Set<String> out = new LinkedHashSet<>();
        Deque<String> queue = new ArrayDeque<>(List.of(dataset));
        while (!queue.isEmpty()) {
            for (String next : downstream.getOrDefault(queue.poll(), Set.of())) {
                if (out.add(next)) queue.add(next);
            }
        }
        return out;
    }

    /** Root cause: given a wrong dashboard number, which upstream tables are suspects? */
    public Set<String> rootCauses(String dataset) {
        Set<String> out = new LinkedHashSet<>();
        Deque<String> queue = new ArrayDeque<>(upstream.getOrDefault(dataset, Set.of()));
        while (!queue.isEmpty()) {
            for (String prev : upstream.getOrDefault(queue.poll(), Set.of())) {
                if (out.add(prev)) queue.add(prev);
            }
        }
        return out;
    }
}
```

### Policy as code

```java
public sealed interface Policy {
    String id();
    Severity severity();
    void evaluate(List<Dataset> all, List<String> violations);

    record PiiNeedsSteward(Severity sev) implements Policy {
        public String id() { return "GOV-001"; }
        public void evaluate(List<Dataset> all, List<String> v) {
            all.stream()
               .filter(d -> d.classification() == PII || d.classification() == PHI)
               .filter(d -> d.steward() == null || d.steward().isBlank())
               .forEach(d -> v.add(id() + ": PII dataset " + d.id() + " has no steward"));
        }
    }

    record RetentionCeiling(Duration max, Severity sev) implements Policy {
        public String id() { return "GOV-002"; }
        public void evaluate(List<Dataset> all, List<String> v) {
            all.stream()
               .filter(d -> d.classification() == PII)
               .filter(d -> d.retention().compareTo(max) > 0)
               .forEach(d -> v.add(id() + ": PII dataset " + d.id() + " retains "
                       + d.retention().toDays() + "d, ceiling is " + max.toDays() + "d"));
        }
    }

    record OwnerIsActive(String directory, Severity sev) implements Policy {
        public String id() { return "GOV-003"; }
        public void evaluate(List<Dataset> all, List<String> v) {
            all.stream()
               .filter(d -> !directory.isActive(d.owner()))
               .forEach(d -> v.add(id() + ": dataset " + d.id()
                       + " is owned by inactive user " + d.owner() + "; reassign or archive"));
        }
    }
}
```

### Erasure with evidence

```java
public final class ErasureService {
    public record Receipt(String requestId, String subject, Instant receivedAt,
                          List<String> datasetsTouched, List<String> backupsPurged,
                          String verificationQuery, int rowsRemoved) {}

    public Receipt erase(String subject, LegalRequest req, List<Dataset> registry) {
        List<Dataset> affected = registry.stream()
                .filter(d -> subjectLocator.find(d, subject).isPresent())
                .toList();

        List<String> touched = new ArrayList<>();
        int removed = 0;
        for (Dataset d : affected) {
            // Physical removal, not a flag: a deleted_at column still holds the data.
            removed += warehouse.rewriteExcluding(d.location(), subject);
            cache.purge(d.id(), subject);
            searchIndex.delete(d.id(), subject);
            vectorStore.delete(d.id(), subject);
            backups.schedulePurging(d.location(), subject, req.deadline());
            touched.add(d.id());
            audit.append("erasure", req.reference(), d.id(), removed);
        }

        String verification = """
                SELECT COUNT(*) FROM %s
                 WHERE LOWER(email) = LOWER('%s')   -- must return 0
                """.formatted(affected.get(0).location(), escape(subject));
        long remaining = warehouse.countMatching(verification);
        if (remaining != 0) {
            throw new ErasureVerificationFailed(
                    "deletion incomplete: " + remaining + " rows remain in "
                    + affected.get(0).location() + "; escalate to " + req.legalContact());
        }
        return new Receipt(UUID.randomUUID().toString(), subject, Instant.now(),
                touched, affected.stream().map(Dataset::id).toList(), verification, removed);
    }
}
```

### Stretch
- Add a scheduled policy evaluation that fails CI and posts a digest to the owners.
- Add a "no PII in logs" check over emitted application logs.
- Add a residency policy: PII data must remain in region X.

## Deliverables
- [ ] Dataset registry with enforced owner/retention invariants
- [ ] Classifier using name, type, and value evidence
- [ ] Lineage graph answering impact and root-cause queries
- [ ] Policy engine with 3+ rules and actionable messages
- [ ] Erasure service with a verification query and an evidence receipt
- [ ] Policy report generated on a schedule
