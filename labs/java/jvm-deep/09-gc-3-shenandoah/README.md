# README — Shenandoah GC

Shenandoah's idea [JEP]: concurrent evacuation through a Brooks
forwarding pointer — one word per object pointing at the current copy —
so pauses shrink to root-sized handshakes instead of heap-sized copies.

## Status banner (read first) [measured]

On the Oracle JDK 23 used here Shenandoah is compiled out:
`-XX:+UseShenandoahGC` fails at startup ("not supported") and only the
bare `UseShenandoahGC` flag survives in `PrintFlagsFinal`. It ships in
Temurin, Semeru, and Red Hat builds. Every behavior claim in this lab is
labeled [measured] (ran here), [JEP] (primary source), or [reported]
(downstream consumer, not re-measured). Nothing unmeasured is presented
as observed.

## What you will observe [measured]

- Availability probe: startup refuses with "not supported" on Oracle
  builds; the assertion (`supported != refused`) holds on both branches.
- Flag surface: exactly 1 `Shenandoah*` flag (`UseShenandoahGC`) versus a
  full G1 family — the tuning surface compiled out with the collector.
- Pause-gap probe: G1 evacuation pauses in milliseconds versus ZGC
  handshakes in tens of microseconds (10x-or-better asserted) — the gap
  Shenandoah was built [JEP] to close from the Brooks-pointer direction.
- Collector-name matrix: default mentions G1, `-XX:+UseZGC` mentions ZGC;
  Shenandoah's `Shenandoah Cycles`/`Pauses` pair is [reported] via
  Micrometer's collector table, not locally measured.
- Warmup collections are universal [measured]: G1 young work plus ZGC
  warmup majors on identical churn.

## Cycle orientation [JEP]

`Pause Init Mark`, concurrent marking (SATB), `Pause Final Mark`,
concurrent evacuation (forwarder CAS), update-refs phases. Single
generation is the default (JEP 521); generational is opt-in (JEP 404/521).

## Claim-label pocket reference

[measured]: refusal text, single-flag surface, pause-gap numbers, name
matrix, warmup universality. [JEP]: forwarder protocol, phases, modes,
pacing/uncommit/heuristics, JEP trail, generational default. [reported]:
Micrometer `Shenandoah Cycles`/`Pauses`, wiki reference pause figures.
Label every sentence before quoting it elsewhere.
