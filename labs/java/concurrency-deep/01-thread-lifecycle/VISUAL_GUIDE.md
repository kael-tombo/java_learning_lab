# Visual Guide: Thread Lifecycle

## Map 1 — the objects
```
program calls: `start()`, `join()/join(t)`, `sleep()`, `Object.wait/notify`, `LockSupport.park/parkNanos`, `getState()/isAlive()`, `setDaemon()`, `interrupt()`
      |
JDK state:  `java.lang.Thread`, `Thread.State` (NEW/RUNNABLE/BLOCKED/WAITING/TIMED_WAITING/TERMINATED), `LockSupport.park/unpark`, thread-dump `state` token
      |
HotSpot/OS: threads, monitors, fences, CAS
```
Every diagnosis starts by pointing at one box on one row. Vague arrows explain nothing.

## Map 2 — before / after the key operation
```
BEFORE: two threads, shared operand, no edge  -->  race (any interleaving legal)
AFTER:  operation from `start()`, `join()/join(t)`, `sleep()`, `Object.wait/notify`, `LockSupport.park/parkNanos`, `getState()/isAlive()`, `setDaemon()`, `interrupt()` crosses    -->  ordered (edge in MATH_FOUNDATION.md)
```
Draw your two threads, mark the edge, label which rule creates it.

## Map 3 — lab-specific picture
```
NEW --start()--> RUNNABLE <--> BLOCKED (synchronized only)
                   |  ^-- WAITING (wait/join/park) --notify/unpark-->|
                   +-- TIMED_WAITING (sleep/wait(t)/parkNanos) --timeout-->+
                   +--> TERMINATED (sink; start() again = IllegalThreadStateException)
```
ReentrantLock contention parks -> WAITING, never BLOCKED.

## How to read this picture in a dump or trace
- Sources: `java.base/java/lang/Thread.java` (State enum, start/join/sleep), HotSpot `thread.cpp`/`osthread`, `jstack`/`jcmd Thread.print` output.
- Match tokens literally (`BLOCKED (on object monitor)`, `WAITING (parking)`, `monitorenter`, fence/CAS lines) instead of paraphrasing.
- The stack lines under the token name the API that put the thread there — read those, not just the state word.

## Drawing exercise
On paper, draw Map 2 for your EXERCISES.md task: two threads, the shared operand, and the exact edge (or its absence). If you cannot draw the edge, you cannot claim the program is correct.
