# Reflection: Shenandoah GC

## Label drill

Take any behavior sentence you wrote about Shenandoah this week and
attach its label: [measured] (you ran it here), [JEP] (primary source),
or [reported] (Micrometer/wiki, not re-measured). Which sentences lose
their verbs when the label is enforced — and what does that tell you
about where your knowledge actually comes from?

## Forwarder in your words

Explain the Brooks word in three sentences [JEP]: what it points at,
who CASes it, and what a losing mover does. Then state the ZGC contrast
in one: forwarder word in the object versus color bits in the reference.
Where would each tax shape hurt your hottest read path most?

## The refusal as information [measured]

Your JVM refused `-XX:+UseShenandoahGC` with "not supported" and kept
exactly one flag. What three operational conclusions follow (distribution
choice, tuning-surface absence, fallback collectors) — and which deploy
script in your fleet would break today if it assumed presence?

## Gap reasoning [measured]

G1 pauses in milliseconds, concurrent evacuation in tens of microseconds,
10x asserted with ~100x observed. Translate that ratio into your p99
budget: which side of the gap does your SLO sit on, and does that argue
for a distribution switch or for staying on the default with headroom?

## One portability change

Name one hardcoded collector or pool name in your monitoring or scripts.
Write the enumeration-based replacement (as the `WhoAmI`/`NameMatrix`
probes model) so G1, ZGC, and Shenandoah [reported names] all resolve.
Config diff, not essay — precision is the deliverable.

## Distribution question for your fleet

Which base images do your services actually run — Oracle, Temurin,
Semeru, RH, mixed? For each, write the probe outcome you expect [measured
for Oracle, predicted-elsewhere] and the fallback collector the launch
path should select. Unknown answers here are the finding: probe the fleet
before the next base-image migration decides for you.
