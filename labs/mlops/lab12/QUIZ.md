# Infrastructure as Code for ML - Quiz (15 Questions)

**Track:** mlops  |  **Lab:** lab12  |  **Level:** Intermediate

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

### Q1: What is the primary value of infrastructure as code?

A) Automation
B) Changes become reviewable diffs with an author
C) Cost reduction
D) Consistency

**Answer: B** - Console-created resources are invisible to review and untagged by intent.

---

### Q2: How should topology and configuration be separated?

A) They should not be
B) Topology in code; environment values in configuration
C) Configuration in code
D) Both in one file per environment

**Answer: B** - Mixing them forces code copies that drift.

---

### Q3: Why do stateful resources need special treatment?

A) They are slower
B) Destroying them loses data, so recreate requires backups and a restore path
C) They cost more
D) They cannot be coded

**Answer: B** - Most IaC disasters are stateful resources destroyed by an unread plan.

---

### Q4: What should a plan make obvious?

A) Only the creates
B) Every create, update and destroy, with stateful destroys risk-flagged
C) The cost
D) The author

**Answer: B** - Reviewers skim for creates; destroys must be impossible to miss.

---

### Q5: What is drift?

A) An intentional change
B) A divergence between what code says should exist and what does
C) A failed apply
D) A cost anomaly

**Answer: B** - Intentional change is in code; drift is divergence nobody intended.

---

### Q6: Should drift be auto-corrected?

A) Yes, always
B) No; report it with an owner, since manual changes may be intentional
C) Only for compute resources
D) Only after 30 days

**Answer: B** - Blind correction can delete an emergency fix someone made deliberately.

---

### Q7: Why require cost tags?

A) For compliance
B) Chargeback and optimisation are impossible later without them
C) Because clouds require them
D) To speed up applies

**Answer: B** - Tags turn an opaque bill into a per-team number.

---

### Q8: What does a quota plus priority class give you?

A) More GPUs
B) Bounded queueing where interactive work preempts batch
C) Cheaper compute
D) Faster provisioning

**Answer: B** - Without them, contention is an outage instead of a visible queue.

---

### Q9: What is a workspace for?

A) Code organisation
B) Per-team isolated state so applies cannot collide
C) Testing
D) Documentation

**Answer: B** - Shared state means one team's apply can destroy another's resources.

---

### Q10: What is least privilege here?

A) One admin account
B) Per-team credentials scoped to their own resources
C) No credentials
D) Temporary accounts

**Answer: B** - It also means a compromised pipeline cannot reach production data.

---

### Q11: How do you find abandoned GPU quota?

A) Looking at the bill
B) Quota usage under 20% sustained for 7 days
C) Pod restarts
D) Instance type

**Answer: B** - Idle quota costs money whether or not anyone is using it.

---

### Q12: What should a stateful destroy plan display?

A) Nothing special
B) Restore source, verified-at time and the data-loss window
C) The bucket name
D) The cost

**Answer: B** - The plan must state recovery properties, not merely that a replacement happens.

---

### Q13: Why does infrastructure as code help cost control?

A) It is cheaper
B) Tags plus allocation make spend attributable and idle capacity visible
C) It reduces storage
D) It avoids scaling

**Answer: B** - Attribution is what lets someone actually reduce it.

---

### Q14: What is RPO?

A) Recovery time objective
B) Maximum acceptable data loss on restore
C) Recovery point cost
D) Rollback policy

**Answer: B** - RTO is time to usable; RPO is data loss window.

---

### Q15: What is the worst IaC anti-pattern?

A) Using modules
B) Applying a plan with destroys unreviewed in production
C) Using variables
D) Using remote state

**Answer: B** - The destructive part of a plan must be reviewed with the same care as the code.

---

> Score 15/15: you can teach this lab. 12-14: solid. Under 12: re-read THEORY.md sections 3 and 7, then retake.
