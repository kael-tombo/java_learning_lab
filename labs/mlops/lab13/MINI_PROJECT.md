# MINI_PROJECT — Multi-Device Training with Communication Accounting

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

**Brief.** Compare single-device, data-parallel and pipeline-parallel training with explicit communication accounting and convergence checks.

**Timebox.** 4 hours

## 1. Why This Project Exists

The lesson people miss is that adding devices can make training slower. Measuring the exchange rate is the only way to learn that before you pay for a cluster.

## 2. Requirements

- Single-device profile with compute and communication split, plus arithmetic intensity.
- Data-parallel implementation with all-reduce, verified against per-device mean gradients.
- Speedup and efficiency plot across device counts, with communication ratio reported.
- Effective batch computed, logged, and validated against the plan at startup.
- Mixed precision with dynamic loss scaling compared to a full-precision baseline.
- Pipeline schedule with measured bubble ratio across microbatch counts.
- Memory budget covering parameters, gradients, optimiser state and activations.

## 3. Build Order

| Step | Time | What you do | Done when |
|---|---|---|---|
| 1 | 30m | Single-device profile and arithmetic intensity | A profile that predicts scaling |
| 2 | 40m | Data parallel all-reduce with verification | A verified gradient reduction |
| 3 | 30m | Speedup and efficiency across device counts | A plot with the comm ratio |
| 4 | 25m | Effective batch validation and loss-curve comparison | A matched loss curve |
| 5 | 35m | Mixed precision with dynamic loss scaling | An fp32 comparison |
| 6 | 35m | Pipeline scheduler with bubble measurement | A bubble sweep |
| 7 | 30m | Memory budget across configurations | A memory table |

## 4. Architecture Sketch

```text
 single device -- profile --> arithmetic intensity
     |                                |
     |                        predict scaling
     v                                v
 data parallel (all-reduce) --> speedup / efficiency / comm ratio
     |                                |
 effective batch validation      mixed precision vs fp32
     |                                |
 pipeline schedule (M sweep) --> bubble ratio vs activation memory
     |
 memory budget: params + grads + optimiser + activations
```

## 5. Implementation Notes

- Verify all-reduce correctness against a hand-computed mean before timing anything.
- Report the comm ratio with every speedup number; speedup alone is misleading.
- Changing accumulation changes the experiment, so validate the effective batch at startup.
- The bubble sweep should be accompanied by activation memory, since more microbatches cost memory.

## 6. Deliverables

1. Single-device profile with arithmetic intensity and a scaling prediction.
1. Verified data-parallel implementation with a speedup and efficiency plot.
1. Mixed precision comparison against fp32 with matched loss curves.
1. Pipeline bubble sweep and a four-term memory budget table.

## 7. Grading Rubric

| Dimension | Weight | What earns full marks |
|---|---|---|
| Correctness | 30% | Gradients verified; effective batch validated; loss curves matched |
| Measurement | 30% | Compute and comm timed separately; efficiency and comm ratio reported |
| Strategy choice | 20% | Recommendations justified by the numbers, not preference |
| Memory | 20% | Four-term budget with mixed precision and sharding variants |

## 8. Stretch Goals

- Implement bucketed all-reduce overlap and report the hidden fraction.
- Add optimiser state sharding and measure per-device memory.
- Add sequence-parallel attention splitting for long contexts.

## 9. Definition of Done

You are finished when every box below is checked, not when the code compiles.

- [ ] Single-device profile with compute and communication split, plus arithmetic intensity.
- [ ] Data-parallel implementation with all-reduce, verified against per-device mean gradients.
- [ ] Speedup and efficiency plot across device counts, with communication ratio reported.
- [ ] Effective batch computed, logged, and validated against the plan at startup.
- [ ] Mixed precision with dynamic loss scaling compared to a full-precision baseline.
- [ ] Pipeline schedule with measured bubble ratio across microbatch counts.
- [ ] A stranger can reproduce the reported numbers with one command
- [ ] The limitations section says what this cannot do
- [ ] At least one number is alerted on in production

## 10. Retrospective Template

- What worked:
- What surprised me:
- The one number I would alert on in production:
- What I would delete before shipping this to real users:
