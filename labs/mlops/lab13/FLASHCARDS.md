# Distributed Training - Flashcards (60 cards)

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

**Format.** Question (front) -> answer (back). Use for spaced repetition: day 0, day 1, day 3, day 7, day 21. Do not read the answer first.

| # | Front | Back |
|---|---|---|
| 1 | What problem does data parallelism solve? | Compute per device: each device holds the whole model but a slice of the batch. |
| 2 | What problem does model parallelism solve? | Memory per device: each device holds only part of the model. |
| 3 | What dominates data-parallel training for small models? | The all-reduce of gradients, which is proportional to parameter count every step. |
| 4 | What is the pipeline bubble ratio? | (stages - 1) / (microbatches + stages - 1); it shrinks with more microbatches. |
| 5 | Why can adding GPUs make training slower? | Communication per step exceeds the compute saved, especially with a slow interconnect. |
| 6 | What does mixed precision buy? | Halves parameter and gradient memory and speeds up matmuls, with loss-scaling required to avoid divergence. |
| 7 | What is gradient accumulation for? | Simulating a larger effective batch without exceeding per-device memory. |
| 8 | What is ZeRO? | Sharding optimiser, gradient and parameter state across devices to cut per-device memory. |
| 9 | What is The bottleneck moves, it does not vanish? | Splitting a model across devices adds communication. |
| 10 | What is Data parallelism and all-reduce? | Replicate the model on every device, split the batch, and synchronise gradients once per step. |
| 11 | What is Model parallelism? | Split layers across devices so each holds only part of the model. |
| 12 | What is Pipeline parallelism? | Splitting layers into stages and overlapping forward of one microbatch with backward of another keeps devices busy. |
| 13 | What is Parameter servers and asynchronous training? | A parameter server decouples workers from the truth. |
| 14 | What is Memory is the real constraint? | Parameters, gradients, optimiser state and activations each multiply. |
| 15 | In this lab, what does `step_time = compute + comm (or max if overlapped)` mean? | Step time: the diagnostic to start from |
| 16 | In this lab, what does `allreduce_volume = 2 x (p - 1)/p x params x bytes` mean? | All-reduce cost: ring algorithm, per device |
| 17 | In this lab, what does `comm_intensity = flops / bytes_moved` mean? | Arithmetic intensity: above ~10 is compute bound |
| 18 | In this lab, what does `bubble_ratio = (S - 1) / (M + S - 1)` mean? | Pipeline bubble: stages S, microbatches M |
| 19 | In this lab, what does `optimizer_memory = params x 2 (momentum) x bytes` mean? | Optimiser state: the hidden memory cost |
| 20 | In this lab, what does `effective_batch = micro_batch x grad_accum x n_devices` mean? | Effective batch: what you actually optimised |
| 21 | You see 'Adding GPUs makes training slower' in production. What is the cause and the fix? | all-reduce volume per step exceeds the saved compute Fix: check comm intensity; overlap or revert to one device |
| 22 | You see 'Throughput far below peak on multi-GPU' in production. What is the cause and the fix? | pipeline bubbles with too few microbatches Fix: increase micro-batches; watch the bubble ratio |
| 23 | You see 'Training diverges after enabling mixed precision' in production. What is the cause and the fix? | loss scaling missing or too aggressive Fix: use dynamic loss scaling and compare to the fp32 baseline |
| 24 | You see 'Effective batch differs from what was planned' in production. What is the cause and the fix? | gradient accumulation miscounted Fix: compute effective batch explicitly and log it |
| 25 | You see 'Memory error only at long sequences' in production. What is the cause and the fix? | activations dominate, not parameters Fix: activation checkpointing or sequence parallelism |
| 26 | You see 'One device is always slower' in production. What is the cause and the fix? | heterogeneous devices or uneven layer split Fix: balance the split by measured per-stage time |
| 27 | Which Java API is the backbone of: a minimal tensor abstraction for gradient exchange | `DoubleBuffer / tensor row-major layout` |
| 28 | Which Java API is the backbone of: one task per device per phase | `ExecutorService for per-device workers` |
| 29 | Which Java API is the backbone of: half the bytes on the wire and in memory | `float[] for gradients under mixed precision` |
| 30 | Which Java API is the backbone of: separating compute from communication time | `AtomicLong counters for step timing` |
| 31 | Which Java API is the backbone of: explicit, logged parallel configuration | `record ParallelConfig(int devices, int microBatch, int gradAccum)` |
| 32 | Why does The bottleneck moves, it does not vanish matter operationally? | Splitting a model across devices adds communication. |
| 33 | Why does Data parallelism and all-reduce matter operationally? | Replicate the model on every device, split the batch, and synchronise gradients once per step. |
| 34 | Why does Model parallelism matter operationally? | Split layers across devices so each holds only part of the model. |
| 35 | Why does Pipeline parallelism matter operationally? | Splitting layers into stages and overlapping forward of one microbatch with backward of another keeps devices busy. |
| 36 | Why does Parameter servers and asynchronous training matter operationally? | A parameter server decouples workers from the truth. |
| 37 | Why does Memory is the real constraint matter operationally? | Parameters, gradients, optimiser state and activations each multiply. |
| 38 | In the Distributed Training pipeline, what happens next? Profile single-device training to find the actual bottleneck... | Profile single-device training to find the actual bottleneck: compute, memory or communication. |
| 39 | In the Distributed Training pipeline, what happens next? Choose the strategy from that profile: data parallelism firs... | Choose the strategy from that profile: data parallelism first, model parallelism only if memory-bound. |
| 40 | In the Distributed Training pipeline, what happens next? Split the batch so each device's micro-batch fits comfortabl... | Split the batch so each device's micro-batch fits comfortably in memory. |
| 41 | In the Distributed Training pipeline, what happens next? Synchronise gradients with all-reduce, overlapping communica... | Synchronise gradients with all-reduce, overlapping communication with the backward pass. |
| 42 | In the Distributed Training pipeline, what happens next? Tune micro-batch count to fill pipeline stages, watching the... | Tune micro-batch count to fill pipeline stages, watching the bubble ratio. |
| 43 | In the Distributed Training pipeline, what happens next? Validate convergence: a speedup that costs accuracy has trad... | Validate convergence: a speedup that costs accuracy has traded away the thing you were optimising. |
| 44 | Exercise focus: Profile before you scale | Find the actual bottleneck first. |
| 45 | Exercise focus: Data parallel with all-reduce | The workhorse, implemented. |
| 46 | Exercise focus: Effective batch and gradient accumulation | Get the optimisation contract right. |
| 47 | Exercise focus: Mixed precision done properly | Speed and memory without divergence. |
| 48 | Exercise focus: Model parallelism and its cost | See why it is a last resort. |
| 49 | Exercise focus: Pipeline scheduling and bubbles | Keep the devices busy. |
| 50 | State the All-reduce volume and the communication-bound threshold result for Distributed Training. | P = 70M params in fp16 (2 bytes), p = 8: volume per device = 2 x (7/8) x 70M x 2 = 245 MB. At 100 GB/s effective, comm is 2.45 ms per step. If a step is 100 ms of compute, you are compute bound and 8-way data parallel is a good deal. |
| 51 | State the Pipeline bubble ratio result for Distributed Training. | S = 4, M = 4: bubble = 3/7 = 0.43, efficiency 57%. S = 4, M = 8: bubble = 3/11 = 0.27, efficiency 73%. S = 8, M = 8: bubble = 7/15 = 0.47, so doubling stages halved the benefit. |
| 52 | State the Effective batch and the optimisation contract result for Distributed Training. | micro 64, accumulation 4, 8 devices: effective batch 2048. If the plan assumed 1024, the learning rate and schedule need revisiting — the same code with different accumulation is a different experiment. |
| 53 | State the Memory budget for optimiser state result for Distributed Training. | P = 70M: fp32 with momentum = 70M x 4 x 4 = 1.12 GB; fp16 params with fp32 optimiser = 560 MB; ZeRO-3 across 8 devices shards optimiser and params, landing near 210 MB per device plus activations. |
| 54 | What is arithmetic intensity? | FLOPs per byte moved; above roughly 10 you are compute bound and parallelism helps. |
| 55 | How do you overlap all-reduce with compute? | Bucket gradients and start the reduce of earlier buckets while later backward passes still run. |
| 56 | Why does asynchronous training still exist in recommender systems? | Sparse, incremental updates suit parameter servers, where staleness is tolerable. |
| 57 | What is activation checkpointing? | Recomputing activations during backward to save memory at the cost of extra compute. |
| 58 | Assumption / invariant to defend: The interconnect is fast relative to the compute, or communication dom... | The interconnect is fast relative to the compute, or communication dominates and must be overlapped |
| 59 | Assumption / invariant to defend: Devices are homogeneous, so load imbalance does not appear between the... | Devices are homogeneous, so load imbalance does not appear between them |
| 60 | Assumption / invariant to defend: Batch size per device is chosen so memory fits with headroom for activ... | Batch size per device is chosen so memory fits with headroom for activations |

## Deck Notes

- Rows are generated from this lab's own concepts, equations, failure modes and Java APIs - if you disagree with a card, fix the card.
- The last block of cards is deliberately operational: they are the questions a staff engineer gets asked in a design review.
