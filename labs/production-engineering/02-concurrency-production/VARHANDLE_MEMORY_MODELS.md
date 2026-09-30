# ADVANCED GUIDE: Hardware Memory Models, Store Buffers & `VarHandle` Acquire/Release
## Lab 02 | Production Engineering Academy — Top 0.0001% Engineering

---

## 1. Physical Hardware Memory Topology & Store Buffers

To understand the Java Memory Model (JMM), one must understand the physical CPU micro-architecture:

```
[CPU Core 0]                     [CPU Core 1]
    |                                 |
 [Registers]                      [Registers]
    |                                 |
 [Store Buffer] (FIFO writes)      [Store Buffer]
    |                                 |
 [L1d Data Cache (32KB)]          [L1d Data Cache (32KB)]
    \                                 /
     +---- [MESI Invalidate Queue] --+
                   |
         [Unified L2 Cache (512KB)]
                   |
         [Shared L3 Cache (32MB)]
                   |
             [DRAM Memory]
```

### The Micro-Architectural Problem: Why Hardware Reorders Writes
1. Writing to L1 cache is slow compared to register execution (takes ~1ns vs 0.2ns).
2. To avoid stalling the execution pipeline, modern CPUs place store operations into a **Store Buffer** and immediately proceed to subsequent instructions!
3. The Store Buffer drains asynchronously into L1 cache.
4. **Resulting Reordering (StoreLoad Reordering)**:
   If Core 0 executes:
   ```
   Write A = 1
   Read  r1 = B
   ```
   The read of `B` can complete from L1 cache **before** the write to `A` has drained from the Store Buffer to L1 cache!
   To other cores, Core 0 appears to have executed the read of `B` *before* the write to `A`.

---

## 2. Java 9+ `VarHandle` Access Modes Explained

Java provides 4 distinct memory access modes via `VarHandle`:

| Mode | Methods | Hardware Equivalent | Use Case |
|:---|:---|:---|:---|
| **Plain** | `get()`, `set()` | Standard loads/stores (no fences) | Normal fields; JIT free to reorder, hoist out of loops, or cache in registers. |
| **Opaque** | `getOpaque()`, `setOpaque()` | Single-copy atomicity, no register caching | Loop counters where progress must be visible, but cross-variable ordering is irrelevant. |
| **Acquire / Release** | `getAcquire()`, `setRelease()` | Load-Load + Load-Store barrier (`Acquire`); Load-Store + Store-Store barrier (`Release`) | **Lock-Free data structures**; publishing objects safely with zero `MFENCE` overhead on x86. |
| **Volatile** | `getVolatile()`, `setVolatile()` | Full memory barrier (`MFENCE` or `LOCK CMPXCHG`) | Strict sequential consistency; all cores observe all operations in identical order. |

### The x86 Architecture Asymmetry Advantage
On x86_64 CPUs, hardware already enforces Total Store Order (TSO):
- Reads are never reordered with other reads.
- Writes are never reordered with earlier writes.
- Therefore:
  - `getAcquire()` compiles to a **simple assembly `mov` instruction (ZERO fence overhead!)**.
  - `setRelease()` compiles to a **simple assembly `mov` instruction (ZERO fence overhead!)**.
  - Only `setVolatile()` requires an expensive `lock` prefix or `xchg` instruction.
Using Acquire/Release instead of `volatile` yields a **2x–4x throughput boost** on high-frequency concurrency pathways!

---

## 3. Production Lock-Free Michael-Scott Queue Implementation

```java
package com.learning.production.lab02;

import java.lang.invoke.MethodHandles;
import java.lang.invoke.VarHandle;

/**
 * High-performance, lock-free, wait-free read FIFO queue.
 * Implements the seminal Michael & Scott (PODC '96) non-blocking algorithm
 * using Java VarHandle Acquire/Release semantics.
 */
public class LockFreeMichaelScottQueue<T> {

    private static class Node<T> {
        final T item;
        volatile Node<T> next;

        private static final VarHandle NEXT_HANDLE;

        static {
            try {
                NEXT_HANDLE = MethodHandles.lookup().findVarHandle(Node.class, "next", Node.class);
            } catch (ReflectiveOperationException e) {
                throw new ExceptionInInitializerError(e);
            }
        }

        Node(T item) {
            this.item = item;
            this.next = null;
        }

        boolean casNext(Node<T> expected, Node<T> update) {
            return NEXT_HANDLE.compareAndSet(this, expected, update);
        }
    }

    private volatile Node<T> head;
    private volatile Node<T> tail;

    private static final VarHandle HEAD_HANDLE;
    private static final VarHandle TAIL_HANDLE;

    static {
        try {
            MethodHandles.Lookup l = MethodHandles.lookup();
            HEAD_HANDLE = l.findVarHandle(LockFreeMichaelScottQueue.class, "head", Node.class);
            TAIL_HANDLE = l.findVarHandle(LockFreeMichaelScottQueue.class, "tail", Node.class);
        } catch (ReflectiveOperationException e) {
            throw new ExceptionInInitializerError(e);
        }
    }

    public LockFreeMichaelScottQueue() {
        Node<T> dummy = new Node<>(null);
        this.head = dummy;
        this.tail = dummy;
    }

    public void enqueue(T item) {
        Node<T> newNode = new Node<>(item);
        while (true) {
            Node<T> curTail = (Node<T>) TAIL_HANDLE.getAcquire(this);
            Node<T> next = (Node<T>) Node.NEXT_HANDLE.getAcquire(curTail);

            if (curTail == TAIL_HANDLE.getAcquire(this)) {
                if (next == null) {
                    // Try to link new node at the end of the queue
                    if (curTail.casNext(null, newNode)) {
                        // Swing tail forward to new node
                        TAIL_HANDLE.compareAndSet(this, curTail, newNode);
                        return;
                    }
                } else {
                    // Tail was lagging behind; help swing tail forward
                    TAIL_HANDLE.compareAndSet(this, curTail, next);
                }
            }
        }
    }

    public T dequeue() {
        while (true) {
            Node<T> curHead = (Node<T>) HEAD_HANDLE.getAcquire(this);
            Node<T> curTail = (Node<T>) TAIL_HANDLE.getAcquire(this);
            Node<T> next = (Node<T>) Node.NEXT_HANDLE.getAcquire(curHead);

            if (curHead == HEAD_HANDLE.getAcquire(this)) {
                if (curHead == curTail) {
                    if (next == null) {
                        return null; // Queue is empty
                    }
                    // Tail is lagging behind; help advance tail
                    TAIL_HANDLE.compareAndSet(this, curTail, next);
                } else {
                    // Read value before swinging head to prevent race
                    T val = next.item;
                    if (HEAD_HANDLE.compareAndSet(this, curHead, next)) {
                        return val;
                    }
                }
            }
        }
    }
}
```
