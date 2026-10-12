# Synchronized Internals — Theoretical Foundation

## Core Concept

`synchronized` is a **monitor** operation, not a lock object: the JVM binds
each `synchronized` block to an object monitor, acquires it on entry, and
releases it on exit — including exceptional exit. The compiler emits this
pair explicitly:

```
monitorenter
... body ...
monitorexit        // normal path
... exception table routes every Throwable to a second monitorexit ...
```

One `monitorenter`, potentially *multiple* `monitorexit` bytecodes (normal +
exceptional paths) — which is why "synchronized always releases" holds even
when the body throws. (Verified in this lab's CODE_DEEP_DIVE via `javap -c`.)

## The Three Lock Levels (post–biased-locking HotSpot)

Biased locking is gone — disabled by default in JDK 15 (JEP 374), **removed
in JDK 18** (JDK-8256425), and the flag itself unrecognized by JDK 23
(`Unrecognized VM option 'UseBiasedLocking'`). What remains is a two-step
ladder plus the header fast path:

1. **Stack locking (lightweight)**: uncontended acquisition CASes the
   object's mark word to point at a lock record on the acquiring thread's
   stack ("displaced mark word"). No OS mutex, no park — a handful of
   instructions. Recursive entry just pushes another (nearly free) record.
2. **Inflation (heavyweight)**: on real contention the monitor *inflates* —
   HotSpot allocates an `ObjectMonitor` (C++ object with OS mutex +
   condition variables: `_cxq` contention queue, `_EntryList`, `_WaitSet`)
   and swings the mark word to point at it. Contenders now park in the OS.
3. **Deflation**: when the monitor is released and uncontended, HotSpot may
   deflate back to stack locking. The observable contract — mutual
   exclusion — never changes with the level.

The mark word (64-bit object header: identity hash, GC age bits, lock state)
is the traffic light; the monitor is the building behind it. Most programs
live at level 1 almost all the time — which is why uncontended
`synchronized` costs ~10–20ns, not microseconds.

## Memory Semantics: synchronized Is a Happens-Before Edge

JLS §17.4: an unlock on monitor M *happens-before* every subsequent lock of
M. Practical consequences:

- Everything your thread wrote before releasing `synchronized(o)` is visible
  to the next thread that acquires `synchronized(o)` — no `volatile`
  needed on the guarded fields.
- The edge is tied to the *monitor*, not the code: two blocks synchronized
  on *different* objects share no edge, even if they touch the same fields.
  Same fields + different locks = data race wearing a disguise.
- `wait()` releases the monitor and re-acquires it before returning — so
  the post-`wait()` code sees everything the notifier wrote before
  `notify()`, provided both synchronize on the same object.

## wait/notify Protocol (and Its Sharp Edges)

- `wait()`, `notify()`, `notifyAll()` require holding the monitor —
  otherwise `IllegalMonitorStateException`. The check is dynamic (the JVM
  verifies ownership at the call), not static.
- **Always `wait()` in a `while` loop re-checking the condition.**
  Spurious wakeups are real (allowed by the spec, occur on some platforms),
  and `notifyAll()` wakes threads whose condition may already be false
  again (stolen signal). `if (cond) wait()` is a bug; `while (cond) wait()`
  is the idiom.
- `notify()` wakes *one* arbitrary waiter; `notifyAll()` wakes all (they
  then serialize re-acquiring the monitor). Prefer `notifyAll()` unless you
  can prove exactly one waiter can proceed *and* no other waiter exists for
  a different condition on the same monitor (the classic multi-condition
  pitfall that makes `notify()` lose signals).
- `wait()` has two exits — notified/interrupted *or* (timed variant)
  timeout — and re-acquires the monitor before either returns. A notifier
  that still holds the lock keeps waiters BLOCKED after waking them.

## synchronized Methods, Blocks, and Static Locks

- Instance `synchronized` method ⟺ `synchronized(this)` wrapping the body.
- `static synchronized` method ⟺ `synchronized(TheClass.class)`.
- These are **different monitors**: a static and an instance synchronized
  method on the same class do *not* exclude each other. Instance–instance
  pairs on the *same object* do; on *different objects* don't. Every
  "synchronized doesn't seem to work" bug is a wrong-monitor bug — draw
  which object is the lock before anything else.

## Reentrancy

Monitors are reentrant per-thread: a thread holding M may re-enter
`synchronized` on M freely (recursion, nested calls, super-calls). The
monitor counts entries and needs equal exits. Consequences: (a) calling an
overridable method from a constructor inside `synchronized` can't deadlock
against itself; (b) reentrancy means *any* path that re-enters while holding
an inconsistent invariant is a self-inflicted race the lock can't prevent —
locks compose badly with alien (overridable/callback) methods.

## synchronized vs j.u.c. Locks

| | `synchronized` | `ReentrantLock` |
|---|---|---|
| Acquisition | block-structured only (exit at scope end) | `lock()`/`unlock()` anywhere — and must be paired by hand |
| Interruptible wait | no | `lockInterruptibly()` |
| Timeout | no | `tryLock(t, unit)` |
| Fairness option | no (no FIFO guarantee) | optional fair mode |
| Condition queues | one (`wait` set) | many (`newCondition()`) |
| Contended state | BLOCKED | WAITING (parking) |
| JIT treatment | lock elision/coarsening apply | library calls, less transparent to JIT |

`synchronized` wins on simplicity and JIT optimization (lock elision removes
locks on non-escaping objects; lock coarsening merges adjacent blocks on the
same monitor). `ReentrantLock` wins the moment you need timeouts,
interruption, fairness, or multiple conditions.

## Key Invariants

1. Monitor entry and exit are paired on *every* path, including exceptions
   (compiler-generated, not programmer discipline).
2. Unlock → subsequent-lock on the same monitor is a happens-before edge.
3. Wait sets belong to the monitor; `wait`/`notify` without ownership throws.
4. Inflation is one-way per contention episode but deflatable; level is an
   implementation detail — semantics never change with it.
5. No fairness: among BLOCKED threads the winner is unspecified (and on some
   platforms effectively LIFO-ish) — starvation is legal.
