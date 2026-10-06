# Distributed Training - Exercises

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

## How To Work These

Work in order. Each exercise builds the next; do not skip ahead.
Every exercise ends with a *deliverable* you can show someone - code that compiles, a number you can defend, or a table you can regenerate.

Run the lab as you go:

```bash
cd lab13
javac -d out $(Get-ChildItem -Recurse -Filter *.java src | ForEach-Object { $_.FullName })
java -cp out DistributedTrainingLab
```

## Exercise 1: Profile before you scale

**Task.** Find the actual bottleneck first.

**Steps**
- Measure single-device step time split into compute and memory-bound stalls.
- Compute arithmetic intensity for the model.
- Predict whether k-way data parallelism helps.
- Verify the prediction with a 2-device run.

**Deliverable.** A profile that predicts your scaling decision.

## Exercise 2: Data parallel with all-reduce

**Task.** The workhorse, implemented.

**Steps**
- Split the batch across devices and reduce gradients.
- Verify reduced gradients equal the mean of per-device gradients.
- Time compute and communication separately.
- Sweep device count and plot speedup and efficiency.

**Deliverable.** A speedup and efficiency plot with the comm ratio.

## Exercise 3: Effective batch and gradient accumulation

**Task.** Get the optimisation contract right.

**Steps**
- Implement accumulation across micro-batches.
- Compute and log the effective batch.
- Reject a mismatch with the plan at startup.
- Compare loss curves against a single large batch.

**Deliverable.** A validated accumulation implementation.

## Exercise 4: Mixed precision done properly

**Task.** Speed and memory without divergence.

**Steps**
- Add fp16 parameters with fp32 optimiser state.
- Implement dynamic loss scaling.
- Compare the loss curve to fp32.
- Report memory and step time for both.

**Deliverable.** A precision comparison with a loss-curve match.

## Exercise 5: Model parallelism and its cost

**Task.** See why it is a last resort.

**Steps**
- Split layers across two devices.
- Transfer activations at the boundary and time it.
- Measure step time versus the single-device baseline.
- Explain the regime where this is unavoidable.

**Deliverable.** A model-parallel timing comparison.

## Exercise 6: Pipeline scheduling and bubbles

**Task.** Keep the devices busy.

**Steps**
- Implement a microbatch schedule over S stages.
- Compute the bubble ratio and verify occupancy.
- Sweep M and show utilisation improving.
- Trade off against activation memory.

**Deliverable.** A bubble-ratio sweep with an operating point.

## Exercise 7: Memory budget and ZeRO

**Task.** Optimiser state is the surprise.

**Steps**
- Build a memory budget for all four terms.
- Add mixed precision and measure.
- Add optimiser state sharding and measure.
- Report per-device memory in each configuration.

**Deliverable.** A memory table across three configurations.

## Exercise 8: Communication overlap

**Task.** Hide the cost you cannot remove.

**Steps**
- Bucket gradients and start early reduces.
- Overlap reduce with the backward pass.
- Measure step time with and without overlap.
- Report the fraction hidden.

**Deliverable.** An overlap measurement with a hidden fraction.


---

## Self-Check Before You Move On

- [ ] I profiled before scaling out.
- [ ] I can state the communication volume per step.
- [ ] My effective batch matches the plan.
- [ ] Convergence was verified, not assumed.
