# REAL_WORLD_PROJECT — Linear Search in Production: Config/Flag Scan Service
> Production use-case: per-request feature-flag/environment scan over tiny unsorted lists.

## 1. Scenario
- Gateway checks ~20 flags + 50 allowlist entries per request (unsorted, hot-updated).
- Constraint: p99 overhead <100µs; no index rebuild on flag push (seconds matter).
- Choice: linear scan with null-safe equals + first-match semantics; hash index only if list >500.
- Keys: strings, case-sensitive; null = absent (documented).

## 2. Architecture
```
request → snapshot flags (volatile ref) → linear scan → decision + audit log
```
- Copy-on-write flag snapshot (no locks on read path).
- Probe counter metric (avg probes/request) validates Θ(n) model.
- Auto-promote: size>500 flips to HashSet with alert (growth tripwire).

## 3. War-Story
- Incident: `==` on Strings caused intermittent flag misses (interned vs fresh).
- Symptom: 0.3% requests mis-routed; only fresh-push flags affected.
- Root cause: identity compare instead of `.equals`; tests used literals (interned, masked bug).
- Fix: `Objects.equals` + non-interned fixture (`new String`) + mutation test.
- Lesson: equality semantics are the scan's contract; test with adversarial strings.

## 4. Metrics (per request, n=70)
| Metric | Before (buggy) | After | Delta |
|--------|----------------|-------|-------|
| Miss rate | 0.3% | 0.0% | −100% |
| p99 overhead | 41µs | 38µs | −7% |
| Avg probes | 35 | 35 | model holds |
| Flag-push delay | 0s | 0s | kept (no index) |
| Incidents/qtr | 1 | 0 | −100% |

## 5. Prevention Checklist
- [ ] `Objects.equals` enforced (lint rule bans `==` on objects).
- [ ] Non-interned + null + duplicate fixtures.
- [ ] First-match documented + tested.
- [ ] Size tripwire (promote at 500 + alert).
- [ ] Probe-count metric vs `n/2` model.
- [ ] Snapshot isolation (no lock on hot path).
- [ ] Break-even note: when to sort+index (q* math in comments).
- [ ] Audit log on decision for replay.

## 6. What "Good" Looks Like
- Zero misses; p99 flat with flag churn; promotion never surprises.

## 7. Stretch
- Bloom prefilter when absent-heavy; SIMD scan note.

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)
- Object equality + Objects helpers: https://docs.oracle.com/javase/8/docs/api/java/util/Collections.html
- Linear search cost model: https://en.wikipedia.org/wiki/Linear_search
