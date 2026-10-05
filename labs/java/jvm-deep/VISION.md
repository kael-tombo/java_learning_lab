# Vision — JVM Deep

## Direction
- Generational ZGC default low-pause; G1 remains balanced workhorse.
- Leyden AOT + CDS close startup gap; profilers (JFR) always-on in prod.
- Valhalla reduces allocation pressure at the language level.

## 5-Year Bets
1. Sub-ms pauses standard even at 100GB+ heaps.
2. AOT caches standard in containers (startup −50%).
3. Continuous profiling (JFR streaming) drives autotuning.

## Constants
- Measure first (JFR/GC log/flame); flags second.
- Heap + direct + metaspace + stacks budgeted together.

## Signals
- Leyden, generational ZGC, Valhalla JEPs; async-profiler releases.
- eBPF + JFR correlation for kernel-level stalls.

## Career
JVM triage + tuning is principal-level leverage. Run the incident drill.

## Anti-Vision
Don't cargo-cult flags across workloads — every heap differs.
Don't chase 0-pause while ignoring allocation rate.

## 30/60/90
- 30d: bytecode + JIT + G1 logs.
- 60d: dumps + ZGC + NMT.
- 90d: lead tuning drill with report.
