# Distributed Training - Code Deep Dive

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

## 1. Module Map

```text
src/
  DistributedTrainingLab.java   driver: single vs multi-device step timing
  ParallelConfig.java           devices, micro-batch, accumulation, dtype, logged
  Tensor.java                   minimal row-major float/double tensor
  DataParallelTrainer.java      all-reduce over per-device gradients with timing split
  ModelParallelTrainer.java     layer split across devices, activation transfer
  PipelineScheduler.java        microbatch schedule with bubble accounting
  StepTimer.java                compute vs communication timing for diagnosis
```

StepTimer records compute and communication separately for every step. Without that split, 'training is slow' is unactionable; with it, the strategy choice follows from the numbers.

## 2. Core Types

| Type | Responsibility |
|---|---|
| `ParallelConfig` | devices, micro-batch, accumulation, dtype, recorded per run |
| `Tensor` | minimal row-major array with dtype-aware element size |
| `DataParallelTrainer` | per-device gradients, all-reduce, timing split |
| `PipelineScheduler` | microbatch schedule with explicit bubble accounting |

---

## 3.1 All-reduce with compute/communication timing split

Ring all-reduce across devices, with the two phases timed separately so the strategy choice follows from measurement.

```java
StepStats step(Tensor[] perDeviceBatch) {
    long t0 = System.nanoTime();
    // backward on each device produces local gradients
    Tensor localGrad = backwardOnEachDevice(perDeviceBatch);
    long t1 = System.nanoTime();                     // compute boundary, measured

    allReduceInPlace(localGrad, devices);            // ring reduce across devices
    scaleBy(1.0 / devices);                          // average, then step
    optimiser.step(localGrad);
    long t2 = System.nanoTime();

    // the split is the whole point: it tells you which strategy to choose
    return new StepStats(computeMs(t0, t1), commMs(t1, t2), gradientBytes(localGrad));
}

private void allReduceInPlace(Tensor g, int devices) {
    for (int step : ringSchedule(devices)) {         // pipeline the chunks
        Tensor chunk = g.chunk(step);
        for (int d : neighbours(step, devices)) chunk.reduceFrom(d);
        g.putChunk(step, chunk);
    }
}
```


---

## 3.2 Effective batch computed and logged, never assumed

The optimiser's view of the batch is the product of micro-batch, accumulation and device count, and it is part of the run record.

```java
ParallelConfig validate(ParallelConfig cfg, int plannedEffectiveBatch) {
    int effective = cfg.microBatch() * cfg.gradAccum() * cfg.devices();
    if (effective != plannedEffectiveBatch)
        throw new IllegalStateException("effective batch " + effective
                + " != planned " + plannedEffectiveBatch
                + "; LR schedule and results would not match the experiment");
    return cfg;                                      // logged with every run record
}

// log both, so a reproduction knows exactly what the optimiser saw
LOG.info("parallel config: devices={} microBatch={} gradAccum={} effectiveBatch={} dtype={}",
        cfg.devices(), cfg.microBatch(), cfg.gradAccum(), effective, cfg.dtype());
```


---

## 4. Cost Model

| Operation | Complexity | Notes |
|---|---|---|
| All-reduce per step | `O(p x P) bytes per device` | the dominant cost for small models |
| Model-parallel forward | `O(activations at boundaries) per microbatch` | depends on where the split falls |
| Pipeline overhead | `O(S x M) scheduling` | negligible compute; the cost is bubbles |
| Mixed precision step | `~half the bytes of fp32` | 2-3x faster matmul on modern accelerators |

## 5. Correctness and Numerics

- Time compute and communication separately for every step.
- Accumulate gradients in the dtype you reduce in, then cast once.
- Log the effective batch size with every run record.
- Use dynamic loss scaling when enabling mixed precision, and compare to fp32.
- Balance stage assignment by measured per-stage time, not by layer count.

## 6. Test Strategy

- Gradient values after all-reduce equal the mean of the per-device gradients.
- Effective batch computation rejects a mismatch with the plan.
- Mixed precision with dynamic loss scaling matches the fp32 loss curve within tolerance.
- Bubble ratio computed by the scheduler matches the closed form.
- Single-device and data-parallel runs agree on gradients to float tolerance.
- Timing output reports compute and communication separately.

## 7. Extension Points

- Implement bucketed overlap of all-reduce with the backward pass.
- Add ZeRO-style optimiser state sharding and measure per-device memory.
- Add sequence-parallel splitting of attention for long-context training.

## 8. Review Checklist

- [ ] Parallel configuration is explicit and logged with effective batch
- [ ] Compute and communication timed separately
- [ ] Mixed precision validated against a full-precision baseline
- [ ] Effective batch verified against the plan at startup
- [ ] Stage assignment balanced by measured time
- [ ] Convergence verified after any parallelism change
