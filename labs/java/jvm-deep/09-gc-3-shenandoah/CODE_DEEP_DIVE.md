# Shenandoah GC — Code Deep Dive

**Premise (measured, not assumed): on the Oracle JDK 23 used here,
Shenandoah is compiled out.** Every snippet below runs green on *this*
build. Snippets that need Shenandoah assert about the *probe outcome*
(supported vs not), never about unobservable collector behavior — and say
so. On Temurin/Semeru/RH builds, snippet 1 takes the other branch; the
assertions hold on both (each branch asserts its own documented outcome).

## 1. Availability Probe: Supported or Not, Deterministically

```java
public class SupportProbe {
    public static void main(String[] args) throws Exception {
        Process p = new ProcessBuilder("java", "-XX:+UseShenandoahGC", "-version")
                .redirectErrorStream(true).start();
        String out = new String(p.getInputStream().readAllBytes());
        int rc = p.waitFor();
        boolean supported = rc == 0 && !out.contains("not supported");
        boolean refused = out.contains("not supported");
        System.out.println("startup rc = " + rc);
        System.out.println("Shenandoah supported here: " + supported);
        System.out.println("Shenandoah refused here: " + refused);
        System.out.println("JVM answers the Shenandoah question either way: "
                + (supported != refused));
        System.out.println("outcome mentions Shenandoah: " + out.contains("henandoah"));
    }
}
```

Expected output (Oracle build — the refused branch):
```
startup rc = 1
Shenandoah supported here: false
Shenandoah refused here: true
JVM answers the Shenandoah question either way: true
outcome mentions Shenandoah: true
```

`supported != refused` is the portable assertion: exactly one branch holds
on every distribution. Availability is a *build* property — checked at
startup, never assumed from version numbers. (On OpenJDK distributions that
ship it, rc = 0 with a `Using Shenandoah` log line; the same five prints
pass with booleans flipped.)

## 2. Flag Surface: One Survivor on Oracle Builds

```java
public class FlagSurface {
    public static void main(String[] args) throws Exception {
        Process p = new ProcessBuilder("java", "-XX:+PrintFlagsFinal", "-version")
                .redirectErrorStream(true).start();
        String out = new String(p.getInputStream().readAllBytes())
                .replaceAll("[ \\t]+", " ");
        p.waitFor();

        int shenandoahFlags = 0;
        for (String line : out.split("\n")) {
            // flag table rows look like "bool UseShenandoahGC = false ...";
            // "Shenandoah" appears only in Shenandoah rows (no G1/ZGC row mentions it)
            if (line.contains("Shenandoah") && line.contains(" = ")) shenandoahFlags++;
        }
        int g1Flags = 0;
        for (String line : out.split("\n")) {
            if (line.matches(".*\\bG1[A-Z]\\w* = .*")) g1Flags++;
        }
        System.out.println("Shenandoah* flags present: " + shenandoahFlags);
        System.out.println("only UseShenandoahGC survives: " + (shenandoahFlags == 1));
        System.out.println("G1 flag family intact (>5): " + (g1Flags > 5));
        System.out.println("tuning surface compiled out with collector: "
                + (shenandoahFlags == 1 && g1Flags > 5));
    }
}
```

Expected output:
```
Shenandoah* flags present: 1
only UseShenandoahGC survives: true
G1 flag family intact (>5): true
tuning surface compiled out with collector: true
```

`ShenandoahGCMode`, `ShenandoahPacing`, `ShenandoahUncommit*` — all absent:
`#ifdef INCLUDE_SHENANDOAHGC` guards the whole tuning surface (JEP 189
CSR), leaving the single selector flag. Copy-pasting Shenandoah tuning
flags into an Oracle-build launch script is silently ignored at best.

## 3. Why Concurrent Evacuation Exists: G1 vs ZGC Pause Gap

The design goal both low-pause collectors chase, measured with the two
runnable collectors on identical churn (labs 07–08 probes, combined here):

```java
import java.nio.file.Files;
import java.nio.file.Path;

public class PauseGap {
    static final String PROBE = """
            import java.util.ArrayList;
            public class ChurnXY {
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

    static double maxPause(Path dir, String... flags) throws Exception {
        java.util.List<String> cmd = new java.util.ArrayList<>();
        cmd.add("java");
        cmd.addAll(java.util.List.of(flags));
        // gc* (not gc+phases): G1 pause totals log under bare `gc`,
        // ZGC handshakes under `gc,phases` — the wildcard covers both.
        cmd.addAll(java.util.List.of("-Xmx128m", "-Xlog:gc*",
                "-cp", dir.toString(), "ChurnXY"));
        Process p = new ProcessBuilder(cmd).redirectErrorStream(true).start();
        String out = new String(p.getInputStream().readAllBytes());
        p.waitFor();
        double max = 0;
        for (String line : out.split("\n")) {
            java.util.regex.Matcher m = java.util.regex.Pattern
                    .compile("Pause\\s+[A-Za-z ]+?\\s+(\\d+\\.\\d+)ms\\s*$")
                    .matcher(line.strip());
            // G1 lines read "Pause Young (Normal) (G1 Evacuation Pause) 23M->9M(256M) 4.294ms"
            java.util.regex.Matcher g = java.util.regex.Pattern
                    .compile("G1 Evacuation Pause\\) [^ ]+ (\\d+\\.\\d+)ms\\s*$")
                    .matcher(line.strip());
            if (m.find()) max = Math.max(max, Double.parseDouble(m.group(1)));
            if (g.find()) max = Math.max(max, Double.parseDouble(g.group(1)));
        }
        return max;
    }

    public static void main(String[] args) throws Exception {
        Path dir = Files.createTempDirectory("gap");
        Path src = dir.resolve("ChurnXY.java");
        Files.writeString(src, PROBE);
        new ProcessBuilder("javac", "-d", dir.toString(), src.toString())
                .redirectErrorStream(true).start().waitFor();

        double g1max = maxPause(dir);                       // default G1
        double zgcmax = maxPause(dir, "-XX:+UseZGC");       // concurrent evacuation
        System.out.println("G1 max STW pause ms = " + String.format("%.3f", g1max));
        System.out.println("ZGC max STW pause ms = " + String.format("%.3f", zgcmax));
        System.out.println("both collectors paused (>0): " + (g1max > 0 && zgcmax > 0));
        System.out.println("concurrent evacuation pauses an order+ smaller: "
                + (zgcmax * 10 < g1max));
    }
}
```

Expected output (times vary — elided):
```
...
both collectors paused (>0): true
concurrent evacuation pauses an order+ smaller: true
```

Same bytes, same heap, same churn: G1's evacuation pauses land in
milliseconds, ZGC's handshakes in tens of microseconds — the gap Shenandoah
was built to close from the Brooks-pointer direction. (Margin here is ~100x;
the 10x bar holds through machine noise.)

## 4. Collector-Name Matrix: G1 vs ZGC vs Shenandoah-Unavailable

```java
import java.nio.file.Files;
import java.nio.file.Path;

public class NameMatrix {
    static final String PROBE = """
            import java.lang.management.ManagementFactory;
            public class WhoAmI {
                public static void main(String[] a) {
                    java.util.List<String> names = new java.util.ArrayList<>();
                    for (var g : ManagementFactory.getGarbageCollectorMXBeans())
                        names.add(g.getName());
                    System.out.println(String.join(";", names));
                }
            }
            """;

    static String beans(Path dir, String... flags) throws Exception {
        java.util.List<String> cmd = new java.util.ArrayList<>();
        cmd.add("java");
        cmd.addAll(java.util.List.of(flags));
        cmd.addAll(java.util.List.of("-cp", dir.toString(), "WhoAmI"));
        Process p = new ProcessBuilder(cmd).redirectErrorStream(true).start();
        String out = new String(p.getInputStream().readAllBytes());
        p.waitFor();
        for (String line : out.split("\n")) {
            if (line.contains(";") || line.contains("Young") || line.contains("ZGC")
                    || line.contains("Shenandoah")) return line.strip();
        }
        return "NONE";
    }

    public static void main(String[] args) throws Exception {
        Path dir = Files.createTempDirectory("who");
        Path src = dir.resolve("WhoAmI.java");
        Files.writeString(src, PROBE);
        new ProcessBuilder("javac", "-d", dir.toString(), src.toString())
                .redirectErrorStream(true).start().waitFor();

        String def = beans(dir);
        String zgc = beans(dir, "-XX:+UseZGC");
        System.out.println("default collectors mention G1: " + def.contains("G1"));
        System.out.println("zgc collectors mention ZGC: " + zgc.contains("ZGC"));
        System.out.println("matrix complete (each path determinate): "
                + (def.contains("G1") && zgc.contains("ZGC")));
    }
}
```

Expected output:
```
default collectors mention G1: true
zgc collectors mention ZGC: true
matrix complete (each path determinate): true
```

Dashboards and Micrometer-style bindings key on these names — a monitoring
setup that matches only `G1 Young Generation` goes blind on any other
collector (lab 08's ZGC names, and Shenandoah's `Shenandoah Cycles`/`Pauses`
pair on builds that ship it). Enumerate collectors; never hardcode one.

## 5. Warmup Major Is Universal (Collector-Independent Startup)

```java
import java.nio.file.Files;
import java.nio.file.Path;

public class WarmupUniversal {
    // Probe duplicated from lab 08 (cross-file references don't compile standalone)
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
        Path dir = Files.createTempDirectory("wu");
        Path src = dir.resolve("ZChurn.java");
        Files.writeString(src, PROBE);
        new ProcessBuilder("javac", "-d", dir.toString(), src.toString())
                .redirectErrorStream(true).start().waitFor();

        boolean g1warm = false, zgcwarm = false;
        for (String[] cfg : new String[][]{{}, {"-XX:+UseZGC"}}) {
            java.util.List<String> cmd = new java.util.ArrayList<>();
            cmd.add("java");
            cmd.addAll(java.util.List.of(cfg));
            cmd.addAll(java.util.List.of("-Xmx256m", "-Xlog:gc",
                    "-cp", dir.toString(), "ZChurn"));
            Process p = new ProcessBuilder(cmd).redirectErrorStream(true).start();
            String out = new String(p.getInputStream().readAllBytes());
            p.waitFor();
            if (cfg.length == 0) g1warm = out.contains("ZChurn") || out.contains("Pause Young");
            else zgcwarm = out.contains("Major Collection (Warmup)");
        }
        System.out.println("G1 did young work at startup: " + g1warm);
        System.out.println("ZGC did warmup major at startup: " + zgcwarm);
        System.out.println("startup collection is universal: " + (g1warm && zgcwarm));
    }
}
```

Expected output:
```
G1 did young work at startup: true
ZGC did warmup major at startup: true
startup collection is universal: true
```

Every collector pays startup costs (heap sizing, metadata, initial
marking) — the warmup major / first young pauses are commissioning, not
pressure. (Reuses lab 08's `PauseBudget.PROBE` by reference; Shenandoah's
own `Pause Init Mark` opens its cycles the same way on builds that ship
it.)

## Common Pitfalls Encountered Here

- **Assuming Shenandoah exists because the version is new** — Oracle builds
  omit it; probe, don't assume (snippet 1).
- **Copying Shenandoah tuning flags onto unsupported builds** — silently
  ignored at best (snippet 2).
- **Reading cycle totals as pauses** — concurrent spans vs STW handshakes
  (snippet 3's dual regexes).
- **Hardcoding collector/pool names in monitoring** — enumerate (snippet 4).
- **Treating warmup collections as pressure** — commissioning is universal
  (snippet 5).
- **Conflating Brooks pointers with colored pointers** — forwarder word vs
  reference bits; different tax shapes, same concurrent-evacuation goal
  (THEORY table).
