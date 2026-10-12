# Reflection: Synchronized Internals

## Recall without notes
1. State the lab's key fact (Biased locking disabled by default in JDK 15 (JEP 374), removed in JDK 18, flag unrecognized on JDK 23; uncontended stack-locking fast path costs on the order of ~10-20ns; wait/notify require monitor ownership (else IllegalMonitorStateException) with while-loop re-check; static (Class-object) and instance (this) monitors are disjoint; monitors are reentrant per thread; unlock->lock is a happens-before edge.) in under 40 words.
2. List the structures (object mark word (64-bit header: hash, GC age, lock bits), stack lock records (displaced mark word), inflated `ObjectMonitor` (`_cxq`, `_EntryList`, `_WaitSet`), exception-table second `monitorexit`) and one API each from (`synchronized` blocks/methods, `Object.wait()/wait(t)/notify()/notifyAll()`, `ReentrantLock.lockInterruptibly/tryLock` (contrast), `-XX:+PrintFieldLayout`) that touches them.

## Connect
3. Which invariant from THEORY.md did your STEP_BY_STEP.md probe demonstrate? Quote the probe output line that proves it.
4. Where does this lab's mechanism meet the neighboring lab (lifecycle<->monitors<->volatile<->atomics)? Name one concrete handoff (e.g. BLOCKED vs parking, unlock edge vs volatile edge, CAS vs lock for one counter).

## Challenge your intuition
5. Write the wrong version first (one COMMON_MISTAKES.md bug), predict its failure mode, then run it. Where did your prediction differ from the run?
6. Which of your predictions relied on timing or fairness? Restate it using only specified edges and invariants.

## Transfer
7. Name one place in your own codebase where object monitors: monitorenter/monitorexit pairing, lock levels, and wait/notify protocol is assumed but unchecked. What single edge, guard change, or API swap would make it checkable?
8. What will you measure (PERFORMANCE.md harness) before claiming the fix helped?

## Exit ticket
- Two sentences: what breaks, and which source (`javap -c` (monitorenter + 2 monitorexit), HotSpot `objectMonitor.cpp`, `synchronizer.cpp`, `markWord.hpp`, JLS 17.1/17.4) you would open first when it does.

## Prove the pairing (new prompts)
9. Paste your `javap -c` trio (one `monitorenter`, two `monitorexit`, exception-table lines) and annotate which source line each exit serves.
10. Deliberately sketch unbalanced bytecode (enter without the table path) and state what the verifier would reject — pairing as a load-time theorem, not a habit.
11. Which of your three forms (block, instance method, static method) binds which monitor? Answer from the constant-pool loads, not from memory.

## Contention diary
12. Record your EXERCISES.md cliff numbers (1/4/16 threads): the knee value, the BLOCKED-stack excerpt at the knee, and the holder's frame.
13. Name the guard you would split first and the invariant boundary that justifies the split — no split without a stated boundary.
14. State your elision verdict (confirmed-elided vs unconfirmed) with the JIT-log line or its absence quoted.

## Transfer extension
15. Find the widest `synchronized` block in your codebase (by lines held); list what leaves the block (I/O, logging, alien calls) and re-derive the section time after the move.
16. Price the virtual-thread migration (21+): which surviving `synchronized` blocks pin carriers on request paths, and what replaces each?

## Exit-ticket extension
- One more sentence: the monitor identity (`this`, `Clazz.class`, guard, parameter) you mis-identified most recently and the log line that exposed it.
- File the before/after counts from your wrong-monitor fix (lossy total vs exact total) as the lab's receipt.
- Name the wait/notify precondition you now check first (`while`-loop, ownership, notifyAll default) and the production symptom that taught it.
