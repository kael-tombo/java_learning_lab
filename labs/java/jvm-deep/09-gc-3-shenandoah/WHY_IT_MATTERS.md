# Why It Matters: Shenandoah GC

Distribution determines availability before any behavior question
[measured]: Oracle builds omit Shenandoah while Temurin, Semeru, and Red
Hat builds ship it. The first operational act is the support probe, not
flag tuning — copying `ShenandoahPacing` settings onto an Oracle runtime
is silently ignored, and the flag-surface probe proves it with a count
of exactly one surviving flag.

The pause-gap measurement [measured] is why teams bother switching
distributions: G1 evacuations in milliseconds versus concurrent
evacuation in tens of microseconds, 10x-or-better with margin. Any
service whose p99 budget sits between those figures changes feasibility
class under a concurrent-evacuation collector — Shenandoah from the
Brooks direction [JEP], ZGC from the colored-pointer direction
[measured in lab 08].

Monitoring migrates the same way under both [reported]: MXBean names
`Shenandoah Cycles`/`Pauses` replace the G1 triple, and dashboards hardcoded
to `G1 Young Generation` go blind. Micrometer already enumerates the
pair, so the migration is a re-key, not new instrumentation.

The tuning surface that matters on shipping builds [JEP] is pacing
(allocation keeps pace with evacuation), heuristics (`adaptive` default;
`compact`/`aggressive` for extremes), and uncommit delay (idle memory
versus first-touch stall after 5 minutes). None are set from Oracle-build
numbers — they are set on the distribution that ships the collector,
against its own logs, with the same one-flag-per-experiment discipline
lab 10 teaches.

The fleet-level implication [measured + JEP]: collector choice is now a
function of base image, not only workload. Standardize the probe gate in
the launch path (support probe plus flag-surface count) so image changes
surface as deterministic fallback decisions rather than startup refusals
at rollout time. Portability work precedes performance work wherever the
manifest, not the workload, picks the collector.
