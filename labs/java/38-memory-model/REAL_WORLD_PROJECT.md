# REAL-WORLD PROJECT — Memory Model: Config Flag Ignored + Counter Drift

## Incident Scenario
New `killSwitch` to disable a toxic promo never takes effect on 30% of pods
(stale read spins forever), while the `soldCount` oversells limited stock by
1,800 units — finance and customers both escalate within the hour.

## Symptoms
- `while (!killSwitch) { ... }` loop never exits on some cores; no `volatile`.
- `soldCount++` on plain `long` loses updates at 8+ threads (oversell).
- DCL `PromoConfig.getInstance()` occasionally returns half-initialized
  (null rules list → NPE) under cold-start contention.
- `HashMap` config cache updated live → infinite loop on one pod (corrupted bin).
- Tests pass single-threaded; issue vanishes under debugger (Heisenbug).

## Investigation Tasks
1. Threads: `jcmd <pid> Thread.print` × 3 on spinning pod — runnable loop
   on same line (stale-flag signature, not deadlock); note no monitor entry.
2. JFR: `jcmd <pid> JFR.start duration=120s filename=jmm.jfr settings=profile`;
   `jdk.JavaMonitorEnter` (DCL/HM contention), `jdk.ThreadPark`, execution
   samples pinning the spin method for the flame.
3. Heap: `jcmd <pid> GC.heap_dump` — half-constructed `PromoConfig` (null
   final-appearing list) + `HashMap` degenerative bin on corrupted pod.
4. Code audit: `grep -rn "volatile\|synchronized\|Atomic\|HashMap\|getInstance" src/`;
   list every shared mutable field and its HB edge (or absence).
5. Repro: jcstress-style 8-thread counter + flag test on staging hardware;
   record lost-update count and stale-read duration distribution.
6. Log forensics: `grep "soldCount\|oversell\|NullPointer.*rules" app.log`;
   reconcile counter vs DB decrement (ground truth).
7. Config path: trace killSwitch write (admin API) → read (worker) for the
   missing edge (no volatile/lock/queue handoff).

## Root Cause
No happens-before on three paths: plain flag (visibility), plain `++`
(atomicity), racy DCL + `this`-escape (publication), plus unsynchronized
`HashMap` mutation — correct-by-luck on x86/low-core, broken at scale.

## Resolution
- Immediate: `volatile` flag + `AtomicLong/LongAdder` counter with DB guard
  (decrement-check), restart corrupted pod, freeze promo at safe cap.
- Short-term: enum-singleton or `volatile`-DCL config, immutable
  `PromoConfig` (finals, no escape), `ConcurrentHashMap`/copy-on-write,
  jcstress regression tests for all three races.
- Long-term: JMM review checklist + lint (no plain shared mutable), stress
  tier in CI, contention/visibility dashboard (JFR monitor events).

## Runbook
```
1. Thread.print (spin vs deadlock) + JFR + heap_dump off-box.
2. Land volatile/counter/config hotfix on canary; replay race test.
3. Reconcile oversell vs DB; compensate + cap.
4. jcstress green before fleet rollout.
5. Postmortem: HB-edge table + lint rules.
```

## Metrics
- Stale-read 0 in 1M flag-flip trials; counter == DB within 0 drift.
- DCL NPE 0 over 100k cold starts; jcstress forbidden outcomes = 0.
- Contention samples on config path < 1% (JFR monitor proof).

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- JLS memory model (ch. 17): https://docs.oracle.com/en/java/javase/21/docs/specs/jls/se21/html/jls-17.html
- jcstress project: https://openjdk.org/projects/code-tools/jcstress/
