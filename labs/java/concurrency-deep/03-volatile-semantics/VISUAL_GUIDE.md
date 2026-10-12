# Visual Guide: Volatile Semantics

## Map 1 — the objects
```
program calls: `volatile` field read/write, double-checked locking with volatile, `AtomicIntegerArray`/VarHandle array-element volatile access, `VarHandle.getAcquire/setRelease/getOpaque` (contrast)
      |
JDK state:  volatile field access (JLS 17.4.5), program-order/monitor/lifecycle edges, StoreLoad fences (`xchg`+`lock` on x86, `dmb ish` on ARMv8), safe-publication piggybacking, `VarHandle` access modes
      |
HotSpot/OS: threads, monitors, fences, CAS
```
Every diagnosis starts by pointing at one box on one row. Vague arrows explain nothing.

## Map 2 — before / after the key operation
```
BEFORE: two threads, shared operand, no edge  -->  race (any interleaving legal)
AFTER:  operation from `volatile` field read/write, double-checked locking with volatile, `AtomicIntegerArray`/VarHandle array-element volatile access, `VarHandle.getAcquire/setRelease/getOpaque` (contrast) crosses    -->  ordered (edge in MATH_FOUNDATION.md)
```
Draw your two threads, mark the edge, label which rule creates it.

## Map 3 — lab-specific picture
```
write X --program order--> write V(volatile) --hb--> read V --program order--> read X
                        (transitivity: read of X sees write of X)
volatile++ = read,modify,write (3 steps, no edge between threads) --> RACE
```

## How to read this picture in a dump or trace
- Sources: JLS 17.4 (happens-before), 17.5 (final-field safety), 17.7 (word tearing), JSR-133 (2004 memory-model rewrite), `VarHandle.java` (Java 9).
- Match tokens literally (`BLOCKED (on object monitor)`, `WAITING (parking)`, `monitorenter`, fence/CAS lines) instead of paraphrasing.
- The stack lines under the token name the API that put the thread there — read those, not just the state word.

## Drawing exercise
On paper, draw Map 2 for your EXERCISES.md task: two threads, the shared operand, and the exact edge (or its absence). If you cannot draw the edge, you cannot claim the program is correct.
