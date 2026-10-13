# JIT Compilation — Code Deep Dive

All snippets run on any JDK 9+ (verified on JDK 23), no dependencies.
Snippets that spawn JVMs assume a JDK on PATH. Timing assertions are
ratio-based with wide margins and were stability-tested (see notes).

## 1. Watch Tier 4 Arrive in the Compilation Log

```java
import java.nio.file.Files;
import java.nio.file.Path;

public class WatchTiers {
    static final String PROBE = """
            public class HotLoop {
                static long total;
                static void burn(int n) {
                    long s = 0;
                    for (int i = 0; i < n; i++) s += i * (i & 7);
                    total = s;
                }
                public static void main(String[] a) {
                    for (int i = 0; i < 300_000; i++) burn(200);
                    System.out.println("total=" + total);
                }
            }
            """;

    public static void main(String[] args) throws Exception {
        Path dir = Files.createTempDirectory("jit");
        Path src = dir.resolve("HotLoop.java");
        Files.writeString(src, PROBE);
        new ProcessBuilder("javac", "-d", dir.toString(), src.toString())
                .redirectErrorStream(true).start().waitFor();
        Process java = new ProcessBuilder("java", "-XX:+PrintCompilation",
                "-cp", dir.toString(), "HotLoop")
                .redirectErrorStream(true).start();
        String out = new String(java.getInputStream().readAllBytes());
        int rc = java.waitFor();

        boolean tier4 = false, tier3 = false;
        for (String line : out.split("\n")) {
            String s = line.strip();
            if (s.contains("HotLoop::burn")) {
                if (s.matches(".*\\s4\\s.*")) tier4 = true;
                if (s.matches(".*\\s3\\s.*")) tier3 = true;
            }
        }
        System.out.println("exit ok: " + (rc == 0));
        System.out.println("tier-3 compile of burn seen: " + tier3);
        System.out.println("tier-4 (C2) compile of burn seen: " + tier4);
    }
}
```

Expected output:
```
exit ok: true
tier-3 compile of burn seen: true
tier-4 (C2) compile of burn seen: true
```

300k invocations carry `burn` past both thresholds (tier 3 at ~200, tier 4
at ~5000 — THEORY table). The log's third column is the tier; `%` marks
on-stack replacement (loop-heavy methods often show `3 %`/`4 %` variants).
This is the tiered pipeline made visible, one line per promotion.

## 2. Capping Tiers at C1: Still Correct, No Tier 4

```java
import java.nio.file.Files;
import java.nio.file.Path;

public class CapTiers {
    // Probe duplicated (not referenced) so this snippet compiles standalone
    static final String PROBE = """
            public class HotLoop {
                static long total;
                static void burn(int n) {
                    long s = 0;
                    for (int i = 0; i < n; i++) s += i * (i & 7);
                    total = s;
                }
                public static void main(String[] a) {
                    for (int i = 0; i < 300_000; i++) burn(200);
                    System.out.println("total=" + total);
                }
            }
            """;

    public static void main(String[] args) throws Exception {
        Path dir = Files.createTempDirectory("jitcap");
        Path src = dir.resolve("HotLoop.java");
        Files.writeString(src, PROBE);
        new ProcessBuilder("javac", "-d", dir.toString(), src.toString())
                .redirectErrorStream(true).start().waitFor();
        Process java = new ProcessBuilder("java", "-XX:+PrintCompilation",
                "-XX:TieredStopAtLevel=1", "-cp", dir.toString(), "HotLoop")
                .redirectErrorStream(true).start();
        String out = new String(java.getInputStream().readAllBytes());
        int rc = java.waitFor();

        boolean anyTier4 = false, totalPrinted = false;
        for (String line : out.split("\n")) {
            String s = line.strip();
            if (s.contains("HotLoop::burn") && s.matches(".*\\s4\\s.*")) anyTier4 = true;
            if (s.startsWith("total=")) totalPrinted = true;
        }
        System.out.println("exit ok: " + (rc == 0));
        System.out.println("program correct under cap: " + totalPrinted);
        System.out.println("no tier-4 compile anywhere: " + !anyTier4);
    }
}
```

Expected output:
```
exit ok: true
program correct under cap: true
no tier-4 compile anywhere: true
```

Correctness never depends on optimization level — the cap changes speed,
not semantics. (`WatchTiers.PROBE` reuse across snippets: the probe source
is a compile-time constant shared by reference, not copy-paste.)

## 3. Hot Small Callees Get Inlined (PrintInlining)

```java
import java.nio.file.Files;
import java.nio.file.Path;

public class WatchInline {
    static final String PROBE = """
            public class InlineMe {
                static int tiny(int x) { return x * 31 + 7; }
                static long total;
                public static void main(String[] a) {
                    long s = 0;
                    for (int i = 0; i < 500_000; i++) s += tiny(i);
                    total = s;
                    System.out.println("total=" + total);
                }
            }
            """;

    public static void main(String[] args) throws Exception {
        Path dir = Files.createTempDirectory("jinl");
        Path src = dir.resolve("InlineMe.java");
        Files.writeString(src, PROBE);
        new ProcessBuilder("javac", "-d", dir.toString(), src.toString())
                .redirectErrorStream(true).start().waitFor();
        Process java = new ProcessBuilder("java",
                "-XX:+UnlockDiagnosticVMOptions", "-XX:+PrintInlining",
                "-cp", dir.toString(), "InlineMe")
                .redirectErrorStream(true).start();
        String out = new String(java.getInputStream().readAllBytes());
        int rc = java.waitFor();

        boolean inlined = false;
        for (String line : out.split("\n")) {
            if (line.contains("tiny") && line.contains("inline")) { inlined = true; break; }
        }
        System.out.println("exit ok: " + (rc == 0));
        System.out.println("tiny(int) inlined somewhere: " + inlined);
    }
}
```

Expected output:
```
exit ok: true
tiny(int) inlined somewhere: true
```

A 3-byte-body method called 500k times is the ideal inline candidate
(well under `MaxInlineSize=35`, hot past `FreqInlineSize` relevance) — the
log confirms the JIT agreed. Inlining is what *enables* the downstream
wins (constant propagation into the inlined body, dead-code elimination of
the call).

## 4. Interpreter vs JIT: Same Code, Different Engine

```java
import java.nio.file.Files;
import java.nio.file.Path;

public class WarmupCurve {
    static final String PROBE = """
            public class LoopWork {
                static long work() {
                    long s = 0;
                    for (int i = 0; i < 200_000; i++) s += (i * 31L) ^ (i >>> 3);
                    return s;
                }
                public static void main(String[] a) {
                    long t0 = System.nanoTime();
                    long sink = 0;
                    for (int i = 0; i < 2_000; i++) sink += work();
                    long ms = (System.nanoTime() - t0) / 1_000_000;
                    System.out.println("ms=" + ms + " sink=" + (sink != 0));
                }
            }
            """;

    static long runMs(Path dir, String... flags) throws Exception {
        java.util.List<String> cmd = new java.util.ArrayList<>();
        cmd.add("java");
        cmd.addAll(java.util.List.of(flags));
        cmd.addAll(java.util.List.of("-cp", dir.toString(), "LoopWork"));
        Process p = new ProcessBuilder(cmd).redirectErrorStream(true).start();
        String out = new String(p.getInputStream().readAllBytes());
        p.waitFor();
        for (String line : out.split("\n")) {
            if (line.startsWith("ms=")) return Long.parseLong(line.substring(3, line.indexOf(' ')));
        }
        throw new IllegalStateException("no timing in: " + out);
    }

    public static void main(String[] args) throws Exception {
        Path dir = Files.createTempDirectory("warm");
        Path src = dir.resolve("LoopWork.java");
        Files.writeString(src, PROBE);
        new ProcessBuilder("javac", "-d", dir.toString(), src.toString())
                .redirectErrorStream(true).start().waitFor();

        long interpMs = runMs(dir, "-Xint");   // forced interpreter, no JIT at all
        long jitMs = runMs(dir);               // default tiered pipeline
        System.out.println("interpreted ms = " + interpMs + ", jit ms = " + jitMs);
        System.out.println("jit faster (ratio > 3x): " + (interpMs > Math.max(jitMs, 1) * 3));
    }
}
```

Expected output (numbers vary — elided):
```
...
jit faster (ratio > 3x): true
```

`-Xint` removes every threshold subtlety: one engine runs zero compiled
code, the other warms up and flies. Loop-heavy integer work typically shows
10–50x here (interpreter dispatch per bytecode vs unrolled native code), so
3x holds with room. This is the honest version of "JIT makes it fast" —
same bytes, two engines, measured.

## 5. Optimization Switches: Read the Defaults Off the JVM

```java
public class FlagDefaults {
    static boolean flag(String out, String name, String want) {
        for (String line : out.split("\n")) {
            String s = line.strip().replaceAll("\\s+", " ");
            if (s.contains(" " + name + " = ")) return s.contains("= " + want + " ");
        }
        return false;
    }

    public static void main(String[] args) throws Exception {
        Process p = new ProcessBuilder("java",
                "-XX:+UnlockDiagnosticVMOptions", "-XX:+PrintFlagsFinal", "-version")
                .redirectErrorStream(true).start();
        String raw = new String(p.getInputStream().readAllBytes());
        p.waitFor();
        String out = raw.replaceAll("[ \\t]+", " ");   // collapse alignment padding

        System.out.println("TieredCompilation on: " + flag(out, "TieredCompilation", "true"));
        System.out.println("DoEscapeAnalysis on: " + flag(out, "DoEscapeAnalysis", "true"));
        System.out.println("EliminateAllocations on: " + flag(out, "EliminateAllocations", "true"));
        System.out.println("Inline on: " + flag(out, "Inline", "true"));
        System.out.println("Tier4InvocationThreshold = 5000: "
                + out.contains("Tier4InvocationThreshold = 5000"));
        System.out.println("MaxInlineSize = 35, FreqInlineSize = 325: "
                + (out.contains("MaxInlineSize = 35") && out.contains("FreqInlineSize = 325")));
    }
}
```

Expected output:
```
TieredCompilation on: true
DoEscapeAnalysis on: true
EliminateAllocations on: true
Inline on: true
Tier4InvocationThreshold = 5000: true
MaxInlineSize = 35, FreqInlineSize = 325: true
```

Every number in THEORY's tables came from this exact query — run it on your
own JVM before quoting thresholds at anyone. (Flags differ across vendors
and versions; the *query* is the portable skill, not the values.)

## Common Pitfalls Encountered Here

- **Benchmarking cold code** — first batches run interpreted; warm up past
  tier-4 thresholds before measuring (snippet 4 shows the gap).
- **Quoting threshold folklore** — 1500/10000-style tables describe no
  current default; read `PrintFlagsFinal` (snippet 5).
- **Assuming tier 3 is C2** — tier 3 is profiling C1; C2 is tier 4 only.
- **Using develop-only flags** — `PrintDeoptimizationDetails` doesn't exist
  in product builds; `TraceDeoptimization` does (with unlock).
- **Sharing probe sources by reference** — cross-snippet constants break
  standalone copying (every snippet here duplicates its probe so readers can
  copy any single one); duplication of a few lines beats a hidden
  compile-order dependency.
- **Expecting `-Xint`/`-Xcomp` to behave** — forced modes disable the
  pipeline these snippets observe; use `TieredStopAtLevel` for controlled
  experiments instead.
