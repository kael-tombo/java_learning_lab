# MINI_PROJECT — Drift and Quality Monitoring with a Retrain Trigger

**Track:** mlops  |  **Lab:** lab08  |  **Level:** Advanced

> Companion notes to the runnable lab. Everything here is grounded in the source under `src/`, so a claim you cannot reproduce is a claim you do not ship.

| Doc | Read it when you want |
|---|---|
| `THEORY.md` | the mental model and the assumptions |
| `MATH_FOUNDATION.md` | the formulas, the derivations, the numerical traps |
| `CODE_DEEP_DIVE.md` | the Java implementation, line by line |
| `EXERCISES.md` | deliberate practice, one deliverable at a time |
| `QUIZ.md` | to find the gaps before an interview |
| `FLASHCARDS.md` | spaced repetition on the day before a review |
| `VISION.md` | the career-level context and the anti-patterns to avoid |
| `MINI_PROJECT.md` | a self-contained build you finish in one sitting |
| `REAL_WORLD_PROJECT.md` | the production system, on-call runbook included |

**Brief.** Monitor a served model for drift and delayed-label quality, alert on sustained trends, and trigger a retrain on evidence.

**Timebox.** 3–4 hours

## 1. Why This Project Exists

This is the half of MLOps that runs after deployment, and the one that finds problems before the business review does.

## 2. Requirements

- PSI, KL and JS on identically bucketed windows, with correctness tests (JS symmetric, bounded by ln 2).
- Threshold vs slope alerting compared on data with weekly seasonality; choose a slope threshold from your own history.
- Prediction log with a join key; evaluate quality with a simulated 30-day label lag.
- Report label maturity fraction beside every quality number.
- Per-segment drift showing a global-healthy, segment-broken case.
- Retrain trigger requiring drift plus matured quality drop plus a minimum interval.
- Runbook with severity, owner, first action; drill each alert and measure response time.

## 3. Build Order

| Step | Time | What you do | Done when |
|---|---|---|---|
| 1 | 30m | Divergence suite on fixed buckets with tests | A tested divergence implementation |
| 2 | 35m | Seasonal PSI series; threshold vs slope alerting | A comparison with a chosen slope |
| 3 | 35m | Prediction log plus delayed-label evaluation | An honest quality report with maturity |
| 4 | 30m | Per-segment drift; the hidden-break case | A segmented report |
| 5 | 30m | Retrain trigger with three conditions | Explained fire/no-fire decisions |
| 6 | 25m | Servicing metrics alongside quality | One triage dashboard |
| 7 | 30m | Alert runbook drilled end to end | Measured detection and mitigation times |

## 4. Architecture Sketch

```text
 reference window (stored with model version)
     |
 bucketing (edges computed once)
     |
 current window from prediction log --> PSI / KL / JS
     |                                     |
 slope over window                        per-segment
     |                                     |
 sustained-slope alert <-------------------+
     |
 prediction log --(join key)--> outcomes (label lag)
     |
 quality with maturity fraction
     |
 retrain trigger: drift AND quality drop AND interval
     |
 runbook: severity, owner, first action, drill
```

## 5. Implementation Notes

- Generate the seasonality yourself; without it you cannot see the false-positive problem.
- Never count an unmatured prediction as wrong; it will corrupt every recent window.
- The trigger must be explainable: log the inputs behind every fire/no-fire decision.
- Drill one alert end to end; a runbook that has never been followed is fiction.

## 6. Deliverables

1. Divergence suite with correctness tests.
1. Threshold-versus-slope alerting comparison with a chosen slope.
1. Delayed-label quality report with maturity fractions.
1. Retrain trigger with explained decisions plus a drilled runbook.

## 7. Grading Rubric

| Dimension | Weight | What earns full marks |
|---|---|---|
| Correctness | 25% | Divergences correct; fixed buckets; maturity handled |
| Alert quality | 25% | Seasonal false positives eliminated; thresholds from own data |
| Granularity | 15% | Per-segment monitoring catching a hidden break |
| Decision logic | 20% | Trigger requires all three conditions and explains itself |
| Operations | 15% | Runbook drilled with measured response times |

## 8. Stretch Goals

- Add a seasonal reference window per feature.
- Implement per-model learned thresholds from historical excursions.
- Wire the trigger to the pipeline orchestrator and observe one real retrain cycle.

## 9. Definition of Done

You are finished when every box below is checked, not when the code compiles.

- [ ] PSI, KL and JS on identically bucketed windows, with correctness tests (JS symmetric, bounded by ln 2).
- [ ] Threshold vs slope alerting compared on data with weekly seasonality; choose a slope threshold from your own history.
- [ ] Prediction log with a join key; evaluate quality with a simulated 30-day label lag.
- [ ] Report label maturity fraction beside every quality number.
- [ ] Per-segment drift showing a global-healthy, segment-broken case.
- [ ] Retrain trigger requiring drift plus matured quality drop plus a minimum interval.
- [ ] A stranger can reproduce the reported numbers with one command
- [ ] The limitations section says what this cannot do
- [ ] At least one number is alerted on in production

## 10. Retrospective Template

- What worked:
- What surprised me:
- The one number I would alert on in production:
- What I would delete before shipping this to real users:
