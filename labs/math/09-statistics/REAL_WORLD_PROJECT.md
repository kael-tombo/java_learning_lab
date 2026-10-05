# REAL_WORLD_PROJECT — Statistics in Production: Experimentation Platform Readouts
> Production use-case: deciding a rollout from A/B data without p-hacking.

## 1. Scenario
- Service: product experimentation platform computes readouts for feature flags.
- Constraint: peeking inflates false positives; results must be reproducible.
- Choice: fixed-horizon tests with pre-registered α, plus CUPED-style variance reduction.
- Data: `Assignment{userId, arm}, Metric{value}`.

## 2. Architecture
```
assignment log → metric pipeline → readout (CI + p + effect) → gate → rollout flag
```
- Readout locks at the planned sample size; extra looks use sequential correction.
- Every readout stores the analysis config hash for reproducibility.

## 3. War-Story (plausible, representative)
- Incident: a "winning" button color shipped after week 1; engagement fell 3% over the next month.
- Symptom: post-launch dashboards showed the lift evaporating.
- Root cause: early peek when variance was high; no sequential correction; metric not pre-registered.
- Fix: fixed horizon enforced by the platform; sequential p-values for peeks; pre-registration form.
- Lesson: statistics that can't be reproduced by the platform isn't statistics — it's storytelling.

## 4. Metrics (before → after, two quarters)
| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| false-positive rollouts | 3 | 0 | −100% |
| time to decision | 14 days (peeking) | 7 days (fixed) | −50% |
| readouts reproducible | 20% | 100% | +80pp |
| variance reduction (CUPED) | none | ~30% smaller CIs | new |

## 5. Prevention Checklist
- [ ] Horizon + α + metrics fixed before the experiment starts.
- [ ] Sequential correction on any early look.
- [ ] Effect size reported with CI, not just p.
- [ ] Randomization sanity checks (arm sizes, covariate balance).
- [ ] Readout config hashed and stored.
- [ ] No metric peeking in dashboards pre-horizon (or marked exploratory).
- [ ] Post-launch metric tracked for 2 weeks.
- [ ] Dashboard: lift, CI width, time-to-decision, peek count.

## 6. What "Good" Looks Like
- Product trusts readouts: decisions ship on schedule, no reversals from false positives.

## 7. Stretch
- Graduate to Bayesian A/B with decision rules (see probability-deep/08-bayesian-statistics).

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)
- A/B testing: https://en.wikipedia.org/wiki/A/B_testing
- P-value: https://en.wikipedia.org/wiki/P-value
