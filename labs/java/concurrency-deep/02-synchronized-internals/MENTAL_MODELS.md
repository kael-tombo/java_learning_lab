# Mental Models: Synchronized Internals

## 1. The monitor is a building; the mark word is the sign
The 64-bit mark word (hash, age, lock bits) points at the current arrangement: a stack lock record when uncontended, an ObjectMonitor when inflated. Contention changes the sign, never the contract of mutual exclusion.

## 2. Entry is one door, exit is every window
`monitorenter` opens the critical section; the compiler installs a `monitorexit` on the normal path plus one reachable through the exception table. Throwing out of a synchronized block still unlocks — the pairing is compiler-generated, not a discipline you must remember.

## 3. Uncontended synchronized is a sticky note, not a syscall
The stack-locking fast path CASes the mark word to a lock record on your own stack: no mutex, no park, tens of nanoseconds. Budget microseconds only once inflation parks threads in the OS.

## 4. wait() steps out and takes a numbered ticket
`wait()` releases the monitor and joins the WaitSet; `notifyAll()` moves waiters to re-acquire, where they serialize through BLOCKED. A woken thread that finds a still-held lock waits again — waking and re-entering are separate events.

## 5. Locks have addresses; addresses are the whole bug
Instance methods lock `this`, static methods lock `Clazz.class`, blocks lock whatever reference you wrote. Same fields plus different lock objects is a race in uniform. Always draw the arrow from code to lock object first.

## 6. Reentrancy counts; alien calls leak
The monitor counts entries per thread, so recursion and nested synchronized calls on the same monitor just increment. But calling overridable or callback code while holding the count open lets strangers act under your exclusion — keep alien calls outside the block.

## 7. Inflation is an upgrade the JVM performs behind glass
Uncontended code rents a sticky note (stack record); real contention makes the JVM build the courthouse (ObjectMonitor with queues and OS mutex). You never call the builders — but you pay their rates, so keep sections tiny and unshared.

## 8. notify() is a tap on one shoulder in a dark room
Exactly one arbitrary waiter wakes; if it cannot proceed (wrong predicate, stolen signal), the tap is spent and the right waiter sleeps on. `notifyAll()` turns the lights on — every waiter re-checks its own predicate in a `while` loop.

## 9. wait() is checkout plus a numbered ticket
Calling `wait()` releases the monitor (checkout) and files the thread in the WaitSet (ticket); `notifyAll()` moves ticket-holders to the entry queue where they BLOCK and re-acquire one by one. Waking is the move, entry is a second queue — never conflate them.

## 10. The exception table is the second exit door
Every synchronized block has two doors out: the normal `monitorexit` and the exception-table `monitorexit`. Throwing does not pick the lock or break the glass — it walks out the second door with the monitor released.

## 11. Fairness is a policy you never bought
Among BLOCKED threads the winner is unspecified — on some platforms effectively LIFO-ish, always legally starvation. Queue length predicts pressure, never your turn. Buy fairness explicitly (`ReentrantLock(true)`) or bound the wait (`tryLock(t)`) wherever liveness matters.

## Drill
- Sketch the mark-word ladder (unlocked -> stack-locked -> inflated) and narrate what swings it at each step.
- Role-play the wrong-monitor bug: point at the exact reference (`this`, `Clazz.class`, guard, parameter) for three methods sharing one field.
- Recite the wait/notify contract (ownership check, while-loop, notifyAll default) as preconditions before any whiteboard buffer design.
- Time yourself explaining elision vs coarsening in under a minute — one removes, one merges, both are JIT-only.
- Quiz yourself on `_cxq` vs `_EntryList` vs `_WaitSet` populations: contention arrivals, entry waiters, condition waiters — three queues, three reasons to be parked.
- State the static-vs-instance monitor drawing for any class with both, before reasoning about its thread safety.
