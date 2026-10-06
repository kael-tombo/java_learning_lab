# Production ML Architecture - Quiz (15 Questions)

**Track:** mlops  |  **Lab:** lab15  |  **Level:** Advanced

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

### Q1: Why draw training, serving and feedback as separate paths?

A) Clarity
B) They have different constraints and failure domains; one diagram hides the breaks
C) To use more tools
D) Because they run at different times

**Answer: B** - Conflating them is how an architecture ends up with no isolated failure domains.

---

### Q2: What is a degradation ladder?

A) A retry list
B) An ordered set of fallbacks traded by quality cost, ending in a baseline or rules engine
C) A test suite
D) A rollout plan

**Answer: B** - The ordering should reflect the quality-versus-availability trade.

---

### Q3: What must every dependency edge state?

A) Its owner
B) Its metric, SLO, owner and behaviour when it breaks
C) Its cost
D) Its version

**Answer: B** - An edge with no failure behaviour makes the diagram a drawing rather than an architecture.

---

### Q4: Why do per-term p99 latencies add?

A) Because tails compound
B) Tail latencies add, so budgets must be allocated per dependency
C) Because of network hops
D) They do not add

**Answer: B** - A 50 ms budget split three ways is not 50 ms per term.

---

### Q5: How does a bulkhead help?

A) Improves accuracy
B) Bounded pools per dependency so one slow call cannot exhaust the service
C) Reduces cost
D) Simplifies code

**Answer: B** - Isolation is what turns a dependency outage into a rung down the ladder.

---

### Q6: What bounds concept drift detection?

A) Compute
B) Label latency: you cannot detect quality loss faster than outcomes arrive
C) Sampling
D) Model size

**Answer: B** - Monitoring must be designed around the slower signal, with PSI as the early warning.

---

### Q7: Why is feedback biased?

A) Sampling error
B) Outcomes reflect what the current system decided, so it reinforces itself
C) Label noise
D) Drift in features

**Answer: B** - Exploration is needed or the system converges to its own decisions.

---

### Q8: What does availability multiplication tell you?

A) Nothing useful
B) The weakest series dependency dominates, so adding hot-path dependencies is costly
C) Availability is additive
D) It is unrelated

**Answer: B** - Removing the registry from the read path by caching locally is often the cheapest win.

---

### Q9: Why pre-authorise rollback?

A) Governance
B) Rollback time is dominated by finding an approver, not the technical step
C) It is faster technically
D) To reduce cost

**Answer: B** - Drills that skip this find the bottleneck is human, not technical.

---

### Q10: When should a read path reject rather than fall back?

A) Always
B) When a wrong decision is worse than no decision, such as an authorisation
C) Never
D) Only at night

**Answer: B** - Degradation is not universally right; some decisions must fail closed.

---

### Q11: What is unit economics for an ML system?

A) Cost per training run
B) Cost per 1,000 decisions including amortised training
C) Cost per GPU hour
D) Cost per engineer

**Answer: B** - It is the number that connects engineering choices to business outcomes.

---

### Q12: What does shadow scoring allow?

A) Faster deployment
B) Comparing a challenger on live traffic without affecting users
C) Cheaper training
D) Better features

**Answer: B** - It is the only safe way to compare before exposure.

---

### Q13: Which is the weakest link in most ML architectures?

A) The model
B) Integration between components, where failure behaviour is undefined
C) The data
D) Compute

**Answer: B** - Most real failures are integration failures, not algorithm failures.

---

### Q14: How should consistency be chosen?

A) Globally, once
B) Per interaction, with the reason written next to it
C) By the framework default
D) By whoever writes the code

**Answer: B** - A global guarantee is either unaffordable or unnecessary for most interactions.

---

### Q15: What makes an architecture production-ready?

A) A clean diagram
B) Every dependency has an owner, an SLO, a metric and a failure behaviour
C) Latest frameworks
D) Fast training

**Answer: B** - Readiness is the completeness of the failure story, not the elegance of the picture.

---

> Score 15/15: you can teach this lab. 12-14: solid. Under 12: re-read THEORY.md sections 3 and 7, then retake.
