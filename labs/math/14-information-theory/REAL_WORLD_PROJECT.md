# REAL_WORLD_PROJECT — Information Theory in Production: Log Compression & Alerting Budget
> Production use-case: sizing log storage by measured entropy, not guesses.

## 1. Scenario
- Service: platform ships 2 TB/day of app logs to storage.
- Constraint: storage bill must shrink; alert routing must respect channel capacity.
- Choice: zstd with per-service dictionaries; alert channel sized by entropy estimate.
- Data: `LogEvent{ts, svc, level, msg}`; daily rollups.

## 2. Architecture
```
edge → batcher → entropy estimator → zstd(dict) → storage → index
alerts → severity-bucket entropy check → route to pager|slack|ticket
```
- Entropy estimate refreshed daily; compression target set to H + 0.5 bits/byte.
- Alert channel capacity (pages/min to humans) tracked; overshoot = page flood guard.

## 3. War-Story (plausible, representative)
- Incident: a new service logged full stack traces per request; storage bill 30×'d in a week.
- Symptom: budget alert tripped; infra blamed "traffic surge".
- Root cause: nobody measured entropy of the new logs; redundancy (framework frames) was ~95%.
- Fix: template-based logging (drain) reduced payloads 40×; dictionary compression on top.
- Lesson: information you can compress is information you're over-paying for.

## 4. Metrics (before → after, 6 weeks)
| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| storage cost/day | $610 | $180 | −70% |
| avg msg entropy | 6.1 bits/byte | 1.9 bits/byte | −69% |
| pages that pages humans | 140/day | 28/day | −80% |
| indexable field coverage | 40% | 92% | +52pp |

## 5. Prevention Checklist
- [ ] Entropy estimate on every new log source before onboarding.
- [ ] Template/structured logging enforced by schema.
- [ ] Compression ratio + entropy dashboard per service.
- [ ] Alert channel capacity reviewed monthly.
- [ ] Dictionary refresh on template drift (>10% new templates).
- [ ] Regression test: stack-trace-heavy sample routes to ticket, not pager.
- [ ] Retention based on entropy-adjusted value, not age alone.
- [ ] Runbook: what to do when entropy jumps 2×.

## 6. What "Good" Looks Like
- Storage spend predictable; alerts that page humans are always actionable.

## 7. Stretch
- Graduate to streaming compression with online entropy estimation.

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)
- Shannon entropy: https://web.archive.org/web/20190214051145/https://en.wikipedia.org/wiki/Entropy_(information_theory)
- zstd: https://github.com/facebook/zstd
