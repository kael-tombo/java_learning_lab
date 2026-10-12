# Visual Guide: Atomic Classes

## Map 1 — the objects
```
program calls: `compareAndSet/compareAndExchange/weakCompareAndSet`, `getAndIncrement/getAndAdd/getAndUpdate/accumulateAndGet`, `AtomicStampedReference/AtomicMarkableReference`, `LongAdder.increment/sum/sumThenReset`, `LongAccumulator`, `DoubleAdder`
      |
JDK state:  `AtomicInteger.value` (volatile int) + `VALUE` field offset, Unsafe intrinsic `U.getAndAddInt` (= `lock cmpxchg` on x86), VarHandle-specified effects, CAS retry loop, (reference,stamp) pairs, `Striped64` cells + base with `@Contended` padding
      |
HotSpot/OS: threads, monitors, fences, CAS
```
Every diagnosis starts by pointing at one box on one row. Vague arrows explain nothing.

## Map 2 — before / after the key operation
```
BEFORE: two threads, shared operand, no edge  -->  race (any interleaving legal)
AFTER:  operation from `compareAndSet/compareAndExchange/weakCompareAndSet`, `getAndIncrement/getAndAdd/getAndUpdate/accumulateAndGet`, `AtomicStampedReference/AtomicMarkableReference`, `LongAdder.increment/sum/sumThenReset`, `LongAccumulator`, `DoubleAdder` crosses    -->  ordered (edge in MATH_FOUNDATION.md)
```
Draw your two threads, mark the edge, label which rule creates it.

## Map 3 — lab-specific picture
```
do { prev = get(); next = f(prev); } while (!compareAndSet(prev, next));
                                        ^ linearization point (winning lock cmpxchg)
LongAdder: base + Cell[0..n] (hashed stripes); sum() walks cells (fuzzy, non-atomic)
```

## How to read this picture in a dump or trace
- Sources: `java.base/java/util/concurrent/atomic/AtomicInteger.java` (JDK 23), `Striped64.java` class javadoc, `VarHandle` specs, JSR-166 (2004, Doug Lea).
- Match tokens literally (`BLOCKED (on object monitor)`, `WAITING (parking)`, `monitorenter`, fence/CAS lines) instead of paraphrasing.
- The stack lines under the token name the API that put the thread there — read those, not just the state word.

## Drawing exercise
On paper, draw Map 2 for your EXERCISES.md task: two threads, the shared operand, and the exact edge (or its absence). If you cannot draw the edge, you cannot claim the program is correct.
