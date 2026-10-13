# Exercises: JVM Tuning

Runnable tasks with exact flags. One variable per experiment.

## 1. Derive ergonomics from RAM

```bash
java -XX:+PrintFlagsFinal -version | grep -E "InitialHeapSize|MaxHeapSize"
```

Divide each by detected RAM and confirm RAM/64 and RAM/4 within wide
tolerance (reference: 256M/4G at 16 GB). Re-run inside your container or
constrained environment and record how the derivation shifts — that shift
is the "measure inside the deployment" lesson.

## 2. Prove explicit beats ergonomic

```bash
java -Xmx256m -XX:+PrintFlagsFinal -version | grep "MaxHeapSize"
```

Expect exactly 268435456. Then set `-Xms256m -Xmx256m` on a sample
service and confirm resize-pause lines vanish from `-Xlog:gc` during
ramp — the fixed-heap posture priced in committed memory.

## 3. Read the layout contract

```bash
java -XX:+PrintFlagsFinal -version | grep -E "NewRatio|SurvivorRatio|TargetSurvivorRatio|TLABSize|MinTLABSize"
```

Expect 2, 8, 50, 0, 2048. Compute your heap's young/Eden/survivor sizes
in MB from these before any churn experiment — geometry first, behavior
second.

## 4. Measure the TLAB gap (diagnostic-only off-switch)

```bash
javac TAlloc.java
java -cp . TAlloc
java -XX:-UseTLAB -cp . TAlloc
```

Using the lab's `TAlloc` probe (3M nodes): record both millisecond
figures, assert ratio >3x (reference ~35 vs ~250-315 ms, ~8x). Re-enable
TLABs immediately — the off-switch never ships to production.

## 5. Verify the three planes

```bash
java -XX:+PrintFlagsFinal -version | grep -E "UseCompressedOops|UseCompressedClassPointers|ReservedCodeCacheSize|CompressedClassSpaceSize"
```

Expect true/true/251658240/1073741824, plus `Metaspace` and `CodeHeap*`
pools enumerated in-process. Write one sentence per plane: what pressure
there looks like and which graph would show it first.

## 6. Move pause count with one flag

```bash
javac ChurnT.java
java -XX:+UseParallelGC -Xmx128m -Xlog:gc -cp . ChurnT
java -XX:+UseParallelGC -Xmx512m -Xlog:gc -cp . ChurnT
```

Count `Pause Young (` lines per run; assert smaller heap collects more
often with heap size as the only variable. Re-run both under default G1,
record the flattening, and state the adaptivity finding in one sentence.
