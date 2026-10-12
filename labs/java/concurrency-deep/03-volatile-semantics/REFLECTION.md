# Reflection: Volatile Semantics

## Recall without notes
1. State the lab's key fact (Volatile gives visibility + access atomicity (incl. long/double) but NOT compound-action atomicity (volatile++ races: read-modify-write in three steps); DCL is correct only with volatile (or holder idiom/enum singleton); transitivity A->B->C chains edges; volatile reads are near-free on x86 (TSO) while writes need a fence, both directions need fences on ARM (qualitative only); volatile arrays cover the reference, never the elements.) in under 40 words.
2. List the structures (volatile field access (JLS 17.4.5), program-order/monitor/lifecycle edges, StoreLoad fences (`xchg`+`lock` on x86, `dmb ish` on ARMv8), safe-publication piggybacking, `VarHandle` access modes) and one API each from (`volatile` field read/write, double-checked locking with volatile, `AtomicIntegerArray`/VarHandle array-element volatile access, `VarHandle.getAcquire/setRelease/getOpaque` (contrast)) that touches them.

## Connect
3. Which invariant from THEORY.md did your STEP_BY_STEP.md probe demonstrate? Quote the probe output line that proves it.
4. Where does this lab's mechanism meet the neighboring lab (lifecycle<->monitors<->volatile<->atomics)? Name one concrete handoff (e.g. BLOCKED vs parking, unlock edge vs volatile edge, CAS vs lock for one counter).

## Challenge your intuition
5. Write the wrong version first (one COMMON_MISTAKES.md bug), predict its failure mode, then run it. Where did your prediction differ from the run?
6. Which of your predictions relied on timing or fairness? Restate it using only specified edges and invariants.

## Transfer
7. Name one place in your own codebase where the Java Memory Model happens-before edges for volatile fields: visibility, ordering, and limits is assumed but unchecked. What single edge, guard change, or API swap would make it checkable?
8. What will you measure (PERFORMANCE.md harness) before claiming the fix helped?

## Exit ticket
- Two sentences: what breaks, and which source (JLS 17.4 (happens-before), 17.5 (final-field safety), 17.7 (word tearing), JSR-133 (2004 memory-model rewrite), `VarHandle.java` (Java 9)) you would open first when it does.

## Draw the chain (new prompts)
9. Write the piggyback chain for your own config-reload path in -po-/-hb- symbols; circle the single cross-thread arrow and name its JLS rule.
10. Exhibit the colliding `volatile++` schedule for two threads (both read 5, both write 6) and mark the edge-free gap the race lives in.
11. State the DCL counterexample execution (reference visible, fields zero) as a legal schedule — then point at the keyword that removes it from the legal set.

## Break one link
12. Take a working publication harness and move the flag write first; predict the failure in symbols, run it, and record where prediction and run diverged.
13. Make the DCL field plain and stress it; characterize the outcome honestly (likely still passes — races hide) and explain why passing changes nothing about the verdict.
14. Swap `AtomicIntegerArray` back to `volatile int[]` in the array exercise; name the exact hop that vanishes (element edge) while the reference edge stays.

## Transfer extension
15. Find every cross-thread flag in your codebase; classify each as volatile/atomic/interrupt/plain — plain ones are bugs until proven single-threaded.
16. Find every `++`/`+=` on a shared field; sort into AtomicLong/LongAdder/lock replacements with the contention level that picks the winner.

## Exit-ticket extension
- One more sentence: the hb arrow you omitted most often (po-vs-hb confusion, array trap, DCL keyword) and the incident that taught it.
- File your StaleSpin numbers (plainSpins vs volSpins with BOUND) as the lab's receipt.
- Name the weakest hb chain currently in your codebase (fewest explicit edges) and the single keyword that hardens it.
