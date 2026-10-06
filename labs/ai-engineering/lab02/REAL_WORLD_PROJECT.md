# Lab 02: Vector Database Integration — Real-World Project

## Project: Production Vector Retrieval Service

Design and build the retrieval data plane for a multi-tenant product: ingestion,
indexing, hybrid search with reranking, isolation, freshness, evaluation, and
operational ownership.

## Context

The retrieval service is where an AI product's accuracy is won or lost before the model
is ever called. It must be fast, exact enough, isolated, and rebuildable — and its
quality must be measured continuously, because retrieval regressions are silent.

## Sourced field notes (fetched Oct 2026 — verify before citing)

- "Efficient Memory Management for Large Language Model Serving with PagedAttention"
  (Kwon et al., submitted 20 Jun 2023; v3 12 Feb 2024) —
  https://arxiv.org/abs/2309.06180 — takeaway for this lab: memory layout and reuse
  discipline (paged allocation, prefix sharing) dominate what a serving system can
  hold, which is the same principle behind index memory budgets, copy-on-write prefix
  sharing, and the compaction discipline in this retrieval service.
- "Dense Passage Retrieval for Open-Domain Question Answering" (Karpukhin et al., submitted
  25 Sep 2020; EMNLP 2020) — https://arxiv.org/abs/2004.04906 — takeaway for this lab:
  dense retrieval trained with in-batch negatives depends on hard negative mining for
  its quality, which is why this service treats negative selection, not index type, as
  the primary quality lever and tracks recall@k as its headline metric.

## System Architecture

```
   CORPORA (documents, tickets, wiki, product catalog)
        |
   +----v----------------------------------------------------------------+
   |  INGEST PIPELINE                                                    |
   |  parse -> clean -> structure-aware chunk -> contextual prefix      |
   |  content hash -> dedupe -> embed (cached) -> index upsert          |
   |  idempotent; tombstones for deletes; index freshness metric        |
   +----+----------------------------------------------------------------+
        |
   +----v----------------------------------------------------------------+
   |  INDEX MANAGER                                                      |
   |  namespace = (tenant, corpusVersion, embedVersion)                 |
   |  per-namespace: HNSW or IVF-PQ, quantized vectors, block tables   |
   |  prefix sharing (COW) | compaction | rebuild from chunk store    |
   +----+----------------------------------------------------------------+
        |
   +----v-------------+     +------------------+
   |  DENSE RETRIEVAL  |     |  LEXICAL RETRIEVAL|
   |  ANN + pre-filter |     |  BM25 + filter    |
   +----+---------------+     +--------+---------+
        |                          |
        +------------+-------------+
                     v
        +------------------------+        +------------------+
        |  FUSION (RRF default)  |        |  RERANK          |
        |  weighted as an option |        |  cross-encoder   |
        +-----------+------------+        |  top 50 -> top 5  |
                    |                     +--------+---------+
                    v                              |
        +-----------+------------------------------+
        |  RESULT ASSEMBLY                             |
        |  dedupe | diversify | metadata attach      |
        +-----------+--------------------------------+
                    |
   +----------------v---------------------------------------------------+
   |  QUERY PATH                                                       |
   |  query rewrite -> embed -> namespace -> filter -> dense+lexical   |
   |  -> fuse -> rerank -> assemble -> return (with scores)            |
   +-------------------------------------------------------------------+
        |
   +----------------v---------------------------------------------------+
   |  EVALUATION & OPERATIONS                                          |
   |  recall@k | nDCG | MRR | latency percentiles | memory | freshness |
   |  alert on recall drop | index_age_hours | rebuild status            |
   +---------------------------------------------------------------------+
```

## Component Specs

### 1. Ingestion
- Structure-aware parsing: headings build a `sectionPath`; tables kept whole plus a
  text rendering for embedding; code blocks preserved with language metadata.
- **Contextual chunk prefixes** (document title, section path, updated timestamp)
  prepended to the embedded text while `text` is kept unmodified for citations.
- **Idempotent** by `sha256(docId + chunkText)`: a re-ingest inserts zero vectors.
- Near-duplicate suppression at ingest (cosine > 0.97 against an existing chunk in the
  same document) with the highest-OCR-quality bbox retained.
- Deletes create tombstones; compaction runs in the maintenance window.
- Embedding cache keyed by `(embedVersion, contentHash)` so re-ingests are nearly free.
- `index_age_hours` per namespace with a freshness SLO and an alert.

### 2. Namespace and Isolation
- Namespace = `(tenantId, corpusVersion, embedVersion)`. The namespace is a required
  argument in the query API, not an optional filter.
- Changing the embedding model or the corpus creates a new namespace; a background
  dual-index migration serves both, then the old namespace is retired.
- Randomized isolation test in CI: for N random (tenant, query) pairs, every returned
  chunk id must belong to that tenant.
- ACL beyond tenancy (roles, sensitivity levels) as a mandatory pre-filter with a
  per-(user, doc) predicate cache.

### 3. Index Selection and Tuning
- Selection recorded per namespace: flat under ~1M vectors with an exactness
  requirement, HNSW for high recall, IVF-PQ when memory-bound.
- `nprobe` / `efSearch` / `M` tuned from a sweep against the namespace's own eval set,
  not from defaults.
- The tuned configuration and its recall/latency curve stored alongside the namespace.
- Memory budget per namespace enforced at creation; exceeding it forces a smaller
  footprint or an approval.

### 4. Query Path
```
rewrite (pronouns, abbreviations, normalization)
  -> embed with the namespace's model
  -> dense search (pre-filtered)
  -> lexical search (BM25, pre-filtered)
  -> fusion (RRF default; weighted when a corpus favours one side)
  -> rerank top 50 -> top 5
  -> dedupe (inflateThreshold comparator)
  -> assemble with chunk ids, scores, and metadata
```
- Query embedding cache keyed by `(embedVersion, normalizedQuery)`.
- Per-stage latency recorded so bottlenecks are attributable.

### 5. Fusion
- RRF default: no score calibration between cosine and BM25, robust when one retriever
  returns degenerate scores.
- Weighted fusion available for corpora where a specific mix is measurably better; the
  weight is tuned per namespace.
- A/B between fusion modes is a canaried change like any other.

### 6. Reranking
- Cross-encoder over `(query, chunk)`; `k` tuned per corpus from the quality knee.
- Batched for latency; a smaller reranker where the delta is not needed.
- Rerank result cache keyed by `(queryHash, chunkId)` for repeated questions.
- Report the recall delta and the latency cost; expose a per-namespace switch.

### 7. Freshness and Rebuild
- Full rebuild from the chunk store (the source of truth); the index is derived.
- Blue/green index swap: build a new index, verify recall on the eval set, then flip
  the namespace pointer.
- Rebuild progress visible; partial namespaces never serve.
- `index_age_hours` alerted; a stale index silently degrades answer quality, which is
  why it is a first-class metric.

### 8. Evaluation
- Per-namespace gold set: 500+ queries with gold chunk ids and graded relevance.
- Metrics: recall@1/5/10, nDCG@10, MRR, filtered vs unfiltered recall, latency
  percentiles per stage, memory per namespace, build time.
- Continuous evaluation on production query logs: sample, compare retrieved ids to
  click/answer signals, feed failures into the gold set.
- Alert on recall drop per namespace; a 5-point drop blocks index changes.

### 9. Operations
- Dashboards: quality per namespace, latency per stage, memory, freshness, cache hit
  rates, index build status.
- Alerts: recall drop, latency regression, memory pressure, `index_age_hours` breach,
  rebuild failure, tenant isolation test failure (page immediately).
- Runbooks per alert with the first question and the containment action.
- Ownership: the team that owns a corpus also owns its freshness and its eval set.

## Non-Functional Targets

| Metric | Target |
|--------|--------|
| recall@5 (per namespace gold set) | >= 0.90 |
| nDCG@10 | >= 0.85 |
| p50 query latency | < 30 ms |
| p99 query latency | < 150 ms |
| Index freshness | <= 2 h after a document change |
| Cross-tenant leakage | 0 |
| Ingest idempotency | Second run inserts 0 |
| Memory per 1M chunks (768d) | <= 12 GB |
| Recall drop alert threshold | 5 points |
| Availability | 99.9% |

## Failure Modes and Mitigations

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| Embedding version mismatch | Namespace validation | Pin version; reject mismatched queries |
| Cross-tenant leak | Randomized isolation tests | Required namespace arg; pre-filter |
| Recall drop after index change | recall@5 alert | Block change; roll back index pointer |
| Stale index | `index_age_hours` | Freshness SLO; incremental re-ingest |
| Recall collapse with filters | Filtered recall metric | Pre-filter; revisit selectivity |
| p99 spike from rerank | Stage latency | Lower k; batch; cache rerank scores |
| OOM after ingestion | Memory metric | IVF-PQ; smaller footprint; approval gate |
| Duplicate chunks at top | Duplicate rate metric | Ingest dedupe; query dedupe |
| Lexical-only identifiers missed | Identifier query subset metric | Hybrid fusion |
| Partial rebuild served | Build status check | Blue/green swap; never serve partial |
| Unbounded index growth | Compaction metric | Maintenance compaction; tombstone GC |
| Query latency from cold cache | Cold-start metric | Warmup on deploy |
| Index params un-tuned | Config audit | Tuned config stored with namespace |

## Milestones

- **M1** — ingest pipeline with idempotency, dedupe, contextual prefixes.
- **M2** — namespace manager with blue/green rebuild and dual-index migration.
- **M3** — index selection and per-namespace tuning from sweeps.
- **M4** — query path: rewrite, embed, dense + lexical, fusion.
- **M5** — reranking with tuned k and a per-namespace switch.
- **M6** — isolation: mandatory namespace, ACL pre-filter, randomized tests in CI.
- **M7** — evaluation harness with per-namespace gold sets.
- **M8** — freshness SLO, alerting, compaction.
- **M9** — observability dashboards and runbooks.
- **M10** — game day: force an embedding version change and verify the migration path.

## Deliverables

1. Retrieval service implementation.
2. Index management with rebuild and migration.
3. Evaluation harness and gold sets.
4. Dashboards, alerts, and runbooks.
5. `REPORT.md` — per-namespace index configuration with recall/latency/memory, the
   fusion comparison, rerank deltas, and the freshness SLO.
6. `RETRIEVAL_RUNBOOK.md` — triage per alert.

## Definition of Done

- [ ] recall@5 >= 0.90 on every namespace gold set.
- [ ] Zero cross-tenant leakage across 10,000 randomized tests.
- [ ] Re-ingest inserts zero vectors; compaction reclaims deleted storage.
- [ ] p99 query latency <= 150 ms at target corpus size.
- [ ] Index freshness <= 2 h, with alerting and a measured rebuild time.
- [ ] An embedding model migration completed via dual-index with no quality dip.
- [ ] A recall-dropping index change blocked by the gate.