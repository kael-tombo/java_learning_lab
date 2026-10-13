# Quiz: ZGC

Real Q&A; answers follow each question.

## 1. How do you select ZGC, and what are the two most important defaults?

ZGC is opt-in: `-XX:+UseZGC`. On the measured JDK 23, `ZGenerational=true`
(generational minors/majors) and `ZCollectionInterval=0.0` (no periodic
majors) hold. Both verified via `PrintFlagsFinal` with the opt-in flag on.

## 2. What are colored pointers, and what heals a stale one?

Color (GC phase metadata) is stored in reference bits. Every load runs a
barrier checking color; a stale ("bad color") reference traps into a slow
path that remaps it to the current copy before the application proceeds.

## 3. Name the STW pauses in a cycle and their measured size.

`Pause Mark Start`, `Pause Mark End`, `Pause Relocate Start` — three
handshakes per cycle, measured 0.010-0.026 ms here (bar: every pause
<1 ms). Marking and copying between them are concurrent, not pauses.

## 4. What distinguishes a minor from a major in the log?

Minors collect young only (`y:` prefixes, reasons like `(High Usage)` /
`(Allocation Rate)`); majors coordinate young plus old (`Y:`/`O:` phase
lines). Every JVM opens with a warmup major (`Major Collection (Warmup)`).

## 5. What are the MXBean names, and why the Cycles/Pauses split?

Collectors: `ZGC Minor/Major Cycles` and `ZGC Minor/Major Pauses`. Pools:
`ZGC Young Generation`, `ZGC Old Generation`. Cycles account concurrent
work, Pauses account STW handshakes — dashboard latency from Pauses,
reclamation rate from Cycles.

## 6. What does ZCollectionInterval do, and how was it verified?

It schedules periodic majors every N seconds independent of allocation
(default 0 = off). Verified: `-XX:ZCollectionInterval=0.1` on a 600 ms
idle sleep produced >= 2 `Major Collection (Timer)` lines (~120 ms apart)
with zero allocation; without the flag, zero.

## 7. What is the JEP trail?

JEP 333 (experimental, 11), JEP 377 (production, 15), JEP 439
(generational, 21).

## 8. When does ZGC stall, and what fixes it?

Sustained allocation outruns concurrent relocation on a tight heap —
allocation stalls (the pause-equivalent). Fix: grow headroom (larger
`-Xmx`), damp bursts (chunk work), not pause-tune. Tight sizing is the
cause; slack is the cure.
