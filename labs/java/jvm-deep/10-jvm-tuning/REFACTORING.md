# Refactoring: JVM Tuning

## Fix the heap posture first

Before: `-Xms512m -Xmx8g` with resize pauses spiking p99 during ramp —
ergonomic initial far below working set, growth pauses on the critical
path.

After: `-Xms8g -Xmx8g` (fixed heap, committed up front). Resize pauses
vanish; the cost (committed memory from boot) is budgeted explicitly.
One-line diff, latency-class change — standard for measured services,
kept ergonomic for elastic batch.

## Reuse large buffers, stop pooling small ones

Before: a pool for 64-byte event wrappers (bookkeeping over an already
lock-free TLAB path) plus fresh 4 MB frames per request (humongous-adjacent
churn stressing evacuation).

After: delete the small-object pool (TLAB bump-pointer already wins ~8x
over shared allocation; the pool only adds contention and stale-state
bugs), introduce a bounded queue for the 4 MB frames sized to peak
concurrency. Allocation profile inverts: hot path gets simpler, GC sees
only genuinely reusable bulk.

## Split metadata churn from object churn

Before: template compilation per request grows Metaspace while heap
churns; operators raise `-Xmx` against a metadata leak and the leak
wins anyway (unbounded `MaxMetaspaceSize`).

After: cache compiled templates (one Class per template, reused loaders),
graph Metaspace separately with its own alert, and cap only with measured
headroom. Heap and metadata symptoms stop masking each other; each plane
gets its own runbook entry.

## Size just under the compression cliff

Before: `-Xmx36g` silently drops compressed oops — references double,
headers grow 12 to 16 bytes, effective capacity falls below the 32 GB
sized-for-compression layout it replaced.

After: `-Xmx30g` (or below 32G boundary with measured margin) keeps
compression on; or commit fully above with eyes open about the doubled
reference footprint. The refactor is one number plus the `UseCompressedOops`
readout proving which side of the cliff the JVM landed on.

## What not to refactor

Do not tune exotic flags before explicit `-Xmx`, collector choice, and
pause target — the three knobs that cover most fleets within ≤3 flags of
default. Do not copy another service's flags; re-derive per deployment.
