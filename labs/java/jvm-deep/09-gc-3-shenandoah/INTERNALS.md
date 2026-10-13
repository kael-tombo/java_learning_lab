# Internals: Shenandoah GC

## Forwarder CAS protocol [JEP]

Each object's Brooks word points at the current copy (initially itself).
A mover allocates space in the target region, copies, then CASes the
forwarder from old to new. Concurrent readers load through the forwarder
(read barrier), so they see old or new but never a half-copy. A losing
mover discards its copy and adopts the winner's — exactly one copy wins
per object per evacuation, decided by a single atomic.

## Barrier complement [JEP]

Read barrier on every through-forwarder access (healing reads), SATB
pre-write barrier on reference stores during marking (snapshot
consistency), plus the CAS on the forwarder itself during evacuation.
ZGC's healing flows through loads on colored references; Shenandoah's
flows through forwarder indirection plus store-side SATB logging. The
write-heavy versus load-heavy placement is the structural difference the
THEORY table names.

## Pause inventory [JEP]

`Pause Init Mark`, `Pause Final Mark`, `Pause Init Update Refs`, `Pause
Final Update Refs`, plus the final-mark outlier as largest routine beat.
All are root/buffer-sized handshakes; none walk the heap. Concurrent
phases between them (marking, precleaning, evacuation, update refs,
cleanups) carry the O(heap) work off the pause path.

## Flag surface on this build [measured]

`PrintFlagsFinal` shows exactly one `Shenandoah*` row
(`UseShenandoahGC`) against a full G1 family (>5 rows). The mode, pacing,
uncommit, and heuristics flags documented in the JEP/CSR trail are absent
because `#ifdef INCLUDE_SHENANDOAHGC` guards them with the collector.
Pasting them into an Oracle-build launch script is silently ignored.

## Observability names [reported]

Micrometer's `JvmGcMetrics` maps MXBean `"Shenandoah Cycles"` (old-gen
accounting) and `"... Pauses"` notifications — the same Cycles/Pauses
split ZGC exposes [measured in lab 08]. Log shape follows `gc` tags with
Shenandoah phase names (`Pause Init Mark`, `Concurrent evacuation`).
Dashboards keyed on `G1 Eden Space` go blind here exactly as under ZGC.

## Generational state [JEP]

JEP 521: single generation stays default; generational mode
(`-XX:+UseGenerationalShenandoah` on builds shipping it) is opt-in, with
minor collections for the young gen. JEP 404 integrated it as
experimental in 24; JEP 521 tracks productization.
