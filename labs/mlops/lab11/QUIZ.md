# Model Governance & Compliance - Quiz (15 Questions)

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

**Instructions.** Answer all 15 questions before reading the bold answer lines. Multiple choice, one best answer. Target: 12/15 before you move on to the mini project.

### Q1: Why can you not satisfy both statistical parity and equal opportunity?

A) You can, with enough data
B) With differing base rates they are mathematically incompatible
C) It depends on the model
D) Parity is about accuracy

**Answer: B** - The impossibility is structural, so the choice of which to prioritise is a policy decision.

---

### Q2: Why must base rates be reported with fairness metrics?

A) For completeness
B) Disparity numbers are uninterpretable without knowing how the groups differ in outcome rates
C) Because regulators ask
D) To increase sample size

**Answer: B** - Equal accuracy can hide very different error distributions across groups.

---

### Q3: What is a model card?

A) Marketing material
B) The contract between the model and the people it affects: use, data, metrics, limitations
C) A training log
D) A licence

**Answer: B** - It lets a downstream team decide whether the model is appropriate at all.

---

### Q4: What should an audit entry record besides actor and action?

A) Nothing else
B) From and to versions, the policy version, and a hash of supporting evidence
C) The file path
D) The engineer's email

**Answer: B** - The policy version and evidence hash make the trail interpretable months later.

---

### Q5: Why version the fairness policy?

A) For auditing
B) So a review can tell which thresholds applied at the time
C) To satisfy legal
D) Because thresholds change

**Answer: B** - Today's thresholds retrofitted onto a past decision are not evidence.

---

### Q6: Should protected attributes be training features?

A) Yes, for fairness
B) No; use them for evaluation so you can measure harm
C) Only if legally permitted
D) It depends

**Answer: B** - Including them creates legal exposure and often worsens the fairness outcome.

---

### Q7: What does a disparate impact ratio below 0.8 indicate?

A) A violation
B) A heuristic flag for review, not proof of discrimination
C) Perfect fairness
D) No effect

**Answer: B** - It is a screening heuristic from equal-employment practice, not a legal test.

---

### Q8: Can a highly accurate model fail a fairness gate?

A) No
B) Yes; accuracy overall can coexist with a disproportionate error rate on one group
C) Only with poor data
D) Only for regression

**Answer: B** - Accuracy and fairness are separate gates; both must pass.

---

### Q9: Why does documentation go stale?

A) Lack of effort
B) Hand-written numbers diverge as features and thresholds change
C) Storage limits
D) Policy

**Answer: B** - Generating the measurable fields from the pipeline is the only version that stays true.

---

### Q10: What is a hash-chained audit log for?

A) Speed
B) Tamper evidence, so a modification is detectable during verification
C) Compression
D) Access control

**Answer: B** - It turns 'we keep a log' into evidence a reviewer can verify.

---

### Q11: What is statistical parity?

A) Equal accuracy
B) Equal selection rates across groups
C) Equal recall
D) Equal latency

**Answer: B** - P(yhat = 1) is the same for every group, which can require unequal error rates.

---

### Q12: What is equal opportunity?

A) Equal selection rates
B) Equal true positive rates across groups
C) Equal accuracy
D) Equal calibration

**Answer: B** - Equally qualified people are equally likely to be flagged.

---

### Q13: How do you keep the blocking gate trustworthy?

A) Add more checks
B) Keep blocking thresholds rare and evidence-based, and report every failure reason
C) Turn everything into warnings
D) Add approvals

**Answer: B** - A gate that fires constantly gets overridden, and then hides real breaches.

---

### Q14: What belongs in limitations?

A) Only accuracy
B) Who the model is likely to harm, out-of-scope uses, and known data gaps, written for a non-technical reader
C) Training time
D) Feature names

**Answer: B** - Limitations are the part a downstream user actually needs.

---

### Q15: How should compliance be operationalised?

A) A policy document
B) Each obligation mapped to an artefact plus a test that proves it
C) An annual audit
D) Training

**Answer: B** - 'We have a policy' is not evidence; a failing test is.

---

> Score 15/15: you can teach this lab. 12-14: solid. Under 12: re-read THEORY.md sections 3 and 7, then retake.
