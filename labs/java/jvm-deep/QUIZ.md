# Quiz — JVM Deep (20 Q)

1. Bytecode vs machine code?
> Stack-based IR vs JIT-compiled native.
2. Classload delegation?
> Child→parent first (except custom).
3. Bootstrap/Platform/App loaders?
> JDK/platform/app classes.
4. C1 vs C2?
> Fast client vs optimizing server compiler.
5. Tiered default?
> C1 then C2 with profiling.
6. Inline condition?
> Small, hot, monomorphic.
7. Deopt?
> Fallback to interp on wrong speculation.
8. Safepoint?
> Global rendezvous for GC/deopt.
9. G1 regions?
> Heap split 1-32MB regions, per-region collect.
10. Young vs Mixed?
> Eden/survivor vs mixed young+old.
11. ZGC barrier?
> Load barrier + colored pointers.
12. Shenandoah?
> Concurrent compacting low-pause.
13. Metaspace?
> Class metadata off-heap (native).
14. OOM kinds?
> Heap/Metaspace/Direct/Threads/FDs.
15. -Xmx vs -Xms?
> Max vs initial heap.
16. MaxGCPauseMillis?
> G1 pause goal (hint).
17. JFR vs jstack?
> Event recorder vs thread snapshot.
18. NMT?
> Native memory tracking detail.
19. CDS?
> Shared archive faster startup.
20. First tuning step?
> Measure (JFR/GC log), not flags.
