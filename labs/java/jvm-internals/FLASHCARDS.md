# FLASHCARDS — JVM Internals

## Object Layout

| Question | Answer |
|----------|--------|
| Object header size (64-bit, compressed OOPs) | 16 bytes (mark word 8B + klass ptr 4B + padding 4B) |
| Object header size (64-bit, no compressed OOPs) | 24 bytes (mark word 8B + klass ptr 8B + padding) |
| Object header size (32-bit JVM) | 8 bytes (mark word 4B + klass ptr 4B) |
| Array header additional field | Length (4 bytes) |
| Mark word unlocked state bits | `01` |
| Mark word lightweight locked bits | `00` |
| Mark word heavyweight locked bits | `10` |
| Mark word GC marked bits | `11` |
| Biased lock mark word bits | `01` (with thread ID in high bits) |
| Compressed klass pointer size | 4 bytes (32-bit offset from heap base) |
| Default object alignment | 8 bytes |
| Max heap with compressed OOPs (8-byte alignment) | 32 GB |
| Max heap with compressed OOPs (16-byte alignment) | 64 GB |

## Synchronization

| Question | Answer |
|----------|--------|
| Lock inflation path | Unlocked → Lightweight (CAS) → Heavyweight (ObjectMonitor) |
| Biased locking purpose | Eliminate CAS for uncontended locks by "biasing" to thread |
| Lock elision | Escape analysis removes lock when object doesn't escape |
| Lock coarsening | Merge adjacent synchronized blocks |
| Adaptive spinning | Spin before parking, based on history |
| `synchronized` vs `ReentrantLock` | `synchronized`: no interrupt, no timeout, single condition |
| ObjectMonitor owner field | Thread currently holding the lock |
| ObjectMonitor EntryList | Threads waiting to enter (blocked on lock) |
| ObjectMonitor WaitSet | Threads in `wait()` state |
| `wait()` requires | Heavyweight lock (ObjectMonitor) |

## Safepoints

| Question | Answer |
|----------|--------|
| What triggers safepoint | GC, deoptimization, class redefinition, thread dump, JFR |
| Safepoint poll locations | Loop backedges, method returns, method entry (non-inlined) |
| Safepoint timeout flag | `-XX:+SafepointTimeout -XX:SafepointTimeoutDelay=5000` |
| Safepoint log flags | `-XX:+PrintSafepointStatistics -XX:PrintSafepointStatisticsCount=1` |
| VM thread role | Initiates safepoint, waits for all threads to block |
| Thread state at safepoint | `_thread_blocked` (in VM) |
| Long safepoint cause | Thread in JNI, native code, or page fault |

## JIT Compilation

| Question | Answer |
|----------|--------|
| Tiered compilation tiers | 0=Interpreter, 1=C1, 2=C1+profiling, 3=C2, 4=C2+profiling |
| CompileThreshold (C2) | ~10,000 invocations (default) |
| Tier3CompileThreshold (C1) | ~200 invocations |
| Inlining MaxInlineSize | 35 bytes bytecode |
| Inlining FreqInlineSize | 325 bytes (hot methods) |
| Escape analysis optimizations | Scalar replacement, lock elision, stack allocation |
| Deoptimization causes | Class loading, uncommon trap, OSR, speculative optimization failure |
| On-Stack Replacement (OSR) | Switch from interpreted to compiled mid-loop |
| Code cache default size | 256 MB reserved |
| Print compilation flag | `-XX:+PrintCompilation` |

## Garbage Collection

| Question | Answer |
|----------|--------|
| G1 region size range | 1-32 MB (power of 2) |
| G1 young GC trigger | Eden full |
| G1 mixed GC trigger | Old gen occupancy > InitiatingHeapOccupancyPercent (45% default) |
| ZGC pause target | < 1 ms |
| ZGC colored pointers | Load barrier (read), Store barrier (write) |
| Shenandoah Brooks pointer | Read barrier with forwarding pointer |
| Generational hypothesis | Most objects die young; few old→young refs |
| Card table purpose | Track old→young references for young GC |
| Remembered set (G1) | Per-region tracking of incoming references |
| Humongous object (G1) | > 50% region size |

## Memory Areas

| Question | Answer |
|----------|--------|
| Heap: young gen structure | Eden + S0 + S1 (survivor spaces) |
| Heap: old gen | Tenured space for long-lived objects |
| Metaspace | Class metadata (Klass, methods, annotations) |
| Code cache | JIT compiled code, stubs, adapters |
| Thread stack | Per-thread, frames, locals, operand stack |
| Direct memory | ByteBuffer.allocateDirect, memory-mapped files |
| Compressed class space | 3GB for compressed klass pointers (Metaspace) |

## Class Loading

| Question | Answer |
|----------|--------|
| Delegation model | Parent first (Bootstrap → Platform → Application → Custom) |
| Loading phase | Find binary, create Class object |
| Linking: Verification | Bytecode validity check |
| Linking: Preparation | Allocate static fields, default values |
| Linking: Resolution | Symbolic refs → direct refs |
| Initialization | `<clinit>`, static initializers |
| Split package error | Same package in multiple modules |

## Threads

| Question | Answer |
|----------|--------|
| Java thread : OS thread mapping | 1:1 (since Java 1.2) |
| Virtual thread stack | Heap-allocated stack chunks (~1KB initial) |
| Virtual thread pinning causes | `synchronized`, native calls, FFI |
| Platform thread stack size | `-Xss` (default 1MB) |
| ThreadLocal storage | ThreadLocalMap per thread (weak keys) |
| VarHandle for thread-local | Fast JVM intrinsic access |

## Diagnostics

| Question | Answer |
|--------|--------|
| jcmd GC.heap_info | Heap summary (regions, occupancy) |
| jcmd GC.class_histogram | Live object counts per class |
| jcmd Thread.print | Thread dump with locks |
| jcmd Compiler.codecache | Code cache usage |
| jcmd VM.native_memory | Native memory tracking (NMT) |
| jstat -gc | GC statistics |
| jmap -histo:live | Live histogram (triggers GC) |
| async-profiler -e alloc | Allocation profiling |
| async-profiler -e lock | Lock contention profiling |
| JFR event: jdk.ObjectAllocationInNewTLAB | Allocation sites |

## Performance Flags

| Question | Answer |
|--------|--------|
| Enable biased locking | `-XX:+UseBiasedLocking` (deprecated) |
| Disable biased locking | `-XX:-UseBiasedLocking` |
| Escape analysis | `-XX:+DoEscapeAnalysis` (default on) |
| Eliminate allocations | `-XX:+EliminateAllocations` |
| Eliminate locks | `-XX:+EliminateLocks` |
| Print inlining | `-XX:+PrintInlining` |
| Print escape analysis | `-XX:+PrintEscapeAnalysis` |
| NMT summary | `-XX:NativeMemoryTracking=summary` |
| Unified GC logging | `-Xlog:gc*:file=gc.log:time,uptime,level,tags` |
| JFR continuous | `-XX:StartFlightRecording=maxsize=250m,maxage=1d` |