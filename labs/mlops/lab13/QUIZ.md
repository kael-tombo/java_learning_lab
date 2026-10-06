# Distributed Training - Quiz (15 Questions)

**Track:** mlops  |  **Lab:** lab13  |  **Level:** Advanced

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

### Q1: What does data parallelism solve?

A) Memory per device
B) Compute per device, by splitting the batch
C) The parameter count
D) The learning rate

**Answer: B** - Each device holds the full model but a slice of the batch, and gradients are reduced.

---

### Q2: What does model parallelism solve?

A) Compute per device
B) Memory per device, by splitting layers
C) Communication
D) Batch size

**Answer: B** - Each device holds only part of the model, so activations cross boundaries.

---

### Q3: Why can adding GPUs make training slower?

A) GPUs are unreliable
B) All-reduce volume per step exceeds the compute saved
C) The dataset is too small
D) Memory fragmentation

**Answer: B** - For small models or slow interconnects, communication dominates.

---

### Q4: What is the pipeline bubble ratio?

A) (S-1)/(M+S-1)
B) 1 - M/S
C) M/(M+S)
D) S/M

**Answer: A** - Stages S and microbatches M give (S-1)/(M+S-1); more microbatches shrink the bubble.

---

### Q5: How do you reduce the pipeline bubble?

A) More stages
B) More microbatches
C) Larger batch per microbatch
D) Lower precision

**Answer: B** - More microbatches fill the schedule, at the cost of activation memory.

---

### Q6: What is gradient accumulation for?

A) Faster steps
B) Simulating a larger effective batch within per-device memory
C) Reducing memory
D) Improving convergence

**Answer: B** - It accumulates gradients over micro-batches before stepping the optimiser.

---

### Q7: What is the effective batch size?

A) The per-device micro-batch
B) Micro-batch times accumulation times device count
C) The dataset size
D) The memory limit

**Answer: B** - That is the batch the optimiser actually sees.

---

### Q8: Why does mixed precision need loss scaling?

A) To save memory
B) To keep small gradients from underflowing in fp16
C) To speed up data loading
D) To reduce noise

**Answer: B** - Gradients underflow fp16's range; scaling restores them, then is reduced adaptively.

---

### Q9: What dominates memory in training?

A) Activations only
B) Often optimiser state, which is 2x parameter bytes for momentum
C) The dataset
D) The loss

**Answer: B** - Adam-style momentum doubles optimiser state, which surprises people who budget only for parameters.

---

### Q10: What does ZeRO shard?

A) Only the data
B) Optimiser, gradient and parameter state across devices
C) The activations
D) The learning rate

**Answer: B** - That is why it cuts per-device memory so much.

---

### Q11: What is arithmetic intensity?

A) FLOPs per byte moved
B) Bytes per FLOP
C) Memory utilisation
D) GPU occupancy

**Answer: A** - Above roughly 10 you are compute bound, so parallelism helps rather than hurts.

---

### Q12: How do you overlap communication with compute?

A) Run it on another thread
B) Bucket gradients and start reducing early buckets during backward
C) Reduce precision
D) Use fewer layers

**Answer: B** - Bucketed overlap hides a substantial fraction of all-reduce time.

---

### Q13: What is asynchronous training good for?

A) Dense transformer training
B) Sparse incremental updates such as recommenders, where staleness is tolerable
C) Small models
D) Evaluation

**Answer: B** - Parameter servers suit sparse updates; synchronous all-reduce dominates dense training.

---

### Q14: What must you verify after changing parallelism?

A) Nothing
B) Convergence, since a speedup can cost accuracy
C) Only memory
D) Only throughput

**Answer: B** - Effective batch changes alter the optimisation trajectory.

---

### Q15: Why balance stages by measured time?

A) Aesthetics
B) Layer counts do not predict compute; uneven stages leave devices idle
C) To reduce memory
D) To simplify code

**Answer: B** - The slowest stage sets the step time, so balance by measurement.

---

> Score 15/15: you can teach this lab. 12-14: solid. Under 12: re-read THEORY.md sections 3 and 7, then retake.
