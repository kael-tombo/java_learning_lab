# REAL_WORLD_PROJECT — Treaps (33)

Production use-case: **ephemeral key-value range store** behind a game-server leaderboard or social feed. Secondary: persistent treap for undo stacks.

## 1. Problem statement
Randomized ordered map serving add/erase/range with expected O(log n) under adversarial arrival orders. SLOs: p99 op latency, throughput, memory.

## 2. Architecture
- Ingest: mutation commands.
- Core: treap behind a narrow interface.
- Serve: query API + metrics + health.
- Persist: in-memory snapshot/WAL of keys.

## 3. Implementation plan (2 weeks)
W1: core + invariants + property tests vs TreeMap model.
W2: API + metrics + JMH + deploy notes.

## 4. Metrics to report
| Metric | Target | How measured |
|---|---|---|
| p99 op latency | SLO-driven | JMH |
| Throughput | ops/s | load gen |
| Memory | O(n) keys | JOL |
| Height distribution | ~ 2 ln n | histogram |
| Correctness | matches model | property tests |

## 5. Risks & prevention
- Weak/duplicate priorities → use full 64-bit Random + uniqueness tiebreak.
- Rotation bugs → property tests comparing to TreeMap on randomized sequences.
- Adversarial key patterns are fine (randomized), but watch integer overflow in priorities — see prevention above.

## 6. Runbook
- Alert on latency regressions; fallback to TreeMap flag.
- Rollback: swap implementation behind the same interface.

## Field notes — sourced (fetched Oct 2026 — verify before citing)
- https://en.wikipedia.org/wiki/Treap
- https://web.stanford.edu/class/cs166/
Confirm API/limit numbers against the live docs before quoting them in reviews.

## 7. Deliverables
- Repo with tests + JMH bench + dashboard screenshot.
- One-page ops runbook: SLOs, alerts, rollback.

## 8. Grading rubric
- Correctness 30 / Perf vs SLO 30 / Operability 20 / Writeup 20.
