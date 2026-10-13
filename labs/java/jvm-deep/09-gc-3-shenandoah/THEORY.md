# Shenandoah GC — Theoretical Foundation

## Status Banner (read first)

Shenandoah is **compiled out of Oracle JDK builds** — on the Oracle JDK 23
used for this lab, `-XX:+UseShenandoahGC` fails at startup ("not
supported") and only the bare `UseShenandoahGC` flag exists (all tuning
flags are compiled out with the collector). It ships in most OpenJDK
distributions (Temurin, Semeru, Red Hat builds). Every claim below is
therefore labeled: **[measured]** (ran here), **[JEP]** (primary source),
or **[reported]** (real downstream consumer, not re-measured). No snippet
pretends to run Shenandoah where it can't.

## Core Concept

Shenandoah's one big idea (JEP 189): **concurrent evacuation**. G1 and CMS
mark concurrently but always stop the world to *move* objects; Shenandoah
moves them while the application runs, via a **Brooks forwarding pointer**
— one indirection word per object pointing at the current copy. Readers go
through the forwarder (read barrier); movers copy and CAS the forwarder;
stragglers see the new copy on next access. Pauses shrink to root scanning
plus handshakes — heap-size-independent, like ZGC, by a different
mechanism (JEP 189: "G1 does some parallel and concurrent work, but it does
not do concurrent evacuation").

## Brooks Pointers vs Colored Pointers (Shenandoah vs ZGC)

| | Shenandoah (Brooks) | ZGC (colored) |
|---|---|---|
| Where the metadata lives | extra word *in the object* (forwarder) | *in the reference* (color bits) |
| Barrier placement | read barrier + write barrier (SATB marking) + CAS on forwarder | load barrier (heal on load) |
| Space cost | one word per object, always | address-space games, no per-object word |
| Throughput tax shape | barrier + extra indirection on hot reads | barrier on every load |
| Evacuation rendezvous | forwarder CAS; losers use winner's copy | remap/heal on next load |

Both make relocation concurrent; they differ in *what the application pays
per access*. Neither dominates universally — allocation shape, read/write
ratio, and heap size decide (measure, per usual).

## The Cycle (single-generation, still the default per JEP 521)

1. `Pause Init Mark` — STW roots handshake (~1 ms at 8 GB in the wiki's
   reference log; scales with root set, not heap).
2. `Concurrent marking` — SATB traversal alongside the application.
3. `Concurrent precleaning` — weak refs, class unloading prep.
4. `Pause Final Mark` — drain SATB buffers, finish marking (~10 ms
   reference figure; the largest routine pause).
5. `Concurrent cleanup` — reclaim empty regions immediately.
6. `Concurrent evacuation` — copy live objects out of the collection set,
   CAS forwarders; application reads heal through them.
7. `Pause Init Update Refs` / `Concurrent update references` /
   `Pause Final Update Refs` — sweep remaining stale references to the new
   copies, then `Concurrent cleanup` again.

Pauses: three short STW beats (init-mark, final-mark, update-refs
boundaries) plus the final-mark outlier — all root-sized, none heap-sized.
Reference figures above are from the OpenJDK wiki's 8 GB log; your pauses
track *your* roots.

## Generational Shenandoah (JEP 404 experimental in 24; JEP 521 ongoing)

**[JEP]** JEP 521: "By default, Shenandoah will continue to use a single
generation" — generational mode is opt-in (`-XX:+UseGenerationalShenandoah`
in builds that ship it... precisely: JEP 404 integrated generational as
experimental in 24; JEP 521 tracks productization). Young/old split with
minor collections for the young gen, mirroring the industry-wide
convergence (G1's regions, ZGC's `ZGenerational`). Not measurable on this
build; stated for orientation so the flag doesn't surprise you elsewhere.

## Tuning Surface (documented; flag names from the JEP/CSR trail)

- Mode: `ShenandoahGCMode` (`normal` default; also `traversal`, `iu`,
  `passive` debug modes in dev builds).
- Pacing: `ShenandoahPacing` (default on) — allocation-paced concurrent
  progress so evacuation outruns allocation (the anti-allocation-stall
  mechanism; ZGC's headroom equivalent).
- Uncommit: `ShenandoahUncommit` (default on) + `ShenandoahUncommitDelay`
  (default 5 min) — return idle regions to the OS; first touch after
  uncommit stalls (the documented trade the delay tunes).
- Heuristics: `ShenandoahGCHeuristics` (`adaptive` default; `static`,
  `compact`, `aggressive` for testing/extremes).
- None of these exist on the measured Oracle build (single surviving flag:
  `UseShenandoahGC`) — the table is for Temurin/Semeru/RH runtimes.

## Observability (reported, via Micrometer's collector table)

**[reported]** Micrometer's `JvmGcMetrics` maps MXBean name `"Shenandoah
Cycles"` (old-gen accounting) and handles `"... Pauses"` notifications —
the same Cycles/Pauses split ZGC exposes (lab 08, measured). Log shape
follows `gc` tags with Shenandoah's phase names (`Pause Init Mark`,
`Concurrent evacuation`, ...). If your dashboards key on `G1 Eden Space`,
they go blind here exactly as under ZGC — pool/collector names are
collector-defined.

## JEP Trail (all primary-source)

- JEP 189 (JDK 12): experimental Shenandoah (Flood/Kennke; PPPJ2016 paper
  is the algorithm reference).
- JEP 379 (JDK 15): production (Shipilёv; cosmetic flag-class change, no
  default-GC change — G1 stays default).
- JEP 404 (JDK 24): generational mode experimental; JEP 521 tracks its
  productization (single-gen remains default).
- Shipped in Red Hat 8u/11u downstream *before* upstream integration —
  the uncommon backport-first history (JEP 379 text).

## Key Invariants

1. Evacuation is concurrent; pauses are root-sized handshakes, never heap
   walks.
2. The forwarder is the single rendezvous: losers of the CAS use the
   winner's copy — no thread ever sees a torn move.
3. SATB marking (shared with G1) means floating garbage dies next cycle,
   never lives wrongly.
4. Single-generation is the default (JEP 521); generational is opt-in.
5. Oracle builds omit the collector: availability is a distribution
   property, checked at startup, not assumed.
