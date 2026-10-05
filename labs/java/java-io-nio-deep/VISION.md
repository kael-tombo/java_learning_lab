# Vision — Java IO / NIO

## Where IO Is Going (2026+)
- Project Loom virtual threads make blocking IO cheap again — simple code, selector-scale.
- Structured concurrency scopes IO tasks with deadlines and cancellation.
- Foreign Memory API replaces DirectByteBuffer for safe off-heap.

## 5-Year Bets
1. Blocking-style code on virtual threads becomes default server style.
2. io_uring backends land in JDK (Linux) for higher IOPS.
3. Scoped arenas replace manual Cleaner handling.

## What Won't Change
- Buffer discipline (flip/clear) mental model persists.
- Backpressure + bounded queues remain mandatory.
- FD hygiene: close everything, always.

## Signals to Watch
- JEPs for async/uring, scoped values, stream gatherers for pipelines.
- OpenJDK Loom + Panama docs and benchmarks.

## Career Implication
Engineers who combine classic correctness with NIO tuning + Loom will own infra roles.
Build the log ingestor (REAL_WORLD_PROJECT) with both selector and virtual-thread variants.

## Anti-Vision
Don't chase "fully async everywhere" — complexity kills. Measure first.
Prefer readable blocking-on-virtual-threads unless profiling says otherwise.

## 30/60/90
- 30d: master buffers + channels + selector echo.
- 60d: ship mini file-indexer with metrics.
- 90d: production-grade ingestor with backpressure + dashboards.
