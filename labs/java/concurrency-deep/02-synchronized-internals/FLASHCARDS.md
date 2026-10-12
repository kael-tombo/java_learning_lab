# Flashcards: Synchronized Internals

Q: Bytecode trio for synchronized? | A: monitorenter + monitorexit (normal) + monitorexit (exception path).
Q: Biased locking status 15/18/23? | A: Disabled-15 (JEP 374), removed-18, flag unrecognized-23.
Q: Stack locking cost? | A: Tens of ns (~10-20ns): mark-word CAS to own-stack record, no syscall.
Q: Inflated monitor contents? | A: ObjectMonitor: OS mutex, _cxq, _EntryList, _WaitSet.
Q: wait/notify without monitor? | A: IllegalMonitorStateException (dynamic ownership check).
Q: wait idiom? | A: while (!cond) wait() — spurious + stolen wakes demand re-check.
Q: notify vs notifyAll default? | A: notifyAll unless single-waiter/single-condition proven.
Q: static vs instance monitors? | A: Disjoint (Clazz.class vs this); no mutual exclusion across them.
Q: Reentrancy meaning? | A: Same thread re-enters freely; monitor counts entries/exits.
Q: Unlock->lock edge scope? | A: Same monitor only (JLS 17.4); different locks share nothing.

## Method
- Cover the A column; recall aloud; check. Cycle missed cards twice before finishing.

## More cards (same deck)
Q: How many `monitorexit` for one `monitorenter`? | A: At least two — normal path plus exception-table path.
Q: What routes the exceptional path to release? | A: The compiler-generated exception table covering the block body.
Q: Displaced mark word lives where? | A: In a lock record on the acquiring thread's own stack (stack locking).
Q: Recursive synchronized entry cost? | A: One more nearly-free record push — no extra CAS word contention.
Q: What swings the mark word to a monitor? | A: Inflation on real contention — mark word then points at the ObjectMonitor.
Q: `_cxq` vs `_EntryList` vs `_WaitSet`? | A: Contention queue vs entry-wait queue vs wait()-waiter set inside ObjectMonitor.
Q: `wait(t)` two exits? | A: Notified/interrupted OR timeout — both re-acquire the monitor before returning.
Q: Notifier still holding the lock — waiter state? | A: BLOCKED after waking: wake and re-entry are separate events.
Q: Synchronized on a method parameter? | A: Locks the caller's object — alien-controlled identity; prefer private final guards.
Q: Locking an interned String literal? | A: JVM-wide shared monitor — unrelated code can hold your lock; never do it.
Q: Lock elision trigger? | A: JIT proves the object never escapes the thread — lock removed entirely.
Q: Lock coarsening trigger? | A: Adjacent blocks on the same monitor merged into one acquisition.

## Drill
- Recite the monitor trio (`_cxq`, `_EntryList`, `_WaitSet`) and each queue's population without peeking.
- For every wait/notify card, state the ownership precondition (`IllegalMonitorStateException` otherwise) before flipping.
- Draw the mark-word states (unlocked, stack-locked, inflated) from memory, then diff against THEORY.md.
- Retire a card only after three consecutive clean recalls across two sittings.
