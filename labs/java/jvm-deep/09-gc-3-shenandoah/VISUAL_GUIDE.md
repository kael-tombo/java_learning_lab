# Visual Guide: Shenandoah GC

## The forwarder sketch [JEP]

Draw each object as a box with a small tab on top (the Brooks word).
The tab holds an arrow to the current copy — initially a loop back to
itself. During evacuation draw two boxes (old, new) with the tab arrow
swung to the new one after the CAS. Readers enter through the tab, so
every path lands on the live copy regardless of when it arrives.

## Brooks vs colored, side by side [JEP]

Left panel: object with tab (metadata in the object), plain arrows.
Right panel: plain object, arrows with colored bands (metadata in the
reference). Annotate the left's cost as "tab storage + read indirection"
and the right's as "no tab + check per load". Same concurrent goal, costs
in different places — the diagram to reach for whenever someone asks
which dominates (answer: measure your shape).

## The phase timeline [JEP]

Hairline red ticks for `Pause Init Mark`, `Pause Final Mark` (tallest
routine tick), and the two update-refs pauses; wide blue bands for
concurrent marking, evacuation, update references, and the two cleanups.
Reference widths (~1 ms init, ~10 ms final at 8 GB wiki log) annotate the
ticks as root-scaled, never heap-scaled.

## The probe-outcome matrix [measured]

Two-by-two grid: rows Oracle / Temurin-class builds, columns support
probe / flag probe. Oracle cells read "refused: not supported" and "1
flag survives"; Temurin-class cells read "`Using Shenandoah`" and "full
surface present". Every cell asserts its documented outcome — the matrix
is the portability story in one glance.

## The pause-gap bars [measured]

Two bars on identical churn: G1 evacuation in milliseconds (tall),
concurrent evacuation in tens of microseconds (hairline). The 10x
assertion line sits far below the measured ~100x gap as margin. Label the
Shenandoah arrow as closing this gap from the Brooks direction [JEP].
