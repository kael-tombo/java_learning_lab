# Refactoring: Shenandoah GC

Label discipline applies: behavior claims [JEP]/[reported], probe claims
[measured].

## Probe availability before configuring [measured]

Before: deploy scripts set `-XX:+UseShenandoahGC` plus pacing flags and
roll to Oracle-based containers; the JVM refuses at startup ("not
supported") and the rollout fails as a config error, not a GC event.

After: gate collector selection on the support probe (exit code plus
marker text) with a fallback to the measured collectors (G1 default, ZGC
opt-in). One branching check in the launch path replaces an outage with
a deterministic fallback. The flag-surface count (1 vs many) is the CI
assertion that the gate stays honest per base image.

## Re-key monitoring for collector mobility [measured+reported]

Before: alerts match `G1 Young Generation`; any move to ZGC or
Shenandoah flatlines every panel (snippet 4 shows the G1/ZGC flip;
Shenandoah's `Shenandoah Cycles`/`Pauses` pair is [reported] via
Micrometer).

After: enumerate `GarbageCollectorMXBeans` and match on Cycles/Pauses
suffix families instead of one collector name. Config-only change, made
once, covers all three collectors in this module.

## Damp allocation to respect concurrent evacuation [JEP]

Before: bursty producers outrun concurrent evacuation; pacing throttles
late and tail latency suffers whether the forwarder [JEP] or the color
barrier absorbs the race.

After: chunk bursts into bounded pages with buffer reuse so allocation
rate stays under concurrent drain. Same bytes, even cadence — the
`gc`-log stall/pacing lines flatten on shipping builds [JEP], and the
portable gap probe [measured] confirms the healthy ordering.

## Separate huge-object paths [JEP]

Before: multi-MB values churn through the general allocator and stress
every evacuation path regardless of collector.

After: pool or reuse large buffers (bounded queue sized to peak
concurrency) and keep scratch allocation small and short-lived. Evacuation
sets shrink, update-refs sweeps shorten [JEP], and humongous-style
fragmentation never starts.

## What not to refactor [measured]

Do not tune `ShenandoahPacing`/`ShenandoahUncommit`/heuristics on the
Oracle build — the knobs do not exist there. Tune the runnable
collectors with lab 10's one-flag method instead.
