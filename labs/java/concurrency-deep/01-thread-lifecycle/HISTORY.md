# History: Thread Lifecycle

## Green threads to platform threads to virtual threads
- **1996, JDK 1.0 (James Gosling team, Sun):** `java.lang.Thread` with `start/join/sleep` and the six-state model foundations; early VMs used green threads (user-space scheduling).
- **Late 1990s-2000s:** native-thread mapping becomes standard; `jstack` and thread-dump culture emerge as the primary production diagnostic.
- **2004, JSR-166 (Doug Lea):** `java.util.concurrent` adds park-based primitives (`LockSupport`), so dumps learn the `WAITING (parking)` vs `BLOCKED (on object monitor)` split this lab drills.
- **2023, Java 21 (JEP 444, Ron Pressler / Alan Bateman teams):** virtual threads ship; same six `Thread.State` values, unmounting carriers when parked, with `synchronized` pinning as the documented limitation through JDK 23.

## What changed and what did not
- Scheduling substrates changed twice (green -> native -> virtual); the six-state vocabulary and the BLOCKED-means-monitor rule never changed.
- `Thread.getState` javadoc has always restricted the API to monitoring, not control.

## Dates to remember (confident facts only)
- JSR-133 memory-model rewrite: 2004 (Java 5). JSR-166 concurrency utilities: 2004 (Java 5).
- `LongAdder`: Java 8. `VarHandle`: Java 9. Biased locking off by default: JDK 15 (JEP 374); removed: JDK 18.
- Virtual threads: Java 21 (JEP 444). *Java Concurrency in Practice* (Goetz et al.): 2006.

## Sources
- REFERENCES.md entries for JLS 17.4/17.5/17.7, JSR-133 FAQ (Pugh), JSR-166, OpenJDK source paths.

## Why the six-state vocabulary survived
- Each substrate change (green -> native -> virtual) reimplemented parking and blocking underneath while keeping the reported states fixed, so dumps stayed readable across decades.
- The BLOCKED-means-monitor rule survived because the monitor subsystem stayed distinct from the park-based subsystem added by JSR-166 in 2004 — two mechanisms, two dump tokens.
- `getState()` stayed monitoring-only through every revision: no release ever blessed branching on sampled states, because sampling races are structural rather than version-specific.
- The daemon-exit rule never changed either: green, native, and virtual runtimes all exit when the non-daemon set empties, so shutdown reasoning ports across eras.

## Mechanism depth on the dated entries
- Green-thread era (JDK 1.0): user-space scheduling meant RUNNABLE covered even more ground — the VM multiplexed many Java threads onto few OS threads, so ready-vs-running was invisible by design.
- Native-mapping era: dumps gained the parenthetical API tokens (`parking`, `sleeping`, `on object monitor`) because one WAITING value alone was not actionable — the token names the API that must supply the wake.
- JSR-166 (2004, Doug Lea): `LockSupport.park` gave locks, queues, and futures a non-monitor wait, which is exactly when dump readers had to learn that contention no longer implies BLOCKED.
- JSR-133 (2004) matters to lifecycle readers too: the `start()`/`join()` edges specified in JLS 17.4 are why joining a TERMINATED thread is a safe publication point, not merely a state observation.
- JEP 444 (Java 21): virtual threads kept all six values and added unmount-on-park underneath; the `synchronized`-pins-carrier note (through JDK 23) is a scheduler limitation of that release range, not a seventh state.
- Production practice stabilized on two dumps plus CPU (`jstack` twice, `top -H`): one dump is a photograph, two make a film — a technique independent of substrate.

## How to use these dates
- Cite the substrate (green/native/virtual) when an old dump looks alien; cite the subsystem (monitor vs park) when explaining any BLOCKED-vs-WAITING split.
- When a guide predates 2004, check whether its "blocked" means modern BLOCKED or just "not running" — pre-JSR-166 writing often conflates them.
- When a guide predates Java 21, its thread-count advice assumes platform threads; re-derive pool sizes before applying it to virtual-thread systems.
- Treat any state-transition timing claim ("WAITING threads wake in X ms") as unportable folklore — the specification promises events and expiries, never latencies.
