# Data Validation & Quality - Quiz (15 Questions)

**Track:** mlops  |  **Lab:** lab09  |  **Level:** Intermediate

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

### Q1: What is a data expectation?

A) A dashboard
B) An executable statement about data that can be evaluated and stored
C) A test fixture
D) A schema file

**Answer: B** - Expectations are the atomic unit that makes validation a trend rather than a spot check.

---

### Q2: Why separate blocking from warning expectations?

A) For clarity
B) So blocking failures stay rare and trustworthy
C) To reduce cost
D) Because warnings are unsupported

**Answer: B** - A gate that fires daily gets ignored, and then hides the real break.

---

### Q3: Which check catches an integer column becoming a string?

A) A range check
B) A type or schema contract on the boundary
C) A uniqueness check
D) A freshness check

**Answer: B** - Schema contracts are cheap and catch the most destructive failures.

---

### Q4: Why validate freshness and volume?

A) To satisfy auditors
B) They catch upstream stalls and partial loads before a model sees bad data
C) They are easy to compute
D) For dashboards

**Answer: B** - Stalled pipelines are the most common real-world data failure.

---

### Q5: What is the risk of sampling for validation?

A) It is slow
B) A small sample misses low-frequency corruptions entirely
C) It cannot compute rates
D) Sampling is not supported

**Answer: B** - A 0.1% sample detects a 50% corruption but essentially never a 0.01% one.

---

### Q6: What does a rank-based shape comparison add over a range check?

A) Speed
B) It detects distribution shape change without assuming a form
C) It handles nulls
D) It samples better

**Answer: B** - Range checks pass while the shape changes, which is where harm usually comes from.

---

### Q7: Why compare rates against a sampling-noise floor?

A) For speed
B) Otherwise normal variation produces alerts and the suite gets ignored
C) Because rates are unreliable
D) To reduce storage

**Answer: B** - A two-proportion significance test is what makes a threshold defensible.

---

### Q8: What is a validation suite for?

A) Documentation
B) Grouping expectations under an identity so results are comparable over time
C) Performance
D) Access control

**Answer: B** - The suite identity is what turns spot checks into a trend.

---

### Q9: What does the blocking rule protect that a score does not?

A) Storage
B) The invariant that the pipeline never proceeds on broken data
C) Speed
D) Schema

**Answer: B** - A weighted score informs; the blocking rule decides.

---

### Q10: Where should validation predicates run?

A) In the JVM after loading
B) Pushed down to the query engine
C) In the browser
D) In the model

**Answer: B** - Pushing down makes full validation affordable on large tables.

---

### Q11: How should you pick a null-rate threshold?

A) A round number
B) From observed production history with a review cadence
C) From last quarter's value
D) Zero

**Answer: B** - Thresholds from history are defensible; round numbers are not.

---

### Q12: What is a window-aware volume expectation?

A) One that ignores volume
B) One that compares to the same period in a reference window
C) One that samples
D) One that alerts daily

**Answer: B** - Flat volume alerts fire on every seasonality peak and get muted.

---

### Q13: Why does an upstream type change need a contract rather than a cast?

A) Performance
B) A cast silently produces wrong values instead of failing
C) Casts are deprecated
D) Types change often

**Answer: B** - Silent wrongness is worse than a failure, because downstream metrics look plausible.

---

### Q14: What should a quality trend dashboard show?

A) A pass or fail
B) The score over time with a slope and per-expectation breakdown
C) Only alerts
D) Row counts

**Answer: B** - A trend shows degradation before a threshold trips.

---

### Q15: Who owns a data quality expectation?

A) Nobody, it is shared
B) A named team responsible for the data and the threshold
C) The platform team
D) The first author

**Answer: B** - Ownership is what turns a gate into something a team will actually fix.

---

> Score 15/15: you can teach this lab. 12-14: solid. Under 12: re-read THEORY.md sections 3 and 7, then retake.
