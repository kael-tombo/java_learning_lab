# Math Foundation: Shenandoah GC

Defensible content only. Labels: [measured]/[JEP]/[reported].

## Gap arithmetic [measured]

G1 max ~5 ms vs concurrent-evacuation max ~0.02 ms on identical churn:
5 / 0.02 = 250x observed. Lab asserts `zgc_max * 10 < g1_max` (10x), a
25x safety factor under the observation. The assertion is engineered for
machine noise, not for the headline ratio.

## Why pauses are root-sized [JEP]

Per cycle STW work = root scan + SATB-buffer drain + handshake protocol:
O(roots + mutations), never O(heap). Concurrent work = marking plus
evacuation copying: O(live), off the pause path. Growing the heap scales
the concurrent bands, not the pause ticks — the same decomposition ZGC
measures, stated here as mechanism [JEP] rather than re-measured timing.

## Forwarder space cost [JEP]

One word per object: 8 bytes on 64-bit (4 compressed where applicable —
forwarder is a reference-width word). For N objects the tax is 8N bytes
regardless of heap size: 1M objects cost 8 MB. ZGC's color bits cost
address-space games instead of per-object words — the space trade the
THEORY table contrasts without pricing either universally.

## CAS contention bound [JEP]

Per object at most one CAS wins per evacuation; losers discard and adopt.
Total winning CASes per cycle = O(live in collection set); total loser
work scales with mover oversubscription, bounded by worker count, not by
heap size. Contention concentrates on popular objects, resolved by exactly
one atomic each — no retry storms beyond the worker fan-in.

## Uncommit delay arithmetic [JEP]

`ShenandoahUncommitDelay` default 5 min: a region idle for 300 s returns
to the OS. A service idle 50% of each hour uncommits roughly half its
cold set per hour of idleness, minus first-touch recommits on wake. The
trade is bytes-returned versus recommit stalls — tuned by the delay, not
by heap size.

## Probe assertions as Boolean algebra [measured]

`supported != refused` (XOR) holds on every distribution: Oracle gives
(false, true), Temurin-class gives (true, false). Flag count `== 1`
implies compiled-out surface; `> 5` G1 rows confirm the query itself
works. Conjunction (`== 1 AND > 5`) separates "collector absent" from
"query broken" — the measurement logic in one line.
