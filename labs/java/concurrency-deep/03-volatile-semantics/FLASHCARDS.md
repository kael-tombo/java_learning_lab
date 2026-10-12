# Flashcards: Volatile Semantics

Q: Volatile guarantees? | A: Visibility (write hb later read) + access atomicity incl. long/double.
Q: Volatile non-guarantee? | A: No compound-action atomicity — volatile++ races.
Q: Four hb rules? | A: Program order; volatile write->read; unlock->lock; start/join/executor edges.
Q: Piggyback chain? | A: writeX -po-> writeV -hb-> readV -po-> readX (transitivity publishes payload).
Q: DCL fix? | A: Field must be volatile (JSR-133, 2004) — or holder idiom / enum singleton.
Q: x86 volatile costs? | A: Reads ~free (TSO); writes pay StoreLoad fence (xchg+lock).
Q: ARM volatile costs? | A: Both directions need fences (dmb ish) — qualitative only.
Q: volatile int[] coverage? | A: Reference only; elements plain (use AtomicIntegerArray/VarHandle).
Q: JLS 17.7 tearing? | A: Plain long/double may split; volatile forbids it.
Q: VarHandle vs volatile default? | A: Default volatile; acquire/release/opaque only profiler-driven.

## Method
- Cover the A column; recall aloud; check. Cycle missed cards twice before finishing.

## More cards (same deck)
Q: Piggyback pattern in one sentence? | A: Plain payload writes before a volatile write are visible after a later volatile read (transitivity).
Q: Program-order alone orders threads? | A: No — po orders within one thread only; cross-thread needs vol/mon/lifecycle edges.
Q: Volatile write vs later plain writes? | A: No edge pulling them in — only the specified write->read arrow exists; draw it.
Q: Transitivity across three threads? | A: Two volatile edges compose (A->B->C): C sees A's write via chained hb.
Q: Final-field safety (JLS 17.5)? | A: Properly constructed final fields visible without volatile — covers immutable payloads.
Q: Static holder idiom mechanism? | A: JVM class-init lock synchronizes publication — zero keywords, same guarantee.
Q: Enum singleton mechanism? | A: Class init + single instance (Bloch Item 3) — serialization-safe publication free.
Q: Hoisted read in one line? | A: JIT lifts loop-invariant plain reads out of the loop — spinner goes stale forever.
Q: OSR's role in stale-flag demos? | A: On-stack replacement compiles the hot loop mid-run — the hoist lands after warmup, not at start.
Q: `getAcquire`/`setRelease` meaning? | A: One-directional edges (cheaper): acquire pairs with release, no full fence both ways.
Q: `getOpaque`/`setOpaque` meaning? | A: Visibility-progress without ordering — no happens-before; never for publication.
Q: Shutdown flag correct forms? | A: volatile boolean, AtomicBoolean, or interrupt/latch — never a plain boolean spin.

## Drill
- Write the piggyback chain in symbols from memory for three payload shapes (scalar, object graph, array swap) before flipping.
- For every DCL card, state the broken execution (reference before field stores) aloud — one counterexample suffices to condemn plain-field DCL.
- Sort six scenarios into volatile-sufficient vs needs-atomic-or-lock without hesitation; log the compound-action traps you miss.
- Retire a card only after three consecutive clean recalls across two sittings.
