# Code Deep Dive — JVM

## 1. Source Tour
- HotSpot: `src/hotspot/share/{oops,gc/g1,compiler,runtime}`.
- G1: `g1CollectedHeap.cpp`, `heapRegion.hpp`; ZGC: `gc/z/*`.
- JIT: `c1/`, `opto/` (C2), `ci/` specs.

## 2. Bytecode Lab
```java
int add(int a, int b) { return a + b; }
```
`javap -c` → `iload_1, iload_2, iadd, ireturn`. Loop adds `goto`.
Escape: `new Point(x,y)` scalar-replaced if no-escape (JFR alloc absent).

## 3. JIT Log Reading
```bash
java -XX:+UnlockDiagnosticVMOptions -XX:+PrintCompilation -XX:+PrintInlining -XX:CompileCommand=print,*Main.hot Main
```
`made zombie/deopt` → speculation failed; split megamorphic call.

## 4. Assembly (hsdis)
`-XX:+PrintAssembly` needs hsdis lib; look for `call` vs inlined body, vector `vmovdqu`.
Compare C1 (quick) vs C2 (unrolled/vectorized).

## 5. GC Log Anatomy (G1)
`[gc,start] Young → [gc] Eden 400M→0, Pause 12ms`. Mixed adds `Old 800M→600M`.
Tune: `-XX:MaxGCPauseMillis=100 -XX:G1HeapRegionSize=4m`.

## 6. ZGC Internals
Colored pointers (metadata in ref bits) + load barriers; `ZPage` manage.
Flags: `-XX:+UseZGC -Xlog:gc* -XX:+ZGenerational` (default gen in 21+).

## 7. NMT + JFR
```bash
java -XX:NativeMemoryTracking=detail -XX:+UnlockDiagnosticVMOptions -XX:+PrintNMTStatistics -version
jcmd <pid> VM.native_memory detail; jcmd <pid> JFR.start duration=60s filename=a.jfr
```

## 8. OOM Triage Map
Heap dump dominator → static field; Metaspace → loader/proxy leak; `unable to create thread` → Xss/ulimit.

## 9. Refs
JVMS (bytecode), HotSpot wiki, `java -Xlog:help`, JEP 376 (ZGC), G1 paper.
