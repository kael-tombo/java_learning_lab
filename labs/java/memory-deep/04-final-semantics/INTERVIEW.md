# Interview: Final Field Semantics

## Q1: What guarantee do final fields have that plain fields lack?
**A:** Initialization safety per JLS 17.5: finals of a properly
constructed object (no `this` escape) are visible to any thread that
obtains the reference, through any publication path including data
races. No volatile or lock needed for the initial state.

## Q2: State the freeze chain precisely.
**A:** `w ->hb f ->hb a ->mc r1 ->dc r2`: final write, constructor-end
freeze, publication action, reference read (memory chain), final read
(dereference chain). When the chain holds, the reader observes the
written value.

## Q3: What voids the guarantee? Give a concrete demo.
**A:** `this` escape before the stores. Publishing `this` to a static,
registering a listener, or starting a thread from the constructor, then
storing the final, lets an early reader see the default value. The lab
demo with a 300 ms construction window shows default 0 deterministically.

## Q4: Does `final` make the referent immutable?
**A:** No. `final` publishes the reference; a mutable referent (`final
ArrayList`, record wrapping a mutable list) still races on its contents.
Only genuinely immutable contents (freshly allocated and filled in the
constructor, `List.of`) inherit safety transitively.

## Q5: Why is String safe to share without synchronization?
**A:** Its state is `final byte[] value` + `final byte coder`. Every
unsynchronized handoff leans on 17.5, including array contents via the
transitive rule. There are no read-path locks because none are needed.

## Q6: The mutable twin passes 3000 rounds on x86. Ship it?
**A:** No. It passes by TSO/coherence accident with no specification
behind it; a weaker CPU or reordering JIT may expose staleness. The
final version's identical run is a theorem; the mutable one is weather.

## Q7: Do finals cover later mutation or reflective writes?
**A:** Neither. Finals cover initialization only; post-construction
mutation needs volatile/locks. Reflective or `Unsafe` writes to finals
after construction are outside the model entirely — unspecified,
version-dependent behavior.

## Q8: How do records fit in?
**A:** Record components are final fields, so a published record is a
safe snapshot under races — with the same mutable-contents caveat for
whatever the components point at.
