# DCL Pattern — Theoretical Foundation

## Core Concept

Double-checked locking publishes a lazily-initialized singleton with one
volatile read on the fast path instead of a monitor acquisition:

```java
Helper helper;                       // MUST be volatile (see below)
Helper get() {
    Helper h = instance;             // (1) unsynchronized read
    if (h == null) {
        synchronized (this) {
            if ((h = instance) == null)   // (2) checked again under lock
                h = instance = new Helper();
        }
    }
    return h;
}
```

Three elements, each load-bearing: the `volatile` field, the *first*
(unsynchronized) check, and the *second* (locked) check. Remove any one
and the idiom breaks a different way — this lab demonstrates all three
failure modes by removing each in turn (one observably, two by proof).

## Why Pre-2004 DCL Was Broken (the reorder)

`helper = new Helper()` is three steps: allocate → init fields → store
reference. Without `volatile`, the JMM permits publishing the reference
*before* the field stores complete (write-write reorder across the
constructor/store boundary, plus visibility staleness for the reader).
A second thread passes check (1), reads a non-null but half-constructed
object. JSR-133 (Java 5) fixed the *model* — `volatile` write/read edges
order construction before publication — but only if the keyword is
present. `volatile` here is not "extra safety"; it is the *entire*
correctness argument.

## The Second Check (snippet 5's lesson)

Drop check (2) and two racing threads serialize on the monitor but *both*
initialize: T1 inits and exits; T2 enters (its check-(1) read predates
T1's write) and inits again — two instances, last publication wins,
constructor side effects run twice. The second check re-reads *under the
lock* (where T1's write is visible via the monitor edge), so exactly one
thread initializes. Deterministically demonstrable — unlike the
reorder itself, which needs adversarial timing to observe.

## The Local-Variable Read (Bloch's shape)

`Helper h = instance` reads the volatile *once* per call instead of twice
(once in each check). Beyond saving a fence: if `instance` is reassigned
between the checks (it can't be here — single assignment — but the shape
generalizes), the method could return a different object than it checked.
Effective Java's prescribed form; the snippets use it throughout.

## The Three Alternatives (when DCL is the wrong answer)

| Idiom | Lazy? | Cost | Notes |
|---|---|---|---|
| `volatile` DCL | yes | 1 volatile read/call | correct; subtle (this lab) |
| Static holder | yes | 0 (class-init lock, once) | simplest correct lazy singleton |
| Enum (`INSTANCE`) | no (eager) | 0 | serialization-safe free (Bloch Item 3); no laziness |
| `synchronized` accessor | yes | monitor/call | obviously correct; fine at low call rates |

The holder idiom deserves emphasis: the JVM's class-initialization lock
(JLS §12.4.2 — recursive, thread-safe, exactly-once) does the
synchronization *for you*, lazily on first access of the holder class.
DCL is for the residual cases (parameterized singletons, framework
constraints, non-static scope) — reach for the holder first.

## What `volatile` Costs Here (measured context)

One volatile read per `get()` call (~1 ns, lab 03 measurements) vs one
monitor enter/exit pair (~20+ ns uncontended). DCL pays for itself above
roughly millions of calls per second per thread — below that, the
`synchronized` accessor's clarity wins. (No microbenchmark in this lab
asserts the crossover; it moves with hardware. The shapes differ
structurally: fence vs monitor.)

## Key Invariants

1. Field `volatile` + check + recheck-under-lock: all three, always.
2. Unsynchronized check without `volatile` publishes half-constructed
   objects (pre-2004 bug, still reproducible by deleting the keyword).
3. Locked recheck without the outer check is just locking (correct but pointless).
4. Single volatile read into a local (Bloch shape) — never read twice.
5. Prefer holder/enum unless laziness-with-parameters forces DCL.
