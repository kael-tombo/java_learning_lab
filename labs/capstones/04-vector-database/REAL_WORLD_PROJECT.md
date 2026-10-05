# Vector Database — REAL WORLD PROJECT

## Context

An enterprise knowledge platform serves semantic search over 41M internal
documents for 12,000 users. Recall on the current single-node HNSW index has
degraded from 0.97 to 0.88 over eight months as documents were updated and
deleted, and users have stopped trusting search — the "I know the answer is in
there" complaints turned into a support queue. Filters (department, document
type, region) are applied on every query and cause the recall cliff. You own
the index.

## Scale & Constraints

| Dimension | Value |
|---|---|
| Vectors | 41M, 1,024 dimensions, f32 (168GB raw) |
| Updates | 2.4M docs/month modified, 340k/month deleted |
| QPS | 1,100 peak, 140 mean; p99 budget 120ms |
| Filters | department, doc_type, region, classification — 2-5 per query |
| Recall SLO | >= 0.95 @ k=10, measured against a nightly ground-truth sample |
| Latency SLO | p99 120ms including embedding the query |
| Compliance | classification filter is a security control, not a UX filter |
| Constraint | no full reindex downtime; 8-node cluster already provisioned |

## Architecture (target)

```
 documents -> [embedding service] -> [partitioned vector store, 8 nodes]
                                       |
 query -> [embedding, 35ms] -> [filter resolver] -> [routing]
                                       |
                        +--------------+--------------+
                        |              |              |
                  partition-scoped   global HNSW   late-refresh
                   HNSW (3 replicas)   (fallback)   index (5 min)
                        |
                        +--> [rerank: cross-encoder, top 50 -> top 10]
                                     |
                              [response + citations]
```

## Key Implementation — the recall decline, diagnosed

The decline was not mysterious once measured; it was three causes that
compounded.

| Cause | Contribution to recall loss | Fix |
|---|---|---|
| Tombstones from 340k/month deletes, never compacted | -0.045 | compaction threshold at 15% tombstones, not 20% |
| Filters applied post-search with a fixed `efSearch=64` | -0.030 | filter-aware ef expansion + partition routing |
| Embedding model upgraded in month 3 without a full reindex, so the graph mixes two embedding spaces | -0.020 | per-version index with a routing layer; no mixed spaces |

The third is the one worth dwelling on: **a graph index over vectors from two
different embedding models is meaningless**, and nothing warns you. Distance
between vectors from different spaces is not a distance. The fix is one index
per embedding version, with a router, and a hard rule that they never mix.

```java
/**
 * A vector index may only contain vectors from one embedding space. Mixing
 * models (e.g. during a model upgrade) silently destroys recall and produces
 * no error, because the search still returns plausible-looking neighbours.
 * The invariant is enforced in the routing layer, not hoped for.
 */
public record EmbeddingSpace(String modelId, int dim, double meanNorm, double stdNorm) {
    public void assertCompatible(float[] v) {
        if (v.length != dim) {
            throw new DimensionMismatch(modelId + " expects " + dim + ", got " + v.length);
        }
    }
    public boolean sameSpace(EmbeddingSpace o) {
        return modelId.equals(o.modelId);
    }
}

public final class SpaceRouter {
    public VectorIndex route(EmbeddingSpace space) {
        if (activeSpace() != null && !activeSpace().sameSpace(space)) {
            throw new MixedSpaceException("refusing to search across embedding spaces: "
                    + activeSpace().modelId() + " vs " + space.modelId());
        }
        return indexFor(space);
    }
}
```

## Key Implementation — the four fixes, measured

**Fix 1: compaction at 15% tombstones, and nightly by default.** 340k deletes a
month against 41M vectors is 0.8%/month, so a 15% threshold fires roughly every
19 days. That is fine — compaction is cheap at 8 nodes and it removes a
recurring silent loss.

```java
public record CompactionPolicy(double tombstoneRatioThreshold,
                               int maxTombstonesPerNode, boolean nightly) {}

public final class CompactionScheduler {
    /**
     * Compaction builds a new index and swaps by reference, so there is no
     * downtime and no partial-visibility window. What it costs is build time
     * (measured at 41 min for 41M vectors across 8 nodes) and a transient
     * 2x memory spike, which is why the threshold is a ratio and not a
     * calendar.
     */
    public void maybeSchedule() {
        double ratio = tombstones() / (double) liveVectors();
        if (ratio > policy.tombstoneRatioThreshold() || policy.nightly() && isNightWindow()) {
            executor.submit(this::compact);
        }
    }
}
```

**Fix 2: filter-aware search, and the partition layout that makes it work.**
This is the biggest latency *and* recall win.

```java
/**
 * Partition by department. Then a filter on department routes to a subset of
 * partitions, and each partition is searched independently. The result: the
 * filter is applied *before* the graph search, so the recall cliff disappears
 * rather than being mitigated.
 *
 * The trade, stated: a query without a department filter must search all
 * partitions. That is why the partition key must be the filter that is
 * present on (nearly) every query, not the one that is easiest to partition.
 * In this workload department is present on 94% of queries; doc_type on 61%.
 */
public final class PartitionedVectorStore {
    public SearchResult search(float[] q, int k, QueryFilters filters, int ef) {
        Set<Integer> partitions = partitionResolver.resolve(filters);   // empty = all
        if (partitions.size() == 1) {
            return searchPartition(partitions.iterator().next(), q, k, ef);
        }
        // Multiple partitions: search each, merge. Over-fetch a little so the
        // global top-k is right, then trim.
        int perPartition = (int) Math.ceil(k * 1.5);
        PriorityQueue<Hit> merged = new PriorityQueue<>(
                Comparator.comparingDouble(Hit::distance).reversed());
        for (int p : partitions) {
            searchPartition(p, q, perPartition, ef).forEach(merged::add);
            if (merged.size() >= k * 2) break;                 // early exit
        }
        return new SearchResult(merged.stream().sorted(Comparator.comparingDouble(Hit::distance))
                .limit(k).toList(), partitions.size());
    }
}
```

**Fix 3: classification filter is a security control, so it is enforced
separately from search.** This distinction is the one that matters legally.

```java
/**
 * Two different things arrive as "filters" and must not be conflated:
 *
 *   RELEVANCE filters (department, doc_type): affect ranking quality only.
 *      Failing to apply them gives a worse result, not a breach.
 *
 *   SECURITY filters (classification, region, entitlement): affect who may
 *      see what. These are applied at the storage layer as a partition/row
 *      bound, and the result set is post-verified against the caller's
 *      entitlements before it leaves the service.
 *
 * Conflating them means a relevance-filter bug becomes a data breach.
 */
public record QueryFilters(Set<String> departments, Set<String> docTypes,
                           Set<Classification> maxClassifications,
                           Set<String> allowedRegions) {
    public boolean hasSecurityConstraints() {
        return !maxClassifications.isEmpty() || !allowedRegions.isEmpty();
    }
}

public SearchResult searchAndVerify(float[] q, int k, QueryFilters f, Principal caller) {
    SearchResult r = store.search(q, k, f, ef);
    if (!f.hasSecurityConstraints()) return r;
    // Defence in depth: the index already excludes these, so this should be a
    // no-op. It exists because a bug in partition routing is a breach.
    return r.filter(h -> entitlements.permits(caller, h.documentId()));
}
```

**Fix 4: recall measured, on a schedule, against ground truth.** A recall number
that is not recomputed is a guess.

```java
/**
 * Nightly ground truth: 2,000 sampled queries (real ones, from the query log)
 * brute-forced against the partitioned index. This is affordable because the
 * queries are sampled, not all of them, and it turns recall into an SLO with a
 * burn rate rather than a number in a slide.
 */
public record RecallSlo(double target, Double current, int sampleSize,
                        double driftFrom7d) {
    public boolean breached() { return current != null && current < target; }
    /** A slow decline is more alarming than a dip: a dip is an incident, a
     *  decline is a degradation that will become an incident. */
    public boolean degrading() { return driftFrom7d < -0.005; }
}
```

## Measured outcomes

| Metric | Before | After |
|---|---|---|
| Recall@10 (measured, 2k queries) | 0.88 | 0.968 |
| Recall@10 with a department filter | 0.79 | 0.962 |
| p99 latency, filtered query | 640ms | 88ms |
| p99 latency, unfiltered query | 210ms | 104ms |
| Tombstones present | 2.1M (5.1%) | 340k (0.8%) |
| Compaction frequency | never | nightly + on threshold |
| Embedding spaces in one index | 2 (mixed) | 1 per index, routed |
| Support tickets about missing results | 41/month | 3/month |

The filtered-query recall number (0.79 → 0.962) is the one that changed the
product. Users filter by department almost always, so they were experiencing
the cliff, not the headline number.

## Failure Modes and the Runbook

1. **Recall degrades between compactions.** Symptom: slow decline in the recall
   SLO. Fix: the nightly compactor plus the 15% threshold; the decline alarm is
   the early warning.
2. **A query filters to nothing.** Symptom: empty results for a valid query.
   Cause: a document's partition assignment does not match its department
   metadata (an update that changed one and not the other). Fix: a consistency
   job comparing partition keys to metadata, run hourly.
3. **A security filter is mis-routed.** Symptom: a user sees a document above
   their clearance. This is a breach, not an incident. Fix: the
   post-verification step exists precisely for this, and a synthetic probe runs
   hourly to prove it works.
4. **An embedding model upgrade is rolled out partially.** Symptom: recall
   collapses to near-chance, with no error. Fix: the space router refuses
   mixed searches, and a dual-index period is explicit with a cutover date.
5. **Index build exceeds the nightly window after a growth spurt.** Fix: the
   build is parallelized per partition and partitions are added independently;
   a partition can be built and swapped while others still serve.
6. **Memory pressure during compaction.** Symptom: an OOM-killed node. Fix:
   compaction writes to a temp file and swaps by reference, so peak memory is
   1.2x not 2x, and the node limit is set below the physical limit
   deliberately.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Approximate nearest-neighbour indexes trade exactness for speed; HNSW is a
  layered graph index whose recall is governed by its construction and search
  parameters, and which is what most vector databases implement.
  - Reference: https://arxiv.org/abs/1603.09320
  - Reference: https://www.pinecone.io/learn/series/faiss/hnsw/
- Vector search systems commonly combine an approximate index with a
  re-ranking stage (a more expensive, more accurate model) over the top
  candidates, which is why a pure ANN recall number is not the user-visible
  quality figure.
  - Reference: https://www.pinecone.io/learn/series/faiss/
  - Reference: https://docs.weaviate.io/weaviate/concepts/vector-search
- Filters applied after an approximate search can lose recall, because the
  candidate set may be almost entirely filtered out; systems address this with
  filter-aware search, larger candidate sets, or pre-filtered partitions.
  - Reference: https://docs.pinecone.io/guides/data/filter-by-metadata
  - Reference: https://docs.weaviate.io/weaviate/concepts/filtering

## Deliverables

- [ ] Recall loss root-cause analysis with the 3 causes and their magnitudes
- [ ] Embedding-space router that structurally prevents mixed-space indexes
- [ ] Department-partitioned layout with filter-aware routing, and a stated
      trade for unfiltered queries
- [ ] Compaction at a tombstone ratio plus a nightly schedule, swap-by-reference
- [ ] Security filters enforced at the storage layer with post-verification and
      an hourly synthetic probe
- [ ] Nightly ground-truth recall SLO with a 7-day drift alarm
- [ ] Before/after table for recall (overall and filtered), latency, tombstones
- [ ] Runbook for the six failure modes
