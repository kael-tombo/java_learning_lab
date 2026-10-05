# Real-World Project — Tuning + Incident Drill

## Problem
p99 spiked 40ms→400ms after deploy; diagnose and fix with evidence.

## Setup
App + load script (k6 500rps) + broken flags (tiny NewRatio, 2GB heap, debug agent).

## Milestones
1. **M1 Repro**: GC log + JFR baseline; capture p50/p99, pause%, alloc rate.
2. **M2 Triage**: heap dump dominators, top alloc (JFR), thread dump (blocked?), `VM.native_memory`.
3. **M3 Fix**: code (cache leak/static list) + flags (`-Xmx4g -XX:+UseG1GC -XX:MaxGCPauseMillis=100` or ZGC).
4. **M4 Verify**: p99 back < 60ms, pause% < 1%, 24h soak flat RSS.
5. **M5 Report**: one-page RCA: symptom→evidence→fix→numbers + guardrail alert.

## Key Commands
```bash
java -Xmx4g -Xlog:gc*:file=gc.log -XX:+UseG1GC -XX:MaxGCPauseMillis=100 \
  -XX:+HeapDumpOnOutOfMemoryError -XX:NativeMemoryTracking=detail App
jmap -dump:live,format=b,file=h.hprof <pid>
jcmd <pid> Thread.print > threads.txt
```

## Testing
- Load: k6 500rps×30min, 0 errors, p99 documented.
- Chaos: pod kill + heap pressure → recovers, no Full GC storm.

## Ops
- K8s 4Gi/2CPU, probes, VPA suggestion; alerts: pause>50ms, old-gen>80%, codecache>85%.

## Interview Angles
- How distinguished GC vs lock vs JIT? Which single metric decided?

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Oracle GC tuning: https://docs.oracle.com/en/java/javase/21/gctuning/
- OpenJDK HotSpot: https://openjdk.org/groups/hotspot/
- JFR docs: https://docs.oracle.com/javacomponents/jmc-5-4/jfr-runtime-guide/run.htm
