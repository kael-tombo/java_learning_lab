# History: Atomic Classes

## From compare-and-swap hardware to java.util.concurrent.atomic
- **1970s-80s:** CAS/LL-SC instructions appear on mainframes and multiprocessors (IBM System/370 `CS`, later x86 `cmpxchg` with `lock` prefix) as the hardware primitive for lock-free algorithms.
- **2004, JSR-166 (Doug Lea):** `java.util.concurrent.atomic` ships with Java 5 — AtomicInteger/Long/Reference/Arrays built on Unsafe CAS intrinsics.
- **2012, Java 7:** `compareAndExchange` conceptual groundwork and fork-join época; weak-compare semantics clarified across platforms.
- **2014, Java 8:** `LongAdder/LongAccumulator/DoubleAdder` (inspired by striped counting) relieve single-word CAS contention; `getAndUpdate/accumulateAndGet` add side-effect-free functional loops.
- **2017, Java 9 (JEP 193):** `VarHandle` gives a supported specification vocabulary (`compareAndSet`, `getAndAdd`) above the Unsafe mechanics.
- **Ongoing:** `Striped64` cell design (per class javadoc: `@Contended`-padded cells, demand growth) stays the standard answer to CAS-word contention.

## What changed and what did not
- Mechanism migrated from raw Unsafe toward VarHandle-specified effects; the CAS-loop contract (single linearization point, retry on loss, ABA exposure) never changed.

## Dates to remember (confident facts only)
- JSR-133 memory-model rewrite: 2004 (Java 5). JSR-166 concurrency utilities: 2004 (Java 5).
- `LongAdder`: Java 8. `VarHandle`: Java 9. Biased locking off by default: JDK 15 (JEP 374); removed: JDK 18.
- Virtual threads: Java 21 (JEP 444). *Java Concurrency in Practice* (Goetz et al.): 2006.

## Sources
- REFERENCES.md entries for JLS 17.4/17.5/17.7, JSR-133 FAQ (Pugh), JSR-166, OpenJDK source paths.

## Why hardware CAS won the primitive contest
- Mainframe `CS` (IBM System/370) and later x86 `lock cmpxchg` gave one indivisible compare-and-swap: enough to build lock-free structures without OS mutexes, retries replacing parking as the contention strategy.
- LL-SC (ARM/POWER load-linked/store-conditional) offered the same power with a different contract — reservations instead of comparison — which is why weak/spurious-failure semantics exist in the Java API at all.
- The performance bet: uncontended CAS costs ~10-20ns (one instruction plus coherence) vs monitor inflation's mutex-plus-park microseconds — orders apart, so single-variable RMW migrated off locks wherever semantics allowed.

## Mechanism depth on the dated entries
- JSR-166 (2004, Doug Lea): shipped `AtomicInteger/Long/Reference/Arrays` on Unsafe CAS intrinsics — volatile memory effects with single-instruction commits, specified before VarHandle vocabulary existed.
- Java 7-8 era: single-word CAS contention collapse under metrics workloads motivated striped counting (CHM `CounterCell` thinking applied to counters) — `LongAdder`/`LongAccumulator`/`DoubleAdder` landed in Java 8 with demand-grown `Cell[]`.
- Java 8 functional loops (`getAndUpdate`/`accumulateAndGet`): pre-wrote the CAS loop with the function outside the CAS — the re-execution contract (side-effect-free only) follows directly from retry geometry, not from API taste.
- Java 9 (JEP 193, `VarHandle`): gave the supported specification vocabulary (`compareAndSet`, `getAndAdd`, acquire/release modes) above the Unsafe mechanics — source now reads VarHandle, silicon still runs the intrinsic.
- `Striped64` design (per class javadoc): `@Contended`-padded cells, thread-hash spreading, demand growth on contention — the standard answer to CAS-word saturation, documented where the code lives.

## How to read old atomic advice
- Pre-Java-8 "atomics don't scale" benchmarks measured single-word CAS under many writers — true then for that shape, superseded by striping for counters; sequence numbers still want `AtomicLong`.
- Any ABA discussion predating stamped/markable references treats CAS equality as history — translate to stamp/mark/fresh-allocation terms before applying.
- "Weak CAS is faster, prefer it" without the loops-only qualifier is a portability bug in waiting — ARM/LL-SC spurious failures make one-shot weak CAS incorrect, not merely slower.
