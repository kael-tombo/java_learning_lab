# Performance: ZGC

## Pause numbers with margin

Reference run: 0.010-0.026 ms per handshake; lab assertion <1 ms. The
~40x margin absorbs machine noise deliberately — the claim is "tens of
microseconds, structurally," not any particular digit. G1's 2-5 ms young
pauses on similar churn are the comparison baseline: expect roughly two
orders of magnitude between them, asserted as 10x-or-better in the
cross-collector probe.

## Throughput tax shape

Load barriers execute on every reference load (a few instructions, always
on) plus concurrent workers consume cores during marking/relocation.
Allocation-heavy workloads typically show single-digit percent throughput
cost versus G1. Read-heavy pointer-chasing shapes pay relatively more
(loads dominate); compute-heavy shapes with few loads pay relatively
less. Measure your allocation profile; do not generalize across shapes.

## Sizing for headroom

Because relocation races allocation, tight heaps are the failure mode:
sustained allocation past the concurrent budget triggers allocation
stalls (the pause-equivalent). Size with slack, keep old-gen occupancy
moderate, and treat stall counters as the primary capacity signal —
pause charts will look fine right up until they don't.

## Minor/major cost split

Minors are the frequent cheap path (young only, concurrent, microsecond
handshakes). Majors are infrequent and span longer (young plus old
phases). If majors dominate cycle counts on a young-heavy workload, the
old set is retaining too much — investigate promotion, not pause tuning.

## Timer cost awareness

`ZCollectionInterval` spends a major per interval even idle. At 0.1 s
that is ~10 majors/second of concurrent work for hygiene. Price it
against the burst-latency win it buys; on constantly busy heaps the timer
adds nothing and should stay at default 0.
