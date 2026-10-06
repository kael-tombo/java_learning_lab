# Model Serving with Docker - Quiz (15 Questions)

**Track:** mlops  |  **Lab:** lab05  |  **Level:** Intermediate

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

### Q1: Why use a multi-stage Docker build?

A) Faster builds
B) Compile with a JDK, ship only a JRE plus the artefact
C) To enable caching
D) For security scanning

**Answer: B** - The runtime image drops from ~450 MB to ~90 MB.

---

### Q2: Why prefer MaxRAMPercentage over -Xmx?

A) It is faster
B) The JVM sizes itself to the container limit, so one image works under any limit
C) It avoids OOM
D) It reduces startup

**Answer: B** - Absolute -Xmx ignores the cgroup limit and causes OOMKilled pods.

---

### Q3: What is outside the Java heap?

A) Nothing
B) Metaspace, thread stacks, code cache, direct buffers and native libraries

**Answer: B** - All of it counts toward the container limit, so heap must be well below it.

---

### Q4: What should the readiness probe wait for?

A) The process to start
B) Warm-up completion, so users do not pay the JIT cost
C) The registry to respond
D) The first successful prediction

**Answer: B** - Otherwise startup latency is charged to the first users.

---

### Q5: Why must /healthz stay cheap?

A) Cost
B) A liveness probe doing work turns load spikes into restart storms
C) To reduce image size
D) Because the API requires it

**Answer: B** - Dependency calls in liveness cause cascading restarts.

---

### Q6: What is the main serving throughput lever?

A) A faster CPU
B) Batching several examples into one inference
C) Caching predictions
D) Smaller models

**Answer: B** - Batching amortises per-request overhead, which dominates at small feature counts.

---

### Q7: How is the batch window chosen?

A) By feel
B) From the latency budget: window plus inference must fit p99
C) To maximise batch fill
D) Randomly

**Answer: B** - The window is pure added latency, so it must be subtracted from the budget.

---

### Q8: Why do requests and limits differ?

A) They should not
B) Requests drive scheduling; limits drive throttling, so limits sit above p99 for burst headroom
C) Limits are optional
D) Requests are for memory, limits for CPU

**Answer: B** - Setting limits equal to requests causes permanent throttling and mysterious p99.

---

### Q9: What causes an OOMKilled container with free heap?

A) A JVM bug
B) Native memory above the limit: metaspace, stacks, direct buffers
C) Too many requests
D) A cold cache

**Answer: B** - The container limit covers all memory, not just the heap.

---

### Q10: How do you make image builds reproducible?

A) Cache aggressively
B) Pin base images by digest and lock dependencies
C) Use a fixed tag
D) Build on a clean VM

**Answer: B** - Mutable tags make 'it works here' a permanent packaging defect.

---

### Q11: What should a liveness probe never do?

A) Return fast
B) Call the model or an external dependency
C) Use HTTP
D) Be frequent

**Answer: B** - Anything slow or dependent turns load into restarts.

---

### Q12: Why record the image digest with the deployment?

A) For billing
B) So you can prove which artefact is running and roll back to it
C) To speed up pulls
D) Because registries require it

**Answer: B** - Version identity is what makes rollback and incident forensics possible.

---

### Q13: What is graceful model reload?

A) Restarting the pod
B) Swapping models without dropping in-flight requests, with readiness covering the swap
C) Loading at build time
D) Using a blue-green deployment

**Answer: B** - Draining in-flight requests while new ones go to the warmed model avoids errors.

---

### Q14: Why is the first request after deploy slower?

A) Cold network
B) JIT compilation, class loading and lazy initialisation
C) Cache misses only
D) DNS

**Answer: B** - Warm-up moves that cost off the request path before readiness.

---

### Q15: Which flag helps capture evidence before a container dies?

A) -Xmx tuning
B) -XX:+HeapDumpOnOutOfMemoryError
C) -XX:MaxMetaspaceSize
D) G1 tuning

**Answer: B** - Dumps preserve evidence; note that OOMKilled itself is external to the JVM.

---

> Score 15/15: you can teach this lab. 12-14: solid. Under 12: re-read THEORY.md sections 3 and 7, then retake.
