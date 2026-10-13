# Math Foundation: ZGC

Defensible content only; numbers from this lab's reference runs.

## Pause budget arithmetic

Worst measured handshake 0.026 ms against a 1 ms bar: 1 / 0.026 ~= 38x
margin. Against G1's ~4 ms young pause: 4 / 0.026 ~= 150x. The lab asserts
the weaker 10x cross-collector bar so the inequality survives machine
noise: `zgc_max * 10 < g1_max`.

## Why size-independence holds

STW work per cycle = root scan + handshake protocol, O(roots), never
O(heap). Concurrent work = marking plus copying, O(live), off the pause
path. Growing the heap from 128m to terabytes scales the concurrent bands
on the timeline, not the hairline handshake ticks.

## Barrier cost model

Let L = loads per second, c = fast-path instructions per load (~2-3).
Barrier CPU ~= L * c instructions/second, linear in load rate, independent
of heap size. Workloads are ordered by loads-per-byte-allocated: chasing
shapes pay most, compute kernels least. No closed-form percent applies
across shapes — measure L via profiler, not via heap size.

## Race inequality (headroom)

Let A = allocation bytes/second, R = concurrent relocation
bytes/second, H = free headroom bytes. Collection stays stall-free while
`H + R * t >= A * t` for every interval t — i.e., headroom covers the
instantaneous deficit whenever A exceeds R. Tight heaps shrink H toward
zero and any burst with A > R stalls. This is why `-Xmx` is a floor for
slack, not a target for fullness.

## Timer cadence check

Interval 0.1 s over a 600 ms sleep predicts 6 scheduling opportunities;
measured >= 2 majors (~120 ms spacing) after handshake overhead. General
rule: expected majors ~= sleep / interval minus startup skew. Production
intervals in seconds scale the same division.

## Regex as measurement instrument

Pause extraction anchors `Pause\s+[A-Za-z ]+?\s+(\d+\.\d+)ms\s*$` to line
end so `0.009s` totals (seconds unit, mid-line position) cannot match.
The unit letter plus anchor is the instrument's calibration — dropping
either admits three-orders-of-magnitude contamination.
