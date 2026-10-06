# llm-genai-deep — Real-World Project

## Project: An Enterprise Knowledge Assistant with Evaluation, Governance, and Safety

Build a production knowledge assistant for an organization: ingestion of 200k documents into
a hybrid index, tenant-aware retrieval, a grounded generation path with abstention and
citation validation, an evaluation harness with human labels, a tiered safety stack, an
attack programme, and the governance artifacts a regulated enterprise requires.

## Context

Enterprise assistants sit on the boundary between a company's most sensitive content and
every user in the company. That makes four things non-optional that would be optional in a
prototype: point-in-time correct access control, an evaluation set that does not get gamed,
a safety layer designed around the real base rate, and a governance trail. This project
builds all of it.

## Sourced field notes (fetched Oct 2026 — verify before citing)

- "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" (Lewis et al.,
  submitted 12 May 2020; v2 18 Jul 2022) — https://arxiv.org/abs/2005.11401 — takeaway for
  this lab: retrieval quality and generation conditioning are separate problems that must be
  measured separately, and the parametric-plus-retrieval division of labour — behaviour from
  the model, facts from the index — is the architecture decision this system makes
  explicitly rather than by default.
- "Dense Retrieval" (Retrieval guide) — https://huggingface.co/learn — takeaway for this
  lab: the practical retrieve-then-rerank framing, and specifically that a bi-encoder's
  expressiveness is bounded because query and passage are encoded independently, which is
  why a cross-encoder reranker sits after the index and why the rerank candidate budget is
  treated as a first-class cost rather than an afterthought. It is also why recall here is
  measured against an exact-search baseline instead of assumed.

## System Architecture

```
  ingestion                              serving
  --------                              -------
  connectors -> parse -> chunk ->        request
                dedupe -> ACL stamp        |
                embed -> index              v
                              hybrid index (dense + lexical)
                                          |  pre-filtered by ACL
                                    dense retrieve + lexical retrieve
                                          |  RRF fusion
                                    cross-encoder rerank (budgeted)
                                          |
                              +-----------v------------+
                              |  context assembly      |
                              |  ordering + dedupe     |
                              |  conflict detection    |
                              +-----------+------------+
                                          |
                              +-----------v------------+
                              |  LLM                   |
                              |  grounded generation   |
                              +-----------+------------+
                                          |
                              +-----------v------------+
                              |  output guardrails     |
                              |  schema | faithfulness|
                              |  citations | PII      |
                              |  policy | abstention  |
                              +-----------+------------+
                                          |
                                    answer or abstain
                                          |
                                    audit + feedback

  offline: eval harness | attack programme | drift | governance
```

## Component Specs

### 1. Ingestion
- Connectors for the content types the organization actually has: wikis, tickets, PDFs,
  code repositories, internal mail, incident runbooks. Each with a parser and a stated
  fidelity limit.
- **Chunking by content type**, not by a single global rule. Runbooks split by step; code
  split by symbol with the file path and module in the embedded text; tickets split by
  comment thread with the issue title included. This is where answer quality is won.
- Dedupe near-identical chunks at ingest (MinHash), because duplicated boilerplate crowds
  the top-k.
- **ACL stamped onto every chunk at ingest** from the source system, never inferred at query
  time. Pre-filtering by ACL happens inside the index query, not after.
- Point-in-time correctness: a document version carries its effective dates; retrieval
  respects them so that a question about "current policy" does not return a superseded
  version.
- Ingestion provenance recorded per chunk: source, connector version, ingested at,
  effective dates, ACL version.

### 2. Index and Retrieval
- **Hybrid retrieval**: dense (bi-encoder) plus lexical (BM25-style), fused by reciprocal
  rank fusion. Hybrid is not optional for enterprise content, because exact identifiers,
  error codes, and product names are lexical matches that dense retrieval misses.
- RRF: `score(d) = sum_r 1 / (k + rank_r(d))` with `k = 60`. It combines rankings without
  requiring score calibration between the two retrievers.
- Cross-encoder rerank over the top `N`, with `N` as an explicit budget knob.
- **ACL pre-filtering inside the query**: unauthorized candidates never enter the candidate
  set, so they cannot influence the result through reranking or through leakage of their
  existence in scores.
- Recall measured against exact search on a labelled set. Never assumed.
- Index updates: incremental with a staleness metric and a full rebuild cadence; recall cost
  of staleness measured and reported.

### 3. Query Understanding
- Query classification: factual lookup, how-to, policy question, multi-hop, ambiguous,
  out-of-scope.
- Routing by class: factual lookups go to precise retrieval with reranking; how-to queries
  get procedure-shaped context; ambiguous queries get clarifying questions rather than a
  confident wrong answer.
- **Multi-hop decomposition**: split into sub-queries, retrieve per sub-query, fuse. Scored
  on a labelled multi-hop set, with the failure mode (a missing intermediate hop) identified.
- Entity and identifier extraction so that an error code is retrieved lexically even when
  phrased in prose.

### 4. Grounded Generation and Abstention
- System message establishes policy and states that untrusted document text is data, not
  instruction.
- Context assembly with **position measured**: the most relevant passage placed where
  attention attends best, verified on the internal set rather than assumed.
- Duplicate-contradiction detection: two retrieved passages disagreeing on a fact is
  detected and surfaced as a conflict rather than silently resolved by the model.
- **Every sentence carries a citation** to a span; citations validated against the index
  after generation. Fabricated citations are a hard failure, not a warning.
- **Abstention**: "the retrieved material does not answer this". Accuracy and coverage
  reported together at three thresholds; the operating point is a product decision made with
  the numbers in front of it.
- Faithfulness verified post-generation by claim extraction. Claims without support are
  removed or the whole answer is withheld, depending on the category.
- Refusal and over-refusal measured as a pair.

### 5. Evaluation Harness
- **A frozen, human-labelled evaluation set** that is versioned, never auto-extended from
  production traffic, and whose labels are re-adjudicated on a schedule. An eval set that
  grows from logged traffic drifts toward the model's own behaviour and stops detecting
  regressions.
- 1,000+ queries with graded relevance labels per passage, plus reference answers and
  required-abstention flags.
- **Retrieval metrics** (recall@k, MRR, NDCG, MAP) reported separately from **generation
  metrics** (faithfulness, answer correctness, citation validity, abstention correctness).
- Human evaluation on a stratified sample with inter-annotator agreement reported. An
  agreement below threshold invalidates the labels, not the model.
- LLM-as-judge with a structured rubric, calibrated against human labels, with position-bias
  correction and a documented judge model version. Judge-human correlation re-verified each
  time the judge model changes.
- Slice reporting: by query class, department, document type, language, and query length. The
  headline metric hides the failures that generate tickets.
- **Regression gate**: any candidate release must not regress on any slice beyond its stated
  delta, and safety regression of any size blocks.

### 6. Safety Stack
- Input layer: normalization, recursive decode detection, length caps, per-user and
  per-tenant rate limits, injection signature detection.
- Tiered content filter: cheap high-recall first stage on 100% of traffic, precise classifier
  on the survivors. Confusion matrix reported with precision at the real base rate — at a
  low disallowed rate a single classifier is mostly false flags.
- Prompt boundary: policy in the system message, document text wrapped and labelled as data,
  privilege separation so capability never comes from model narration.
- **No tools in the base assistant.** Agentic capability is a separate, opt-in deployment
  with its own tool gate, arg-scoped approvals, idempotency keys, and its own release gate.
- Output pipeline: schema, refusal appropriateness, faithfulness, citation validity, PII
  scrub with re-scan, policy classifier — all fail closed on exception.
- Tenant isolation: pre-filtered retrieval, tenant-scoped caches, tenant-tagged traces with
  retention, per-tenant deletion enforced.
- Red-team programme: threat-modelled attack library, nightly mutation runs, quarterly
  expert sessions, and an intake SLA converting every found bypass into a permanent test
  within one business day.

### 7. Operations
- Per-request latency budget: retrieval, rerank, generation, guardrails, each measured
  separately with a target. Rerank size `N` is the main dial and is justified explicitly.
- Caching: query embedding cache, retrieval cache (tenant-scoped), generation cache for
  repeated questions — each with invalidation on index version change.
- Rate limiting and admission control; a tenant cannot consume the whole fleet.
- Multi-region deployment with a defined consistency model: an index update is
  region-specific until propagated, and the behaviour is documented rather than discovered.
- Cost per answer measured and budgeted; cost per **correct** answer reported as well.
- Content staleness: documents with an expiry, flagged in output when the answer depends on
  old material.

### 8. Drift and Feedback
- Query-distribution drift (JS divergence against a frozen reference window).
- Answer-distribution drift: refusal rate, abstention rate, citation density, answer length.
- Index-quality drift: abstention rate rising means retrieval has degraded — the earliest
  signal, because it appears before user complaints.
- Feedback loop risk: if answers cite only recent documents, retrieval narrows over time.
  Monitor citation-age distribution and coverage of the long tail.
- Content drift: source systems changing format, which breaks parsers silently. Monitor
  ingestion parse-success rate as a first-class metric.
- Retraining/refresh triggers on drift thresholds, with a pipeline-first investigation
  ladder.

### 9. Governance
- Model card per release: intended use, out-of-scope uses, evaluation results overall and
  per slice, known limitations, owner.
- Data processing record: what is indexed, from where, under what ACL, with what retention.
- Access audit: who queried what, when — the access log is itself a governed artifact.
- Deletion: a source document deletion propagates to the index, caches, and traces, with a
  verified propagation time.
- Approval trail per release with the model card diff.
- Transparency: what the assistant can and cannot do, what is logged, and the appeal path.

## Non-Functional Targets

| Metric | Target |
|--------|--------|
| Retrieval recall@10 on the frozen eval set | >= 0.90 |
| Reranked answer faithfulness | >= 0.95 |
| Citation validity | >= 0.98; fabricated citations = 0 |
| Abstention correctness | >= 0.90 on the required-abstention set |
| Over-refusal on benign queries | <= 0.05 |
| Safety filter precision at the real base rate | >= 0.90 after tiering |
| Unauthorized retrieval | 0 across 10,000 randomized cross-tenant tests |
| p95 latency, retrieval + rerank + generation | Per the stated budget, enforced by a release gate |
| Rerank candidate budget `N` | Explicit and justified; reported in the latency breakdown |
| Eval human inter-annotator agreement | Above the stated threshold; below it, labels are re-adjudicated |
| Slice regression tolerance | Per slice; safety regression tolerance = 0 |
| Judge-human agreement | Tracked and re-verified on judge model change |
| Deletion propagation | Verified, with the propagation time published |
| Abstention rate drift | Alert on a sustained rise |

## Failure Modes and Mitigations

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| ACL applied after ranking | Cross-tenant test finds a hit | Pre-filter inside the index query; ACL stamped at ingest |
| Dense retrieval misses exact identifiers | Lexical-only eval set | Hybrid retrieval with RRF fusion |
| Chunking destroys procedure structure | Task-success rate on how-to queries | Type-aware chunking; steps and headings preserved |
| Evaluation set drifts toward the model | Slice metrics all improving suspiciously | Frozen labelled set; re-adjudication schedule |
| Judge model silently changed | Human-label agreement drops | Judge version pinned; agreement re-verified on change |
| Position bias in the judge | Order-swapped agreement rate | Randomized order; report corrected agreement |
| High BLEU, low faithfulness | Side-by-side report | Faithfulness as the release gate; BLEU as diagnostic only |
| Fabricated citations | Post-generation citation validation | Hard failure; citations verified against the index |
| Model states a permission it lacks | Privilege-separation test | Capability from code only |
| Single classifier at a low base rate | Flag precision near 0.1 | Tiered filtering |
| Indirect injection via an internal doc | Attack suite over the real corpus | Data labels; privilege separation; output guardrails |
| Rerank budget inflated for one query class | Latency by class | Per-class rerank budget with a global cap |
| Cache leaks across tenants | Isolation test | Tenant-scoped cache keys including ACL version |
| Index staleness after a bulk update | Staleness metric | Incremental update with a measured recall cost; rebuild cadence |
| Content-format change breaks a parser | Parse-success rate alert | Monitor ingestion health as a product metric |
| Deletion not propagated | Periodic propagation audit | Verified propagation with a published SLA |
| Missing telemetry | Instrumentation check | Blocks release |
| Answer depends on expired content | Content-staleness flag in output | Expiry metadata surfaced to the user |

## Milestones

- **M1** — connectors and parsers, with per-type fidelity limits documented.
- **M2** — type-aware chunking with provenance and ACL stamping.
- **M3** — hybrid index: dense plus lexical, RRF fusion, ACL pre-filter.
- **M4** — cross-encoder reranker with an explicit budget and measured recall.
- **M5** — query classification, routing, multi-hop decomposition.
- **M6** — grounded generation with citation validation.
- **M7** — conflict detection for contradictory passages.
- **M8** — abstention with the accuracy/coverage frontier.
- **M9** — frozen labelled evaluation set of 1,000 queries.
- **M10** — retrieval and generation metrics reported separately, with slices.
- **M11** — human evaluation with agreement reported.
- **M12** — judge calibration with position-bias correction.
- **M13** — tiered safety filter with the confusion matrix.
- **M14** — output pipeline fail-closed, PII scrub with re-scan.
- **M15** — tenant isolation with 10,000 randomized cross-tenant tests.
- **M16** — red-team programme with mutation runs and the intake SLA.
- **M17** — agentic capability as a separate gated deployment.
- **M18** — drift monitoring with the pipeline-first ladder.
- **M19** — governance pack: model card, data record, access audit, deletion verification.
- **M20** — staged rollout with the release gate and rollback.

## Deliverables

1. Ingestion and hybrid index with ACL pre-filtering and provenance.
2. Query routing, retrieval, reranking, and grounded generation with citation validation.
3. Evaluation harness with a frozen labelled set, human evaluation, and calibrated judging.
4. Tiered safety stack, output guardrails, tenant isolation, and a red-team programme.
5. Operations: latency budget, caching, cost per correct answer, deletion propagation.
6. `REPORT.md` — the platform posture: retrieval and generation metrics overall and per
   slice, faithfulness and citation validity, abstention frontier, safety filter confusion
   matrix, tenant isolation results, attack results with attribution, drift sensitivity, and
   residual risks accepted with reasons.

## Definition of Done

- [ ] ACL pre-filtered inside the index query; 10,000 cross-tenant tests return zero
      unauthorized documents.
- [ ] Hybrid retrieval beats dense-only on the identifier-heavy eval slice, by a stated
      margin.
- [ ] Recall@10 at or above 0.90 on the frozen eval set, measured against exact search.
- [ ] Every answer sentence carries a citation; fabricated citations are zero over 10,000
      answers.
- [ ] Faithfulness at or above 0.95 on the generated-answer set.
- [ ] Abstention correctness at or above 0.90 on the required-abstention slice.
- [ ] Over-refusal at or below 0.05 on benign queries.
- [ ] Contradictory passages surfaced as conflicts rather than silently resolved.
- [ ] Slice metrics reported; a slice regression beyond its delta blocks the release.
- [ ] Human inter-annotator agreement reported; below threshold triggers re-adjudication.
- [ ] Judge position bias corrected and the corrected agreement reported.
- [ ] Safety filter precision at or above 0.90 at the real base rate, with the confusion
      matrix.
- [ ] Output stage exception blocks (fail closed verified).
- [ ] Direct and indirect injection suites pass with per-layer attribution published.
- [ ] Every found bypass becomes a permanent test within one business day.
- [ ] Agentic tools absent from the base deployment; the separate deployment has its own
      gate and arg-scoped approvals.
- [ ] Deletion propagation verified with the time published.
- [ ] Missing telemetry blocks the release.
- [ ] Model card, data processing record, and access audit complete and versioned.
