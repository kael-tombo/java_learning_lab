# Distributed Training - Mathematical Foundations

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

## Notation

| Symbol | Meaning |
|---|---|
| `step_time = compute + comm (or max if overlapped)` | Step time - the diagnostic to start from |
| `allreduce_volume = 2 x (p - 1)/p x params x bytes` | All-reduce cost - ring algorithm, per device |
| `comm_intensity = flops / bytes_moved` | Arithmetic intensity - above ~10 is compute bound |
| `bubble_ratio = (S - 1) / (M + S - 1)` | Pipeline bubble - stages S, microbatches M |
| `optimizer_memory = params x 2 (momentum) x bytes` | Optimiser state - the hidden memory cost |
| `effective_batch = micro_batch x grad_accum x n_devices` | Effective batch - what you actually optimised |

## Why the Math Matters

Distributed training is a memory-versus-communication trade: bandwidth, bubble arithmetic and optimiser state dominate the accounting, and arithmetic intensity tells you which regime you are in.


---

## 1. All-reduce volume and the communication-bound threshold

```text
ring all-reduce per device: 2 (p - 1)/p x P x bytes
comm_time = volume / bandwidth
compute_time = flops / device_flops
compute bound iff flops/bytes > bandwidth/device_flops
```

The ratio of communication to compute decides whether parallelism helps at all. Model size and interconnect bandwidth, not GPU count, determine whether you are in a good regime.

**Worked example.** P = 70M params in fp16 (2 bytes), p = 8: volume per device = 2 x (7/8) x 70M x 2 = 245 MB. At 100 GB/s effective, comm is 2.45 ms per step. If a step is 100 ms of compute, you are compute bound and 8-way data parallel is a good deal.


---

## 2. Pipeline bubble ratio

```text
bubble_ratio = (S - 1) / (M + S - 1)
efficiency = 1 - bubble_ratio
S stages, M microbatches
```

Pipeline utilisation depends on the ratio of stages to microbatches. Memory for stored activations rises with M, so you trade utilisation against memory, and the optimum is usually a small M for inference and a larger one for training.

**Worked example.** S = 4, M = 4: bubble = 3/7 = 0.43, efficiency 57%. S = 4, M = 8: bubble = 3/11 = 0.27, efficiency 73%. S = 8, M = 8: bubble = 7/15 = 0.47, so doubling stages halved the benefit.


---

## 3. Effective batch and the optimisation contract

```text
effective_batch = micro_batch x grad_accum x p
each optimiser step uses gradients averaged over the effective batch
LR scaling should account for the change
```

Gradient accumulation changes the batch the optimiser sees, which changes the optimisation trajectory. Logging the effective batch makes a reproduction possible and prevents a silent mismatch with the plan.

**Worked example.** micro 64, accumulation 4, 8 devices: effective batch 2048. If the plan assumed 1024, the learning rate and schedule need revisiting — the same code with different accumulation is a different experiment.


---

## 4. Memory budget for optimiser state

```text
total = P x bytes x (1 params + 1 grads + 2 optimiser + A activations)
mixed precision: P x 2 x (1 + 1 + 2) = 8P bytes
ZeRO stage 3: divide sharded terms by p
```

Optimiser state usually dominates, which surprises people who budget only for parameters and gradients. ZeRO and mixed precision attack different terms, which is why they compose.

**Worked example.** P = 70M: fp32 with momentum = 70M x 4 x 4 = 1.12 GB; fp16 params with fp32 optimiser = 560 MB; ZeRO-3 across 8 devices shards optimiser and params, landing near 210 MB per device plus activations.


---

## Cheat Sheet

- `step_time = compute + comm (or max if overlapped)` - Step time
- `allreduce_volume = 2 x (p - 1)/p x params x bytes` - All-reduce cost
- `comm_intensity = flops / bytes_moved` - Arithmetic intensity
- `bubble_ratio = (S - 1) / (M + S - 1)` - Pipeline bubble
- `optimizer_memory = params x 2 (momentum) x bytes` - Optimiser state
- `effective_batch = micro_batch x grad_accum x n_devices` - Effective batch

## Numerical Traps

- Scaling to more devices without checking whether communication dominates.
- Computing bubble ratio with microbatches and stages confused.
- Changing accumulation or parallelism without recomputing the effective batch.
- Enabling mixed precision without a loss scale or a divergence check.
- Budgeting memory for parameters while ignoring optimiser state.

## Self-Check Problems

1. Compute all-reduce volume per device and step for a given parameter count, device count and dtype.
2. Compare compute and communication time for a given interconnect and device throughput; state the regime.
3. Compute bubble ratio and efficiency for several stage and microbatch combinations; pick an operating point.
4. Compute effective batch for micro-batch, accumulation and device count; compare against the plan.
5. Build a memory budget for parameters, gradients, optimiser state and activations, with mixed precision and ZeRO variants.
