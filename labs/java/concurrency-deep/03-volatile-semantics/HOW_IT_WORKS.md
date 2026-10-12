# How It Works: Volatile Semantics

## The mechanism in one paragraph
Volatile Semantics is the Java Memory Model happens-before edges for volatile fields: visibility, ordering, and limits. The moving parts are volatile field access (JLS 17.4.5), program-order/monitor/lifecycle edges, StoreLoad fences (`xchg`+`lock` on x86, `dmb ish` on ARMv8), safe-publication piggybacking, `VarHandle` access modes, driven through `volatile` field read/write, double-checked locking with volatile, `AtomicIntegerArray`/VarHandle array-element volatile access, `VarHandle.getAcquire/setRelease/getOpaque` (contrast), implemented as described in JLS 17.4 (happens-before), 17.5 (final-field safety), 17.7 (word tearing), JSR-133 (2004 memory-model rewrite), `VarHandle.java` (Java 9). Volatile gives visibility + access atomicity (incl. long/double) but NOT compound-action atomicity (volatile++ races: read-modify-write in three steps); DCL is correct only with volatile (or holder idiom/enum singleton); transitivity A->B->C chains edges; volatile reads are near-free on x86 (TSO) while writes need a fence, both directions need fences on ARM (qualitative only); volatile arrays cover the reference, never the elements.

## Step-by-step through the parts
1. **Name the operands.** Before reasoning, write down the exact objects/fields involved (which thread, which monitor, which field, which atomic). Most bugs are wrong-operand bugs.
2. **Trace one operation end to end.** Pick a single call from `volatile` field read/write, double-checked locking with volatile, `AtomicIntegerArray`/VarHandle array-element volatile access, `VarHandle.getAcquire/setRelease/getOpaque` (contrast) and follow it: JDK entry -> HotSpot primitive -> observable result. Use INTERNALS.md source paths to confirm each hop.
3. **Add the second thread.** Re-trace with two actors interleaved. Ask at each step: which edge orders these two actions? If none, you have a race; say so explicitly.
4. **Check the exits.** Every acquisition has a release path (including exceptions/interrupts/timeouts). Verify yours, then compare with COMMON_MISTAKES.md.
5. **Confirm empirically.** Run the STEP_BY_STEP.md commands (`jstack`, `javap -c`, `jshell`) and match output against the predicted tokens/bytecodes.

## Worked trace
- Start from README.md item 4: Volatile gives visibility + access atomicity (incl. long/double) but NOT compound-action atomicity (volatile++ races: read-modify-write in three steps); DCL is correct only with volatile (or holder idiom/enum singleton); transitivity A->B->C chains edges; volatile reads are near-free on x86 (TSO) while writes need a fence, both directions need fences on ARM (qualitative only); volatile arrays cover the reference, never the elements.
- Reproduce it with the smallest program in STEP_BY_STEP.md, then explain each line of output using the vocabulary of volatile field access (JLS 17.4.5), program-order/monitor/lifecycle edges, StoreLoad fences (`xchg`+`lock` on x86, `dmb ish` on ARMv8), safe-publication piggybacking, `VarHandle` access modes.

## What people get wrong
- Skipping step 1 (reasoning about "the lock" or "the flag" without saying which object/field).
- Treating monitoring output as control input (thread states, fuzzy sums).
- Assuming edges that do not exist (different monitors, plain fields, element access through a volatile array reference).

## Next
- INTERNALS.md for source paths; MATH_FOUNDATION.md for the ordering rules in symbols.

## Second trace: the three-step race inside volatile++
- Disassemble `volCount++` mentally (or via `javap -c`): `getfield` (volatile read), `iadd`, `putfield` (volatile write) — three bytecodes, one edge-free gap between read and write.
- Interleave two threads at the gap: both read 5, both compute 6, both write 6 — one update lost with every step fully visible; visibility never overlaps the gap.
- Replace with `AtomicInteger.incrementAndGet()`: the read-compute-write collapses into one `lock cmpxchg` — the gap (and the race) ceases to exist.
- Conclusion to write down: visibility answers "do I see the latest value when I look"; atomicity answers "does look-plus-write happen as one step" — different questions, different tools.

## Publication-pattern map (fill from your runs)
- Flag shutdown (`volatile boolean stop`): writer sets, readers spin-or-check — visibility only, single writer, no RMW.
- Piggyback publish (plain payload + trailing `volatile ready`): batch all writes before one flag write; readers check flag first — one edge carries arbitrary payload.
- DCL singleton (`volatile Helper instance` + check-lock-recheck + local read): publication plus lazy init; the local variable halves volatile reads on the fast path.
- Holder idiom / enum singleton: publication via class-init lock — correct with zero volatile, preferred unless laziness needs the manual form.
- Array elements: `AtomicIntegerArray` or `VarHandle` element access — the `volatile` keyword on the array buys nothing per element.

## Fence-intuition trace (qualitative)
- x86 read path: volatile read ≈ plain read (TSO orders loads; only compiler reordering is fenced) — reads are the cheap direction.
- x86 write path: StoreLoad fence via `xchg`+`lock` — the write pays, on the order of an uncontended CAS (~10-20ns scale).
- ARM path: explicit `dmb ish` barriers both directions — reads cost more than x86 reads, writes cost more than x86 writes; keep every number qualitative and per-architecture.
- Design consequence: batch payload writes before a single volatile publish — one fence per publication, not one per field.

## Self-check
- Cover the map above and reproduce, from live runs, the stale-spin divergence plus the DCL single-instance assertion — both from memory, then diffed against output.
