# REAL_WORLD_PROJECT — Sets Deep

Production use-case: **tag/feature-flag store**: hash for de-dup, sorted for reporting, BitSet for dense ID sets. Secondary: EnumSet for permission flags.

## 1. Problem statement
Serve set operations (add/contains/remove/iterate) with SLO and correct iteration semantics per use case.

## 2. Architecture
- Ingest: admin/user commands.
- Core: pluggable set backend.
- Serve: tag API + metrics.
- Persist: snapshot / WAL.

## 3. Implementation plan (2 weeks)
W1: core + parity tests.
W2: API + metrics + JMH + runbook + deploy notes.

## 4. Metrics to report
| Metric | Target | How measured |
|---|---|---|
| p99 add latency | SLO | JMH |
| Throughput | ops/s | load gen |
| Iteration order correctness | matches spec | property tests |
| Memory | O(n) | JOL |
| Recovery | < 5 s | restart drill |

## 5. Risks & prevention
- Broken equals/hashCode → validate keys at ingress; test with tampered keys.
- TreeSet compareTo inconsistent with equals → document contract; property test vs HashSet.
- BitSet silently overgrown → bound by domain; monitor word count.

## 6. Runbook
- Alert on p99 and on iteration-order regressions.
- Rollback flag to HashSet backend.

## Field notes — sourced (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/HashSet.html
- https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/BitSet.html
Confirm API/limit numbers against the live docs before quoting them in reviews.

## 7. Deliverables
- Repo + JMH + runbook.

## 8. Grading rubric
- Correctness 30 / Perf 30 / Operability 20 / Writeup 20.
