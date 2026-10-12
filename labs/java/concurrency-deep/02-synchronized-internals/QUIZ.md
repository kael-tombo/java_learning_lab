# Quiz: Synchronized Internals

1. **What bytecodes implement a synchronized block, and why two exits?**
   A: One monitorenter plus (at least) two monitorexit sites — normal path and exception-table path — so throwing still releases the monitor.

2. **Where do biased locks stand on JDK 15/18/23?**
   A: Disabled by default in 15 (JEP 374), removed in 18, flag unrecognized on 23. Reason only about stack-locking vs inflated.

3. **What lives in an inflated ObjectMonitor?**
   A: OS mutex + condition state: _cxq contention queue, _EntryList, _WaitSet; the mark word points at it after inflation.

4. **State the unlock->lock visibility rule and its scope.**
   A: JLS 17.4: unlock on M happens-before later locks of M. Same monitor only — different objects share no edge even over the same fields.

5. **Why must wait() sit in a while loop?**
   A: Spurious wakeups are legal and notifyAll can wake threads whose condition is already false again (stolen signal). Re-check after every return.

6. **Do a static synchronized and an instance synchronized method on one class exclude each other?**
   A: No — Class-object monitor vs this monitor are disjoint. Same-object instance pairs exclude; cross-object pairs do not.

7. **What do lock elision and coarsening do?**
   A: JIT removes locks on non-escaping objects (elision) and merges adjacent same-monitor blocks (coarsening). synchronized-only benefits; library locks are opaque to these.

8. **synchronized vs ReentrantLock: when does each win?**
   A: synchronized: simplicity, JIT treatment, auto-release. ReentrantLock: lockInterruptibly, tryLock timeouts, fairness, multiple conditions; contention parks (WAITING) instead of BLOCKED.

## Scoring
- 7-8 correct: done. 5-6: re-read THEORY.md + INTERNALS.md. Below 5: redo STEP_BY_STEP.md before retrying.

9. **How do you prove the exceptional release exists for your own build?**
   A: Compile a throwing synchronized block and run `javap -c -p`: one `monitorenter`, two `monitorexit` sites, plus an `Exception table:` routing the throw path to the second exit.

10. **Two threads guard one counter with two different lock objects. Exact or lossy?**
    A: Lossy — different monitors share no happens-before edge (JLS 17.4, same-M only), so increments race despite both being "synchronized".

11. **A waiter wakes from `wait()` but finds its predicate false. Name two legal causes.**
    A: Spurious wakeup (spec-allowed, real on some platforms) and stolen signal (a `notifyAll` sibling consumed the condition first) — both are why the loop is `while`, not `if`.

12. **Why does holding a monitor across `sleep` or I/O hurt more than a long computation inside?**
    A: Computation holds the fast path briefly; sleep/I/O hold exclusion for wall-clock time while waiters queue BLOCKED (uninterruptibly) — nanosecond mechanism, seconds-long serialization.

13. **Your dump shows BLOCKED threads whose holder is parked in `LockSupport`. Which API is actually contended?**
    A: Both, in layers: the BLOCKED threads want a `synchronized` monitor held by a thread that itself waits on a park-based primitive — fix the parked holder first; freeing it drains the BLOCKED queue.

## After scoring
- For every miss, quote the proving line: `javap -c` output, dump token, or JLS section — no paraphrase accepted until the source line is pasted.
