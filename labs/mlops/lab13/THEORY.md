# Distributed Training

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

## 1. The Problem This Solves

A model that no longer fits on one device must be split across many, and the split you choose determines whether it trains in minutes or never converges.

Data, model and pipeline parallelism are the vocabulary of modern training. Understanding the communication cost of each strategy is what makes the choice defensible.

## 2. Learning Objectives

- Distinguish data, model, pipeline and sequence parallelism
- Compute communication volume and step time for each strategy
- Implement parameter-server and all-reduce data parallelism
- Explain when model parallelism is unavoidable and what it costs
- Design gradient accumulation and mixed precision correctly
- Diagnose a training run that is slow because of communication, not compute

## 3. Core Concepts

### 3.1 The bottleneck moves, it does not vanish

Splitting a model across devices adds communication. For small models, communication dominates and you are strictly worse off than one device. Data parallelism reduces compute per device; model parallelism reduces the memory that one device must hold. They solve different problems.

### 3.2 Data parallelism and all-reduce

Replicate the model on every device, split the batch, and synchronise gradients once per step. Communication volume per device is proportional to the parameter count, so it is paid every step. Overlapping communication with computation is what makes it tolerable.

### 3.3 Model parallelism

Split layers across devices so each holds only part of the model. Communication is per forward and per backward pass, and activations must cross boundaries. Without pipelining, small microbatches idle most of the devices almost all of the time.

### 3.4 Pipeline parallelism

Splitting layers into stages and overlapping forward of one microbatch with backward of another keeps devices busy. The cost is pipeline bubbles and the memory for stored activations. Bubble ratio falls as microbatches rise, and rises as stages rise.

### 3.5 Parameter servers and asynchronous training

A parameter server decouples workers from the truth. It scales to many cheap workers but introduces staleness, which is why synchronous all-reduce dominates for dense model training and asynchronous schemes survive in recommendation systems with sparser updates.

### 3.6 Memory is the real constraint

Parameters, gradients, optimiser state and activations each multiply. Mixed precision halves the parameter and gradient footprint; gradient checkpointing trades compute for activation memory; sharding the optimiser state is what ZeRO does.

## 4. Key Equations at a Glance

| Symbol | Name | Meaning |
|---|---|---|
| `step_time = compute + comm (or max if overlapped)` | Step time | the diagnostic to start from |
| `allreduce_volume = 2 x (p - 1)/p x params x bytes` | All-reduce cost | ring algorithm, per device |
| `comm_intensity = flops / bytes_moved` | Arithmetic intensity | above ~10 is compute bound |
| `bubble_ratio = (S - 1) / (M + S - 1)` | Pipeline bubble | stages S, microbatches M |
| `optimizer_memory = params x 2 (momentum) x bytes` | Optimiser state | the hidden memory cost |
| `effective_batch = micro_batch x grad_accum x n_devices` | Effective batch | what you actually optimised |

## 5. How the Pieces Fit Together

1. Profile single-device training to find the actual bottleneck: compute, memory or communication.

2. Choose the strategy from that profile: data parallelism first, model parallelism only if memory-bound.

3. Split the batch so each device's micro-batch fits comfortably in memory.

4. Synchronise gradients with all-reduce, overlapping communication with the backward pass.

5. Tune micro-batch count to fill pipeline stages, watching the bubble ratio.

6. Validate convergence: a speedup that costs accuracy has traded away the thing you were optimising.

## 6. Assumptions and Invariants

- The interconnect is fast relative to the compute, or communication dominates and must be overlapped
- Devices are homogeneous, so load imbalance does not appear between them
- Batch size per device is chosen so memory fits with headroom for activations
- Gradient accumulation matches the intended effective batch size
- Mixed precision is validated against the full-precision baseline for loss of accuracy
- Convergence is verified, not assumed, after any parallelism change

## 7. Failure Modes You Will Meet in Production

| Symptom | Root cause | Fix |
|---|---|---|
| Adding GPUs makes training slower | all-reduce volume per step exceeds the saved compute | check comm intensity; overlap or revert to one device |
| Throughput far below peak on multi-GPU | pipeline bubbles with too few microbatches | increase micro-batches; watch the bubble ratio |
| Training diverges after enabling mixed precision | loss scaling missing or too aggressive | use dynamic loss scaling and compare to the fp32 baseline |
| Effective batch differs from what was planned | gradient accumulation miscounted | compute effective batch explicitly and log it |
| Memory error only at long sequences | activations dominate, not parameters | activation checkpointing or sequence parallelism |
| One device is always slower | heterogeneous devices or uneven layer split | balance the split by measured per-stage time |

## 8. Java Building Blocks

| API / class | Why it earns its place here |
|---|---|
| `DoubleBuffer / tensor row-major layout` | a minimal tensor abstraction for gradient exchange |
| `ExecutorService for per-device workers` | one task per device per phase |
| `float[] for gradients under mixed precision` | half the bytes on the wire and in memory |
| `AtomicLong counters for step timing` | separating compute from communication time |
| `record ParallelConfig(int devices, int microBatch, int gradAccum)` | explicit, logged parallel configuration |

## 9. Where This Sits in the Larger System

- **labs/ml/lab09** supplies the boosting or model this training runs.
- **mlops/lab06** provides the node pool and the interconnect that sets the ceiling.
- **mlops/lab12** provisions and quotas the accelerators this lab uses.
- **mlops/lab14** runs hyperparameter sweeps on top of this training loop.

## 10. Self-Assessment Before You Ship Anything

Score yourself 0-2 on each. Any zero below means you are not ready to operate this in production.

- [ ] 0 — cannot yet — Distinguish data, model, pipeline and sequence parallelism
- [ ] 0 — cannot yet — Compute communication volume and step time for each strategy
- [ ] 0 — cannot yet — Implement parameter-server and all-reduce data parallelism
- [ ] 0 — cannot yet — Explain when model parallelism is unavoidable and what it costs
- [ ] 0 — cannot yet — Design gradient accumulation and mixed precision correctly
- [ ] 0 — cannot yet — Diagnose a training run that is slow because of communication, not compute

## 11. Summary Checklist

- [ ] I profiled single-device training before scaling out.
- [ ] I can state the communication volume per step for my strategy.
- [ ] The effective batch size is computed and logged.
- [ ] Mixed precision is validated against a full-precision baseline.
- [ ] Pipeline bubble ratio is measured, not assumed.
- [ ] Convergence was verified after the change.
