# REAL_WORLD_PROJECT — MinHash & SimHash (28)

Production use-case: **near-duplicate suppression in a crawl/ingest pipeline** (web pages or support tickets). Secondary: candidate-pair generation for a recommender.

## 1. Problem statement
Detect near-duplicates over millions of docs with bounded memory and tunable recall/precision. SLOs: p99 per-doc signing latency, pair-candidate recall ≥ target, memory per doc.

## 2. Architecture
- Ingest: crawler/consumer emitting documents.
- Core: shingler → signer (MinHash or SimHash) → LSH/hamming index.
- Serve: candidate API + metrics + health.
- Persist: signature table + banding metadata.

## 3. Implementation plan (2 weeks)
W1: shingler + MinHash signer + banding index + unit tests.
W2: SimHash variant + recall curve + JMH bench + deploy notes.

## 4. Metrics to report
| Metric | Target | How measured |
|---|---|---|
| p99 signing latency | < 2 ms | JMH |
| Candidate recall | ≥ 95% | seeded duplicates |
| Candidate precision | ≥ 90% | manual sample |
| Throughput | docs/s | load generator |
| Memory/doc | ≤ 256 B | JOL |
| Index rebuild | < 30 s | restart drill |

## 5. Risks & prevention
- Recall collapse on tiny docs → enforce min shingle count.
- Banding false negatives → tune (b,r); sweep parameters offline.
- Hash seed drift → pin seed config; version signatures.
- Duplicate flood DoSing review queues → cap candidates per doc.

## 6. Runbook
- Alerts on recall drop below target and p99 > 2 ms.
- Rollback: exact hash dedup for small corpus; re-sign on seed change.

## Field notes — sourced (fetched Oct 2026 — verify before citing)
- https://en.wikipedia.org/wiki/MinHash
- https://en.wikipedia.org/wiki/SimHash
Confirm API/limit numbers against the live docs before quoting them in reviews.

## 7. Deliverables
- Repo with tests + JMH bench + recall curve.
- One-page ops runbook: SLOs, alerts, rollback.

## 8. Grading rubric
- Correctness 30 / Perf vs SLO 30 / Operability 20 / Writeup 20.
