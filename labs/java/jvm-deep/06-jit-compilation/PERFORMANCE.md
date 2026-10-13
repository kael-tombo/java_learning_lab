# Performance: JIT Compilation

## The warmup curve is the whole game

First iterations of `LoopWork` run interpreted or in C1 code: each
bytecode pays dispatch. After ~5000 invocations C2 installs unrolled,
register-allocated code and per-iteration cost collapses. The reference
run measured ~29x between `-Xint` and fully warmed JIT; the lab asserts
>3x so the signal survives slow or noisy machines.

## How to measure honestly

Warm up past tier-4 thresholds before starting the timer, or include
warmup explicitly as the thing under test. Pin the heap (`-Xmx`) so GC
pauses do not contaminate compile timings. Use ratio assertions with wide
margins rather than absolute millisecond claims that vary per machine.

## What actually moves the needle

Inlining hot callees under `MaxInlineSize=35` (or 325 hot) dominates,
because it enables constant propagation and escape analysis downstream.
Escape analysis dissolving a non-escaping allocation removes both the
allocation and its GC pressure — a double win no source tweak matches.

Loop transforms (unrolling, invariant hoisting, range-check elimination)
matter for numeric kernels like `burn()`: fewer branches, fewer checks,
SIMD where vectorization fires. These only apply at tier 4, which is why
capping at `TieredStopAtLevel=1` costs steady-state throughput while
preserving correctness.

## Compile cost versus run gain

C2 compiles are expensive (hundreds of microseconds to milliseconds), so
the JVM queues them only past proven hotness. Short-lived CLIs may never
reach tier 4 before exit — that is by design, not failure. Long servers
amortize the cost over millions of invocations.

## Anti-patterns with numbers attached

Benchmarking cold code reports interpreter speed as product speed.
Quoting folklore thresholds (1500/10000 tables) mis-predicts promotion by
an order of magnitude — read `PrintFlagsFinal` instead. Forcing `-Xcomp`
compiles everything eagerly and measures compile time, not run time.
