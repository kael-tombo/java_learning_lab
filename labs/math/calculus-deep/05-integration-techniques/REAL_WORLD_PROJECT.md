# REAL_WORLD_PROJECT — Integration Techniques in Production: Signal Area Reports
> Production use-case: choosing the right integration path per channel.

## 1. Scenario
- Service: audio analytics reports area-under-spectrum per band.
- Constraint: exact for known shapes (exponential decays), numeric for unknown.
- Choice: pattern-match to a decaying exponential → closed form; else Simpson.
- Data: `Spectrum{band, samples[]}`.

## 2. Architecture
```
spectrum → pattern match → closed-form or Simpson → report → CI on the area
```

## 3. War-Story (plausible, representative)
- Incident: a known exponential was integrated numerically; error drifted with n.
- Root cause: Simpson with too-small n on a steep decay.
- Fix: exponential pattern match → closed form; numeric fallback flagged.
- Lesson: a known shape deserves a known answer.

## 4. Metrics
| Metric | Before | After |
|--------|--------|-------|
| area error on decay channels | 2% | 0.01% |
| report latency | 40ms | 42ms |

## 5. Prevention Checklist
- [ ] Pattern match before numeric integration.
- [ ] Error table logged for numeric fallbacks.
- [ ] Golden fixtures: pure decay, flat, noisy.

## 6. What "Good" Looks Like
- Reports cite method used and error bound.

## 7. Stretch
- Adaptive quadrature on the numeric path.

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)
- Integration by parts: https://en.wikipedia.org/wiki/Integration_by_parts
- Simpson's rule: https://en.wikipedia.org/wiki/Simpson%27s_rule
