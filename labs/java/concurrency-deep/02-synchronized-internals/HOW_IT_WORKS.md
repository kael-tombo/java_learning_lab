# How It Works: Synchronized Internals

## The mechanism in one paragraph
Synchronized Internals is object monitors: monitorenter/monitorexit pairing, lock levels, and wait/notify protocol. The moving parts are object mark word (64-bit header: hash, GC age, lock bits), stack lock records (displaced mark word), inflated `ObjectMonitor` (`_cxq`, `_EntryList`, `_WaitSet`), exception-table second `monitorexit`, driven through `synchronized` blocks/methods, `Object.wait()/wait(t)/notify()/notifyAll()`, `ReentrantLock.lockInterruptibly/tryLock` (contrast), `-XX:+PrintFieldLayout`, implemented as described in `javap -c` (monitorenter + 2 monitorexit), HotSpot `objectMonitor.cpp`, `synchronizer.cpp`, `markWord.hpp`, JLS 17.1/17.4. Biased locking disabled by default in JDK 15 (JEP 374), removed in JDK 18, flag unrecognized on JDK 23; uncontended stack-locking fast path costs on the order of ~10-20ns; wait/notify require monitor ownership (else IllegalMonitorStateException) with while-loop re-check; static (Class-object) and instance (this) monitors are disjoint; monitors are reentrant per thread; unlock->lock is a happens-before edge.

## Step-by-step through the parts
1. **Name the operands.** Before reasoning, write down the exact objects/fields involved (which thread, which monitor, which field, which atomic). Most bugs are wrong-operand bugs.
2. **Trace one operation end to end.** Pick a single call from `synchronized` blocks/methods, `Object.wait()/wait(t)/notify()/notifyAll()`, `ReentrantLock.lockInterruptibly/tryLock` (contrast), `-XX:+PrintFieldLayout` and follow it: JDK entry -> HotSpot primitive -> observable result. Use INTERNALS.md source paths to confirm each hop.
3. **Add the second thread.** Re-trace with two actors interleaved. Ask at each step: which edge orders these two actions? If none, you have a race; say so explicitly.
4. **Check the exits.** Every acquisition has a release path (including exceptions/interrupts/timeouts). Verify yours, then compare with COMMON_MISTAKES.md.
5. **Confirm empirically.** Run the STEP_BY_STEP.md commands (`jstack`, `javap -c`, `jshell`) and match output against the predicted tokens/bytecodes.

## Worked trace
- Start from README.md item 4: Biased locking disabled by default in JDK 15 (JEP 374), removed in JDK 18, flag unrecognized on JDK 23; uncontended stack-locking fast path costs on the order of ~10-20ns; wait/notify require monitor ownership (else IllegalMonitorStateException) with while-loop re-check; static (Class-object) and instance (this) monitors are disjoint; monitors are reentrant per thread; unlock->lock is a happens-before edge.
- Reproduce it with the smallest program in STEP_BY_STEP.md, then explain each line of output using the vocabulary of object mark word (64-bit header: hash, GC age, lock bits), stack lock records (displaced mark word), inflated `ObjectMonitor` (`_cxq`, `_EntryList`, `_WaitSet`), exception-table second `monitorexit`.

## What people get wrong
- Skipping step 1 (reasoning about "the lock" or "the flag" without saying which object/field).
- Treating monitoring output as control input (thread states, fuzzy sums).
- Assuming edges that do not exist (different monitors, plain fields, element access through a volatile array reference).

## Next
- INTERNALS.md for source paths; MATH_FOUNDATION.md for the ordering rules in symbols.

## Second trace: inflation under contention
- Start two threads on one uncontended guard: both acquire via stack locking (mark-word CAS to own-stack records), no OS involvement — confirm with JFR showing zero `jdk.JavaMonitorEnter` stall events.
- Add sixteen rivals on the same guard: the monitor inflates (ObjectMonitor allocated, `_cxq`/`_EntryList` fill), contenders park in the OS, and `jstack` shows identical BLOCKED stacks at the entry frame.
- Release the pressure back to one thread: HotSpot may deflate to stack locking — semantics never change across the episode, only the cost per acquisition.
- Conclusion to write down: lock *level* is an implementation detail driven by contention; mutual exclusion and the happens-before edge hold at every level.

## Monitor-identity map (fill from your runs)
- `synchronized` instance method: monitor is `this` — same-object callers exclude, different-object callers overlap freely.
- `static synchronized` method: monitor is `Clazz.class` — excludes only other holders of that exact `Class` object.
- `synchronized (private final Object guard)`: monitor is the guard — the only form where the identity is fully yours; the default for new code.
- `synchronized (param)` or boxed/interned value: monitor is caller-visible or JVM-shared — audit every holder before trusting exclusion.
- `wait()/notify()/notifyAll()`: monitor is the receiver object — calling on an unheld monitor throws `IllegalMonitorStateException` at runtime.

## Reentrancy trace
- Nest `synchronized (guard)` across two methods on one thread: entry count rises twice, exits twice — no deadlock against yourself, provable via `Thread.holdsLock(guard)` at each depth.
- Call an overridable method inside the block and watch a subclass re-enter: allowed by counting, dangerous by invariant — the alien path observes your half-open state under your own exclusion.
- Refactor the alien call outside with a snapshot: same exclusion for your fields, zero exclusion lent to strangers.

## Self-check
- Cover the map above and produce, from live runs, one `javap -c` pairing plus one BLOCKED dump with holder traced — both from memory, then diffed against output.
