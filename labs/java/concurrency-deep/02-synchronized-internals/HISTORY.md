# History: Synchronized Internals

## From monitors to stack locking to un-biased HotSpot
- **1970s, C.A.R. Hoare:** monitors as a language construct (mutual exclusion + condition variables) — the idea Java later bakes into every object.
- **1996, JDK 1.0:** `synchronized` methods/blocks with `monitorenter/monitorexit` bytecodes; `wait/notify` on every object's monitor.
- **2004, JSR-133 (Bill Pugh, Jeremy Manson, Brian Goetz and others):** memory-model rewrite specifies unlock->lock happens-before (JLS 17.4), giving `synchronized` its visibility meaning.
- **2006, Java 6:** biased/stack-locking optimizations mature in HotSpot for the uncontended fast path.
- **JDK 15 (JEP 374, 2020):** biased locking disabled by default; **JDK 18 (2022):** biased locking removed; on JDK 23 the `-XX:+UseBiasedLocking` flag is unrecognized.
- **2023, Java 21 (JEP 444):** virtual threads expose synchronized pinning as the interaction to watch.

## What changed and what did not
- Lock *implementation* changed repeatedly (biased -> stack -> inflated/deflated); the contract (paired enter/exit, reentrancy, ownership-checked wait/notify, same-monitor visibility edge) never changed.

## Dates to remember (confident facts only)
- JSR-133 memory-model rewrite: 2004 (Java 5). JSR-166 concurrency utilities: 2004 (Java 5).
- `LongAdder`: Java 8. `VarHandle`: Java 9. Biased locking off by default: JDK 15 (JEP 374); removed: JDK 18.
- Virtual threads: Java 21 (JEP 444). *Java Concurrency in Practice* (Goetz et al.): 2006.

## Sources
- REFERENCES.md entries for JLS 17.4/17.5/17.7, JSR-133 FAQ (Pugh), JSR-166, OpenJDK source paths.

## Why Hoare's monitor maps so cleanly onto Java
- Hoare's 1970s construct paired mutual exclusion with condition variables per monitor — Java copied the pairing verbatim: every object carries a monitor, `wait`/`notify` are the condition operations.
- The while-loop idiom predates Java: Mesa/Cedar practice (spurious wakeups on real hardware) forced re-check discipline, which JCIP later codified for `Object.wait()` users.
- Reentrancy per thread was in the original design: nested monitor entry counting entries/exits, so recursion and super-calls compose — a deliberate departure from non-recursive mutex lore.

## Mechanism depth on the dated entries
- JDK 1.0 `monitorenter`/`monitorexit`: the JVM verified structured pairing at class-load (plus the exception table at compile time), so unbalanced手工 locking was unrepresentable in bytecode — unlike later library locks.
- JSR-133 (2004, Pugh/Manson/Goetz and others): gave `synchronized` its visibility meaning (unlock -> lock happens-before, JLS 17.4), turning monitors from exclusion-only into publication edges.
- Java 6 era optimizations: stack locking made the uncontended path a mark-word CAS (~10-20ns scale) while biased locking chased the single-thread-repeated-entry case — two different fast paths for two different patterns.
- JEP 374 (JDK 15, 2020) disabled bias by default after measurements showed modern workloads rarely benefit and the bookkeeping costs every acquisition; JDK 18 (JDK-8256425) removed it, and JDK 23 no longer parses the flag.
- JEP 444 (Java 21): virtual threads re-exposed inflation cost — a BLOCKED virtual thread pins its carrier, so the old "BLOCKED is cheap-ish" intuition from platform-thread days needed re-pricing at virtual scale.

## How to read old tuning guides
- Any flag, table, or benchmark mentioning `UseBiasedLocking` describes a JVM that no longer exists — translate its advice into stack-lock vs inflated terms or discard it.
- Pre-2004 visibility claims ("synchronized flushes caches") predate the happens-before specification; restate them as same-monitor unlock -> lock edges or drop them.
- Pre-2023 contention advice assumes platform threads; at virtual-thread scale the same BLOCKED queue costs carriers, so re-measure before applying old pool-sizing rules.
