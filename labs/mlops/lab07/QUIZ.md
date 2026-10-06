# CI/CD for ML Pipelines - Quiz (15 Questions)

**Track:** mlops  |  **Lab:** lab07  |  **Level:** Intermediate

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

### Q1: What belongs in pre-merge for an ML pipeline?

A) Full training on production data
B) Compile, unit tests, contracts and a smoke training run on a fixture
C) Shadow deployment
D) Registry promotion

**Answer: B** - Pre-merge must be fast; expensive work belongs post-merge.

---

### Q2: Why is a smoke training run valuable?

A) It is fast
B) It catches broken feature code that unit tests cannot
C) It replaces evaluation
D) It warms caches

**Answer: B** - A tiny training run exercises the pipeline end to end.

---

### Q3: What is an evaluation regression gate?

A) A dashboard
B) A check that a candidate's metric on a frozen eval set does not regress beyond epsilon
C) A type checker
D) A code review

**Answer: B** - A gate blocks the build; a dashboard does not.

---

### Q4: How should epsilon for a metric gate be chosen?

A) By preference
B) From historical run-to-run variance of the same code
C) As a round number
D) From last quarter's drop

**Answer: B** - Below the noise floor the gate fires randomly and gets ignored.

---

### Q5: Why must the evaluation set be frozen?

A) For speed
B) So deltas between runs are comparable
C) To save storage
D) Because the API requires it

**Answer: B** - A moving eval set makes every delta uninterpretable.

---

### Q6: How should CI caches be keyed?

A) By commit time
B) By content hash of commit, data version and lockfile
C) By branch name
D) Randomly

**Answer: B** - Content addressing makes a stale cache structurally impossible.

---

### Q7: Why does CI deploy to shadow rather than production?

A) Shadow is faster
B) Promotion needs shadow evaluation and a registry gate
C) Production has no CI
D) To avoid cost

**Answer: B** - CI proves soundness; the registry decides promotion.

---

### Q8: What is a data contract?

A) A legal agreement
B) An agreement on upstream data shape and semantics, checked in CI
C) A schema file
D) A test fixture

**Answer: B** - It catches upstream changes that would silently break features.

---

### Q9: Why do ML pipelines get slower over time?

A) More data
B) Uncached data and features, plus growing evaluation suites
C) More engineers
D) Tooling

**Answer: B** - Caching and splitting fast from slow suites fixes it.

---

### Q10: What is time-to-detect?

A) Build duration
B) Merge to alert, including queue time
C) Test runtime
D) Deployment time

**Answer: B** - Queue time usually dominates for scheduled pipelines.

---

### Q11: How do you keep engineers waiting for CI?

A) Add approvals
B) Keep pre-merge under ten minutes
C) Make it mandatory in writing
D) Run it more often

**Answer: B** - Beyond about ten minutes people route around the gate.

---

### Q12: Which change type needs the full evaluation suite?

A) A comment change
B) A hyperparameter change
C) A rename
D) A log line

**Answer: B** - A hyperparameter change alters model behaviour, so it needs the expensive gate.

---

### Q13: What is the biggest CI anti-pattern in ML?

A) Caching
B) Putting full training in pre-merge so people bypass CI
C) Using a fixture
D) Timing stages

**Answer: B** - It makes the gate optional, which is worse than having none.

---

### Q14: Should CI write a cache entry when a stage fails?

A) Yes, for speed
B) No, a failed stage must not leave a cache entry
C) Only for the first stage
D) Only on flaky tests

**Answer: B** - A partial artefact in the cache is a correctness bug waiting to be served.

---

### Q15: What separates CI from deployment?

A) Nothing
B) CI proves the change is sound; promotion to production goes through shadow evaluation and the registry gate
C) CI deploys, deployment monitors
D) Deployment runs CI

**Answer: B** - Conflating them gives you either slow merges or unreviewed production.

---

> Score 15/15: you can teach this lab. 12-14: solid. Under 12: re-read THEORY.md sections 3 and 7, then retake.
