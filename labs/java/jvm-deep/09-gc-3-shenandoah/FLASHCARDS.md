# Flashcards: Shenandoah GC

Q: What is Shenandoah's one big idea? [JEP]
A: Concurrent evacuation via a Brooks forwarding pointer — one word per
object pointing at the current copy; movers CAS it while readers heal
through it.

Q: Is Shenandoah available on the Oracle JDK 23 measured here? [measured]
A: No — compiled out. `-XX:+UseShenandoahGC` fails ("not supported");
only the bare `UseShenandoahGC` flag survives. It ships in Temurin,
Semeru, Red Hat builds.

Q: Brooks pointer vs colored pointer — where does metadata live? [JEP]
A: Shenandoah: extra word in the object (forwarder). ZGC: color bits in
the reference. Different tax shapes (read indirection vs per-load check),
same concurrent-evacuation goal.

Q: Name the Shenandoah cycle phases. [JEP]
A: `Pause Init Mark`, concurrent marking (SATB), precleaning, `Pause
Final Mark`, concurrent cleanup, concurrent evacuation, init/final
update-refs around concurrent reference updating, final cleanup.

Q: Which pause is largest, and what does it scale with? [JEP]
A: `Pause Final Mark` (drains SATB buffers; ~10 ms reference at 8 GB wiki
log). All pauses scale with roots/buffers, never heap size.

Q: What are the tuning knobs on shipping builds? [JEP, documented]
A: `ShenandoahGCMode` (normal/traversal/iu/passive), `ShenandoahPacing`,
`ShenandoahUncommit` + 5-min delay, `ShenandoahGCHeuristics` (adaptive
default). Absent on the Oracle build [measured].

Q: What are the MXBean names? [reported]
A: `Shenandoah Cycles` / `Shenandoah Pauses` via Micrometer's collector
table — the same Cycles/Pauses split ZGC measures.

Q: What is the JEP trail? [JEP]
A: JEP 189 experimental (12), JEP 379 production (15), JEP 404
generational experimental (24), JEP 521 productization ongoing with
single-gen default.

Q: What gap motivates concurrent evacuation? [measured]
A: G1 evacuation pauses ~5 ms vs concurrent handshakes ~0.02 ms on
identical churn (10x asserted, ~100x observed).

Q: What does SATB guarantee, and what does it retain? [JEP]
A: No live object ever missed (overwrites logged as extra roots); deleted
objects float as garbage until next cycle — correctness over precision.

Q: Single-gen or generational default? [JEP]
A: Single-generation default (JEP 521); generational opt-in (JEP 404).

Q: What fails first when Shenandoah flags are pasted onto Oracle builds?
A: Nothing visibly — startup refuses the collector ("not supported") and
unknown tuning flags are ignored [measured]. Gate on the probe instead.
