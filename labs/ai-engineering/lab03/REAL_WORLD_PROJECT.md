# Lab 03: RAG System Architecture — Real-World Project

## Project: Enterprise Knowledge RAG Service

Design and build the RAG service a regulated enterprise runs on: multi-tenant
ingestion with ACLs, hybrid retrieval with reranking, citation-grade answers,
evaluation, freshness guarantees, and operations.

## Context

Enterprise RAG answers questions about documents that change hourly, contain
structure (tables, forms, headers), are access-controlled, and must be auditable. The
engineering burden is in ingestion correctness, isolation, citations, and evaluation —
not in the retrieval call itself.

## Sourced field notes (fetched Oct 2026 — verify before citing)

- "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" (Lewis et al.,
  submitted 22 May 2020; NeurIPS 2020) — https://arxiv.org/abs/2005.11401 — takeaway for
  this lab: combining parametric seq2seq memory with a non-parametric dense index is the
  architecture implemented here, and the paper's evaluation framing (retrieval quality
  plus generation quality) is why this service measures both separately.
- "Introducing Contextual Retrieval" (Anthropic Engineering, published 19 Sep 2024) —
  https://www.anthropic.com/engineering/contextual-retrieval — takeaway for this lab:
  prepending chunk-specific context before embedding plus contextual BM25, and adding a
  reranker over the top candidates, cut retrieval failures substantially — the direct
  evidence for the contextual prefix, hybrid search, and rerank stages in this design.

## System Architecture

```
  SOURCES (Confluence | SharePoint | S3 PDFs | tickets | DB views)
        |
   +----v----------------------------------------------------------------+
   |  INGEST                                                             |
   |  parse -> de-skew -> OCR -> layout -> regions (200-600 tok)          |
   |  contextual prefix | tables kept whole | dedupe | content hash       |
   |  PII scan | embed (cached) | index upsert | tombstone deletes      |
   |  idempotent | index_age_hours metric                                 |
   +----+----------------------------------------------------------------+
        |
   +----v-------------------+     +-------------------+
   |  INDEX PER NAMESPACE   |     |  CHUNK STORE      |
   |  (tenant, corpusV,     |     |  text, metadata,   |
   |   embedV)              |     |  bbox, source ref  |
   |  dense HNSW + BM25     |<----|  source of truth   |
   +----+-------------------+     +-------------------+
        |
   +----v----------------------------------------------------------------+
   |  QUERY PATH                                                        |
   |  rewrite -> embed -> namespace -> ACL PRE-FILTER                     |
   |  -> dense top-50 + BM25 top-50 -> RRF -> rerank 50->5                |
   |  -> dedupe -> budget pack (best last) -> grounded prompt             |
   |  -> generate -> citation verify -> faithfulness -> PII scrub         |
   +----+----------------------------------------------------------------+
        |
   +----v-------------------+     +-------------------+
   |  EVALUATION             |     |  OBSERVABILITY    |
   |  recall@k, nDCG, MRR    |     |  per-stage latency|
   |  citation validity      |     |  cost per query   |
   |  faithfulness, abstain  |     |  freshness        |
   +-------------------------+     +-------------------+
```

## Component Specs

### 1. Ingestion
- **Structure-aware parsing**: headings build a `sectionPath`; tables kept whole and
  additionally rendered as per-row text for embedding; forms mapped to fields;
  handwriting flagged low-confidence.
- **Region granularity**: 200-600 tokens. Pages are too coarse to cite and waste
  tokens; whole documents are impossible.
- **Contextual prefix**: `[Document | Section | Updated | Owner]` prepended to the
  embedded text; the display text stays unmodified for citations.
- **Idempotent** by `sha256(docId + chunkText)`; a re-ingest inserts zero chunks.
- **Near-duplicate suppression** at ingest (cosine > 0.97 within a document), keeping
  the highest-quality copy — syndicated policy documents are common.
- **Deletions** create tombstones immediately; a soft-deleted chunk still retrievable is
  a data-leak incident.
- **Freshness SLA** per corpus with `index_age_hours` alerting and a re-ingest trigger.
- PII and secret scanning at ingest; quarantine on hit.

### 2. Namespace and Access Control
- Namespace = `(tenantId, corpusVersion, embedVersion)`; required in the query API.
- **ACL pre-filter inside the index query** — never post-filter, and never an API-only
  check. Unauthorized content must not influence ranking or the prompt.
- ACL predicate per chunk (roles, groups, sensitivity), cached per `(user, doc)` for
  60 s.
- **Isolation test in CI**: for random (user, query) pairs, the union of retrievable
  chunk ids must equal the authorized set exactly. Runs on every build.
- Embedding-model migrations use dual indexes (blue/green) with a recall check before
  the flip.

### 3. Retrieval
- Dense: HNSW, `efSearch` tuned per corpus from a sweep.
- Lexical: BM25 with contextual text (prefixed the same way for indexing).
- Fusion: RRF default; weighted fusion behind a flag for corpora where it measurably
  wins, A/B canaried.
- Rerank: cross-encoder top-50 -> 5; `k` tuned from the quality knee; per-corpus
  switch; batched for latency; rerank scores cached per `(queryHash, chunkId)`.
- Stage-level latency recorded so regressions are attributable.

### 4. Context Assembly
- Budget = `maxContext - system - query - maxNew - schema`.
- Emit ascending score so the best region lands nearest the question.
- Deduplicate near-identical regions.
- Number regions; require `[doc page region]` citations.
- Never truncate the schema, the question, or the grounding instruction.
- Record what was dropped for every request.

### 5. Answering and Verification
- Grounding instruction plus the `INSUFFICIENT_CONTEXT` sentinel.
- **Citation verification**: cited ids must exist, and the cited region must have been
  included in the context.
- **Numeric verification**: for form/table questions, recompute from extracted fields
  and flag mismatch. A wrong number is the failure that causes real damage.
- **Faithfulness scoring** per claim, logged as a metric.
- **Abstention** below a retrieval-score threshold with a typed reason (no evidence /
  ungrounded answer / low OCR confidence).
- PII scrub on the response; citations resolve to deep links.
- High-risk categories (legal, financial, HR) route to human review.

### 6. Evaluation
- Golden set per corpus: 500+ questions with gold region ids and graded answers,
  refreshed monthly.
- Metrics: recall@1/5/10, nDCG@10, MRR, citation validity, citation support, answer
  correctness, faithfulness, abstention coverage/accuracy, false-decline rate.
- **Unanswerable subset** at least 15% of the suite.
- Per-document-type breakdown — one aggregate hides chart and form failures.
- Promotion gate: a candidate config must beat the incumbent on correctness and not
  regress p95 latency or cost.
- Continuous eval: sample production queries, score offline, feed failures into the
  golden set.

### 7. Operations
- Dashboards: quality per corpus, latency per stage, cost per query, freshness, cache
  hit rates, ACL denials, abstention rate.
- Alerts: recall drop, freshness breach, latency regression, abstention spike, ACL test
  failure (page), index rebuild failure.
- Runbooks: "answers got worse" (freshness -> recall -> prompt -> model, in that
  order), "index stale", "ACL incident".
- Blue/green index rebuilds with a recall verification step before the flip.

## Non-Functional Targets

| Metric | Target |
|--------|--------|
| recall@5 | >= 0.90 |
| nDCG@10 | >= 0.85 |
| Answer correctness | >= 0.85 |
| Numeric accuracy on forms | >= 0.95 |
| Citation validity | >= 0.98 |
| Faithfulness | >= 0.90 |
| Abstention on unanswerable | >= 0.95 |
| False-decline rate | <= 0.10 |
| p95 end-to-end latency | <= 3 s |
| Index freshness | <= 2 h |
| Cost per query | <= $0.05 |
| ACL leakage | 0 |

## Failure Modes and Mitigations

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| ACL regression | Per-role retrieval set test | Pre-filter; deny by default |
| Stale index | `index_age_hours` | Freshness SLA + auto re-ingest |
| Wrong region, right page | Citation support rate | Finer regions; bbox citations |
| Wrong page | recall@5 | Hybrid, rerank, query rewrite |
| Chart value hallucinated | Numeric verification | Structured field preference |
| Low-quality scan answered | OCR confidence gate | Reject/flag; do not guess |
| Context overflow | `finish_reason=length` | Region caps, lower k |
| Injection via document | Injection canary suite | Treat retrieved text as data |
| PII in prompt | PII scan at ingest and on OCR text | Redact before assembly |
| Embedding migration dip | Recall check before flip | Dual index, blue/green |
| Rerank latency blowout | Stage latency | Tune k, batch, per-corpus switch |
| Cost growth from chunk size | Cost per query | Region caps, dedupe |

## Milestones

- **M1** — ingestion with regions, contextual prefixes, idempotency, freshness.
- **M2** — namespace manager with ACL pre-filter and isolation tests in CI.
- **M3** — hybrid retrieval with RRF and tuned rerank.
- **M4** — assembly with budget, ordering, dedupe, drop reporting.
- **M5** — answering with citations, numeric verification, abstention.
- **M6** — golden sets per corpus with per-document-type metrics.
- **M7** — promotion gate wired into CI.
- **M8** — continuous eval on production queries.
- **M9** — dashboards, alerts, runbooks.
- **M10** — blue/green rebuild; embedding migration exercised.
- **M11** — game day: delete a policy section and verify the system notices.

## Deliverables

1. Ingestion, retrieval, assembly, answering, and verification services.
2. Evaluation harness with golden sets and the promotion gate.
3. ACL isolation test suite in CI.
4. Dashboards, alerts, runbooks.
5. `REPORT.md` — quality per corpus, latency per stage, cost per query, freshness.
6. `RAG_RUNBOOK.md` — triage by symptom, starting with freshness.

## Definition of Done

- [ ] recall@5 >= 0.90 and citation validity >= 0.98 on every corpus.
- [ ] Zero ACL leakage across 10,000 randomized isolation tests.
- [ ] Index freshness <= 2 h with alerting and a measured rebuild time.
- [ ] Abstention >= 0.95 on unanswerable with false declines <= 0.10.
- [ ] Numeric accuracy >= 0.95 on form/table questions.
- [ ] A recall-dropping config blocked by the promotion gate.
- [ ] A stale-index incident detected by the freshness alert before user reports.