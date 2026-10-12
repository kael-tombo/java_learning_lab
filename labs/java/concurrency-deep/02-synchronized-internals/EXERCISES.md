# Exercises: Synchronized Internals

## 1. See the two monitorexits (15 min)
Compile a `synchronized` block that throws, run `javap -c -p`, and highlight `monitorenter` plus both `monitorexit` sites (normal + exception-table target). State in one line why throwing cannot leak the monitor.

## 2. Wrong-monitor bug hunt (20 min)
Two threads increment one field under two different guards; show lost updates with 1M iterations. Fix with a single guard and show the count go exact. APIs: `synchronized`, `Thread.join`.

## 3. Static vs instance disjointness (15 min)
One thread loops in a `static synchronized` method, another in an instance `synchronized` method; timestamp both and show overlap (no exclusion). Then guard both on one private static object and show serialization.

## 4. while-wait + notifyAll (25 min)
Bounded buffer (capacity 4) with `wait/notifyAll` in `while` loops; producers/consumers run 10k items with zero loss. Then swap to `if`+`notify` and record the hang or corruption; revert.

## 5. Reentrancy + alien-call audit (15 min)
Nested `synchronized (guard)` across two methods works (reentrancy count). Then add a listener callback inside and demonstrate the invariant break; refactor the call outside with a snapshot.

## Submission checklist
- [ ] Each task ran on your JVM with output pasted. [ ] Predictions written before runs. [ ] One deliberate break-and-fix per lab recorded.

## 6. Bytecode pairing on methods (15 min)
Task: compile one `synchronized` instance method and one `static synchronized` method; run `javap -c -p` on both and mark the `monitorenter` plus both `monitorexit` sites in each.
Check: state which monitor each method binds (`this` vs `Clazz.class`) purely from the constant-pool loads preceding `monitorenter`.
APIs: `javac`, `javap -c -p`; success = both pairings quoted line-for-line from your JVM output.

## 7. Contention cliff measurement (20 min)
Task: guard one counter with a single monitor; time 1M increments at 1, 4, and 16 threads (warmup included, as in CODE_DEEP_DIVE.md snippet 5).
Check: plot ops/s vs thread count and mark where adding threads stops helping; capture a `jstack` at peak showing the identical BLOCKED stacks.
APIs: `synchronized`, `System.nanoTime`, `jstack`; success = the plateau point stated with numbers from your machine.

## 8. Elision proof (15 min)
Task: write a method synchronizing on a method-local (non-escaping) object; benchmark it, then benchmark the same body with the lock on a shared guard.
Check: explain the gap via lock elision (JIT removes the non-escaping lock); confirm with `-XX:+PrintCompilation`/`LogCompilation` output showing the eliminated site.
APIs: `synchronized`, JMH or hand harness, JIT logs; success = elision evidence quoted, not assumed.

## Submission additions
- [ ] `javap -c` pairing excerpts pasted for block, instance-method, and static-method forms.
- [ ] Contention-cliff numbers (1/4/16 threads) with warmup described.
- [ ] Elision evidence quoted from JIT logs or stated as unconfirmed.
- [ ] Every wrong-monitor break recorded with the two identities logged.
- [ ] `while`-vs-`if` wait comparison run with the failure mode named.
