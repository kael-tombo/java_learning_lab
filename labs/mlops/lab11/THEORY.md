# Model Governance & Compliance

**Track:** mlops  |  **Lab:** lab11  |  **Level:** Advanced

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

## 1. The Problem This Solves

In a regulated decision, 'the model was accurate' is not an answer. You need to show who approved what, on which data, with which measured harm across groups.

Governance is becoming an engineering discipline rather than a spreadsheet exercise: model cards, fairness metrics and audit trails are buildable artefacts with testable properties.

## 2. Learning Objectives

- Write a model card with intended use, data, metrics and limitations
- Compute and interpret core fairness metrics on real data
- Design an immutable audit trail covering every lifecycle transition
- Map a compliance obligation to an artefact and a test
- Distinguish fairness metrics that trade off from those that do not
- Build a governance workflow that produces evidence rather than promises

## 3. Core Concepts

### 3.1 Fairness metrics are in tension

Statistical parity (equal selection rates) and equal opportunity (equal true positive rates) cannot both hold when base rates differ. Choosing which to prioritise is a policy decision that must be written down, not a modelling accident.

### 3.2 Base rates drive everything

Two groups with different fraud rates will have different false positive rates under any threshold that treats them identically. This is why fairness analysis must always report base rates alongside the fairness metrics, or the numbers are uninterpretable.

### 3.3 Model cards are interfaces

A model card is not documentation; it is the contract between the model and the people affected by it. Intended use, out-of-scope use, known limitations and the metrics that were actually measured are what let someone downstream decide whether to use the model at all.

### 3.4 Audit trails must be immutable and complete

The trail has to answer: who promoted what, when, on which evidence, and under which version of the policy. If the policy can change silently, the trail is meaningless. Policy versions belong in the record.

### 3.5 Obligations map to artefacts and tests

A compliance requirement is satisfied by an artefact plus a test that proves it. 'We have a fairness policy' is not evidence; 'the promotion gate fails when group disparity exceeds 0.05, and a test proves it' is.

### 3.6 Documentation decays silently

Model cards go stale as features and thresholds change. Generating the measurable parts of the card from the pipeline, so it cannot drift from reality, is the only version that stays true.

## 4. Key Equations at a Glance

| Symbol | Name | Meaning |
|---|---|---|
| `selection_rate = TP + FP over group` | Statistical parity | P(yhat=1 | group) |
| `TPR_g = TP_g / (TP_g + FN_g)` | Equal opportunity | equal true positive rates |
| `FPR_g = FP_g / (FP_g + TN_g)` | False positive disparity | the metric that moves with base rates |
| `demographic_parity_gap = max_g rate - min_g rate` | Disparate impact | the quantity a regulator measures |
| `disparate_impact_ratio = min_g rate / max_g rate` | Four-fifths style ratio | below 0.8 flags review |
| `audit_record = (actor, action, from, to, policy_version, evidence_hash)` | Audit entry | immutable and complete |

## 5. How the Pieces Fit Together

1. Register the model with intended use, out-of-scope use, and the decision it informs.

2. Record the data: sources, time window, population, known gaps.

3. Evaluate metrics overall and per group, reporting base rates alongside fairness metrics.

4. Write the limitations explicitly, including who the model is likely to harm.

5. Run the promotion gate: fairness thresholds plus lineage plus required sign-offs.

6. Store the model card, the audit entries and the evidence hash together.

## 6. Assumptions and Invariants

- Protected attributes are available for evaluation even if they are excluded from training
- Group definitions are documented and reviewed rather than chosen per analysis
- Fairness thresholds are set as policy and enforced by the gate
- Policy versions are recorded in every audit entry
- Model card metrics are generated from the pipeline rather than typed
- Limitations are written for a non-technical reader

## 7. Failure Modes You Will Meet in Production

| Symptom | Root cause | Fix |
|---|---|---|
| Fairness analysis omits base rates | uninterpretable disparity numbers | always report base rate per group first |
| A metric improved for one group and worsened for another | unexamined trade-off | publish the full group matrix and get the policy choice in writing |
| Model card is accurate at launch and wrong after two releases | hand-written documentation | generate measurable fields from the pipeline |
| Audit log exists but records no policy version | policy changed silently | record the policy version in every entry |
| Disparate impact threshold ignored because 'the model is accurate' | accuracy as an argument against fairness | accuracy and fairness are separate gates; both must pass |
| Protected attribute used as a training feature | legal exposure and worse fairness | exclude from training, include in evaluation only, with justification recorded |

## 8. Java Building Blocks

| API / class | Why it earns its place here |
|---|---|
| `record ModelCard(String name, String version, IntendedUse, Data, Metrics, Limitations)` | the generated contract |
| `Map<String, GroupStats> for per-group evaluation` | base rate plus every metric per group |
| `Append-only audit log with a hash chain` | tamper evidence for the compliance export |
| `record PolicyVersion(String id, Instant effectiveFrom, Map<String,Double> thresholds)` | the version recorded in every audit entry |
| `BigDecimal for disparity ratios` | ratios at four-fifths granularity need exact reporting |

## 9. Where This Sits in the Larger System

- **mlops/lab03** provides the promotion gate that governance extends.
- **mlops/lab10** provides the live evidence that a rollout did not cause harm.
- **mlops/lab02** provides the run records that audit entries reference.
- **mlops/lab08** provides ongoing fairness and quality monitoring after launch.

## 10. Self-Assessment Before You Ship Anything

Score yourself 0-2 on each. Any zero below means you are not ready to operate this in production.

- [ ] 0 — cannot yet — Write a model card with intended use, data, metrics and limitations
- [ ] 0 — cannot yet — Compute and interpret core fairness metrics on real data
- [ ] 0 — cannot yet — Design an immutable audit trail covering every lifecycle transition
- [ ] 0 — cannot yet — Map a compliance obligation to an artefact and a test
- [ ] 0 — cannot yet — Distinguish fairness metrics that trade off from those that do not
- [ ] 0 — cannot yet — Build a governance workflow that produces evidence rather than promises

## 11. Summary Checklist

- [ ] Base rates are reported per group before any fairness metric.
- [ ] The fairness trade-off is documented as a policy choice, in writing.
- [ ] Model card metrics are generated, not typed.
- [ ] Every audit entry records actor, action, versions and policy version.
- [ ] Fairness thresholds are enforced by the promotion gate.
- [ ] Limitations are written for a non-technical reader.
