# Data Catalogs — MINI PROJECT

## Project: Searchable Catalog with Lineage and Trust Signals

A catalog service: automatic metadata ingestion, glossary-aware search,
column-level lineage, and a certification/deprecation lifecycle.

### Scope
- `CatalogStore`: entities (dataset, field, glossary term, owner).
- Ingestion: connectors reading metadata from 3 sources (files, a SQL catalog,
  a table-format catalog), normalized into one model.
- Search: tokenized index with synonym expansion, ranked by usage + trust.
- Lineage: dataset-level and field-level edges with a propagation walk.
- Lifecycle: `DRAFT -> REVIEW -> CERTIFIED -> DEPRECATED -> RETIRED`, with review
  expiry and a consumer notification list.
- API: `/search?q=`, `/datasets/{id}`, `/lineage/{id}`, `/impact/{id}`.

### Architecture

```
  warehouse catalog --+--> [normalizer] --> [CatalogStore] --> search index
  file layout --------+                        |                |
  table format (log) -+                        |                +--> /search?q=
                                             lineage graph       /datasets/{id}
                                             glossary
                                             trust signals (freshness, cert, users)
```

### Implementation — the model

```java
public record DatasetRef(String id, String name, String qualifiedName,
                         String owner, String steward, String description,
                         DatasetKind kind, String location, int rowCountEstimate,
                         long bytes, Instant createdAt, Instant lastModified,
                         LifecycleState state, Instant reviewDue,
                         Set<String> tags, List<String> consumers) {
    public enum Kind { TABLE, VIEW, TOPIC, FILE_SET, STREAM, MODEL_FEATURE }
}

public enum LifecycleState {
    DRAFT,        // created, nobody has looked at it
    REVIEW,       // description submitted, awaiting a steward
    CERTIFIED,    // description + owner + quality checks passed; safe to advertise
    DEPRECATED,   // still readable, not for new use, has a successor + end date
    RETIRED       // metadata retained for history, physically gone
}

public record FieldRef(String id, String datasetId, String name, String dataType,
                       boolean nullable, boolean primaryKey, String description,
                       String piiClass, Set<String> sensitiveTags) {
    public boolean sensitive() { return piiClass != null || !sensitiveTags.isEmpty(); }
}
```

### Automatic ingestion

```java
public interface MetadataConnector {
    String name();
    Stream<DatasetRef> datasets();
    default Stream<FieldRef> fields(String datasetId) { return Stream.empty(); }
    default Stream<LineageEdge> lineage() { return Stream.empty(); }
}

public final class SqlCatalogConnector implements MetadataConnector {
    public String name() { return "sql-catalog"; }

    @Override public Stream<DatasetRef> datasets() {
        return jdbc.query("""
                SELECT table_catalog, table_schema, table_name, table_type,
                       table_rows, (data_length + index_length) * 1024 AS bytes
                  FROM information_schema.tables
                 WHERE table_schema NOT IN ('pg_catalog','information_schema')
                """, (rs, i) -> new DatasetRef(
                rs.getString("table_catalog") + "." + rs.getString("table_schema")
                        + "." + rs.getString("table_name"),
                rs.getString("table_name"),
                rs.getString("table_schema"),
                null,                                    // owner filled by the stewardship service
                null,
                null,                                    // description: enriched later from the glossary
                rs.getString("table_type").contains("VIEW")
                        ? DatasetRef.Kind.VIEW : DatasetRef.Kind.TABLE,
                null, rs.getLong("table_rows"), rs.getLong("bytes"),
                null, null, LifecycleState.DRAFT, null, Set.of(), List.of()));
    }
}
```

### Search: business terms, not identifiers

```java
public record SearchHit(DatasetRef dataset, double score, List<String> matchedTerms) {}

public final class CatalogSearch {
    private static final Map<String, Set<String>> SYNONYMS = Map.of(
            "revenue",  Set.of("sales", "gmv", "turnover", "income"),
            "customer", Set.of("client", "user", "account", "buyer"),
            "churn",    Set.of("attrition", "lapsed", "cancelled"),
            "basket",   Set.of("order", "cart", "transaction"));

    private static Set<String> expand(String q) {
        String lower = q.toLowerCase(Locale.ROOT);
        Set<String> out = new LinkedHashSet<>();
        out.add(lower);
        SYNONYMS.forEach((k, v) -> {
            if (lower.contains(k)) out.addAll(v);
            v.forEach(s -> { if (lower.contains(s)) out.add(k); });
        });
        return out;
    }

    public List<SearchHit> search(String query, SearchContext ctx) {
        Set<String> terms = expand(query);
        return ctx.datasets().stream()
                .map(d -> score(d, terms, ctx))
                .filter(h -> h.score() > 0)
                .sorted(Comparator.comparingDouble(SearchHit::score).reversed())
                .toList();
    }

    private SearchHit score(DatasetRef d, Set<String> terms, SearchContext ctx) {
        double s = 0;
        List<String> matched = new ArrayList<>();
        String haystack = (d.name() + " " + d.description() + " " + String.join(" ", d.tags())
                           + " " + glossary.termsFor(d.id())).toLowerCase(Locale.ROOT);
        for (String t : terms) {
            if (d.name().toLowerCase(Locale.ROOT).equals(t)) { s += 10; matched.add(t); }
            else if (d.name().toLowerCase(Locale.ROOT).contains(t)) { s += 5; matched.add(t); }
            else if (haystack.contains(t)) { s += 2; matched.add(t); }
        }
        // Ranking must favour things a human would use: certified and popular
        // datasets float, abandoned drafts sink. Otherwise search returns the
        // alphabetically first stale table and people stop using it.
        s *= switch (d.state()) {
            case CERTIFIED -> 1.5; case REVIEW -> 1.1;
            case DRAFT, DEPRECATED, RETIRED -> 0.5;
        };
        s *= 1 + Math.log10(1 + ctx.usageCount(d.id()));
        if (Instant.now().isAfter(d.reviewDue())) s *= 0.4;   // stale description: demote
        return new SearchHit(d, s, matched);
    }
}
```

### Column-level lineage

```java
public record LineageEdge(String fromDataset, String fromField,
                          String toDataset, String toField, Derivation derivation) {}

public enum Derivation { DIRECT, RENAME, EXPRESSION, AGGREGATE, JOIN, FILTER }

public final class LineageGraph {
    private final Map<String, Set<LineageEdge>> fieldEdges = new HashMap<>();
    private final Map<String, DatasetRef> datasets = new HashMap<>();

    public void add(LineageEdge e) {
        validate(e);          // every dataset must be registered; orphans are a bug
        fieldEdges.computeIfAbsent(key(e.fromDataset(), e.fromField()), k -> new LinkedHashSet<>())
                  .add(e);
    }

    /** Where did this field's value come from? Walks until it hits raw sources. */
    public Set<FieldOrigin> traceOrigin(String dataset, String field) {
        Set<FieldOrigin> out = new LinkedHashSet<>();
        Deque<FieldOrigin> queue = new ArrayDeque<>(List.of(new FieldOrigin(dataset, field)));
        Set<FieldOrigin> seen = new HashSet<>();
        while (!queue.isEmpty()) {
            FieldOrigin cur = queue.poll();
            if (!seen.add(cur)) continue;
            if (isRawSource(cur)) { out.add(cur); continue; }
            fieldEdges.getOrDefault(key(cur.dataset(), cur.field()), Set.of()).stream()
                    .map(e -> new FieldOrigin(e.fromDataset(), e.fromField()))
                    .forEach(queue::add);
        }
        return out;
    }

    /** Which fields are affected if this source field is wrong or removed? */
    public Set<FieldOrigin> impactOf(String dataset, String field) {
        Set<FieldOrigin> seen = new LinkedHashSet<>();
        Deque<FieldOrigin> queue = new ArrayDeque<>(List.of(new FieldOrigin(dataset, field)));
        while (!queue.isEmpty()) {
            FieldOrigin cur = queue.poll();
            if (!seen.add(cur)) continue;
            fieldEdges.values().stream()
                    .filter(es -> es.stream().anyMatch(e ->
                            e.fromDataset().equals(cur.dataset()) && e.fromField().equals(cur.field())))
                    .flatMap(es -> es.stream())
                    .map(e -> new FieldOrigin(e.toDataset(), e.toField()))
                    .forEach(queue::add);
        }
        seen.remove(new FieldOrigin(dataset, field));
        return seen;
    }
}
```

### Lifecycle with a review clock

```java
public final class LifecycleManager {
    public TransitionResult submit(DatasetRef d, String steward, String description) {
        if (description.length() < 40) {
            return TransitionResult.rejected("description must explain the grain, "
                    + "the owner, and one example query; 40 characters minimum");
        }
        return TransitionResult.ok(d.withState(LifecycleState.REVIEW).withSteward(steward));
    }

    public TransitionResult certify(DatasetRef d, QualityReport report) {
        if (d.state() != LifecycleState.REVIEW) {
            return TransitionResult.rejected("only a table in REVIEW can be certified");
        }
        if (report.failingBlockChecks() > 0) {
            return TransitionResult.rejected("cannot certify: "
                    + report.failingBlockChecks() + " blocking quality check(s) failing");
        }
        return TransitionResult.ok(d.withState(LifecycleState.CERTIFIED)
                                    .withReviewDue(Instant.now().plus(Duration.ofDays(180))));
    }

    /** Deprecation is a process, not a state change: successors, dates, and consumers. */
    public DeprecationPlan deprecate(DatasetRef d, String successor, Duration notice) {
        if (successor == null) return DeprecationPlan.rejected("a successor is required");
        Instant end = Instant.now().plus(notice);
        notify(d.consumers(), "Dataset " + d.name() + " is deprecated at " + end
                + "; use " + successor);
        return DeprecationPlan.ok(d.withState(LifecycleState.DEPRECATED)
                                   .withTags(union(d.tags(), Set.of("deprecated:" + successor))),
                end);
    }

    public List<DatasetRef> overdueForReview(Instant now) {
        return store.all().stream()
                .filter(d -> d.state() == LifecycleState.CERTIFIED)
                .filter(d -> d.reviewDue() != null && now.isAfter(d.reviewDue()))
                .toList();
    }
}
```

### API sketch

```java
@GET   /search?q={query}&kind={kind}&state={state}
@GET   /datasets/{id}                        // + owners, consumers, quality, lineage count
@GET   /lineage/{id}?direction=upstream|downstream&columnLevel=true
@GET   /impact/{id}                          // blast radius for a change or deletion
@POST  /datasets/{id}/submit                 // -> REVIEW
@POST  /datasets/{id}/certify                // -> CERTIFIED (requires quality report)
@POST  /datasets/{id}/deprecate?successor=X&noticeDays=90
@GET   /reviews/overdue
```

### Stretch
- Add usage-based auto-tagging: tables with 0 consumers for 180 days get flagged for retirement.
- Add a "similar tables" recommendation using column-set overlap.
- Add an OpenLineage-compatible emit endpoint so the catalog federates.

## Deliverables
- [ ] Unified model for datasets, fields, glossary terms, lineage
- [ ] Three metadata connectors with automatic ingestion
- [ ] Synonym-aware ranked search with trust and usage weighting
- [ ] Column-level lineage with origin tracing and impact analysis
- [ ] Lifecycle state machine with a review clock and consumer notifications
- [ ] REST API for search, detail, lineage, impact, and lifecycle actions
- [ ] Adoption metrics: searches per week, time-to-first-answer, zero-consumer tables
