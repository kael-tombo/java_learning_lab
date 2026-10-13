# Performance: Shenandoah GC

## Pause posture [JEP]

Root-sized STW beats (init-mark, final-mark plus update-refs boundaries)
with the heap walked concurrently — the same size-independence ZGC
measures at 0.010-0.026 ms [measured for ZGC; Shenandoah figures are
reference-log shaped: ~1 ms init-mark, ~10 ms final-mark at 8 GB wiki
log, scaling with roots]. Final mark is the largest routine beat because
it drains the full SATB backlog; the rest are handshakes.

## Tax shape versus ZGC [JEP]

Brooks indirection taxes hot reads (extra hop through the forwarder)
while ZGC taxes every load (color check). Read-heavy shapes feel
Shenandoah's hop relatively more; mixed shapes historically showed lower
tax on some profiles and higher on others. No universal winner exists —
the lab's G1-vs-ZGC gap probe [measured] quantifies the evacuation win,
not the barrier race; run your allocation profile on both collectors on
a shipping build before generalizing.

## Pacing and heuristics [JEP, documented-not-measured-here]

`ShenandoahPacing` (default on) keeps evacuation ahead of allocation so
mutators pace instead of stall. `ShenandoahGCHeuristics` (`adaptive`
default) picks collection-set aggression; `compact`/`aggressive` serve
testing and extremes. `ShenandoahUncommit` with its 5-minute delay trades
idle footprint against first-touch stalls after uncommit. All three are
set on Temurin/Semeru/RH runtimes [JEP], never inferred from the Oracle
build [measured], which compiles the surface out.

## Sizing posture [JEP]

Headroom logic mirrors ZGC: concurrent evacuation must outrun
allocation, so size for slack rather than minimal footprint. Uncommit
softens the cost of slack on idle services by returning regions to the
OS — the delay tunes how quickly idleness converts to returned memory.

## What not to tune here [measured]

On Oracle builds there is nothing to tune: one surviving flag, no modes,
no pacing knob. Performance work on this build means choosing among the
runnable collectors (G1 default, ZGC opt-in) with the pause-gap probe —
not pasting Shenandoah flags into a runtime that ignores them.
