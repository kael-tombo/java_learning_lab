# Mini Project — Allocation Profiler

## Goal
Report top-5 allocating methods + bytes/s using JFR, no agent code.

## Steps
1. Workload: loop allocating Point/String/Box variants.
2. `jcmd <pid> JFR.start duration=30s filename=a.jfr settings=profile`.
3. Parse with `jfr` tool / JDK Mission Control; extract `jdk.ObjectAllocationInNewTLAB`.
4. Rank by total bytes; propose one fix (reuse/record/EA-friendly).

## Skeleton
```bash
java -XX:+UseG1GC -Xlog:gc* App &
jcmd $! JFR.start duration=30s filename=a.jfr
jfr summary a.jfr | grep -i alloc
```

## Acceptance
- Top-5 table with bytes + rate; one fix halves top allocator.
- GC pause before/after recorded.

## Stretch
- async-profiler alloc flame; compare EA on/off.

## Demo (2 min)
Show flame + table + fix diff.
