# Lab 04: RAG System Design — Real-World Project

## Project: Production RAG Service for an Enterprise Knowledge Base

Design and build the retrieval-augmented generation service that answers employee
and customer questions over a large, changing, access-controlled document corpus —
with the evaluation harness, freshness guarantees, and failure handling that a real
deployment requires.

## Context

Enterprise RAG is not a demo. The hard parts are: a corpus that changes hourly,
documents with real structure (tables, headings, footnotes), per-document access
control, the need to cite sources so a human can verify, and a measurable accuracy
target that finance will audit. This project builds all of those.

## Sourced field notes (fetched Oct 2026 — verify before citing)

- "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" (Lewis et al.,
  submitted 22 May 2020; NeurIPS 2020) — https://arxiv.org/abs/2005.11401 —
  takeaway for this lab: the RAG-sequence/RAG-token framing of combining parametric
  seq2seq memory with a non-parametric dense index is the architecture this service
  implements; the paper's reported gains on open-domain QA justify the retrieval
  quality gates below.
- "Introducing Contextual Retrieval" (Anthropic Engineering, published 19 Sep 2024) —
  https://www.anthropic.com/engineering/contextual-retrieval — takeaway for this
  lab: prepending chunk-specific context before embedding plus hybrid contextual
  BM25 cut top-20 retrieval failures substantially, and a reranker over the top
  candidates cut failures further — the direct evidence behind the contextual
  prefix, hybrid, and rerank stages in this design.

## System Architecture

```
                     +-------------------- Upstream sources --------------------+
                     |  Confluence | SharePoint | S3 PDFs | Git repos | DB views |
                     +------------------------------------+----------------------+
                                          |
                          +---------------v----------------+
                          |  Ingest workers (idempotent)    |
                          |  parse -> clean -> structure   |
                          |  chunk -> contextual prefix    |
                          |  embed -> index upsert        |
                          +---------------+----------------+
                                          |  events: doc.created/updated/deleted
   +------------------+------------------+------------------+
   |                  |                  |                  |
+--v--------+  +------v-------+  +-------v------+  +--------v--------+
| Vector    |  | Lexical index |  | Chunk store  |  | Graph of       |
| index     |  | (BM25/ES)     |  | (Postgres)   |  | doc references |
| (HNSW/IVF)|  |               |  | text+meta    |  | (citations)    |
+--+--------+  +------+-------+  +-------+------+  +--------+--------+
   |                  |                  |                  |
   +------------------+--------+---------+------------------+
                            |
                   +--------v---------+
                   | Query gateway    |  auth, tenant, ACL filter, query logging
                   +--------+---------+
                            |
              +-------------v--------------+
              |  Retrieval service        |
              |  dense + lexical + RRF    |
              |  metadata pre-filter      |
              |  rerank (cross-encoder)   |
              +-------------+--------------+
                            |  chunk ids + scores
              +-------------v--------------+
              |  Context assembly         |
              |  budget, dedupe, order,   |
              |  numbering, grounding     |
              +-------------+--------------+
                            |  rendered prompt
              +-------------v--------------+
              |  LLM gateway              |  routing, retries, model cache
              +-------------+--------------+
                            |  raw answer
              +-------------v--------------+
              |  Answer verifier          |  citation parse, entailment,
              |                           |  abstention, PII scrub
              +-------------+--------------+
                            |
                   +--------v--------+
                   | Response +      |  answer, [n] citations, confidence,
                   | citations        |  "sources" deep links
                   +-----------------+
                            |
          +-----------------+-----------------+
          |                                   |
   [response API]                  [telemetry: metrics, traces, audit log]
```

## Component Specs

### 1. Ingestion
- Idempotent by `sha256(docId + corpusVersion + chunkText)`; second pass is a no-op.
- Structure-aware parsing: headings build a `sectionPath` breadcrumb; tables stay
  whole and are additionally rendered as a per-row text view for embedding.
- Contextual prefix: prepend `[Document: {title} | Section: {path} | Updated: {ts}]`
  to the text used for embedding. Keep `text` and `embeddingText` separate.
- Handle deletions with tombstones and a hard filter at query time — a soft
  delete that stays searchable is a data-leak incident.
- Track `index_age_hours` per corpus; alert past the freshness SLA.

### 2. ACL Enforcement
- Every chunk carries `tenantId` and an `aclPredicate` (roles, groups, sensitivity).
- Filter is applied **inside** the index query (pre-filter), not after retrieval,
  so unauthorized content can never influence the prompt.
- Cache ACL predicates per (user, doc) for 60 s to bound latency.
- Regression test: for every user role, assert the union of retrievable chunks
  equals the authorized set exactly.

### 3. Retrieval
- Dense (HNSW, `M=32`, `efSearch` tuned per corpus) + BM25.
- Fusion: RRF as the default (no calibration), weighted fusion behind a flag.
- Rerank top-50 -> top-5 with a cross-encoder; measure the recall delta and the
  latency cost, and expose a per-corpus switch to disable it where it does not pay.
- Metrics emitted per query: `recall_proxy@k`, `rerank_time_ms`, `k_final`.

### 4. Context Assembly
- Budget = `maxContext - systemTokens - queryTokens - maxNewTokens`.
- Deduplicate near-identical chunks (cosine > 0.97) — syndicated policy documents
  are a common source of wasted budget.
- Emit lowest-score-first so the strongest chunk sits nearest the question.
- Number chunks; require `[n]` citations; state the `INSUFFICIENT_CONTEXT` sentinel.

### 5. Answer Verifier
- Parse citations; reject ids outside the supplied set.
- Optional NLI/entailment check per cited sentence; flag unsupported claims.
- PII scrub on the response (emails, phone numbers, account numbers) before return.
- Return `confidence` derived from retrieval score + entailment margin, so callers
  can decide whether to show the answer or escalate to a human.

### 6. Evaluation Harness
- Golden set: 500+ questions with gold doc ids and graded answers, refreshed monthly.
- Track: recall@5, nDCG@10, MRR, citation precision/recall, answer correctness,
  abstention coverage/accuracy, p50/p95/p99 latency, cost per query.
- Any candidate config must beat the incumbent on correctness **and** not regress
  p95 latency by more than the agreed budget. This is a promotion gate, not a report.

### 7. Observability and Cost
- Trace per query: stages with timings, retrieved ids with scores, final prompt hash.
- Cost attribution: embedding calls, rerank calls, prompt tokens, completion tokens,
  per tenant and per feature.
- Cache: prefix caching for the system prompt, embedding cache keyed by content hash.
- Dashboard panels: quality, latency, cost, freshness, cache hit rate.

## Failure Modes and Mitigations

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| Stale index after bulk update | `index_age_hours` alert | Idempotent re-ingest job + freshness SLA |
| ACL regression (leak) | Per-role retrieval set test | Pre-filter inside the index; deny by default |
| Retrieval collapse after embed change | recall@k drop alarm | Namespace by model version; dual-index during migration |
| Rerank blows latency budget | stage timing p95 | Reduce k, batch, or disable per corpus |
| Context overflow | finish_reason=length | Shrink chunks, lower k, add summarization tier |
| Confident fabrication | verification failure rate | Threshold + abstention + escalation |
| Prompt cache misses | prefix hit rate drop | Move volatile fields to the tail |
| Hot tenant starving others | per-tenant p95 skew | Weighted fair queueing |

## Non-Functional Targets

| Metric | Target |
|--------|--------|
| recall@5 (golden set) | >= 0.90 |
| Answer correctness | >= 0.80 on answerable questions |
| Citation precision | >= 0.95 |
| p95 end-to-end latency | <= 3 s |
| p99 end-to-end latency | <= 8 s |
| Index freshness | <= 2 h after a document change |
| Availability | 99.9% |

## Milestones

- **M1** — ingest pipeline with idempotency and tombstones; freshness metrics.
- **M2** — dense + BM25 + RRF retrieval; golden set of 100 questions; baseline recall.
- **M3** — ACL pre-filter with the per-role retrieval-set test passing.
- **M4** — contextual prefixes; measure recall delta.
- **M5** — reranking stage with latency accounting and a per-corpus switch.
- **M6** — answer verifier with citation validation and PII scrub.
- **M7** — eval harness wired into CI as a promotion gate.
- **M8** — full observability, cost dashboard, and an operator runbook.

## Deliverables

1. Service implementation (gateway, retrieval, assembly, verification).
2. `EvalHarness` runnable locally and in CI, emitting the metric table.
3. `REPORT.md` — quality/latency/cost trade-offs with the promotion-gate results.
4. `runbook.md` — triage for "answers got worse" (freshness, recall, prompt, model).
5. `acl_test.md` — the authorization matrix the tests enforce.

## Definition of Done

- [ ] Golden-set recall@5 >= 0.90 and correctness >= 0.80.
- [ ] No prompt ever contains a chunk the caller is not authorized to read (proved
      by the per-role test over 500 randomized queries).
- [ ] Re-ingest is idempotent and deletions remove content within the SLA.
- [ ] Promotion gate blocks a deliberately degraded config.
- [ ] Every metric in the observability list is queryable and alerted.