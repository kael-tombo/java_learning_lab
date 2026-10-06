# Distributed Training - Vision & Where This Is Going

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

## 1. The Future State

Distributed training converges on sequence and expert parallelism with 3D sharding, plus adaptive parallelism that chooses the split per layer from measured cost. The load-bearing skill is the communication accounting that tells you which strategy is even worth trying.

The test of that future state is boring: a new engineer ships a change to distributed training on day two without asking anyone where the magic lives.

## 2. What "Good" Looks Like in Practice

- Single-device profiling precedes any scaling decision.
- Communication volume per step is computed and reported.
- Effective batch is logged and verified against the plan.
- Mixed precision is validated against a full-precision baseline.

## 3. Capability Ladder

| Level | Capability | You can... |
|---|---|---|
| L1 | Diagnose | Profile single-device training and compute arithmetic intensity. |
| L2 | Scale | Data parallel with all-reduce, timing compute and comm separately. |
| L3 | Fit | Model and pipeline parallelism with bubble accounting. |
| L4 | Tune | Overlap, sharding and mixed precision validated against a baseline. |

## 4. Behaviours to Build

Profile before scaling. Compute the communication cost before adding devices. Verify convergence after any parallelism change, because a speedup that costs accuracy is not a speedup.

## 5. Anti-Vision (the failure mode we are avoiding)

- Eight GPUs trained because the cluster was free.
- Mixed precision switched on with no loss scaling and no baseline.
- Pipeline stages split by layer count.
- Effective batch silently changed by accumulation settings.

## 6. Technology Shifts That Change the Work

1. 3D parallelism combining tensor, pipeline and sequence sharding.
1. Expert parallelism for mixture-of-experts models with all-to-all communication.
1. FSDP-style full sharding of parameters, gradients and optimiser state.
1. Adaptive parallelism choosing per-layer strategy from measured cost.

## 7. Your 30/60/90 Commitment

- **30 days.** Profile single-device training and compute arithmetic intensity.
- **60 days.** Implement data parallel all-reduce with separate compute and comm timing.
- **90 days.** Add pipeline scheduling with bubble accounting and validate mixed precision against fp32.

## 8. How To Tell You Are Actually Getting Better

- I can state the communication volume per step for my strategy.
- I profile before scaling.
- My effective batch matches the plan.
- Convergence is verified after every parallelism change.

## 9. Principles That Should Not Change

- **Distinguish data, model, pipeline** Distinguish data, model, pipeline and sequence parallelism
- **Compute communication volume** Compute communication volume and step time for each strategy
- **Implement parameter-server** Implement parameter-server and all-reduce data parallelism

> Parallelism is a trade of memory for communication; knowing the exchange rate is the whole skill.
