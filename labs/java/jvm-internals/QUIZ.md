# QUIZ — JVM Internals

## Multiple Choice

### 1. Object Header Size (64-bit JVM, compressed OOPs)
What is the size of a standard object header in a 64-bit JVM with compressed OOPs enabled (heap < 32GB)?

A) 8 bytes
B) 12 bytes
C) 16 bytes
D) 24 bytes

**Answer: C) 16 bytes** — Mark word (8B) + compressed klass pointer (4B) + padding to 8-byte alignment (4B) = 16 bytes

---

### 2. Mark Word States
Which mark word state indicates a heavyweight (inflated) lock?

A) `01` (unlocked)
B) `00` (lightweight locked)
C) `10` (heavyweight locked)
D) `11` (GC marked)

**Answer: C) `10`** — The two lowest bits `10` indicate a pointer to ObjectMonitor (heavyweight lock)

---

### 3. Biased Locking
In which Java version was biased locking deprecated?

A) Java 11
B) Java 15
C) Java 17
D) Java 21

**Answer: B) Java 15** — Deprecated in 15, disabled by default in 15, removed in 21

---

### 4. Safepoint Polling
Where does the JVM insert safepoint polls in compiled code?

A) Only at method entry
B) At loop backedges and method returns
C) Only at allocation sites
D) Every 100 bytecode instructions

**Answer: B) At loop backedges and method returns** — Also at method entry for non-inlined methods

---

### 5. Tiered Compilation
What is the default compilation tier for C2 (server compiler)?

A) Tier 1
B) Tier 2
C) Tier 3
D) Tier 4

**Answer: C) Tier 3** — Tier 3 = C2 with profiling; Tier 4 = C2 full optimization

---

### 6. ZGC Barriers
Which barrier type does ZGC use?

A) SATB (write barrier)
B) Brooks (read barrier)
C) Load/Store barriers (colored pointers)
D) Card marking

**Answer: C) Load/Store barriers** — ZGC uses colored pointers with load/store barriers for concurrent relocation

---

### 7. Code Cache
What happens when the code cache fills up?

A) JVM crashes
B) JIT compilation stops, interpreter only
C) Old code is evicted automatically
D) Heap is reduced to make space

**Answer: B) JIT compilation stops** — "CodeCache is full. Compiler has been disabled." Interpreter continues.

---

### 8. Metaspace
Where is Metaspace allocated?

A) Java Heap
B) Native memory (off-heap)
C) PermGen (Java 7)
D) Code Cache

**Answer: B) Native memory** — Metaspace uses native memory, not Java heap

---

### 9. TLAB Allocation
What is the primary benefit of Thread-Local Allocation Buffers (TLABs)?

A) Reduces GC pressure
B) Enables lock-free allocation via bump pointer
C) Improves cache locality
D) Reduces object header size

**Answer: B) Lock-free allocation** — Each thread allocates from its own TLAB without synchronization

---

### 10. Compressed OOPs
At what heap size does the JVM disable compressed OOPs by default?

A) 16 GB
B) 32 GB
C) 64 GB
D) 128 GB

**Answer: B) 32 GB** — Above 32GB heap, compressed OOPs are disabled (can be forced with `-XX:-UseCompressedOops`)

---

## True/False

### 11. Object alignment is always 8 bytes in 64-bit JVM.
**False** — Default is 8 bytes, but can be changed with `-XX:ObjectAlignmentInBytes` (affects max heap with compressed OOPs)

### 12. Virtual threads have their own stack memory separate from carrier threads.
**True** — Virtual threads use stack chunks allocated on heap, not OS thread stack

### 13. `synchronized` on a virtual thread never pins the carrier thread.
**False** — `synchronized` pins the virtual thread to its carrier thread

### 14. Escape analysis can eliminate synchronization on non-escaping objects.
**True** — Lock elision (`-XX:+EliminateLocks`) removes synchronization when object doesn't escape

### 15. The JVM uses a single global code cache for all compiled code.
**True** — Code cache is shared, segmented into non-compiled, C1, C2, adapters

---

## Scenario-Based

### 16. Long Safepoint Pause
Your application experiences 500ms safepoint pauses during GC. What is the most likely cause?

A) Too many threads
B) Thread stuck in JNI/native code
C) Code cache full
D) Metaspace OOM

**Answer: B) Thread stuck in JNI/native code** — Safepoint requires all threads to reach safe state; JNI/native code blocks this

### 17. Megamorphic Call Site
A call site has 5 different implementations. What optimization will the JIT apply?

A) Inline all 5 with guards
B) Inline top 2, guard rest
C) No inlining, use invokeinterface
D) Create polymorphic inline cache

**Answer: C) No inlining** — Megamorphic (>2 targets) typically not inlined; uses invokeinterface

### 18. Class Loader Leak
You see Metaspace growing continuously. What is a common cause?

A) Too many objects created
B) ThreadLocal not cleaned in thread pool
C) Custom ClassLoader not released
D) String interning

**Answer: C) Custom ClassLoader not released** — Classes loaded by unreachable ClassLoaders can be unloaded

---

## Code Analysis

### 19. Lock State
```java
Object lock = new Object();
synchronized(lock) {
    lock.wait(); // What lock state after wait()?
}
```
After `wait()`, the lock state becomes:
A) Unlocked
B) Lightweight locked
C) Heavyweight locked (ObjectMonitor)
D) Biased locked

**Answer: C) Heavyweight locked** — `wait()`/`notify()` require ObjectMonitor

### 20. Allocation Path
```java
// Hot loop
for (int i = 0; i < 1_000_000; i++) {
    new Object(); // Allocation path?
}
```
Primary allocation path:
A) Shared eden allocation (slow)
B) TLAB fast path (bump pointer)
C) Direct old gen allocation
D) Stack allocation (escape analysis)

**Answer: B) TLAB fast path** — Most allocations go through thread-local TLABs