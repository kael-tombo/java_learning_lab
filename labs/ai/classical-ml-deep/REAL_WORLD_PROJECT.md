# classical-ml-deep — Real-World Project

## Project: Credit Risk Scoring Platform with Governance

Build a production credit risk scoring platform: a decisioning service over a tabular
lending dataset, an interpretable challenger model beside a gradient boosting champion, a
monitoring system that catches drift and fairness regressions, and the governance
artifacts a regulated lender has to produce.

## Context

Lending decisions are made by a model, enforced in code, reviewed by a regulator, and
challenged by applicants. That combination makes classical ML unusually consequential:
accuracy is necessary and nowhere near sufficient. This project builds the whole system,
not just the model.

## Sourced field notes (fetched Oct 2026 — verify before citing)

- "A Unified Approach to Interpreting Model Predictions" (Lundberg & Lee, submitted
  25 Jun 2017; v2 1 Nov 2017) — https://arxiv.org/abs/1705.07874 — takeaway for this
  lab: local attribution with a signed local accuracy guarantee is what makes a
  gradient-boosting champion reviewable; the SHAP fast-interventional algorithm here is
  the explainability layer the governance package depends on, and the "explainability
  must be local, not a global list" discipline is why the adverse-action reason codes are
  per-decision rather than per-model.
- "Trustworthy Machine Learning" — https://huggingface.co/learn — takeaway for this
  lab: the practical production framing that a model card is a delivery artifact with
  stated scope, evaluation slices, and known limitations, and that dataset documentation
  and shift monitoring are part of the model, not documentation about the model. This is
  the checklist the release gate here enforces before any scoring model is promoted.

## System Architecture

```
   applicant           scoring service                  decisioning
   --------           ---------------                  -----------
   application  -->  feature store  -->  champion (GBM)   -->  decision
                          |                    |                  |
                          |               challenger (GBM+monotone)  |
                          |                    |                  |
                          |               SHAP explainer         |
                          |                    |                  |
                          |              adverse-action codes    |
                          v                    v                  v
                    monitoring           governance pack     decision log
                    (drift, PSI,        (model card,         (immutable,
                     slice metrics,      validation report,   reason codes)
                     fairness)           approval trail)
```

## Component Specs

### 1. Data and Feature Platform
- Typed schema with a data contract; the build fails on a schema violation.
- Point-in-time correct feature construction: every feature carries an `as_of` timestamp,
  and the join rejects any row whose feature timestamp is after the application time.
  **This is the single highest-value control in the whole system** — a temporal join bug
  produces a model that scores beautifully in backtest and fails on day one.
- Missingness as signal, but with an indicator column so the model can distinguish
  "missing" from "zero".
- Monotone constraints declared in configuration and **enforced in code**, not requested
  from the trainer: income up cannot decrease approval score.
- Training/serving feature computation shares one implementation. A reimplemented
  feature pipeline in serving is a guaranteed skew incident.

### 2. Champion and Challenger
- Champion: gradient boosting with histogram split finding, second-order leaf values,
  L2 leaf penalty, early stopping on a time-based validation split.
- Challenger: gradient boosting with monotone constraints, tuned for a different
  objective (recall at a fixed approval rate rather than raw AUC).
- A **baseline ladder** gates everything: mean-prediction, logistic regression, shallow
  decision tree, random forest, gradient boosting. If the champion does not beat the
  logistic baseline by a meaningful margin on the decision metric, the champion is not
  justified and its complexity is rejected.
- Model selection on a **time-based** split, never random: random splits leak the future
  into the past for any data with trend.

### 3. Calibration
- Isotonic calibration on a held-out slice; probability calibration is a separate gate
  from discrimination.
- Reliability diagram and expected calibration error as release metrics.
- Rationale: a lender's adverse-action pricing needs probabilities, and a boosting model
  trained for AUC is not calibrated out of the box.

### 4. Thresholding and the Operating Point
- The threshold is a **business** decision expressed in expected cost: expected loss
  = `P(default) * LGD * exposure` versus operating cost, plus a capital charge.
- Threshold tuned on the PR curve, not on accuracy. Report the confusion matrix at the
  shipping threshold: approvals, denials, false approvals, false denials, in money.
- Two-sided thresholds when regulation requires (e.g. a rate above a statutory ceiling
  triggers a manual review queue rather than an automatic approval).

### 5. Explainability and Adverse Action
- SHAP-style local attribution per decision, signed and bounded, with the local accuracy
  guarantee checked on a sample.
- Top-`k` contributors become **adverse-action reason codes** in a form the applicant can
  read. Code stability across versions matters: an applicant denied last year and denied
  today should see comparable reasons.
- Explanations computed from the deployed artifact, in the same request path, so the
  reason codes cannot drift from the decision.
- Global surrogate tree for a human-readable summary; agreement with local attributions
  measured, not assumed.

### 6. Monitoring
- **Population stability index** on input features and on the score:

```
PSI = sum_i (p_i - q_i) * ln(p_i / q_i)
```

  PSI below 0.1 stable, 0.1-0.25 moderate shift, above 0.25 material. Bins fixed at
  training time, so the comparison is against a frozen reference.
- Score distribution monitoring against a training baseline, by month.
- Calibration drift: rolling expected calibration error, because the score distribution
  can look stable while the calibration collapses.
- Slice metrics by every protected and business-relevant group, computed on every refresh,
  with thresholds and alerts.
- **Champion-challenger shadow scoring**: the challenger runs on all traffic, decisions
  unaffected, disagreement rate tracked. This is the cheapest early-warning system
  available and it costs only inference.

### 7. Fairness and Compliance Controls
- Demographic parity and equalized odds computed per release and per month, per slice.
- Slice metrics gated: a group whose performance drops beyond the documented delta
  blocks promotion.
- Reason codes mandatory on every adverse action; a decision without codes cannot be
  written to the decision log.
- Retention of decision inputs, outputs, reasons, and model version for the applicable
  retention period; deletion requests honoured end to end including derived features.
- Adverse-action notice content is a template fed by the reason codes, reviewed by legal,
  and versioned.

### 8. Governance Pack
- **Model card**: intended use, out-of-scope uses, training data description, metrics
  overall and per slice, calibration, known limitations, and a named owner.
- **Validation report**: independent review of methodology, challenger results,
  robustness tests (missing features, extreme values, distribution shift simulation).
- **Approval trail**: who approved, when, on what evidence, with the diff of the model
  card.
- Release gate: discrimination metric within delta, calibration within bound, no slice
  regression, fairness metrics within threshold, explanation availability verified, and
  monitoring instrumentation present. Missing telemetry blocks.
- Model inventory with a deprecation ladder and a retraining cadence.

### 9. Serving and Drift Response
- Decision log records the model version, feature values, score, threshold, decision,
  reason codes, and latency. The log is the training set three months from now.
- Drift response ladder: investigate the data pipeline first, then the population, then
  the model, then retrain. Retraining is the **last** step, because most drift is a
  pipeline bug and retraining bakes it in.
- Champion retrained on a rolling window with a shadow period against the incumbent, and
  promoted only through the gate.

## Non-Functional Targets

| Metric | Target |
|--------|--------|
| Decision latency p99 | < 80 ms, in-process scoring |
| Scoring throughput | 2,000 decisions/second sustained |
| Discrimination (ROC-AUC) | >= 0.78 on the time-based validation split |
| PR-AUC at the operating point | Reported; PR-AUC, not accuracy |
| Expected calibration error | <= 0.03 |
| PSI, any feature | < 0.10 green; > 0.25 pages |
| Slice performance delta | <= 2 points for any monitored group |
| Fairness metric delta | Within the documented threshold per release |
| Adverse-action reason coverage | 100% of adverse decisions |
| Explanation availability | 100% of decisions, same request path |
| Champion/challenger disagreement | Tracked, alerted above a threshold |
| Decision log completeness | 100%; missing fields block the write |
| Model card freshness | Reviewed every 6 months |

## Failure Modes and Mitigations

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| Temporal join leak | Backtest suspiciously high; point-in-time test | `as_of` timestamp enforced in the feature store |
| Train/serve skew | Shadow comparison of feature values | One shared feature implementation |
| Random split on trending data | Time-based validation scores far below live | Always split on time |
| Threshold tuned on accuracy | PR-AUC collapses at the operating point | Expected-cost threshold on the PR curve |
| Uncalibrated probabilities | Reliability diagram bends off the diagonal | Isotonic calibration as a release gate |
| Probability drift | Rolling ECE rises while PSI stays green | Monitor calibration independently |
| Population drift | PSI above 0.25 | Investigate pipeline before retraining |
| Slice regression | Per-slice metric delta alert | Release gate blocks promotion |
| Missing adverse-action codes | Log completeness check | Decision cannot be written without codes |
| Explanation drifts from decision | Code-stability test across versions | Compute explanations in the same request path |
| Monotone constraint violated | Constraint assertion in the serving path | Enforce in code, not in the trainer |
| Champion overfits the validation window | Rolling-window retrain degrades live score | Time-based split plus shadow period |
| Retraining bakes in a pipeline bug | Feature-level PSI after retrain | Drift response ladder puts the pipeline first |
| Missing monitoring telemetry | Instrumentation check in CI | Missing telemetry blocks the release |
| Category encoding leaks target | CV score far above holdout | Ordered statistics from train rows only |

## Milestones

- **M1** — data contract, point-in-time-correct feature store, temporal split.
- **M2** — logistic baseline with calibration; the reference every model must beat.
- **M3** — gradient boosting champion with early stopping and a tuned threshold.
- **M4** — calibration gate with reliability diagram and ECE.
- **M5** — challenger with monotone constraints, shadow scoring live.
- **M6** — SHAP explainer with a local-accuracy check; reason-code mapping.
- **M7** — decision log with completeness enforcement.
- **M8** — PSI and score-distribution monitoring with alerting.
- **M9** — slice metrics and fairness gates per release.
- **M10** — governance pack: model card, validation report, approval trail.
- **M11** — rolling retrain with a shadow period and promotion gate.
- **M12** — drift response runbook exercised with a simulated incident.

## Deliverables

1. Scoring service with champion and challenger, calibrated and thresholded.
2. Feature store with point-in-time correctness and a shared train/serve implementation.
3. Explanation and adverse-action code pipeline.
4. Monitoring: PSI, score distribution, calibration drift, slice metrics, challenger
   disagreement.
5. Governance pack: model card, validation report, approval trail, deprecation ladder.
6. `REPORT.md` — the platform posture: decision metrics overall and per slice, calibration
   quality, threshold economics in money, explanation coverage, drift sensitivity, and
   residual risks accepted with reasons.

## Definition of Done

- [ ] Point-in-time correctness test fails when a feature timestamp is after the
      application time.
- [ ] Train and serving feature values match exactly for 10,000 sampled requests.
- [ ] Champion beats the logistic baseline on the decision metric by a stated margin.
- [ ] Time-based validation only; no random split anywhere in the pipeline.
- [ ] ECE at or below 0.03 with a reliability diagram in the report.
- [ ] Threshold chosen by expected cost; confusion matrix reported in money.
- [ ] Every adverse decision carries reason codes, verified over 10,000 decisions.
- [ ] Explanation computed in the serving path and stable across model versions.
- [ ] PSI alert fires on a simulated 15% distribution shift.
- [ ] A slice regression blocks promotion, verified by a deliberate regression.
- [ ] Challenger disagreement tracked continuously with a threshold.
- [ ] Model card, validation report, and approval trail complete and versioned.
