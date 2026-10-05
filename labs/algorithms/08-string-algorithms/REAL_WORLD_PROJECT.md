# REAL_WORLD_PROJECT — String Algorithms in Production: Log Search + Dedup
> Production use-case: 2TB/day log grep (multi-pattern) + near-dedup for alerts.

## 1. Scenario
- Observability: 500 alert signatures scanned per GB; dedup similar stack traces.
- Constraint: line-rate 5GB/s aggregate; worst-case (attacker `a*` payload) must not stall.
- Choice: Aho-Corasick (multi) + KMP (single worst-case) + RK (fuzzy/hash prefilter).
- Output: hits + dedup clusters + spurious-hit stats.

## 2. Architecture
```
stream → normalize (codePoints) → AC scan → KMP confirm → RK-cluster dedup
```
- `char`→codePoint normalization (emoji-safe); empty-pattern policy documented.
- RK verify-on-hit (no hash-only verdicts); dual-mod for low FP.
- Overlap fixture (`aaa…b`) in perf gate (naive would be 100× slower).

## 3. War-Story
- Incident: naive `indexOf` loop on `aⁿb` attacker pattern → 1 shard 100% CPU, 20min lag.
- Symptom: alerts delayed; CPU correlated with pattern length, not traffic.
- Root cause: quadratic worst on overlaps; no worst-case matcher in path.
- Fix: KMP for singles + AC for multis + overlap perf fixture (must-pass).
- Lesson: matcher choice is a security decision (ReDoS-style blowup).

## 4. Metrics (per GB, 500 patterns)
| Metric | Before (naive) | After | Delta |
|--------|----------------|-------|-------|
| p99 scan | 14s | 0.9s | −94% |
| Overlap payload | 20min lag | 1.1s | −99.9% |
| CPU/shard | 100% | 34% | −66% |
| False dedup | 1.2% | 0.05% | verify fix |
| Emoji misses | 3/wk | 0 | codePoint fix |

## 5. Prevention Checklist
- [ ] Overlap perf fixture (attacker pattern).
- [ ] π-table golden test (`ababaca`).
- [ ] Verify-on-hit (no hash-only).
- [ ] Empty-pattern + unicode fixtures.
- [ ] Multi-pattern via AC (not 500× single).
- [ ] Spurious-hit metric + alert.
- [ ] Normalization documented (case/unicode).
- [ ] Rate-limit + isolate worst-case shard.

## 6. What "Good" Looks Like
- Sub-second GB scans; zero blowup payloads; dedup explainable.

## 7. Stretch
- Suffix-automaton for substring analytics; WAF signature pipeline.

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)
- String search primitives in Java: https://docs.oracle.com/javase/8/docs/api/java/util/Collections.html
- KMP failure-link linear bound: https://en.wikipedia.org/wiki/Knuth%E2%80%93Morris%E2%80%93Pratt_algorithm
