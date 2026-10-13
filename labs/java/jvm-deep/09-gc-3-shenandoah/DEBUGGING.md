# Debugging: Shenandoah GC

## First question: is it even here [measured]

Before any phase analysis, run the support probe: `java
-XX:+UseShenandoahGC -version` and read exit code plus "not supported"
text. On Oracle builds every later Shenandoah question is moot — debug
with the runnable collectors (G1 logs, ZGC `gc+phases`) instead of
chasing absent phase names.

## Second question: does the flag exist [measured]

Count `Shenandoah` rows in `PrintFlagsFinal`. Exactly one
(`UseShenandoahGC`) means the tuning surface compiled out; pasting
`ShenandoahGCMode`/`ShenandoahPacing`/`ShenandoahUncommit*` into scripts
is silently ignored. On shipping builds the same count returns the full
family — verify per distribution, never per version number.

## Reading Shenandoah phases (shipping builds) [JEP]

`Pause Init Mark` opens with roots; concurrent marking plus precleaning
walk while the app runs; `Pause Final Mark` drains SATB buffers (largest
routine beat — check its width against root growth, not heap growth);
concurrent evacuation copies with forwarder CAS; update-refs phases sweep
stale references. A swollen final mark means SATB backlog (mutation
outran draining); stalled evacuation progress means pacing/allocation
imbalance rather than pause mechanics.

## The portable triage that runs here [measured]

Identical churn under G1 and ZGC with the dual pause regexes separates
evacuation cost (milliseconds) from handshake cost (microseconds) and
proves the 10x-or-better gap. Warmup collections on both (G1 young work,
ZGC warmup major) calibrate "startup commissioning versus pressure"
before any Shenandoah phase is ever read. Collector-name enumeration
(`WhoAmI` probe) catches G1-hardcoded dashboards before migration.

## Log hygiene across collectors [measured]

Tags join with `+` (`-Xlog:gc*` covers both G1 pause totals and ZGC
handshakes in the gap probe). Cycle totals in seconds are concurrent
spans, never pauses — the dual-regex design (ZGC handshake pattern plus
G1 evacuation pattern) exists because one pattern cannot read both
collectors honestly.

## MXBean cross-check [reported]

On shipping builds expect `Shenandoah Cycles`/`Pauses` via the same
Cycles/Pauses split ZGC measures. If dashboards show G1 names against a
Shenandoah JVM, monitoring is misconfigured, not the collector silent.
