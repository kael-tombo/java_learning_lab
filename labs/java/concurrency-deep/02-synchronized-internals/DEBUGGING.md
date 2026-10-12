# Debugging: Synchronized Internals

## Capture
```
javap -c -p suspect/Sync.class | grep -A3 monitorenter
jstack <pid> | grep -B2 -A8 "BLOCKED"
```

## Decode
- Missing second `monitorexit` in old/patched bytecode -> broken pairing; recompile, never hand-edit.
- `BLOCKED (on object monitor)` clusters at one method -> contested monitor; confirm identity: which object (`this`, `Clazz.class`, explicit guard)?
- `WAITING (on object monitor)` with no notifier in code search -> lost-signal hang; require the `while`-loop + notify path.
- Unrecognized `UseBiasedLocking` flag on JDK 23 output -> remove the flag; reasoning must assume stack-lock/inflated only.

## Triage recipe
1. Identify the contested monitor address, then its allocation site (private guard? `this`? `Class`? interned string?).
2. Verify static-vs-instance disjointness: is the "protection" even on the same monitor?
3. Check wait sites for `while` + `notifyAll` discipline; convert `notify` to `notifyAll` unless single-condition proven.
4. For hot uncontended paths confirm elision/coarsening opportunities (non-escaping objects, adjacent blocks) via JIT logs rather than guessing.

## Five-minute checklist
- [ ] Monitor identity written down? [ ] Same monitor on all paths touching the invariant? [ ] wait in while? [ ] notifyAll unless proven single? [ ] No alien calls inside?

## Sources
- `javap -c` (monitorenter + 2 monitorexit), HotSpot `objectMonitor.cpp`, `synchronizer.cpp`, `markWord.hpp`, JLS 17.1/17.4. Keep THEORY.md open; every diagnosis ends by naming the violated invariant.

## Monitor-identity audit
- Print the guard's identity at each site (`System.identityHashCode(guard)`): two synchronized blocks logging different identities around one field prove the wrong-monitor bug before any dump is opened.
- Suspect guards in order: method parameter, `this` leaking to callers, boxed primitives and interned strings (shared JVM-wide), then `Class` objects — each is a way to lock a different object than intended.
- Static-vs-instance check: log `this` vs `Clazz.class` at entry; overlapping timestamps with different identities confirm disjoint monitors, matching CODE_DEEP_DIVE.md snippet 4.

## Inflation and deflation evidence
- JFR `jdk.JavaMonitorEnter` rates plus `jstack` EntryList depth: rising rates with flat critical-section time mean more contenders, not slower code — split the guard instead of speeding the body.
- Suspected deflation churn (inflate/deflate cycles on a bursty lock): the symptom is latency variance with no throughput change; narrowing the block or splitting the monitor settles it.
- Confirm elision/coarsening with `-XX:+PrintCompilation -XX:+LogCompilation` (or JFR `jdk.Compilation`): non-escaping locks should vanish, adjacent same-monitor blocks should merge — absent entries mean the JIT could not prove safety.

## wait/notify forensics
- `WAITING (on object monitor)` with zero `notify`/`notifyAll` textual hits on that guard -> lost-signal hang by inspection; add the notifier or convert to a timed wait with re-check.
- `notify()` on a monitor with two distinct wait predicates -> stolen-signal suspect: wake the wrong predicate and the right one sleeps; `notifyAll()` plus `while` re-check closes it.
- Waiter that wakes then stays BLOCKED: the notifier still holds the lock past `notify()` — move the notify to the block exit (or shrink the post-notify section) so wake and re-entry are not serialized by your own holder.
