# Visual Guide: Synchronized Internals

## Map 1 — the objects
```
program calls: `synchronized` blocks/methods, `Object.wait()/wait(t)/notify()/notifyAll()`, `ReentrantLock.lockInterruptibly/tryLock` (contrast), `-XX:+PrintFieldLayout`
      |
JDK state:  object mark word (64-bit header: hash, GC age, lock bits), stack lock records (displaced mark word), inflated `ObjectMonitor` (`_cxq`, `_EntryList`, `_WaitSet`), exception-table second `monitorexit`
      |
HotSpot/OS: threads, monitors, fences, CAS
```
Every diagnosis starts by pointing at one box on one row. Vague arrows explain nothing.

## Map 2 — before / after the key operation
```
BEFORE: two threads, shared operand, no edge  -->  race (any interleaving legal)
AFTER:  operation from `synchronized` blocks/methods, `Object.wait()/wait(t)/notify()/notifyAll()`, `ReentrantLock.lockInterruptibly/tryLock` (contrast), `-XX:+PrintFieldLayout` crosses    -->  ordered (edge in MATH_FOUNDATION.md)
```
Draw your two threads, mark the edge, label which rule creates it.

## Map 3 — lab-specific picture
```
mark word: [hash | age | lock bits] --uncontended--> stack lock record (displaced mark)
                                  --contended--> ObjectMonitor [_cxq | _EntryList | _WaitSet]
bytecode: monitorenter ... body ... monitorexit (normal) + monitorexit (exception table)
```

## How to read this picture in a dump or trace
- Sources: `javap -c` (monitorenter + 2 monitorexit), HotSpot `objectMonitor.cpp`, `synchronizer.cpp`, `markWord.hpp`, JLS 17.1/17.4.
- Match tokens literally (`BLOCKED (on object monitor)`, `WAITING (parking)`, `monitorenter`, fence/CAS lines) instead of paraphrasing.
- The stack lines under the token name the API that put the thread there — read those, not just the state word.

## Drawing exercise
On paper, draw Map 2 for your EXERCISES.md task: two threads, the shared operand, and the exact edge (or its absence). If you cannot draw the edge, you cannot claim the program is correct.
