# Kubernetes for ML - Quiz (15 Questions)

**Track:** mlops  |  **Lab:** lab06  |  **Level:** Advanced

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

### Q1: What does a failing readiness probe do?

A) Restarts the pod
B) Removes it from the Service without restarting
C) Deletes the pod
D) Restarts the node

**Answer: B** - Readiness controls routing; liveness controls restarts.

---

### Q2: Why must liveness not check external dependencies?

A) It is slower
B) A dependency blip would restart the whole fleet
C) It uses more memory
D) Kubernetes forbids it

**Answer: B** - That converts a dependency outage into a cluster-wide restart storm.

---

### Q3: What is a startup probe for?

A) Faster boots
B) Allowing long cold starts without liveness killing the pod mid-load
C) Reporting versions
D) Setting resources

**Answer: B** - Startup gates the other probes until the process is actually serving.

---

### Q4: What do requests control?

A) Throttling
B) Scheduling: the amount reserved on the node
C) Memory only
D) Pod priority

**Answer: B** - The scheduler packs by requests, so under-requesting overcommits.

---

### Q5: What do limits control?

A) Scheduling
B) Hard caps that cause throttling or OOMKill
C) Autoscaling
D) Routing

**Answer: B** - Exceeding memory is an OOMKill; exceeding CPU is throttling.

---

### Q6: Why set limits above requests?

A) Convention
B) So a burst is not permanently throttled and native memory has headroom
C) To reduce cost
D) To allow larger requests

**Answer: B** - Equal limits cause permanent throttling and mysterious p99 spikes.

---

### Q7: What is a PodDisruptionBudget for?

A) Memory limits
B) Keeping a floor on available replicas during voluntary disruption
C) Cost control
D) Image pinning

**Answer: B** - Without one, a node drain or cluster upgrade can take the service down.

---

### Q8: Why is CPU a poor autoscaling signal for inference?

A) CPU metrics are unreliable
B) Inference is batched and bursty, so CPU lags user-visible latency
C) CPU is expensive
D) Autoscalers cannot read CPU

**Answer: B** - Queue depth or in-flight requests track experience more directly.

---

### Q9: What causes p99 spikes minutes after a deploy?

A) Cold DNS
B) The rollout removing too much capacity at once
C) A feature bug
D) Cache eviction

**Answer: B** - maxUnavailable controls how much Service capacity disappears mid-rollout.

---

### Q10: Why spread replicas across zones?

A) Cost
B) A zone outage or drain would otherwise remove every replica in that zone
C) To improve latency
D) To satisfy the scheduler

**Answer: B** - Topology spread turns a zone event into a degradation rather than an outage.

---

### Q11: What does a node affinity rule do?

A) Spread pods
B) Pin pods to node pools with specific hardware or memory profiles
C) Set limits
D) Gate readiness

**Answer: B** - Affinity selects the pool; spread distributes within it.

---

### Q12: A pod is Running but never becomes Ready. Check first?

A) Node capacity
B) The readiness probe path, thresholds and warm-up gating
C) Image size
D) Service selector

**Answer: B** - Running says the process started; Ready says the probe passed.

---

### Q13: How many replicas can be unavailable during a rollout with maxUnavailable 25% and 40 replicas?

A) 40
B) 10
C) 25
D) 0

**Answer: B** - 25% of 40 is 10 pods removed from Service capacity during the update.

---

### Q14: Why do people set CPU limits at all?

A) They should not
B) To bound contention on a shared node, accepting burst throttling
C) To reserve CPU
D) To speed up scheduling

**Answer: B** - Limits bound blast radius on shared nodes; requests do the reservation.

---

### Q15: What is the main purpose of a readiness gate on warm-up?

A) To reduce memory
B) So the Service never routes to a cold pod
C) To trigger autoscaling
D) To satisfy the scheduler

**Answer: B** - Otherwise the first users after each deploy absorb JIT and lazy-load cost.

---

> Score 15/15: you can teach this lab. 12-14: solid. Under 12: re-read THEORY.md sections 3 and 7, then retake.
