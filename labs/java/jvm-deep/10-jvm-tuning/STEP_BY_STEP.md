# Step by Step: JVM Tuning

1. Query ergonomics: `java -XX:+PrintFlagsFinal -version`, collapse
   alignment padding, extract `InitialHeapSize` and `MaxHeapSize`. Divide
   by detected RAM (OS MXBean total) and confirm RAM/64 and RAM/4 within
   wide tolerance. Record your box's absolute numbers.
2. Prove explicit wins: add `-Xmx256m`, re-query, confirm `MaxHeapSize ==
   256*1048576` exactly. This byte-exactness is the control you will rely
   on for every later experiment.
3. Read the layout contract: grep `NewRatio = 2`, `SurvivorRatio = 8`,
   `TargetSurvivorRatio = 50`, `TLABSize = 0`, `MinTLABSize = 2048`. Write
   the derived geometry for your heap (young size, Eden size, survivor
   sizes) in megabytes before proceeding.
4. Measure the TLAB win: run the `TAlloc` probe (3M nodes) with default
   flags, record ms; re-run with `-XX:-UseTLAB`, record ms; assert ratio
   >3x (reference ~35 vs ~250-315 ms, ~8x). Never leave the flag off
   after measuring — it is diagnostic-only.
5. Verify compression and planes: grep `UseCompressedOops = true`,
   `UseCompressedClassPointers = true`, `ReservedCodeCacheSize =
   251658240`, `CompressedClassSpaceSize = 1073741824`; enumerate MXBeans
   for `Metaspace` and `CodeHeap*` pools. Three planes, three evidences.
6. Run the one-flag experiment: identical churn (`ChurnT`, 400 x 256 KB
   bounded) under `-XX:+UseParallelGC` at `-Xmx128m` and `-Xmx512m`,
   both `-Xlog:gc`; count `Pause Young (` lines per run. Assert smaller
   heap collects more often with exactly one variable changed.
7. Re-run step 6 under default G1 and record the flattening: adaptive
   young-sizing absorbs the heap lever. Write the sentence "ParallelGC's
   fixed young fraction makes heap size a clean lever; G1 adaptivity
   absorbs it" with your two count pairs attached.
8. Container check: repeat step 1 inside your tightest cgroup-limited
   environment and diff the ergonomic numbers against the host reading —
   file the diff as the reason laptop-derived flags never ship directly.
