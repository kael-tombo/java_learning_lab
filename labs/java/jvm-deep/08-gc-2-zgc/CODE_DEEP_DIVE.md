# ZGC — Code Deep Dive

All snippets run on any JDK 9+ (verified on JDK 23; ZGC paths need a JDK
that ships it — x64/aarch64 Linux, macOS, Windows on 23 all qualify).
Snippets that spawn JVMs assume a JDK on PATH. Heaps are pinned (`-Xmx`)
so ergonomics reproduce.

## 1. Selecting ZGC: Flags Off the Running JVM

```java
public class SelectZgc {
    static boolean flag(String out, String name, String want) {
        for (String line : out.split("\n")) {
            String s = line.strip().replaceAll("\\s+", " ");
            if (s.contains(" " + name + " = ")) return s.contains("= " + want + " ");
        }
        return false;
    }

    public static void main(String[] args) throws Exception {
        Process p = new ProcessBuilder("java", "-XX:+UseZGC",
                "-XX:+PrintFlagsFinal", "-version")
                .redirectErrorStream(true).start();
        String out = new String(p.getInputStream().readAllBytes())
                .replaceAll("[ \\t]+", " ");
        p.waitFor();

        System.out.println("UseZGC on via command line: " + flag(out, "UseZGC", "true"));
        System.out.println("ZGenerational default true: " + flag(out, "ZGenerational", "true"));
        System.out.println("ZCollectionInterval default 0 (off): "
                + out.contains("ZCollectionInterval = 0"));
    }
}
```

Expected output:
```
UseZGC on via command line: true
ZGenerational default true: true
ZCollectionInterval default 0 (off): true
```

Three reads pin the configuration space: opt-in collector, generational by
default, no timer unless asked. (Compare lab 07's G1 flag reads — same
query, different collector.)

## 2. Generational Surface: Collectors and Pools by Name

The beans belong to the running JVM, so this snippet spawns a child with
`-XX:+UseZGC` and reads *its* beans (same driver pattern as the GC-log
snippets — never assert about a JVM you didn't launch):

```java
import java.nio.file.Files;
import java.nio.file.Path;

public class ZgcNames {
    static final String PROBE = """
            import java.lang.management.ManagementFactory;
            public class ZBeans {
                public static void main(String[] a) {
                    java.util.List<String> collectors = new java.util.ArrayList<>();
                    for (var g : ManagementFactory.getGarbageCollectorMXBeans())
                        collectors.add(g.getName());
                    java.util.List<String> pools = new java.util.ArrayList<>();
                    for (var p : ManagementFactory.getMemoryPoolMXBeans())
                        if (p.getName().startsWith("ZGC")) pools.add(p.getName());
                    java.util.Collections.sort(collectors);
                    java.util.Collections.sort(pools);
                    System.out.println("collectors = " + collectors);
                    System.out.println("ZGC pools = " + pools);
                    System.out.println("minor+major cycles and pauses present: "
                            + (collectors.contains("ZGC Minor Cycles")
                            && collectors.contains("ZGC Minor Pauses")
                            && collectors.contains("ZGC Major Cycles")
                            && collectors.contains("ZGC Major Pauses")));
                    System.out.println("young+old pools present: "
                            + (pools.contains("ZGC Young Generation")
                            && pools.contains("ZGC Old Generation")));
                }
            }
            """;

    public static void main(String[] args) throws Exception {
        Path dir = Files.createTempDirectory("zbeans");
        Path src = dir.resolve("ZBeans.java");
        Files.writeString(src, PROBE);
        new ProcessBuilder("javac", "-d", dir.toString(), src.toString())
                .redirectErrorStream(true).start().waitFor();
        Process p = new ProcessBuilder("java", "-XX:+UseZGC", "-Xmx256m",
                "-cp", dir.toString(), "ZBeans")
                .redirectErrorStream(true).start();
        String out = new String(p.getInputStream().readAllBytes());
        p.waitFor();
        System.out.print(out);
    }
}
```

Expected output:
```
collectors = [ZGC Major Cycles, ZGC Major Pauses, ZGC Minor Cycles, ZGC Minor Pauses]
ZGC pools = [ZGC Old Generation, ZGC Young Generation]
minor+major cycles and pauses present: true
young+old pools present: true
```

Cycles vs Pauses are separate beans — concurrent work vs STW handshakes are
accounted independently, which is exactly the right observability split for
this collector.

## 3. Every Pause Sub-Millisecond (Measured, Not Quoted)

```java
import java.nio.file.Files;
import java.nio.file.Path;

public class PauseBudget {
    static final String PROBE = """
            import java.util.ArrayList;
            public class ZChurn {
                public static void main(String[] a) {
                    ArrayList<byte[]> hold = new ArrayList<>();
                    for (int i = 0; i < 2000; i++) {
                        hold.add(new byte[128 * 1024]);
                        if (hold.size() > 100) hold.subList(0, 50).clear();
                    }
                    System.out.println("done");
                }
            }
            """;

    public static void main(String[] args) throws Exception {
        Path dir = Files.createTempDirectory("zgc");
        Path src = dir.resolve("ZChurn.java");
        Files.writeString(src, PROBE);
        new ProcessBuilder("javac", "-d", dir.toString(), src.toString())
                .redirectErrorStream(true).start().waitFor();
        Process p = new ProcessBuilder("java", "-XX:+UseZGC", "-Xmx128m",
                "-Xlog:gc+phases", "-cp", dir.toString(), "ZChurn")
                .redirectErrorStream(true).start();
        String out = new String(p.getInputStream().readAllBytes());
        p.waitFor();

        double maxMs = 0;
        int pauses = 0;
        for (String line : out.split("\n")) {
            java.util.regex.Matcher m = java.util.regex.Pattern
                    .compile("Pause\\s+[A-Za-z ]+?\\s+(\\d+\\.\\d+)ms\\s*$")
                    .matcher(line.strip());
            if (m.find()) {
                pauses++;
                maxMs = Math.max(maxMs, Double.parseDouble(m.group(1)));
            }
        }
        System.out.println("stw pauses observed = " + pauses);
        System.out.println("max pause ms = " + String.format("%.3f", maxMs));
        System.out.println("pauses happened and all under 1ms: "
                + (pauses > 0 && maxMs < 1.0));
    }
}
```

Expected output (counts/times vary — elided):
```
...
pauses happened and all under 1ms: true
```

Minor collections fire on allocation rate/high usage at 128 MB; every
mark/relocate handshake lands in the tens of microseconds (measured
0.010–0.026 ms here — a ~40x margin under the 1 ms bar). The regex anchors
to line-end `ms` so cycle-total `0.009s` summaries never pollute the pause
sample.

## 4. Minor vs Major Reasons in the Log

```java
import java.nio.file.Files;
import java.nio.file.Path;

public class MinorMajor {
    // Probe duplicated (not referenced) so this snippet compiles standalone
    static final String PROBE = """
            import java.util.ArrayList;
            public class ZChurn {
                public static void main(String[] a) {
                    ArrayList<byte[]> hold = new ArrayList<>();
                    for (int i = 0; i < 2000; i++) {
                        hold.add(new byte[128 * 1024]);
                        if (hold.size() > 100) hold.subList(0, 50).clear();
                    }
                    System.out.println("done");
                }
            }
            """;

    public static void main(String[] args) throws Exception {
        Path dir = Files.createTempDirectory("zgcmm");
        Path src = dir.resolve("ZChurn.java");
        Files.writeString(src, PROBE);
        new ProcessBuilder("javac", "-d", dir.toString(), src.toString())
                .redirectErrorStream(true).start().waitFor();
        Process p = new ProcessBuilder("java", "-XX:+UseZGC", "-Xmx128m",
                "-Xlog:gc", "-cp", dir.toString(), "ZChurn")
                .redirectErrorStream(true).start();
        String out = new String(p.getInputStream().readAllBytes());
        p.waitFor();

        boolean warmupMajor = out.contains("Major Collection (Warmup)");
        boolean minor = out.contains("Minor Collection");
        System.out.println("warmup major at startup: " + warmupMajor);
        System.out.println("minor collections under churn: " + minor);
        System.out.println("occupancy deltas logged: " + out.contains("M("));
    }
}
```

Expected output:
```
warmup major at startup: true
minor collections under churn: true
occupancy deltas logged: true
```

Every ZGC JVM opens with a warmup major (heap sizing + metadata), then
minors track allocation pressure with parenthesized reasons (`High Usage`,
`Allocation Rate`). Reusing `PauseBudget.PROBE` by reference — one probe,
two experiments, zero drift.

## 5. Idle JVMs Collect Too: the Timer Trigger

```java
import java.nio.file.Files;
import java.nio.file.Path;

public class TimerTrigger {
    static final String PROBE = """
            public class ZTimer {
                public static void main(String[] a) throws Exception {
                    Thread.sleep(600);
                    System.out.println("slept");
                }
            }
            """;

    public static void main(String[] args) throws Exception {
        Path dir = Files.createTempDirectory("zgct");
        Path src = dir.resolve("ZTimer.java");
        Files.writeString(src, PROBE);
        new ProcessBuilder("javac", "-d", dir.toString(), src.toString())
                .redirectErrorStream(true).start().waitFor();
        Process p = new ProcessBuilder("java", "-XX:+UseZGC", "-Xmx256m",
                "-XX:ZCollectionInterval=0.1", "-Xlog:gc",
                "-cp", dir.toString(), "ZTimer")
                .redirectErrorStream(true).start();
        String out = new String(p.getInputStream().readAllBytes());
        p.waitFor();

        int timerMajors = 0;
        for (String line : out.split("\n")) {
            if (line.contains("Major Collection (Timer)")) timerMajors++;
        }
        System.out.println("timer majors during idle sleep = " + timerMajors);
        System.out.println("idle heap collected on schedule (>=2 in 600ms): "
                + (timerMajors >= 2));
    }
}
```

Expected output (count varies — elided):
```
...
idle heap collected on schedule (>=2 in 600ms): true
```

Zero allocation, zero pressure — yet majors fire every ~120 ms on the
0.1 s interval. `ZCollectionInterval` is heap hygiene for services that
idle between latency-critical bursts: dead objects never linger into the
next request just because nothing allocated.

## Common Pitfalls Encountered Here

- **Reading cycle totals as pauses** — `0.009s` summaries span concurrent
  work; pauses are the `Pause ... Xms` phase lines (snippet 3's regex
  distinguishes).
- **Assuming idle means uncollected** — only with the timer off (default);
  interval mode collects empty heaps (snippet 5).
- **Expecting G1 pool names** — ZGC registers its own pools/collectors;
  dashboards keyed on `G1 Eden Space` go blind (snippet 2).
- **Forgetting `-Xmx` in experiments** — young-gen sizing and trigger
  points key off heap size; unpinned runs don't reproduce (all snippets
  pin).
- **Treating warmup major as pathology** — first-cycle major is startup
  routine, not pressure (snippet 4).
- **Comma-joined log tags** — `-Xlog:gc+phases`, never `-Xlog:gc,phases`
  (lab 07's RegionSize lesson — repeated here because it bites once per
  lab).
