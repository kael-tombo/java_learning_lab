# MINI_PROJECT — Model Card, Fairness Gate and Audit Trail

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

**Brief.** Generate a model card from the pipeline, enforce a fairness policy in the promotion gate, and record a tamper-evident audit trail.

**Timebox.** 3–4 hours

## 1. Why This Project Exists

Governance is learnable as engineering: each obligation becomes an artefact and a test, and the tension between fairness metrics becomes a documented choice.

## 2. Requirements

- Per-group fairness evaluation with base rates reported before any disparity metric.
- Demonstrate the parity-versus-opportunity trade-off numerically and write the policy choice.
- Threshold sweep showing how disparity and error rates move with the operating point.
- Versioned governance policy enforced by a promotion gate that reports every failure reason.
- Hash-chained audit log with the policy version in each entry; demonstrate tamper detection.
- Model card generated from the pipeline, with a test proving generated metrics match recomputation.
- Obligation-to-test mapping with at least three tests running in CI.

## 3. Build Order

| Step | Time | What you do | Done when |
|---|---|---|---|
| 1 | 30m | Per-group fairness evaluation with base rates first | A correct fairness report |
| 2 | 35m | Show the trade-off numerically; write the policy | A signed-off policy choice |
| 3 | 30m | Threshold sweep with disparity and cost curves | A defended operating point |
| 4 | 30m | Hash-chained audit log; demonstrate tamper detection | A verifiable trail |
| 5 | 35m | Versioned governance policy in the promotion gate | A gate that blocks on breach |
| 6 | 30m | Generated model card with a parity test | A card that cannot go stale |
| 7 | 25m | Obligation-to-test mapping with three CI tests | An evidence report |

## 4. Architecture Sketch

```text
 snapshot metadata --> ModelCard (generated)
                              |
                    per-group evaluation (base rates first)
                              |
                    disparity ratio + gap vs policy thresholds
                              |
                    GovernancePolicy (versioned) --> PromotionGate
                              |                    (all reasons reported)
                        audit entry (hash chain, policy version)
                              |
                    CI tests: fairness, evidence, lineage, additivity
```

## 5. Implementation Notes

- Put base rates first in the output; everything after it is uninterpretable without them.
- Demonstrate the trade-off yourself rather than asserting it exists.
- Generate the card from the pipeline and prove it with a parity test.
- Change the policy mid-project and show a previously passing model now blocked.

## 6. Deliverables

1. Fairness report with base rates, disparity metrics and a threshold sweep.
1. Written fairness policy with the trade-off and its cost.
1. Verifiable audit export demonstrating tamper detection.
1. Generated model card plus the CI evidence report.

## 7. Grading Rubric

| Dimension | Weight | What earns full marks |
|---|---|---|
| Correctness | 25% | Base rates first; metrics verified; no NaN edge cases |
| Policy | 25% | Trade-off demonstrated numerically and the choice justified |
| Enforcement | 25% | Versioned policy blocks promotion with named reasons |
| Evidence | 15% | Tamper-evident audit with policy version |
| Durability | 10% | Card generated with a parity test proving it cannot drift |

## 8. Stretch Goals

- Add counterfactual fairness checking by protected attribute.
- Add continuous post-launch fairness monitoring with segment alerts.
- Export an audit package in a regulator-friendly format.

## 9. Definition of Done

You are finished when every box below is checked, not when the code compiles.

- [ ] Per-group fairness evaluation with base rates reported before any disparity metric.
- [ ] Demonstrate the parity-versus-opportunity trade-off numerically and write the policy choice.
- [ ] Threshold sweep showing how disparity and error rates move with the operating point.
- [ ] Versioned governance policy enforced by a promotion gate that reports every failure reason.
- [ ] Hash-chained audit log with the policy version in each entry; demonstrate tamper detection.
- [ ] Model card generated from the pipeline, with a test proving generated metrics match recomputation.
- [ ] A stranger can reproduce the reported numbers with one command
- [ ] The limitations section says what this cannot do
- [ ] At least one number is alerted on in production

## 10. Retrospective Template

- What worked:
- What surprised me:
- The one number I would alert on in production:
- What I would delete before shipping this to real users:
