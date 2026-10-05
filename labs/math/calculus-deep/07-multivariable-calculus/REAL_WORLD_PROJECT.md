# REAL_WORLD_PROJECT — Multivariable Calculus in Production: Feature Sensitivity Report
> Production use-case: explaining model outputs via gradient sensitivity.

## 1. Scenario
- Service: fintech model scores loan applicants; audit needs "what moves the score?".
- Constraint: per-decision explanation must be local (at the applicant's point).
- Choice: gradient of the model score wrt features; report top-3 movers.
- Data: `Applicant{income, debtRatio, age, history}`, score s(x).

## 2. Architecture
```
applicant → model → score → local gradient → top-3 movers → explanation card
```

## 3. War-Story (plausible, representative)
- Incident: applicants with a thin "history" flipped between accept/reject weekly.
- Root cause: the gradient wrt history was huge near the decision boundary; tiny data errors moved the outcome.
- Fix: boundary-width flag on the explanation card; human review within that band.
- Lesson: a gradient is local — its size tells you how fragile the local decision is.

## 4. Metrics
| Metric | Before | After |
|--------|--------|-------|
| decision-flip complaints/mo | 12 | 2 |
| median explanation time | 3 days | 0.5 day |

## 5. Prevention Checklist
- [ ] Gradient magnitude threshold before trusting an explanation.
- [ ] Boundary-width flag on the card.
- [ ] Golden applicants with known expected movers.
- [ ] Model version stamped on every explanation.

## 6. What "Good" Looks Like
- Every adverse action notice carries a defensible local explanation.

## 7. Stretch
- Replace gradients with SHAP for a global view.

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)
- Gradient: https://en.wikipedia.org/wiki/Gradient
- Directional derivative: https://en.wikipedia.org/wiki/Directional_derivative
