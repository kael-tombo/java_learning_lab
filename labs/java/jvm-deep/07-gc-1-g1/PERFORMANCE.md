# Performance: G1 GC

## Where time goes

Young evacuations dominate most G1 profiles: 2-5 ms per pause at 256 MB
in this lab, scaling with live-set size (bytes copied) rather than heap
size. Concurrent marking and refinement cost background CPU but no STW
time; the STW remark/cleanup beats are small beside evacuation. Full GC
is off the chart by design — its absence is the healthy state.

## Reading a pause line

`Pause Young (Normal) (G1 Evacuation Pause) 23M->9M(256M) 4.294ms` says:
collected the young set, heap went 23M to 9M, the pause cost 4.294 ms.
Track the after-number across pauses for live-set growth and the ms
number against the 200 ms goal. A rising after-number with steady churn
means promotion pressure; a rising ms with steady bytes means RSet or
to-space strain.

## Tuning levers that work

Size the heap so young pauses fit the goal with margin — `-Xmx` is the
first lever, and every experiment pins it. Lower `MaxGCPauseMillis` only
when pauses already fit; it shrinks young sets and collects more often,
trading throughput for pause size. Raise `InitiatingHeapOccupancyPercent`
above 45 only with measured marking headroom; starting marking late
risks evacuation failure when the old set fills mid-mark.

## Pathologies with signatures

Humongous churn: old-gen growth invisible at info logging, confirmed at
`gc+humongous=debug` with spanning `type array` lines. To-space
exhaustion: evacuation pauses spike then a full GC appears — the log's
way of saying the young sizing overshot free space. RSet bloat: pauses
grow while copied bytes stay flat, under heavy cross-region mutation.

## Throughput versus pause posture

G1 keeps more throughput than the concurrent-evacuation collectors
because only marking is concurrent — evacuation still stops the world
without barrier tax on every load. The price is pauses that grow with
live data (milliseconds here versus hundredths of a millisecond under
ZGC). Choose by live-set size and pause budget, measured per workload.
