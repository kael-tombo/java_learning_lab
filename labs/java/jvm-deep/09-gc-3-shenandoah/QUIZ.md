# Quiz: Shenandoah GC

Real Q&A. Labels: [measured]/[JEP]/[reported]. No unmeasured behavior
presented as observed.

## 1. Is Shenandoah runnable on the Oracle JDK 23 here? [measured]

No. `-XX:+UseShenandoahGC` exits nonzero with "not supported"; only the
bare `UseShenandoahGC` flag survives in `PrintFlagsFinal`. It ships in
Temurin, Semeru, Red Hat builds — availability is a distribution
property checked at startup.

## 2. What is a Brooks pointer, and how does it differ from a colored pointer? [JEP]

Brooks: one forwarder word per object pointing at the current copy;
readers go through it, movers CAS it, losers adopt the winner's copy.
Colored (ZGC): GC bits live in the reference, healed on load. Word
overhead plus read indirection versus address-space games plus per-load
checks — same concurrent-evacuation goal, different tax shape.

## 3. Sketch the cycle with its pauses. [JEP]

`Pause Init Mark` (roots handshake) -> concurrent marking (SATB) ->
precleaning -> `Pause Final Mark` (drain buffers; largest routine beat)
-> concurrent cleanup -> concurrent evacuation (copy + forwarder CAS) ->
update-refs pauses around concurrent reference updating -> cleanup.
Reference figures (wiki 8 GB log): ~1 ms init, ~10 ms final — root-scaled.

## 4. What are the documented tuning knobs? [JEP, not measured here]

`ShenandoahGCMode` (normal default; traversal/iu/passive debug),
`ShenandoahPacing` (allocation-paced progress), `ShenandoahUncommit` +
5-min delay (idle regions to OS), `ShenandoahGCHeuristics` (adaptive
default). None exist on the measured Oracle build (single surviving
flag proves it).

## 5. What JEPs define the trail? [JEP]

JEP 189 (experimental, 12 — "G1 does some parallel and concurrent work,
but it does not do concurrent evacuation"), JEP 379 (production, 15 —
G1 stays default), JEP 404 (generational experimental, 24), JEP 521
(productization; single-gen default).

## 6. What MXBean names does monitoring use? [reported]

`Shenandoah Cycles` (old-gen accounting) and `... Pauses` notifications
via Micrometer's `JvmGcMetrics` — the Cycles/Pauses split lab 08
measures for ZGC. G1-keyed dashboards go blind here.

## 7. What gap justifies concurrent evacuation? [measured]

Identical churn: G1 evacuation ~5 ms vs concurrent handshakes ~0.02 ms
(asserted 10x-or-better, observed ~100x+). The portable `PauseGap` probe
quantifies the design goal without running Shenandoah itself.

## 8. Generational or single-gen default? [JEP]

Single-generation default (JEP 521); generational opt-in (JEP 404/521).
Same convergence as G1 regions and ZGC `ZGenerational` — by choice, not
surprise.
