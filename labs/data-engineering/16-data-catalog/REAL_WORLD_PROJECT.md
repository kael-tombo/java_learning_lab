# Data Catalogs — REAL WORLD PROJECT

## Context

A data-driven insurer has 6,200 tables across a warehouse, a lakehouse, Kafka,
and four SaaS tools. Analysts find what they need by asking colleagues in Slack,
which means discovery is bottlenecked on ~8 senior people, onboarding takes
months, and two duplicate "customer master" tables have silently diverged. A
first catalog attempt was deployed in 2023 and abandoned after 4 months because
descriptions had to be typed by hand and nobody could find anything. You own
the second attempt, with adoption as the success metric rather than coverage.

## Scale & Constraints

| Dimension | Value |
|---|---|
| Assets | 6,200 tables, 41 topics, 340 dashboards, 1,900 saved queries |
| Sources | Snowflake, Databricks, Kafka, Power BI, S3 |
| People | 2,400 internal, 340 analysts, 90 contractors |
| Prior attempt | abandoned; reason: no search quality, manual description burden |
| Constraint | zero additional headcount; must integrate with what exists |
| Success metric | median time-to-first-answer, and weekly active analysts |
| Compliance | descriptions and owners required for PCI/PHI tables |

## Architecture (target)

```
  Snowflake      --information_schema + ACCESS_HISTORY--> \
  Databricks     --Unity catalog API + query history  --->  [ingestion]
  Kafka          --topic + consumer-group metadata   --->      |
  Power BI       --semantic model + usage            --->  [normalizer]
  S3             --Iceberg/Delta metadata + manifests -->     |
                                                               v
                                                      +------------------+
                                                      | metadata store   |
                                                      | (Postgres)       |
                                                      +------------------+
                                                            |        |
                                          glossary + embeddings    lineage
                                          + synonyms               (column-level)
                                                            |        |
                                                            v        v
                                                      [search index] [graph]
                                                            |        |
                                          +-----------------+--------+
                                          |  portal / API / IDE plugin
                                          v
                                        analysts
```

## Key Implementation — the four design decisions that determine adoption

**Decision 1: description burden moves from humans to evidence.** The previous
catalog died because 2,400 descriptions had to be written. Descriptions are now
*drafted automatically* from column statistics, sample values, PII detection,
upstream lineage, and existing query text — a human reviews rather than writes.

```java
/**
 * A generated description is a draft, always labelled as one, and never
 * published without steward review. The generated text is deliberately
 * mechanical: grain, row count, freshness, PII, and the top columns by usage.
 * Inventing prose nobody wrote is how a catalog becomes untrustworthy.
 */
public final class DescriptionDrafter {
    public Draft draft(DatasetFacts f) {
        StringBuilder sb = new StringBuilder();
        sb.append("Grain: ").append(f.inferredGrain() == null
                ? "UNKNOWN - a steward must state this" : f.inferredGrain()).append(". ");
        sb.append("Rows: ").append(format(f.rowCountEstimate()))
          .append(" (estimated ").append(f.estimatedAt()).append("). ");
        sb.append("Freshness: ").append(f.lastRefresh() == null ? "UNKNOWN"
                : "last refreshed " + f.lastRefresh()).append(". ");
        if (f.hasPii()) sb.append("Contains PII: YES (")
                .append(f.piiColumns().size()).append(" fields). ");
        sb.append("Upstream: ").append(f.upstream().isEmpty() ? "source system"
                : String.join(", ", f.upstream().stream().limit(3).toList())).append(". ");
        sb.append("Most used columns: ").append(
                String.join(", ", f.topColumnsByUsage(5))).append(".");
        return new Draft(sb.toString(), GeneratedBy.AUTOMATIC, Confidence.MEDIUM,
                List.of("grain inferred from primary key; confirm"));
    }
}
```

**Decision 2: search must answer business questions.** Analysts do not know
table names. Search combines a keyword index, a glossary with synonyms, and
embeddings over descriptions, with a re-ranking step that prefers high-trust
assets.

```java
public record QueryIntent(String raw, Set<String> entities, String metric,
                          TimeGranularity time, String qualifier) {
    /**
     * Query understanding, lightly. Analysts type things like
     * "monthly churn by region last quarter" - three intents in one string.
     * Splitting them deterministically beats an LLM for search recall,
     * because it is inspectable and cannot hallucinate an entity.
     */
    public static QueryIntent parse(String q) {
        String s = q.toLowerCase(Locale.ROOT);
        TimeGranularity t = s.contains("by month") || s.contains("monthly") ? MONTH
                : s.contains("by week") ? WEEK : s.contains("daily") ? DAY : NONE;
        return new QueryIntent(q, Entities.extract(s), Metrics.extract(s), t, null);
    }
}

public final class SearchPipeline {
    public List<SearchHit> search(QueryIntent intent, SearchContext ctx) {
        List<Candidate> keyword = ctx.keywordIndex().search(intent.raw(), 200);
        List<Candidate> semantic = ctx.vectorIndex().search(
                ctx.embed(intent.raw()), 200);
        List<Candidate> glossary = ctx.glossaryIndex().search(intent.entities(), 100);

        List<Candidate> fused = reciprocalRankFusion.fuse(
                Map.of("keyword", keyword, "semantic", semantic, "glossary", glossary), k = 60);

        return rerank(fused, ctx).stream()
                .map(c -> toHit(c, ctx))
                .toList();
    }

    /** Trust and usage re-ranking: this is the difference between a search
     *  engine and a catalog people trust. */
    private List<Candidate> rerank(List<Candidate> fused, SearchContext ctx) {
        return fused.stream().sorted(Comparator.comparingDouble(c -> {
            DatasetRef d = ctx.dataset(c.datasetId());
            double trust = switch (d.state()) {
                case CERTIFIED -> 1.0; case REVIEW -> 0.8;
                case DRAFT, DEPRECATED -> 0.3; case RETIRED -> 0.0;
            };
            double usage = Math.log10(1 + ctx.usageCount30d(d.id()));
            double freshness = freshnessPenalty(d);      // demote if not refreshed in 30d
            return -c.baseScore() * (0.6 + 0.25 * trust + 0.1 * usage + 0.05 * freshness);
        })).toList();
    }
}
```

**Decision 3: lineage is column-level and automatic, from query logs.** Asking
people to declare lineage produced 22% coverage. Deriving it from actual
query text and join predicates produced 91% and found the two diverging customer
masters in week one.

```java
/**
 * Lineage inferred from observed query behavior, not declared intentions.
 * A column-level edge is created when queries consistently read
 * A.col and write B.col_transformed. Confidence rises with observation count.
 */
public final class ObservedLineageInferrer {
    public record Edge(String fromDataset, String fromColumn, String toDataset,
                       String toColumn, long observations, double confidence) {}

    public List<Edge> infer(QueryLog log, Duration window) {
        Map<EdgeKey, Counter> counts = new HashMap<>();
        for (Query q : log.successfulQueries(window)) {
            for (var pred : q.predicates()) {
                if (!pred.isColumnEquality()) continue;
                EdgeKey k = new EdgeKey(pred.leftDataset(), pred.leftColumn(),
                                        q.targetDataset(), targetColumnMatching(pred));
                counts.computeIfAbsent(k, x -> new Counter()).increment();
            }
        }
        long threshold = 20;    // below this it is a one-off query, not a dependency
        return counts.entrySet().stream()
                .filter(e -> e.getValue().count() >= threshold)
                .map(e -> new Edge(e.getKey().fromDataset(), e.getKey().fromColumn(),
                        e.getKey().toDataset(), e.getKey().toColumn(),
                        e.getValue().count(),
                        confidence(e.getValue().count())))
                .sorted(Comparator.comparing(Edge::observations).reversed())
                .toList();
    }
}
```

**Decision 4: deprecation is a workflow with dates and consumers.** Half the
value of a catalog is knowing what to stop using. Every deprecation carries a
successor, a notice period, and a consumer notification list, and consumers
are derived from query logs rather than asked for.

```java
public final class DeprecationService {
    public DeprecationPlan deprecate(String datasetId, String successor,
                                     Duration notice, String reason) {
        DatasetRef d = store.get(datasetId);
        if (d.state() == LifecycleState.RETIRED) {
            return DeprecationPlan.rejected("already retired");
        }
        // Consumers come from ACCESS_HISTORY, not from a maintainer list nobody updates.
        List<Consumer> consumers = queryLog.distinctConsumers(datasetId, days = 180);
        if (consumers.isEmpty()) {
            return DeprecationPlan.ok(retireNow(d, reason), Duration.ZERO);
        }
        Instant end = Instant.now().plus(notice);
        notifications.sendAll(consumers, DeprecationNotice(d, successor, end, reason));
        calendar.schedule(end, () -> retire(d, reason));
        calendar.schedule(end.minus(Duration.ofDays(30)), () -> remind(consumers, d, successor));
        return DeprecationPlan.ok(d.withState(DEPRECATED), end);
    }
}
```

## Adoption as the Success Metric

The previous attempt failed on adoption, so adoption is measured weekly and
published internally, including the numbers that indicate failure.

| Metric | Baseline (2023 attempt) | Target (6 months) | Current design lever |
|---|---|---|---|
| Weekly active analysts | 40 | 240 | IDE/BI plugin, not a separate website |
| Median time-to-first-answer | 6 days (asking a person) | < 10 min | search quality + previews |
| Searches returning a useful result (click-through) | n/a | > 60% | trust + usage re-ranking |
| Descriptions reviewed by stewards | 0 | 3,000/quarter | auto-drafts, review not writing |
| Lineage coverage (column-level) | 0% | > 85% | inferred from query logs |
| Zero-consumer tables retired | 0 | 900 | lifecycle automation |
| Questions to senior staff in `#data-help` | 40/week | < 8/week | the actual goal |

## Failure Modes and the Runbook

1. **Nobody uses the catalog.** Symptom: weekly active analysts < 15% of the
   analyst population. Fix: put the search inside the tools people already use
   (BI tool, SQL IDE, notebook) rather than on a website; a catalog is a
   destination people must visit, and they will not.
2. **Stale descriptions.** Symptom: search results describe an old schema.
   Fix: auto-regenerate on schema change, mark the description stale after 90
   days, and demote stale entries in ranking until reviewed.
3. **Lineage is too noisy.** Symptom: 90,000 edges, half spurious. Fix: the
   observation threshold, plus a UI that shows confidence and lets a steward
   delete a wrong edge; deleted edges feed a suppression list.
4. **Two divergent "customer master" tables both certified.** Symptom: analysts
   pick either. Fix: a duplicate detector on schema+semantic similarity that
   blocks certification of a near-duplicate and forces a reconciliation or an
   explicit "different purpose" declaration.
5. **Deprecation notice ignored.** Symptom: a deprecated table is still the top
   search result for its topic. Fix: deprecated assets are demoted in ranking
   but never hidden (people still need to find them), and the successor is
   highlighted in the result.
6. **Catalog becomes a second source of truth that disagrees with the engines.**
   Symptom: the catalog says a table has 4 columns, the engine says 5. Fix: the
   engines are authoritative for technical metadata; the catalog owns only
   business metadata, and a reconciliation job flags disagreement.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- OpenLineage is an open standard for capturing lineage metadata across the data
  ecosystem, which is the practical foundation for a catalog that can answer
  impact and provenance questions.
  - Reference: https://openlineage.io/
  - Reference: https://openlineage.io/docs/
- Data contracts formalize producer/consumer agreements, and a catalog is where
  a contract becomes discoverable rather than a document people must be given.
  - Reference: https://datacontract.com/
- Apache Iceberg and Delta Lake both expose table metadata (schemas, partitions,
  snapshots) that a catalog can ingest automatically instead of requiring
  hand-written descriptions.
  - Reference: https://iceberg.apache.org/docs/latest/
  - Reference: https://docs.delta.io/latest/index.html

## Deliverables
- [ ] Five-source ingestion with the engines authoritative for technical metadata
- [ ] Auto-drafted descriptions with explicit confidence and a steward review queue
- [ ] Three-way search fusion with trust and usage re-ranking, plus click-through tracking
- [ ] Column-level lineage inferred from query logs, with a confidence score
- [ ] Deprecation workflow with successor, notice period, and log-derived consumers
- [ ] Duplicate detector blocking certification of near-duplicates
- [ ] Weekly adoption dashboard against the seven metrics above
- [ ] Runbook for the six failure modes
