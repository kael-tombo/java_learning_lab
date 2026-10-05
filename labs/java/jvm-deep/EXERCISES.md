# Exercises — JVM Deep (10 hands-on)

## E1 — javap Reading
```bash
javac Main.java && javap -c -p Main
```
Tasks: find aload/invokevirtual; map loop to goto/if_icmp.

## E2 — Classloading Delegation
Tasks: custom URLClassLoader child-first; break + fix NoClassDefFoundError.

## E3 — JIT Tiers
```bash
java -XX:+PrintCompilation -XX:+UnlockDiagnosticVMOptions -XX:+PrintInlining Main
```
Tasks: spot C1→C2, inline fail (too big), fix by splitting method.

## E4 — Escape Analysis
Tasks: alloc-in-loop bench; `-XX:+DoEscapeAnalysis` on/off + JFR alloc profile.

## E5 — G1 Log Reading
```bash
java -Xlog:gc*:file=gc.log -Xmx1g -XX:+UseG1GC Main
```
Tasks: Eden→Survivor→Mixed; measure pause avg/p99.

## E6 — ZGC Switch
```bash
java -XX:+UseZGC -Xlog:gc* Main
```
Tasks: compare p99 vs G1 on 4GB heap workload.

## E7 — Heap Dump Triage
```bash
jmap -dump:live,format=b,file=h.hprof <pid>
```
Tasks: MAT/jxray top dominators; find static cache leak.

## E8 — Metaspace/Threads
Tasks: dynamic-proxy leak → Metaspace growth; 5k threads → stack math; fix with pool.

## E9 — Safepoint/JFR
Tasks: `jcmd <pid> JFR.start`; find long TTSP / lock stalls in JFR viewer.

## E10 — Tuning Capstone
Tasks: given slow service (GC logs provided), propose 3 flags + code fix.
Flags matrix: `-Xmx -Xms -XX:MaxGCPauseMillis -XX:+UseZGC`. Checklist: evidence cited.
