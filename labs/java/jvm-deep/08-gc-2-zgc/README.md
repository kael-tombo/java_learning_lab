# README — ZGC

ZGC keeps stop-the-world pauses sub-millisecond by relocating objects
concurrently: colored pointers plus load barriers let stragglers heal on
next access instead of rendezvousing. This lab measures generational ZGC
on JDK 23.

## What you will observe [measured]

- Opt-in via `-XX:+UseZGC`; `ZGenerational=true` default;
  `ZCollectionInterval=0.0` (timer off unless asked).
- Collectors `ZGC Minor/Major Cycles` plus `ZGC Minor/Major Pauses`;
  pools `ZGC Young Generation` and `ZGC Old Generation`.
- Every STW handshake 0.010-0.026 ms in the reference run (asserted as
  <1 ms for machine margin) — three beats per cycle (mark start, mark
  end, relocate start), everything else concurrent.
- Log reasons `(Warmup)` (always the first cycle), `(High Usage)`,
  `(Allocation Rate)`, `(Timer)` when the interval flag is set.
- `ZCollectionInterval=0.1` collects an idle JVM every ~120 ms with zero
  allocation — heap hygiene without pressure.

## Phase prefixes

Lowercase `y` = young-only work in a minor; uppercase `Y`/`O` = young and
old phases interleaved in a major. Roots scan inside the microsecond
pauses; the heap walks concurrently between them.

## Logging rule

`-Xlog:gc`, `-Xlog:gc+phases` (tags join with `+`, never commas). Cycle
totals in seconds are concurrent spans, not pauses — pauses are the
`Pause ... Xms` phase lines. Heaps pinned with `-Xmx` throughout.

## Exit criteria

You can separate a pause from a cycle total, name the minor/major split,
explain load-barrier healing in one paragraph, and trigger an idle
collection on the timer.

## Numbers pocket reference

Opt-in `-XX:+UseZGC`; `ZGenerational=true`; `ZCollectionInterval=0` off.
Pauses 0.010-0.026 ms reference (<1 ms bar). Reasons: Warmup (first,
always), Allocation Rate, High Usage, Timer, explicit causes. Prefixes:
`y` minor, `Y`/`O` major phases. Heaps pinned throughout.
