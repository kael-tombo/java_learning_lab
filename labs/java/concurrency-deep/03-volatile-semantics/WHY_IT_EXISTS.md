# Why It Exists: Volatile Semantics

## The problem before the mechanism
Shared-memory threads interleave arbitrarily: without the Java Memory Model happens-before edges for volatile fields: visibility, ordering, and limits, every multi-threaded program is a pile of races — stale reads, torn updates, lost signals, deadlocks misdiagnosed. Developers needed a specified, implementable contract rather than folklore about "flushes" and "luck".

## What this mechanism contributes
- A precise vocabulary: volatile field access (JLS 17.4.5), program-order/monitor/lifecycle edges, StoreLoad fences (`xchg`+`lock` on x86, `dmb ish` on ARMv8), safe-publication piggybacking, `VarHandle` access modes.
- Specified operations: `volatile` field read/write, double-checked locking with volatile, `AtomicIntegerArray`/VarHandle array-element volatile access, `VarHandle.getAcquire/setRelease/getOpaque` (contrast).
- A verifiable implementation: JLS 17.4 (happens-before), 17.5 (final-field safety), 17.7 (word tearing), JSR-133 (2004 memory-model rewrite), `VarHandle.java` (Java 9).
- The guarantee: Volatile gives visibility + access atomicity (incl. long/double) but NOT compound-action atomicity (volatile++ races: read-modify-write in three steps); DCL is correct only with volatile (or holder idiom/enum singleton); transitivity A->B->C chains edges; volatile reads are near-free on x86 (TSO) while writes need a fence, both directions need fences on ARM (qualitative only); volatile arrays cover the reference, never the elements.

## What it deliberately does not do
- It does not make all concurrent code correct — compound actions, multi-variable invariants, and cross-monitor assumptions stay the programmer's job (see COMMON_MISTAKES.md).
- It does not promise fairness, timing, or performance levels — only the semantics in THEORY.md.
- It does not replace higher-level tools (executors, concurrent collections, structured concurrency) for task management.

## The alternative and why it loses
Ad-hoc reasoning ("it worked in testing", "sleep fixes it", "one more null check") passes demos and fails under load, on ARM, or after a JIT upgrade. The specified mechanism fails loudly at review time instead of silently in production.

## Bottom line
Volatile Semantics exists so that ordering, exclusion, or atomicity claims can be checked against a written contract and its sources — not against machine behavior on one laptop.

## Before happens-before: folklore and its casualties
- Developers reasoned in "flushes" and "main memory" — metaphors with no specification, so two engineers could agree on the metaphor and ship opposite orderings.
- DCL circulated as a correct idiom for years while being broken: the folklore ("synchronize the write side and it publishes") narrowed the race without closing it, and testing could not tell the difference.
- Stale-flag hangs were diagnosed as scheduler bugs: the real culprit (hoisted reads, legal under the old model) was invisible without an edge vocabulary — teams tuned priorities and poll intervals instead.

## What JSR-133 contributed (and what it refused)
- Contributed: a closed vocabulary (program order, volatile, monitor, lifecycle edges plus transitivity) in which every visibility claim is either exhibited as a chain or admitted as a race — reviewable on paper.
- Contributed: the volatile write -> read edge that fixed DCL with one keyword, and the final-field safety rule that freed immutable payloads from ceremony.
- Refused: ordering for compound actions (volatile++ still races — atomicity stayed a separate tool), fairness or timing promises (events and expiries only), and element coverage for volatile arrays (handle, not cells).

## Why the bundle stays the default over VarHandle modes
- `volatile` buys the full edge in both directions with one keyword — correct for flags and publication without mode arithmetic.
- Acquire/release and opaque exist for measured hot paths (sequence barriers, atomic indexes) where half the fence is provable waste — profiler-driven descents, not defaults.
- The rule "stay volatile until forced down" keeps the edge visible in source: a reader sees the keyword and knows the guarantee; mode tables require the reader to recompute it.

## The alternative, priced
- `sleep`-then-read publication: latency floor of one poll interval plus zero ordering guarantee — slower and still racy, the worst of both.
- `synchronized`-everywhere for visibility: correct but parks and serializes pure readers — a monitor per flag read at scale is contention bought for nothing.
- "Works on x86" confidence: passes CI, tears on ARM (barriers), tears 64-bit values anywhere (JLS 17.7) — portability failures billed per platform.
