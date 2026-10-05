# MINI PROJECT — Memory Model: Prove It with jcstress

## Goal (2 weeks, ~8–10h)
Build a `jmm-proofs` suite turning 4 classic races (stale flag, lost update,
broken DCL, unsafe publication) into failing-then-passing jcstress tests with
documented happens-before edges.

## Requirements
### Functional
1. Cases: (a) non-volatile stop-flag hang, (b) `count++` lost update,
   (c) DCL without volatile (half-constructed), (d) `this`-escape listener.
2. Each case: broken version + fixed version (`volatile`, `LongAdder`,
   `volatile`-DCL or enum singleton, factory-published immutable).
3. jcstress harness: `@JCStressTest @State` classes asserting forbidden
   outcomes observed on broken, never on fixed (document CPU/trial counts).
4. `ConcurrentHashMap` lab: compound `if-absent-then-put` fixed with
   `computeIfAbsent` (prove race with threaded test + JFR monitor events).
5. VarHandle demo: `VarHandle.getAcquire/setRelease` ordered-flag variant
   with edge diagram; volatile-equivalence note.

### Non-functional
- Suite runs in CI (`./gradlew jcstress` or maven) with tiered time budget.
- JFR + `jcmd Thread.print` capture during contention run (prove liveness:
  blocked vs spinning classification).
- 12+ unit tests around immutability (no setters, final fields, no escape).
- README: per-case HB-edge table (write→read edge name + JLS reference).

## Phases
### Week 1 — Break It (4–5h)
- Steps: write 4 broken cases, observe failures (jcstress + plain-thread
  demo), capture thread dumps of spinning readers.
- Deliverable: failure catalog with interleavings.

### Week 2 — Fix + Prove (4–5h)
- Steps: apply fixes, re-run jcstress to clean, VarHandle + CHM labs.
- Deliverable: green suite + HB-edge doc.

## Evaluation Rubric (100 pts)
| Criterion | Excellent (20) | Pass (12–15) | Fail (<12) |
|-----------|----------------|--------------|------------|
| Race coverage | 4 broken observed | 2–3 shown | Asserted safe |
| Fix quality | Idiomatic + edge cited | Works | volatile-sprinkle |
| jcstress rigor | Modes/arbiters, trials noted | Runs | Main-loop only |
| Immutability | Escape-free, final | Mostly | Mutable shared |
| Docs+threads | HB table + dump analysis | Present | Missing |

Pass >= 70. Stretch: `StampedLock` vs `synchronized` visibility note;
JFR `jdk.JavaMonitorEnter` contention memo; ARM vs x86 discussion.
