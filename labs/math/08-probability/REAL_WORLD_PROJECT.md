# REAL_WORLD_PROJECT — Probability in Production: Fraud Scoring Service
> Production use-case: scoring transactions with base-rate-aware risk.

## 1. Scenario
- Service: payment gateway assigns each txn a fraud-risk score.
- Constraint: alerts must respect base rates; a 99%-accurate test still floods ops if base rate is 0.1%.
- Choice: logistic-ish scoring with explicit prior; threshold set from cost model.
- Data: `Txn{amount, age, device, geo}`; label from chargebacks.

## 2. Architecture
```
txn → features → score → threshold (cost-tuned) → allow/challenge/block → feedback loop
```
- Score calibrated with observed vs predicted rates on a dashboard.
- Every challenge records the score that triggered it.

## 3. War-Story (plausible, representative)
- Incident: marketing launched, txn volume 10×'d, but fraud rate barely moved; alerts exploded 8×.
- Symptom: ops manually reviewed 300 txns/day, 99% legitimate.
- Root cause: threshold tuned on old volume; posterior shifted with the new prior.
- Fix: threshold recomputed from refreshed base rate; precision/recall report added.
- Lesson: a probability model drifts when the world's base rate moves — recalibrate.

## 4. Metrics (before → after, 60-day window)
| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| review queue size | 300/day | 45/day | −85% |
| precision of alerts | 1% | 12% | +1100% |
| chargeback rate | 0.08% | 0.07% | stable |
| calibration error | 0.09 | 0.02 | −78% |

## 5. Prevention Checklist
- [ ] Recalibrate when volume or mix shifts >20%.
- [ ] Threshold derived from explicit cost model, not vibes.
- [ ] Precision@k reported alongside recall.
- [ ] Champion/challenger scores behind a flag.
- [ ] Alert log includes score + threshold + prior snapshot.
- [ ] Weekly calibration plot reviewed by a human.
- [ ] Keep a simple base-rate calculator in the runbook.
- [ ] Dashboard: alert volume, precision, base rate, drift alarms.

## 6. What "Good" Looks Like
- Ops reviews <50/day with >10% precision and no rise in chargebacks.

## 7. Stretch
- Graduate to full Bayesian hierarchical model (see 08-bayesian-statistics in probability-deep).

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)
- Bayes' theorem: https://en.wikipedia.org/wiki/Bayes%27_theorem
- Base rate fallacy: https://en.wikipedia.org/wiki/Base_rate_fallacy
