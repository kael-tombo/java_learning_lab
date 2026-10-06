# Feature Store Architecture - Quiz (15 Questions)

**Track:** mlops  |  **Lab:** lab04  |  **Level:** Intermediate

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

### Q1: Why does a feature store need both online and offline stores?

A) Redundancy
B) Offline holds history for training; online serves the latest value at low latency
C) Compliance
D) To compress features

**Answer: B** - Training needs history and reproducibility; serving needs a fast point lookup.

---

### Q2: What is training-serving skew?

A) Latency
B) Training and serving computing the same feature differently
C) Data volume
D) Model size

**Answer: B** - Different implementations drift, so the model sees inputs it was never trained on.

---

### Q3: How do you structurally prevent skew?

A) Documentation
B) One definition materialised into both stores
C) Manual review
D) Different teams

**Answer: B** - One transform feeding two projections leaves no second implementation to drift.

---

### Q4: What is point-in-time correctness?

A) Fast training
B) Joining training rows only to feature values that existed at the label's timestamp
C) Using the latest values
D) Sorting by time

**Answer: B** - Otherwise training rows contain information unavailable at prediction time.

---

### Q5: What should you alert on for a feature store?

A) Pipeline success only
B) Per-feature freshness and staleness rate
C) Storage usage
D) Cluster size

**Answer: B** - Staleness looks like drift and gets misdiagnosed for weeks if you only watch success.

---

### Q6: Push versus pull materialisation?

A) Push is pull with retries
B) Pull recomputes on a schedule; push updates on write
C) Pull is for online, push for offline
D) They are the same

**Answer: B** - Pull is reproducible and cheap; push is fresher and costlier.

---

### Q7: Why version a feature view?

A) For aesthetics
B) A changed definition must not silently alter existing models
C) To reduce storage
D) Because the API requires it

**Answer: B** - Consumers must be able to stay on the definition their model was trained with.

---

### Q8: Why batch online feature reads?

A) To reduce logging
B) Round trips dominate p99 latency
C) Because the API requires it
D) To reduce memory

**Answer: B** - One call per entity instead of one per feature is usually the biggest latency win available.

---

### Q9: What is the parity test?

A) Comparing two models
B) Reading the same entity from both stores and asserting equality
C) Comparing runtimes
D) Checking schema

**Answer: B** - Parity is how you detect skew before it degrades a model.

---

### Q10: What is a feature's staleness tolerance?

A) Its TTL
B) How old it is allowed to be before it materially changes the prediction
C) Its storage size
D) Its query time

**Answer: B** - TTL should come from the tolerance, not from a platform default.

---

### Q11: Why preserve event timestamps?

A) For ordering
B) Point-in-time joins are impossible without them
C) For compression
D) For schema inference

**Answer: B** - Drop them and the training join silently leaks the future.

---

### Q12: Who should own a feature?

A) The platform team alone
B) A named team responsible for its semantics and deprecation
C) Nobody, it is shared
D) The first person who needs it

**Answer: B** - Ownership prevents two teams forking the same feature name.

---

### Q13: How do you measure feature-store adoption?

A) Reuse ratio: features reused divided by features defined
B) Number of features
C) Storage used
D) Query count

**Answer: A** - Reuse ratio is the number that justifies the platform's existence.

---

### Q14: A model degrades after migration. First check?

A) Hyperparameters
B) Feature parity between online and offline stores
C) Learning rate
D) Batch size

**Answer: B** - Skew is the most common cause and the cheapest to check.

---

### Q15: What happens when an online TTL expires?

A) The value is recomputed
B) The read fails and the service must handle it explicitly
C) A stale value is served
D) Nothing

**Answer: B** - Explicit failure is better than silently serving a value you think is fresh.

---

> Score 15/15: you can teach this lab. 12-14: solid. Under 12: re-read THEORY.md sections 3 and 7, then retake.
