# Lab 01: JVM Memory & GC — Mini Project

## Project: `GCSight` — Allocation Rate & Pause Budget Dashboard

**Time**: 8–12 hours | **Difficulty**: Intermediate–Advanced | **Stack**: Java 21, JDK tooling, no frameworks required

You will build a small toolkit that (a) reproduces classic JVM memory pathologies on demand, and (b) parses GC logs into the metrics an SRE actually needs: live set, allocation rate, GC frequency, and pause distribution.

---

## Part 1 — Reproduce the pathologies

Build these as separate runnable mains, each with a CLI flag, so you can trigger them in isolation.

### 1.1 Steady allocation churn (harmless, high GC pressure)

```java
public class Churn {
    public static void main(String[] args) {
        long deadline = System.nanoTime() + 30_000_000_000L;
        long count = 0;
        while (System.nanoTime() < deadline) {
            // short-lived garbage: nothing retained, GC must run constantly
            byte[] buf = new byte[1024];
            buf[0] = (byte) count++;
        }
        System.out.println("iterations=" + count);
    }
}
```

Expected: many young GCs, tiny live set, high `R`. This is the *good* case for a big young gen.

### 1.2 Unbounded cache (the classic leak)

```java
public class LeakyCache {
    private static final Map<Long, byte[]> CACHE = new ConcurrentHashMap<>();

    public static void main(String[] args) {
        long deadline = System.nanoTime() + 30_000_000_000L;
        long i = 0;
        while (System.nanoTime() < deadline) {
            CACHE.put(i++, new byte[64 * 1024]);   // 64 KB per entry, never evicted
        }
        System.out.println("entries=" + CACHE.size()
            + " approxHeap=" + (CACHE.size() * 64L * 1024 / (1024 * 1024)) + "MB");
    }
}
```

Expected: live set climbs ~1.9 MB/s; eventually `OutOfMemoryError: Java heap space`. Then add a `LinkedHashMap` LRU with a cap and show the OOM never happens.

### 1.3 Humongous allocation storm (G1-specific)

```java
public class Humongous {
    public static void main(String[] args) {
        long deadline = System.nanoTime() + 20_000_000_000L;
        while (System.nanoTime() < deadline) {
            // larger than half a G1 region -> allocated straight into old gen
            ByteBuffer.allocateDirect(40 * 1024 * 1024);
        }
    }
}
```

Run with `-XX:+UseG1GC -Xlog:gc*:file=humongous.log` and show `G1 Humongous Allocation` / `Evacuation Failure`. Then chunk into 4 MB buffers and compare pause counts.

### 1.4 Metaspace leak via throwaway classloaders

```java
public class MetaLeak {
    public static void main(String[] args) throws Exception {
        for (int i = 0; i < 100_000; i++) {
            URLClassLoader cl = new URLClassLoader(new URL[0], null);
            Class<?> c = cl.loadClass("java.util.HashMap");  // force a class to be defined
            c.getName();
            if (i % 10_000 == 0) System.out.println("loaded=" + i);
        }
    }
}
```

Run with `-XX:MaxMetaspaceSize=64m` and watch `OutOfMemoryError: Metaspace`. This is the redeploy/app-server leak in miniature.

---

## Part 2 — The metrics tool

### 2.1 Requirements

Parse a unified GC log (`-Xlog:gc*:file=gc.log:time,uptime,tags`) and emit:

- Live set over time (the `after` value of each collection).
- Allocation rate between collections.
- GC frequency (collections/min).
- Pause distribution: p50 / p99 / max, split by cause.
- Humongous allocation count and old-gen promotion events.

### 2.2 Core parser sketch

```java
public record GcEvent(
    long uptimeMs, String cause, double beforeM, double afterM, double totalM, double pauseMs) {}

public final class GcLogParser {
    private static final Pattern PAUSE = Pattern.compile(
        "^\\[\\d+\\.\\d+s\\]\\s+Pause\\s+(.+?)\\s+([\\d.]+)([MG])->([\\d.]+)([MG])\\(([\\d.]+)([MG])\\)\\s+([\\d.]+)ms");

    public static List<GcEvent> parse(Path log) throws IOException {
        List<GcEvent> out = new ArrayList<>();
        for (String line : Files.readAllLines(log)) {
            Matcher m = PAUSE.matcher(line);
            if (!m.find()) continue;
            double scale = m.group(3).equals("G") ? 1024 : 1;
            out.add(new GcEvent(
                uptime(line), m.group(1),
                Double.parseDouble(m.group(2)) * scale,
                Double.parseDouble(m.group(4)) * scale,
                Double.parseDouble(m.group(6)) * scale,
                Double.parseDouble(m.group(8))));
        }
        return out;
    }

    private static long uptime(String line) {
        Matcher t = Pattern.compile("^\\[([\\d.]+)s\\]").matcher(line);
        return t.find() ? (long) (Double.parseDouble(t.group(1)) * 1000) : 0;
    }
}
```

### 2.3 Report output

```
=== GCSight report: gc.log ===
window            : 0s .. 180s
live set (min/med/max) : 118 MB / 132 MB / 141 MB
allocation rate  : 21.4 MB/s  (p95 34.8 MB/s)
GC frequency     : 14.3 /min
pause p50/p99/max: 12ms / 41ms / 88ms
by cause:
  G1 Evacuation Pause      n=43  total=812ms   max=88ms
  G1 Humongous Allocation  n=6   total=310ms   max=74ms
verdict: humongous pressure — see recommendation R2
```

Include a `recommendation()` function with at least: (a) live set > 60% of max heap, (b) allocation rate high with long young-gen interval, (c) humongous allocations present.

---

## Part 3 — Container-aware sizing calculator

Write a small CLI that takes traffic and memory facts and emits a defensible config:

```
$ java -jar Sizer.jar \
    --live-set-mb 6144 --rps 8000 --alloc-kb 900 --container-limit-mb 4096 --concurrency 3000

live set        : 6144 MB
recommended heap: 18432 MB  (3.0x live set)
recommended maxram%: 75       (heap + 25% native headroom)
young gen       : 1024 MB    (GC every ~1.2s at measured allocation rate)
humongous guard : chunk payloads to <= 4 MB
exit flags      : -XX:+HeapDumpOnOutOfMemoryError -XX:+ExitOnOutOfMemoryError
```

Show your arithmetic in the output — the point is a defensible decision, not a magic number.

---

## Part 4 — Runbook artifact

Produce `RUNBOOK_GC.md` in your project with:
1. The exact `-Xlog` flags you use in prod and why (retention, sampling).
2. Your alert rules (e.g. live set > 70% of heap for 10 min; pause p99 > 200 ms; full GC count > 0).
3. The OOM triage flowchart: which OOM type → which two commands → which fix.
4. A canary procedure for changing collector or heap size, with a rollback trigger.

---

## Acceptance Criteria

- [ ] Each pathology reproduces its documented symptom, with a captured log.
- [ ] Parser correctly extracts ≥ 95% of pause lines in your own generated log.
- [ ] Report identifies the humongous pathology and prints a matching recommendation.
- [ ] Sizer output arithmetic is hand-checkable and matches THEORY formulas.
- [ ] `RUNBOOK_GC.md` is usable by an engineer who did not build the service.
- [ ] You can explain, without notes, why `Xmx` alone is not a container-safe memory budget.

---

## Stretch

- Add safepoint log parsing and report safepoint time separately from GC time.
- Compute allocation rate *per class* using JFR (`-XX:StartFlightRecording`) `ObjectAllocationSample` events.
- Compare G1 vs ZGC on the same workload in a container and write a one-page decision record.
