# Lab 08: Multimodal Models — Real-World Project

## Project: Enterprise Visual Document Understanding System

Design and build a multimodal retrieval-and-answer system for a document-heavy
enterprise: scanned forms, invoices, charts, photographs, and screenshots, answered
by a VLM with citations to the exact region of the exact page — with evaluation,
bias audits, and safety controls.

## Context

Visual document understanding is where multimodal models meet real business
pressure: the inputs are messy scans, the questions are specific, the answers must be
traceable to a page region for audit, and a wrong answer can mean a wrong payment.

## Sourced field notes (fetched Oct 2026 — verify before citing)

- "Learning Transferable Visual Models From Natural Language Supervision" (Radford et
  al., submitted 22 Feb 2021) — https://arxiv.org/abs/2103.00020 — takeaway for this
  lab: contrastive pretraining on image-text pairs transfers to downstream tasks
  without labels, which is why the dual-encoder retrieval tower in this system is
  trained contrastively and kept frozen while the generator is tuned separately.
- "Visual Instruction Tuning" (Liu et al., submitted 15 Apr 2023; v2 Oct 2023) —
  https://arxiv.org/abs/2304.08485 — takeaway for this lab: instruction-tuning a
  pretrained vision encoder against a frozen LLM through a connector, without
  touching the language model, produces general multimodal instruction following —
  the architecture and stage ordering used by the answering service here.

## System Architecture

```
  document sources
  +------------------+  +------------------+  +------------------+
  | scanned PDFs     |  | invoices / forms |  | screenshots      |
  +--------+---------+  +--------+---------+  +--------+---------+
           |                     |                     |
           +---------------------+---------------------+
                                 |
                    +------------v-------------+
                    |  Document Ingestion     |
                    |  de-skew, deskew, OCR   |
                    |  layout analysis        |
                    |  page -> region crops   |
                    |  region -> text + bbox  |
                    +------------+-------------+
                                 |
              +------------------+------------------+
              |                                     |
    +---------v----------+              +-----------v---------+
    | Vision tower       |              | Text store          |
    | (frozen CLIP-like) |              | OCR text per region |
    | region embeddings  |              | + bbox + page ref   |
    +---------+----------+              +-----------+---------+
              |                                     |
              +------------------+------------------+
                                 |
                    +------------v-------------+
                    | Multimodal Index         |
                    |  - dense vectors (HNSW)  |
                    |  - BM25 over OCR text    |
                    |  - RRF fusion            |
                    +------------+-------------+
                                 |
   text query ──────────────────>|  (same CLIP text encoder)
                                 |
                    +------------v-------------+
                    | Retrieval + Rerank      |
                    |  cross-encoder over     |
                    |  (query, region) pairs  |
                    +------------+-------------+
                                 |
                    +------------v-------------+
                    | Context Assembly        |
                    |  region crops as images |
                    |  + OCR text as text     |
                    |  budget-aware packing   |
                    +------------+-------------+
                                 |
                    +------------v-------------+
                    | VLM Answering           |
                    |  region images + text   |
                    |  answer with [page,box] |
                    +------------+-------------+
                                 |
                    +------------v-------------+
                    | Verification            |
                    |  citation bbox exists   |
                    |  OCR arithmetic recheck |
                    |  confidence + abstain   |
                    +------------+-------------+
                                 |
                    +------------v-------------+
                    | Response + audit trail  |
                    +-------------------------+
```

## Component Specs

### 1. Ingestion
- De-skew and deskew; normalize DPI; reject pages below a legibility threshold with a
  clear "image quality too low" response rather than a confident guess.
- Layout analysis into regions (header, table, figure, body, footer).
- **Region granularity**: pages alone are too coarse to cite and waste tokens;
  whole documents are impossible. Regions of ~200-600 tokens are the working unit.
- OCR per region with bounding boxes and a confidence score. Low-confidence regions
  are flagged and excluded from generation but remain retrievable.
- Extract structured fields (invoice totals, dates, line items) with a confidence
  per field for deterministic verification downstream.
- Idempotent by `sha256(page content)`; store the crop, the embedding, and the
  bbox metadata together.

### 2. Index and Retrieval
- Dense: region embeddings, HNSW, `M=32`, `efSearch` tuned for recall.
- Lexical: BM25 over OCR text — critical for exact ids, totals, and part numbers.
- Fusion: RRF (no score calibration across the two modalities).
- Metadata filters: tenant, document type, date range, confidence floor.
- **Crop rotation**: adjacent region crops from the same page share nearly identical
  embeddings. Deduplicate at ingest with a cosine threshold, keeping the bbox with the
  highest OCR confidence.

### 3. Reranking
- Cross-encoder over `(query, region_text + region_caption)`.
- For visual questions (charts, diagrams, photos), rerank with a
  `(query, region_image)` vision-language scorer — text-only reranking is blind to
  "what is the shape in this figure".
- Report the recall delta and latency cost per rerank stage; make each stage a
  per-corpus switch.

### 4. Context Assembly
- Each selected region contributes **both** the crop image (for charts, figures,
  handwriting, layout) and its OCR text (for precision and cheapness). Passing both
  is measurably better than either alone.
- Budget: crop tokens count against the context like text tokens. Cap the number of
  regions per answer; ordering puts the strongest region nearest the question.
- Prefetch crops only for the regions that survive budget selection — fetching
  images for regions that get dropped is pure waste.

### 5. Answering and Verification
- Answers must cite `[docId page region]`. Validation:
  - the cited region exists,
  - the crop was actually included in the context,
  - for numeric answers on forms, recompute from extracted fields and flag mismatch.
- Confidence combines retrieval score, OCR confidence, and cross-encoder margin.
- Abstention below threshold with the specific reason ("not found on this page" vs
  "page quality too low").
- Never answer a numeric question from OCR text alone when a structured field
  exists; prefer the field, and say which source was used.

### 6. Evaluation
- Retrieval: recall@k and nDCG@k over a labeled question set with known page and
  region.
- Answering: exact match / F1 for extractive questions; rubric score for reasoning
  questions; **numeric accuracy** computed against the source document.
- **Citation accuracy**: fraction of citations that resolve, and fraction of answers
  whose cited region actually contains the supporting content (verified by a second
  human or by a crop-level entailment check).
- **Abstention quality**: on unanswerable questions, the correct behavior is to
  decline; measure decline rate and false-decline rate separately.
- Per-document-type breakdown — a single aggregate metric hides chart failures.

### 7. Bias and Safety
- Bias audit: run the same question against visually varied documents (different
  name conventions, photo demographics, scan quality) and compare answer rates and
  extract rates.
- Injection: OCR text is untrusted data. Text rendered inside a scanned document is
  an injection vector — treat every OCR region as data, never as instructions, and
  keep policy in the system message.
- PII: redact names, account numbers, and identifiers from OCR text before it enters
  the prompt; retain only what the answer requires.
- Retention: crops and OCR text inherit the source document's retention policy.

### 8. Observability and Cost
- Per request: retrieval scores, rerank margins, citation validity, latency per stage,
  token counts (text and image separately), cost attribution by tenant.
- Dashboards: quality by document type, citation validity rate, abstention rate,
  crop-fetch waste rate, cost per question.
- Cache: embeddings by content hash; crop bytes by region id.

## Non-Functional Targets

| Metric | Target |
|--------|--------|
| Retrieval recall@5 | >= 0.90 |
| Answer correctness (extractive) | >= 0.85 |
| Numeric accuracy on forms | >= 0.95 |
| Citation validity | >= 0.98 |
| Citation support rate | >= 0.90 |
| Abstention rate on unanswerable | >= 0.95 |
| False decline rate | <= 0.10 |
| p95 latency | <= 8 s |
| Cost per question | <= $0.05 |

## Failure Modes and Mitigations

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| Wrong page retrieved | recall@k monitoring | Hybrid search, rerank, query rewrite |
| Wrong region within the right page | Citation support rate | Finer region granularity, bounding-box citations |
| Confident answer from low-quality scan | Image quality gate | Reject/flag below legibility threshold |
| Hallucinated chart value | Numeric recheck against extracted fields | Structured field preference, arithmetic verification |
| Adjacent crops flooding results | Duplicate-region metric | Ingest-time dedup with bbox retention |
| Text-only rerank misses visual content | Per-question-type metrics | Vision-aware reranker for visual questions |
| OCR text carries injection | Injection canary suite | Treat OCR as data, policy in system message |
| PII in prompts | PII scan on OCR text | Redact before prompt assembly |
| Crop fetch waste | Crop-fetch waste metric | Fetch only post-selection |
| Context overflow from images | Token accounting incl. images | Region caps, prefetch after selection |
| Cost spike on chart-heavy traffic | Per-document-type cost | Caching, region caps, cheaper tier for simple questions |
| Bias across scan sources | Bias audit sweep | Balanced evaluation; report per-source metrics |

## Milestones

- **M1** — ingestion with region extraction, OCR, and confidence scores.
- **M2** — dense + BM25 + RRF index; labeled question set of 300 items.
- **M3** — rerank stages with latency accounting and per-corpus switches.
- **M4** — dual-modality context assembly (crop + OCR text) with budget control.
- **M5** — VLM answering with page/region citations and citation validation.
- **M6** — numeric verification against structured fields.
- **M7** — abstention with typed reasons.
- **M8** — bias audit, PII redaction, injection canaries.
- **M9** — observability dashboards and cost attribution.
- **M10** — game day: inject a low-quality scan batch and verify graceful degradation.

## Deliverables

1. Ingestion, index, retrieval, assembly, answering, verification services.
2. `EvalHarness` with the labeled set, citation-validity metric, and abstention test.
3. `REPORT.md` — quality by document type, citation accuracy, bias audit, cost.
4. `runbook.md` — triage by symptom (wrong page, wrong region, bad OCR, refusal spike).
5. `THREAT_MODEL.md` — injection, PII, and cross-tenant leakage analysis.

## Definition of Done

- [ ] Recall@5 >= 0.90 and numeric accuracy >= 0.95 on the labeled set.
- [ ] Citation validity >= 0.98 across 1,000 sampled production answers.
- [ ] Abstention >= 0.95 on unanswerable questions with false declines <= 0.10.
- [ ] All injection canaries caught; no OCR text treated as instructions.
- [ ] Bias audit published per source and reviewed by someone outside the team.
- [ ] Rollback to the previous model/index version under 10 minutes.