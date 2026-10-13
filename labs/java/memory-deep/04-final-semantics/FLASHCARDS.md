# Flashcards: Final Field Semantics

## Q1: What does JLS 17.5 guarantee about final fields?
**A:** Objects built without leaking `this` show their `final` fields
fully initialized to every thread that sees the reference, through any
publication path including data races.

## Q2: State the freeze chain.
**A:** `w ->hb f ->hb a ->mc r1 ->dc r2 ==> r2 observes w`: the final
write, constructor-end freeze, publication, reference read, and final
read chain so the reader sees the written value.

## Q3: What are the mc and dc links?
**A:** Memory chain and dereference chain: ordering edges that carry the
freeze protection through the reference from publisher to reader, even
across a race on the reference itself.

## Q4: Are finals of finals covered?
**A:** Yes, transitively: finals reachable through finals of a safely
constructed object (e.g. `String`'s array elements) inherit the
protection, provided the whole chain was built inside construction.

## Q5: What voids the guarantee?
**A:** `this` escape before the final stores: publication inside the
constructor precedes the freeze, so early readers may legally see
default values (deterministic 0 in the lab's 300 ms-window demo).

## Q6: Do finals cover later mutation?
**A:** No. Finals cover initialization only. A `final` reference to a
mutable object publishes the pointer safely; its contents still race
without their own synchronization.

## Q7: Why is String thread-safe on its read path?
**A:** `final byte[] value` + `final byte coder`: every unsynchronized
`String` handoff leans on 17.5, including array contents via the
transitive rule. No read-path locks exist because none are needed.

## Q8: What is the record caveat?
**A:** Record components are finals (safe snapshot), but a record
holding a mutable `ArrayList` publishes the reference safely while the
list contents stay racy. `List.of` contents are safe by immutability.

## Q9: Why does the mutable twin pass 3000 rounds on x86?
**A:** TSO store ordering plus cache coherence hides the missing
guarantee on this hardware. Same green run as the final version, but
weather, not theorem: a weaker CPU or reordering JIT may show staleness.

## Q10: Are reflective writes to finals covered?
**A:** No. Post-construction reflective or `Unsafe` writes to finals sit
outside the memory model; results are unspecified and version-dependent.
