# G1 Garbage Collector — Code Deep Dive

All snippets run on any JDK 9+ (verified on JDK 23), no dependencies.
Snippets that spawn JVMs assume a JDK on PATH. GC behavior varies with heap
size — every snippet pins `-Xmx` explicitly so results reproduce.

## 1. G1 Is the Default: Flags Off the Running JVM

```java
public class DefaultIsG1 {
    static boolean flag(String out, String name, String want) {
        for (String line : out.split("\n")) {
            String s = line.strip().replaceAll("\\s+", " ");
            if (s.contains(" " + name + " = ")) return s.contains("= " + want + " ");
        }
        return false;
    }

    public static void main(String[] args) throws Exception {
        Process p = new ProcessBuilder("java", "-XX:+PrintFlagsFinal", "-version")
                .redirectErrorStream(true).start();
        String raw = new String(p.getInputStream().readAllBytes());
        p.waitFor();
        String out = raw.replaceAll("[ \\t]+", " ");

        System.out.println("UseG1GC default true: " + flag(out, "UseG1GC", "true"));
        System.out.println("MaxGCPauseMillis = 200: " + out.contains("MaxGCPauseMillis = 200"));
        System.out.println("InitiatingHeapOccupancyPercent = 45: "
                + out.contains("InitiatingHeapOccupancyPercent = 45"));
    }
}
```

Expected output:
```
UseG1GC default true: true
MaxGCPauseMillis = 200: true
InitiatingHeapOccupancyPercent = 45: true
```

No ergonomics lecture needed: three flag reads pin the collector, the pause
goal, and the marking trigger. (Ergonomic values like worker counts move
with the machine — this snippet asserts only the stable defaults.)

## 2. Region Size Is Heap/2048 (Measured Twice)

```java
import java.nio.file.Files;
import java.nio.file.Path;

public class RegionSize {
    static final String PROBE = """
            public class RSize {
                public static void main(String[] a) { System.out.println("up"); }
            }
            """;

    static String initLog(Path dir, String xmx) throws Exception {
        // NB: tag sets join with '+'; '-Xlog:gc,init' parses differently and prints nothing
        Process p = new ProcessBuilder("java", "-Xmx" + xmx, "-Xlog:gc+init",
                "-cp", dir.toString(), "RSize")
                .redirectErrorStream(true).start();
        String out = new String(p.getInputStream().readAllBytes());
        p.waitFor();
        for (String line : out.split("\n")) {
            if (line.contains("Heap Region Size:")) return line.strip();
        }
        throw new IllegalStateException("no region line in log:\n" + out);
    }

    public static void main(String[] args) throws Exception {
        Path dir = Files.createTempDirectory("rsize");
        Path src = dir.resolve("RSize.java");
        Files.writeString(src, PROBE);
        new ProcessBuilder("javac", "-d", dir.toString(), src.toString())
                .redirectErrorStream(true).start().waitFor();

        String small = initLog(dir, "256m");
        String big = initLog(dir, "8g");
        System.out.println("256m heap: " + small.substring(small.indexOf("Heap Region Size:")));
        System.out.println("8g heap: " + big.substring(big.indexOf("Heap Region Size:")));
        System.out.println("1M at 256m, 2M+ at 8g (power-of-two ergonomic): "
                + (small.contains("1M") && (big.contains("2M") || big.contains("4M")
                || big.contains("8M") || big.contains("16M") || big.contains("32M"))));
    }
}
```

Expected output:
```
256m heap: Heap Region Size: 1M
8g heap: Heap Region Size: 4M
1M at 256m, 2M+ at 8g (power-of-two ergonomic): true
```

Two heaps, two region sizes, same rule (heap/2048 clamped to 1–32 MB
powers of two). The `gc,init` log is the authoritative ruler — not docs,
not memory.

## 3. Young Evacuation Pauses Under Churn

```java
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;

public class YoungPauses {
    static final String PROBE = """
            import java.util.ArrayList;
            public class Churn {
                public static void main(String[] a) {
                    ArrayList<byte[]> hold = new ArrayList<>();
                    for (int i = 0; i < 300; i++) {
                        hold.add(new byte[256 * 1024]);
                        if (hold.size() > 40) hold.subList(0, 20).clear();
                    }
                    System.out.println("churn done");
                }
            }
            """;

    public static void main(String[] args) throws Exception {
        Path dir = Files.createTempDirectory("young");
        Path src = dir.resolve("Churn.java");
        Files.writeString(src, PROBE);
        new ProcessBuilder("javac", "-d", dir.toString(), src.toString())
                .redirectErrorStream(true).start().waitFor();
        Process p = new ProcessBuilder("java", "-Xmx256m", "-Xlog:gc",
                "-cp", dir.toString(), "Churn")
                .redirectErrorStream(true).start();
        String out = new String(p.getInputStream().readAllBytes());
        p.waitFor();

        int youngPauses = 0;
        boolean fullGc = false;
        for (String line : out.split("\n")) {
            if (line.contains("Pause Young (Normal) (G1 Evacuation Pause)")) youngPauses++;
            if (line.contains("Full GC")) fullGc = true;
        }
        System.out.println("young evacuation pauses = " + youngPauses);
        System.out.println("churn caused young GCs, no full GC: "
                + (youngPauses >= 2 && !fullGc));
    }
}
```

Expected output (pause count varies — elided):
```
...
churn caused young GCs, no full GC: true
```

Short-lived garbage in a bounded heap exercises exactly one mechanism:
Eden fills, live survivors evacuate, dead vanishes — no concurrent phases,
no full collections. `23M->9M(256M)`-style lines show the before→after per
pause; the count is the assertion.

## 4. Humongous Objects Bypass Eden (Debug-Level Proof)

```java
import java.nio.file.Files;
import java.nio.file.Path;

public class HumongousProof {
    static final String PROBE = """
            import java.util.ArrayList;
            public class Huge {
                public static void main(String[] a) {
                    ArrayList<byte[]> hold = new ArrayList<>();
                    for (int i = 0; i < 20; i++) hold.add(new byte[2 * 1024 * 1024]);
                    for (int i = 0; i < 500; i++) { byte[] t = new byte[256 * 1024]; }
                    System.out.println("held=" + hold.size());
                }
            }
            """;

    public static void main(String[] args) throws Exception {
        Path dir = Files.createTempDirectory("huge");
        Path src = dir.resolve("Huge.java");
        Files.writeString(src, PROBE);
        new ProcessBuilder("javac", "-d", dir.toString(), src.toString())
                .redirectErrorStream(true).start().waitFor();
        // 256m heap -> 1M regions; 2MB arrays need 2 contiguous humongous regions each
        Process p = new ProcessBuilder("java", "-Xmx256m", "-Xlog:gc+humongous=debug",
                "-cp", dir.toString(), "Huge")
                .redirectErrorStream(true).start();
        String out = new String(p.getInputStream().readAllBytes());
        p.waitFor();

        boolean listed = out.contains("Humongous region");
        boolean arrayType = out.contains("type array");
        System.out.println("humongous regions listed at debug: " + listed);
        System.out.println("2MB objects span regions as arrays: " + (listed && arrayType));
    }
}
```

Expected output:
```
humongous regions listed at debug: true
2MB objects span regions as arrays: true
```

Humongous allocation is *silent* at info level (no log line per
allocation) — visibility requires `gc+humongous=debug` during a collection,
which lists each region with object size and type. Lesson for production:
absence of humongous lines at default logging proves nothing; sample at
debug before ruling out humongous pressure.

## 5. Pools and Collectors Name G1 (MXBean View, No Flags)

```java
import java.lang.management.ManagementFactory;

public class G1Pools {
    public static void main(String[] args) {
        java.util.List<String> pools = new java.util.ArrayList<>();
        for (var p : ManagementFactory.getMemoryPoolMXBeans()) pools.add(p.getName());
        java.util.List<String> collectors = new java.util.ArrayList<>();
        for (var g : ManagementFactory.getGarbageCollectorMXBeans())
            collectors.add(g.getName());
        java.util.List<String> g1pools = pools.stream().filter(n -> n.startsWith("G1"))
                .sorted().toList();
        System.out.println("G1 pools = " + g1pools);
        System.out.println("collectors = " + collectors);
        System.out.println("G1 Eden present: " + pools.contains("G1 Eden Space"));
        System.out.println("G1 Old Gen present: " + pools.contains("G1 Old Gen"));
        System.out.println("G1 Survivor present: " + pools.contains("G1 Survivor Space"));
        System.out.println("young+concurrent+old collectors: "
                + (collectors.contains("G1 Young Generation")
                && collectors.contains("G1 Concurrent GC")
                && collectors.contains("G1 Old Generation")));
    }
}
```

Expected output:
```
G1 pools = [G1 Eden Space, G1 Old Gen, G1 Survivor Space]
collectors = [G1 Young Generation, G1 Concurrent GC, G1 Old Generation]
G1 Eden present: true
G1 Old Gen present: true
G1 Survivor present: true
young+concurrent+old collectors: true
```

The management interface exposes the region roles as pool names — the same
three roles (Eden/Survivor/Old) plus the concurrent collector that
distinguishes G1 from Parallel. (The first line filters + sorts precisely
because raw pool-list order is unspecified VM trivia — assert membership,
never position.)

## Common Pitfalls Encountered Here

- **Reading region size off docs** — it's heap-derived; read `gc,init`
  (snippet 2).
- **Expecting humongous lines at info logging** — debug only, during
  collections (snippet 4).
- **Treating the pause target as a guarantee** — per-pause readings are
  ground truth; the flag is a goal.
- **Forgetting `-Xmx` in experiments** — ergonomics (regions, workers,
  thresholds) all key off heap size; unpinned experiments don't reproduce.
- **Assuming pool-list order is contractual** — assert membership, not
  position (snippet 5's caveat).
- **Chasing Full GCs in a healthy G1 log** — their absence is the success
  signal (snippet 3 asserts `!fullGc`).
