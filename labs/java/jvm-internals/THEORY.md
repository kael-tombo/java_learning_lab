# THEORY — JVM Internals

## Overview

Deep dive into HotSpot JVM internals: memory layout, object representation, synchronization, safepoints, and diagnostic tools.

---

## Object Memory Layout

### Ordinary Object Pointer (OOP)

```
64-bit JVM (compressed oops enabled by default < 32GB heap):
┌─────────────────────────────────────────────────────────────┐
│                    Object Header (16 bytes)                  │
├─────────────────────┬───────────────────────────────────────┤
│  Mark Word (8B)     │  Klass Pointer (4B, compressed)       │
├─────────────────────┴───────────────────────────────────────┤
│                    Instance Fields                           │
│              (aligned to 8-byte boundary)                   │
└─────────────────────────────────────────────────────────────┘

32-bit JVM or -XX:-UseCompressedOops:
┌─────────────────────────────────────────────────────────────┐
│                    Object Header (12 bytes)                  │
├─────────────────────┬───────────────────────────────────────┤
│  Mark Word (4B/8B)  │  Klass Pointer (4B/8B)                │
├─────────────────────┴───────────────────────────────────────┤
│                    Instance Fields                           │
└─────────────────────────────────────────────────────────────┘
```

### Mark Word States

| State | 64-bit Layout | Description |
|-------|---------------|-------------|
| Unlocked | `hash:25 | age:4 | 0:1 | 01` | Normal |
| Lightweight Locked | `ptr to lock record | 00` | Locked via CAS |
| Heavyweight Locked | `ptr to monitor | 10` | Inflated monitor |
| GC Marked | `ptr to forward | 11` | During GC |
| Biased | `thread:23 | epoch:2 | age:4 | 1:1 | 01` | Biased locking |

### Klass Pointer

- Points to `InstanceKlass` in Metaspace
- Contains: vtable, itable, method metadata, annotations
- Compressed: 32-bit offset from heap base

---

## Array Layout

```
┌─────────────────────────────────────────────────────────────┐
│                    Array Header                              │
├─────────────────────┬───────────────────────────────────────┤
│  Mark Word          │  Klass Pointer                        │
├─────────────────────┼───────────────────────────────────────┤
│  Length (4 bytes)                                           │
├─────────────────────┴───────────────────────────────────────┤
│                    Elements                                  │
│         (primitives inline, references as oops)             │
└─────────────────────────────────────────────────────────────┘
```

---

## Synchronization

### Lock Inflation Path

```
Unlocked (thin lock)
    │ CAS to install lock record
    ▼
Lightweight Lock (stack-locked)
    │ Contention / wait() / notify()
    ▼
Heavyweight Lock (ObjectMonitor)
    │ Park/unpark threads
    ▼
OS Mutex / Futex
```

### ObjectMonitor

```cpp
// hotspot/src/share/vm/runtime/objectMonitor.hpp
ObjectMonitor {
    _owner          // Thread owning lock
    _EntryList      // Threads waiting to enter
    _WaitSet        // Threads in wait()
    _recursions     // Reentrancy count
    _SpinFreq       // Spinning heuristic
}
```

### Lock Optimizations

| Optimization | Description |
|--------------|-------------|
| Biased Locking | Thread "owns" lock until contention |
| Lock Elision | Escape analysis removes lock |
| Lock Coarsening | Merge adjacent locked regions |
| Adaptive Spinning | Spin before park |

```bash
# Biased locking (deprecated in 15, removed in 21)
-XX:+UseBiasedLocking
-XX:BiasedLockingStartupDelay=4000

# Disable
-XX:-UseBiasedLocking
```

---

## Safepoints

### What Triggers Safepoint

- GC (all collectors)
- Deoptimization
- Class redefinition (JVMTI)
- Thread dump (`jstack`, `jcmd Thread.print`)
- JFR checkpoint
- `Thread.suspend()` (deprecated)

### Safepoint Mechanism

```
1. VM thread sets _safepoint_requested = true
2. Threads poll at safepoint polls (loop backedges, method returns)
3. Threads block at SafepointSynchronize::block()
4. VM thread executes operation
5. Threads released
```

### Safepoint Polling

```asm
; Generated code includes polls
test    %eax, -16384(%r15)    ; Poll page (memory protection)
jne     safepoint_handler
```

### Safepoint Latency

```bash
# Log safepoints
-XX:+PrintSafepointStatistics
-XX:PrintSafepointStatisticsCount=1
-XX:+SafepointTimeout
-XX:SafepointTimeoutDelay=5000
```

---

## Thread Architecture

### Java Thread ↔ OS Thread

```java
// 1:1 mapping (since Java 1.2 on Linux/Windows)
Thread thread = new Thread(() -> { ... });
thread.start();  // Creates OS thread via pthread_create
```

### Thread States

```
NEW → RUNNABLE → BLOCKED/WAITING/TIMED_WAITING → TERMINATED
                     ↑                │
                     └────────────────┘ (notify/park)
```

### Thread-Local Storage

```java
// ThreadLocal (slow, map-based)
ThreadLocal<Connection> tl = ThreadLocal.withInitial(() -> create());

// VarHandle (fast, JVM intrinsic)
static final VarHandle THREAD_LOCAL = 
    MethodHandles.privateLookupIn(Thread.class, MethodHandles.lookup())
        .findVarHandle(Thread.class, "threadLocals", ThreadLocalMap.class);
```

---

## Code Cache

### Structure

```
Code Cache (Reserved: 256MB default)
├── Non-compiled code (interpreter stubs)
├── C1 compiled code (tier 1-2)
├── C2 compiled code (tier 3-4)
├── Adapter frames (JNI, deopt)
└── Free space
```

### Monitoring

```bash
-XX:+PrintCodeCache
-XX:ReservedCodeCacheSize=512m
-XX:InitialCodeCacheSize=32m

# jcmd
jcmd <pid> Compiler.codecache
```

---

## Metaspace

### Structure

```
Metaspace (native memory)
├── Class Space (Klass structures)
├── Non-Class Space (annotations, method metadata)
└── Compressed Class Space (3GB, for compressed klass pointers)
```

### Sizing

```bash
-XX:MetaspaceSize=100m          # Initial committed
-XX:MaxMetaspaceSize=512m       # Max (default unlimited)
-XX:CompressedClassSpaceSize=1g # Compressed klass space
```

### GC of Metaspace

- Triggered by GC (CMS/G1/ZGC)
- Unloads classes when classloader unreachable
- `-XX:+ClassUnloadingWithConcurrentMark` (G1)

---

## Diagnostic Tools

### jcmd (Recommended)

```bash
jcmd <pid> help                    # All commands
jcmd <pid> VM.flags                # JVM flags
jcmd <pid> VM.info                 # Summary
jcmd <pid> GC.heap_info            # Heap details
jcmd <pid> GC.class_histogram      # Class histogram
jcmd <pid> Thread.print            # Thread dump
jcmd <pid> Compiler.codecache      # Code cache
jcmd <pid> JFR.start               # Start recording
```

### jstat

```bash
jstat -gc <pid> 1000              # GC stats every 1s
jstat -gccapacity <pid> 1000      # Generation capacities
jstat -compiler <pid> 1000        # JIT stats
jstat -class <pid> 1000           # Class loading
```

### JFR (Java Flight Recorder)

```bash
# Continuous recording
-XX:StartFlightRecording=maxsize=250m,maxage=1d,name=continuous,settings=profile

# Event types
jfr: jdk.ThreadSleep, jdk.MonitorEnter, jdk.GCPhasePause
```

### async-profiler

```bash
# CPU profiling
./profiler.sh -d 30 -f profile.html <pid>

# Alloc profiling
./profiler.sh -d 30 -e alloc -f alloc.html <pid>

# Lock profiling
./profiler.sh -d 30 -e lock -f lock.html <pid>
```

---

## Advanced Topics

### Compressed OOPs

```bash
# Enabled by default for heap < 32GB
-XX:+UseCompressedOops

# Object alignment affects max heap
-XX:ObjectAlignmentInBytes=16   # Default, supports 64GB with compressed
```

### Escape Analysis

```bash
-XX:+DoEscapeAnalysis           # Enable (default)
-XX:+EliminateLocks             # Lock elision
-XX:+EliminateAllocations       # Scalar replacement
```

### Inline Caches

```bash
# Monomorphic → Bimorphic → Megamorphic
-XX:+PrintInlining              # Show inlining decisions
-XX:MaxInlineSize=35            # Bytecode size limit
-XX:FreqInlineSize=325          # Hot method limit
```