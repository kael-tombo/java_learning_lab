# Model Governance & Compliance - Flashcards (60 cards)

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

**Format.** Question (front) -> answer (back). Use for spaced repetition: day 0, day 1, day 3, day 7, day 21. Do not read the answer first.

| # | Front | Back |
|---|---|---|
| 1 | Why can you not satisfy every fairness metric at once? | With differing base rates, equal selection rates and equal true positive rates are mathematically incompatible. |
| 2 | Why report base rates first? | Because disparity metrics are uninterpretable without knowing how the groups actually differ in outcome rates. |
| 3 | What is a model card for? | It is the contract between the model and the people it affects: intended use, data, metrics, limitations. |
| 4 | What should an audit entry contain? | Actor, action, from and to versions, policy version and a hash of the supporting evidence. |
| 5 | Why version your fairness policy? | So an audit can tell which thresholds applied at the time, rather than today's thresholds retrofitted. |
| 6 | Should protected attributes be training features? | No; they belong in evaluation so you can measure harm, with the exclusion documented. |
| 7 | What does disparate impact measure? | The ratio or gap in selection rates between groups; a ratio below 0.8 traditionally flags review. |
| 8 | How do you stop model cards going stale? | Generate the measurable fields from the pipeline so they cannot diverge from the model. |
| 9 | What is Fairness metrics are in tension? | Statistical parity (equal selection rates) and equal opportunity (equal true positive rates) cannot both hold when base rates differ. |
| 10 | What is Base rates drive everything? | Two groups with different fraud rates will have different false positive rates under any threshold that treats them identically. |
| 11 | What is Model cards are interfaces? | A model card is not documentation; it is the contract between the model and the people affected by it. |
| 12 | What is Audit trails must be immutable and complete? | The trail has to answer: who promoted what, when, on which evidence, and under which version of the policy. |
| 13 | What is Obligations map to artefacts and tests? | A compliance requirement is satisfied by an artefact plus a test that proves it. |
| 14 | What is Documentation decays silently? | Model cards go stale as features and thresholds change. |
| 15 | In this lab, what does `selection_rate = TP + FP over group` mean? | Statistical parity: P(yhat=1 \| group) |
| 16 | In this lab, what does `TPR_g = TP_g / (TP_g + FN_g)` mean? | Equal opportunity: equal true positive rates |
| 17 | In this lab, what does `FPR_g = FP_g / (FP_g + TN_g)` mean? | False positive disparity: the metric that moves with base rates |
| 18 | In this lab, what does `demographic_parity_gap = max_g rate - min_g rate` mean? | Disparate impact: the quantity a regulator measures |
| 19 | In this lab, what does `disparate_impact_ratio = min_g rate / max_g rate` mean? | Four-fifths style ratio: below 0.8 flags review |
| 20 | In this lab, what does `audit_record = (actor, action, from, to, policy_version, evidence_hash)` mean? | Audit entry: immutable and complete |
| 21 | You see 'Fairness analysis omits base rates' in production. What is the cause and the fix? | uninterpretable disparity numbers Fix: always report base rate per group first |
| 22 | You see 'A metric improved for one group and worsened for another' in production. What is the cause and the fix? | unexamined trade-off Fix: publish the full group matrix and get the policy choice in writing |
| 23 | You see 'Model card is accurate at launch and wrong after two releases' in production. What is the cause and the fix? | hand-written documentation Fix: generate measurable fields from the pipeline |
| 24 | You see 'Audit log exists but records no policy version' in production. What is the cause and the fix? | policy changed silently Fix: record the policy version in every entry |
| 25 | You see 'Disparate impact threshold ignored because 'the model is accurate'' in production. What is the cause and the fix? | accuracy as an argument against fairness Fix: accuracy and fairness are separate gates; both must pass |
| 26 | You see 'Protected attribute used as a training feature' in production. What is the cause and the fix? | legal exposure and worse fairness Fix: exclude from training, include in evaluation only, with justification recorded |
| 27 | Which Java API is the backbone of: the generated contract | `record ModelCard(String name, String version, IntendedUse, Data, Metrics, Limitations)` |
| 28 | Which Java API is the backbone of: base rate plus every metric per group | `Map<String, GroupStats> for per-group evaluation` |
| 29 | Which Java API is the backbone of: tamper evidence for the compliance export | `Append-only audit log with a hash chain` |
| 30 | Which Java API is the backbone of: the version recorded in every audit entry | `record PolicyVersion(String id, Instant effectiveFrom, Map<String,Double> thresholds)` |
| 31 | Which Java API is the backbone of: ratios at four-fifths granularity need exact reporting | `BigDecimal for disparity ratios` |
| 32 | Why does Fairness metrics are in tension matter operationally? | Statistical parity (equal selection rates) and equal opportunity (equal true positive rates) cannot both hold when base rates differ. |
| 33 | Why does Base rates drive everything matter operationally? | Two groups with different fraud rates will have different false positive rates under any threshold that treats them identically. |
| 34 | Why does Model cards are interfaces matter operationally? | A model card is not documentation; it is the contract between the model and the people affected by it. |
| 35 | Why does Audit trails must be immutable and complete matter operationally? | The trail has to answer: who promoted what, when, on which evidence, and under which version of the policy. |
| 36 | Why does Obligations map to artefacts and tests matter operationally? | A compliance requirement is satisfied by an artefact plus a test that proves it. |
| 37 | Why does Documentation decays silently matter operationally? | Model cards go stale as features and thresholds change. |
| 38 | In the Model Governance & Compliance pipeline, what happens next? Register the model with intended use, out-of-scope use, and ... | Register the model with intended use, out-of-scope use, and the decision it informs. |
| 39 | In the Model Governance & Compliance pipeline, what happens next? Record the data: sources, time window, population, known gap... | Record the data: sources, time window, population, known gaps. |
| 40 | In the Model Governance & Compliance pipeline, what happens next? Evaluate metrics overall and per group, reporting base rates... | Evaluate metrics overall and per group, reporting base rates alongside fairness metrics. |
| 41 | In the Model Governance & Compliance pipeline, what happens next? Write the limitations explicitly, including who the model is... | Write the limitations explicitly, including who the model is likely to harm. |
| 42 | In the Model Governance & Compliance pipeline, what happens next? Run the promotion gate: fairness thresholds plus lineage plu... | Run the promotion gate: fairness thresholds plus lineage plus required sign-offs. |
| 43 | In the Model Governance & Compliance pipeline, what happens next? Store the model card, the audit entries and the evidence has... | Store the model card, the audit entries and the evidence hash together. |
| 44 | Exercise focus: Fairness metrics with base rates | Get the report in the right order. |
| 45 | Exercise focus: The fairness trade-off, numerically | Show the impossibility with your own numbers. |
| 46 | Exercise focus: Threshold sweep and trade-off curves | See how disparity moves with the operating point. |
| 47 | Exercise focus: Tamper-evident audit log | Make the trail evidence. |
| 48 | Exercise focus: Model card generation | Stop the documentation rotting. |
| 49 | Exercise focus: Governance policy as code | Make obligations testable. |
| 50 | State the Selection and error rates per group result for Model Governance & Compliance. | Group A: 1000 rows, 100 positive, 50 flagged, 40 correct. base 10%, selection 5%, TPR 40%. Group B: 1000 rows, 300 positive, 60 flagged, 55 correct. base 30%, selection 6%, TPR 18%. Group B looks similar on selection and much worse on TPR. |
| 51 | State the Disparate impact metrics result for Model Governance & Compliance. | Selection 6% and 5%: ratio 0.833 (passes 0.8), gap 1 point. Selection 0.6% and 0.4%: ratio 0.667 (flags), gap 0.2 points. The second is far less impactful in absolute terms but fails the standard heuristic. |
| 52 | State the Why parity and equality can conflict result for Model Governance & Compliance. | Base rates 10% and 30%. Equal FPR of 0.05 gives TPR of roughly 0.5 and 0.71. Forcing equal TPR requires raising the second group's FPR above the first's, which is the trade a reviewer must approve. |
| 53 | State the Audit chain integrity result for Model Governance & Compliance. | Changing entry 400's actor value changes every subsequent hash, so a reviewer verifying the chain finds the break at entry 400 rather than discovering an inconsistency months later. |
| 54 | What is equal opportunity? | Equal true positive rates across groups, so equally-qualified people are equally likely to be flagged. |
| 55 | What is statistical parity? | Equal selection rates across groups, which can require a higher error rate for one group when base rates differ. |
| 56 | Why are accuracy and fairness separate gates? | A model can be accurate overall and still impose a disproportionate error rate on one group. |
| 57 | What is the four-fifths rule? | A heuristic flagging review when the disadvantaged group's selection rate is below 80% of the advantaged group's. |
| 58 | Assumption / invariant to defend: Protected attributes are available for evaluation even if they are exc... | Protected attributes are available for evaluation even if they are excluded from training |
| 59 | Assumption / invariant to defend: Group definitions are documented and reviewed rather than chosen per a... | Group definitions are documented and reviewed rather than chosen per analysis |
| 60 | Assumption / invariant to defend: Fairness thresholds are set as policy and enforced by the gate... | Fairness thresholds are set as policy and enforced by the gate |

## Deck Notes

- Rows are generated from this lab's own concepts, equations, failure modes and Java APIs - if you disagree with a card, fix the card.
- The last block of cards is deliberately operational: they are the questions a staff engineer gets asked in a design review.
