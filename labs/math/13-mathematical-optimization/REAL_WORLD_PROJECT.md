# REAL_WORLD_PROJECT — Optimization in Production: Recommendation Model Trainer
> Production use-case: training a ranking model nightly on click data.

## 1. Scenario
- Service: nightly training job minimizes a pairwise ranking loss over 10M pairs.
- Constraint: must finish the window; divergence or NaN fails the train.
- Choice: Adam with gradient clipping, LR warmup + decay, early stop on val loss.
- Data: `Pair{user, itemA, itemB, label}`.

## 2. Architecture
```
data lake → sampler → trainer (Adam+clip) → eval → gate (val metric) → model registry
```
- Checkpoints every 500 steps; resume on failure.
- NaN in loss → abort, alert, keep last good checkpoint.

## 3. War-Story (plausible, representative)
- Incident: after switching to a new dataset, training diverged to NaN on step 3.
- Symptom: nightly train job failed; no model shipped (safe) but pipeline alert fatigue grew.
- Root cause: LR schedule unchanged while dataset scale 100×'d; gradients exploded.
- Fix: warmup + clipping added; LR auto-scaled by batch size; divergence guard in the loop.
- Lesson: optimizer hyperparameters are dataset properties — retune on every data shift.

## 4. Metrics (before → after, quarterly)
| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| divergence failures/mo | 6 | 0 | −100% |
| median train time | 3.2h | 2.1h | −34% |
| val AUC (policy metric) | 0.731 | 0.748 | +1.7pp |
| rollback to previous model | 4 | 1 | −75% |

## 5. Prevention Checklist
- [ ] LR scaled with batch size; warmup mandatory.
- [ ] Gradient clipping value logged per step.
- [ ] NaN/Inf loss aborts training, keeps last good ckpt.
- [ ] Early stopping on val loss with patience.
- [ ] Data-shift detector before train (row count, label rate).
- [ ] New-dataset run re-tunes LR on a small sweep first.
- [ ] Model registry: eval metrics stamped with every artifact.
- [ ] Dashboard: loss curve, LR, grad norm, val AUC, train time.

## 6. What "Good" Looks Like
- Nightly train either ships a validated model or pages with a crisp reason.

## 7. Stretch
- Graduate to L-BFGS for small convex objectives and per-feature second-order methods.

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)
- Gradient descent: https://en.wikipedia.org/wiki/Gradient_descent
- Adam (Kingma & Ba): https://arxiv.org/abs/1412.6980
