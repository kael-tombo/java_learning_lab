# Architecture: Shenandoah GC

## Brooks forwarding pointer [JEP]

Every object carries one extra word: the forwarder pointing at the
current copy. Readers go through the forwarder (read barrier); movers
copy the object and CAS the forwarder to the new copy; losers of the CAS
use the winner's copy. No thread ever observes a torn move — the
forwarder is the single rendezvous for concurrent evacuation.

## Brooks vs colored pointers [JEP]

Shenandoah stores metadata in the object (forwarder word, always present,
one word per object). ZGC stores metadata in the reference (color bits,
no per-object word). Shenandoah pays barrier plus indirection on hot
reads; ZGC pays a barrier on every load. Same goal (concurrent
evacuation), different per-access tax shape — allocation profile and
read/write ratio decide, measured per workload.

## Cycle phases [JEP]

`Pause Init Mark` (STW roots handshake), concurrent SATB marking,
concurrent precleaning, `Pause Final Mark` (drain SATB buffers, finish
marking — the largest routine pause), concurrent cleanup (reclaim empty
regions immediately), concurrent evacuation (copy plus forwarder CAS),
then init/final update-refs pauses bracketing concurrent reference
updating, and a final cleanup. STW beats are root-sized handshakes;
reference figures from the OpenJDK wiki's 8 GB log put init-mark ~1 ms
and final-mark ~10 ms — your pauses track your roots, not those digits.

## SATB shared with G1 [JEP]

Overwritten references during marking log to SATB buffers via the write
barrier and drain as extra roots. Floating garbage dies next cycle; no
live object is reclaimed. Same correctness-over-precision trade as G1.

## Tuning surface (documented, not measured here)

`ShenandoahGCMode` (`normal` default; `traversal`, `iu`, `passive` debug
modes) [JEP]; `ShenandoahPacing` (allocation-paced progress, the
anti-stall mechanism) [JEP]; `ShenandoahUncommit` plus
`ShenandoahUncommitDelay` (5 min default, return idle regions to the OS)
[JEP]; `ShenandoahGCHeuristics` (`adaptive` default; `static`, `compact`,
`aggressive`) [JEP]. None exist on the measured Oracle build [measured]:
a single surviving selector flag proves the surface compiled out.

## Modes and generations [JEP]

Single-generation remains the default (JEP 521); generational mode is
opt-in (JEP 404 experimental in 24, JEP 521 productization ongoing).
