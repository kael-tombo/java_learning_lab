# Performance Profiling — Internal Mechanics

## How JFR Works

### Flight Recorder Architecture

Java Flight Recorder (JFR) is a low-overhead event recorder built into the HotSpot JVM:
1. **Event producers** — JVM subsystems (GC, JIT, threading) emit typed events
2. **Event consumers** — JMC or custom tools read recorded events
3. **Ring buffer** — Events are written to a thread-local, fixed-size ring buffer
4. **Dump mechanism** — Buffer contents are written to a .jfr file on demand

### Overhead Characteristics

JFR is designed for production use:
- Overhead: <1% for typical configurations
- Thread-local buffers avoid synchronization
- Event filtering reduces storage volume
- Stack traces are sampled, not captured every event

### Sampling Profilers

Async-profiler uses:
1. `perf_events` (Linux) or `perfmap` for CPU sampling
2. Signal-based stack trace collection
3. Wall-clock profiling for off-CPU analysis
4. Allocation profiling via TLAB hooks

### JMH (Java Microbenchmark Harness)

JMH works by:
1. Forking isolated JVM processes
2. Running warmup iterations to stabilize JIT
3. Measuring only well-warmed code paths
4. Blackholing results to prevent dead code elimination
