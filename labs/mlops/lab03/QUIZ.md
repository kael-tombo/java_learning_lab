# Model Registry & Versioning - Quiz (15 Questions)

**Track:** mlops  |  **Lab:** lab03  |  **Level:** Intermediate

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

### Q1: What is the difference between a model version and a stage?

A) They are the same
B) A version is the immutable artifact; a stage is a pointer to a version
C) A stage is a copy
D) Versions are pointers

**Answer: B** - Promotion moves a pointer, which makes it instant, atomic and auditable.

---

### Q2: Why must published versions be immutable?

A) For storage
B) Reproducibility and rollback depend on the same bytes
C) To reduce file size
D) Because of licensing

**Answer: B** - Editing a published version breaks every rollback guarantee you had.

---

### Q3: What does a champion/challenger setup do?

A) Runs both in production equally
B) Serves the champion and scores the challenger in shadow
C) Retires the champion
D) A/B tests prices

**Answer: B** - The challenger gets real traffic without affecting decisions.

---

### Q4: How do you prevent concurrent promotions from racing?

A) A database lock on everything
B) Compare-and-set on the expected current version
C) Retry the second one
D) Nothing, it self-resolves

**Answer: B** - CAS makes the second promotion fail loudly instead of overwriting.

---

### Q5: Why is lineage a promotion gate?

A) It is optional metadata
B) So a rollback later needs no archaeology
C) To speed promotion
D) For licensing

**Answer: B** - Complete lineage is what makes rollback safe months later.

---

### Q6: Why compare on matured labels?

A) Matured labels are easier to compute
B) Offline metrics can drift from live behaviour
C) It is faster
D) Shadow traffic is unreliable

**Answer: B** - Matured labels are what actually happened in production.

---

### Q7: What should a promotion gate check?

A) Only the offline metric
B) Metrics within tolerance, lineage, sign-offs, latency and fairness budgets
C) The developer's confidence
D) The file size

**Answer: B** - A declarative gate makes promotion evidence-based rather than opinion-based.

---

### Q8: What does a shadow deployment do?

A) A/B tests prices
B) Scores live traffic without affecting decisions
C) Trains a copy
D) Mirrors the database

**Answer: B** - Shadow scoring gives you live comparison data before you promote.

---

### Q9: How should retention work?

A) Delete old versions immediately
B) Archive unreachable versions after the rollback window, never deleting reachable ones
C) Keep everything forever
D) Delete based on file size

**Answer: B** - Reachability is the safety property; retention is the cost policy on top.

---

### Q10: Why cache the champion artifact locally?

A) To save bandwidth
B) So rollback works even when the artifact store is unavailable
C) For faster startup
D) To reduce memory

**Answer: B** - Rollback speed should not depend on a network dependency being up.

---

### Q11: What is a compare-and-set promotion failure?

A) An error to fix later
B) Proof that another promotion won the race; re-read and retry deliberately
C) A sign of corruption
D) A missing artifact

**Answer: B** - It is correct behaviour, not a bug; the retry must be deliberate.

---

### Q12: Why do stages matter more than folders of model files?

A) They are tidier
B) Promotion and rollback become pointer moves with an audit trail
C) They use less storage
D) They are required by Kubernetes

**Answer: B** - The pointer model is what makes rollback instant and reviewable.

---

### Q13: What belongs in a registry entry?

A) The model file only
B) Hash, artifact, lineage, metrics, shadow results and approvals
C) The training logs
D) The feature list

**Answer: B** - An entry should be enough to justify the promotion without asking anyone.

---

### Q14: How do you detect that a promoted model was wrong?

A) Automated guardrails with rollback
B) Weekly manual review
C) User complaints
D) Comparing file sizes

**Answer: A** - Guardrails plus pre-authorised rollback are the only fast path.

---

### Q15: Why rehearse rollback?

A) Documentation requires it
B) Because rollback time is dominated by decisions, not technology
C) To satisfy auditors only
D) Because it is a best practice

**Answer: B** - Drills find that the bottleneck is approval latency, and pre-authorising fixes it.

---

> Score 15/15: you can teach this lab. 12-14: solid. Under 12: re-read THEORY.md sections 3 and 7, then retake.
