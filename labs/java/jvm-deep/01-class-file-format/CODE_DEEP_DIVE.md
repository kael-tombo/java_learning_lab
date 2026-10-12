# Class File Format — Code Deep Dive

All snippets run on any JDK 9+ (verified on JDK 23), no dependencies.
Snippets that shell out to `javac`/`javap` assume a JDK (not JRE) on PATH.

## 1. Magic + Version From Raw Bytes

Ten bytes, four fields, zero parsing libraries: the class file is just a
big-endian struct, and `constant_pool_count` includes the phantom index 0
(real entries = count − 1). (The major value itself is toolchain-dependent —
snippet 2 pins exact release→major mappings instead of asserting one here.)

```java
import java.io.InputStream;

public class MagicBytes {
    public static void main(String[] args) throws Exception {
        byte[] b;
        try (InputStream in = MagicBytes.class.getResourceAsStream("/MagicBytes.class")) {
            b = in.readAllBytes();
        }
        long magic = ((b[0] & 0xFFL) << 24) | ((b[1] & 0xFFL) << 16)
                | ((b[2] & 0xFFL) << 8) | (b[3] & 0xFFL);
        int minor = ((b[4] & 0xFF) << 8) | (b[5] & 0xFF);
        int major = ((b[6] & 0xFF) << 8) | (b[7] & 0xFF);
        int poolCount = ((b[8] & 0xFF) << 8) | (b[9] & 0xFF);
        System.out.println("magic is CAFEBABE: " + (magic == 0xCAFEBABEL));
        System.out.println("major = " + major);
        System.out.println("major in valid range [45, 67]: " + (major >= 45 && major <= 67));
        System.out.println("minor = " + minor);
        System.out.println("pool has entries: " + (poolCount > 1));
    }
}
```

Expected output (major line varies by toolchain — elided):
```
magic is CAFEBABE: true
...
major in valid range [45, 67]: true
minor = 0
pool has entries: true
```

Ten bytes, four fields, zero parsing libraries: the class file is just a
big-endian struct, and `constant_pool_count` includes the phantom index 0
(real entries = count − 1).

## 2. Release Flag Selects Major Version Exactly

```java
import java.nio.file.Files;
import java.nio.file.Path;

public class ReleaseToMajor {
    static int majorOf(String release) throws Exception {
        Path dir = Files.createTempDirectory("rel");
        Path src = dir.resolve("V.java");
        Files.writeString(src, "public class V{}");
        Process p = new ProcessBuilder("javac", "--release", release, src.toString())
                .redirectErrorStream(true).start();
        if (p.waitFor() != 0) throw new IllegalStateException("javac failed");
        byte[] b = Files.readAllBytes(dir.resolve("V.class"));
        return ((b[6] & 0xFF) << 8) | (b[7] & 0xFF);
    }

    public static void main(String[] args) throws Exception {
        int r8 = majorOf("8"), r17 = majorOf("17"), r21 = majorOf("21");
        System.out.println("8->" + r8 + " 17->" + r17 + " 21->" + r21);
        System.out.println("mapping exact (52/61/65): "
                + (r8 == 52 && r17 == 61 && r21 == 65));
    }
}
```

Expected output:
```
8->52 17->61 21->65
mapping exact (52/61/65): true
```

No table lookup, no memory: three compilations pin three rows of the
version table empirically. (A JVM rejects newer-than-itself majors with
`UnsupportedClassVersionError` — the forward-compat boundary.)

## 3. Long/Double Eat Two Pool Slots

```java
import java.nio.file.Files;
import java.nio.file.Path;

public class PoolGap {
    static final String PROBE = """
            public class Probe2 {
                static final long BIG = 0x1122334455667788L;
                static final int SMALL = 42;
                static final double PI2 = 3.14159265358979;
                static final String S = "hi";
            }
            """;

    public static void main(String[] args) throws Exception {
        Path dir = Files.createTempDirectory("pool");
        Path src = dir.resolve("Probe2.java");
        Files.writeString(src, PROBE);
        new ProcessBuilder("javac", "--release", "17", src.toString())
                .redirectErrorStream(true).start().waitFor();
        Process javap = new ProcessBuilder("javap", "-v", "-p",
                dir.resolve("Probe2.class").toString())
                .redirectErrorStream(true).start();
        String out = new String(javap.getInputStream().readAllBytes());
        javap.waitFor();

        java.util.Set<Integer> present = new java.util.HashSet<>();
        int longIdx = -1, doubleIdx = -1;
        for (String line : out.split("\n")) {
            String s = line.strip();
            if (s.startsWith("#")) {
                int idx = Integer.parseInt(s.substring(1, s.indexOf('=')).trim());
                present.add(idx);
                if (s.contains("= Long")) longIdx = idx;
                if (s.contains("= Double")) doubleIdx = idx;
            }
        }
        System.out.println("Long entry found: " + (longIdx > 0));
        System.out.println("Double entry found: " + (doubleIdx > 0));
        System.out.println("slot after Long missing: " + !present.contains(longIdx + 1));
        System.out.println("slot after Double missing: " + !present.contains(doubleIdx + 1));
    }
}
```

Expected output:
```
Long entry found: true
Double entry found: true
slot after Long missing: true
slot after Double missing: true
```

The pool layout (exact indices like `#12`/`#19`) is deterministic for fixed
source+release but not contractual — so the snippet asserts only the
structural fact (the gap) and reports booleans, never indices.

## 4. Code Attribute: max_stack / max_locals Are Compiler-Computed

```java
import java.nio.file.Files;
import java.nio.file.Path;

public class CodeAttr {
    static final String PROBE = """
            public class Probe3 {
                int counter;
                int absOrNeg(int x, boolean neg) {
                    int y;
                    if (neg) { y = -x; } else { y = x < 0 ? -x : x; }
                    counter += y;
                    return y;
                }
            }
            """;

    public static void main(String[] args) throws Exception {
        Path dir = Files.createTempDirectory("code");
        Path src = dir.resolve("Probe3.java");
        Files.writeString(src, PROBE);
        new ProcessBuilder("javac", "--release", "17", src.toString())
                .redirectErrorStream(true).start().waitFor();
        Process javap = new ProcessBuilder("javap", "-v", "-c", "-p",
                dir.resolve("Probe3.class").toString())
                .redirectErrorStream(true).start();
        String out = new String(javap.getInputStream().readAllBytes());
        javap.waitFor();

        String header = null;
        boolean inMethod = false;
        for (String line : out.split("\n")) {
            if (line.contains("int absOrNeg")) inMethod = true;
            else if (inMethod && line.trim().startsWith("stack=")) {
                header = line.trim();
                break;
            }
        }
        System.out.println("Code header: " + header);
        System.out.println("stack=3 locals=4 (this+x+neg+y): "
                + "stack=3, locals=4, args_size=3".equals(header));
        System.out.println("branch instructions present: "
                + (out.contains("ifeq") && out.contains("goto")));
    }
}
```

Expected output:
```
Code header: stack=3, locals=4, args_size=3
stack=3 locals=4 (this+x+neg+y): true
branch instructions present: true
```

`locals=4` decomposes exactly: slot 0 `this`, 1 `x`, 2 `neg`, 3 `y` —
`args_size=3` is the receiver plus parameters. The verifier re-checks these
numbers at load time; a hand-edited class claiming `stack=1` dies with
`VerifyError`.

## 5. StackMapTable Appears Exactly Where Control Flow Merges

```java
import java.nio.file.Files;
import java.nio.file.Path;

public class StackMaps {
    static final String PROBE = """
            public class Probe4 {
                int straight(int x) { return x * 2 + 1; }
                int branchy(int x) { return x < 0 ? -x : x; }
            }
            """;

    public static void main(String[] args) throws Exception {
        Path dir = Files.createTempDirectory("smt");
        Path src = dir.resolve("Probe4.java");
        Files.writeString(src, PROBE);
        new ProcessBuilder("javac", "--release", "17", src.toString())
                .redirectErrorStream(true).start().waitFor();
        Process javap = new ProcessBuilder("javap", "-v", "-p",
                dir.resolve("Probe4.class").toString())
                .redirectErrorStream(true).start();
        String out = new String(javap.getInputStream().readAllBytes());
        javap.waitFor();

        // split verbose output per method: straight has no jumps, branchy does
        int straightAt = out.indexOf("int straight(");
        int branchyAt = out.indexOf("int branchy(");
        String straightSeg = out.substring(straightAt, branchyAt);
        String branchySeg = out.substring(branchyAt);
        System.out.println("straight-line method has StackMapTable: "
                + straightSeg.contains("StackMapTable"));
        System.out.println("branching method has StackMapTable: "
                + branchySeg.contains("StackMapTable"));
        System.out.println("frames only where merges exist: "
                + (!straightSeg.contains("StackMapTable") && branchySeg.contains("StackMapTable")));
    }
}
```

Expected output:
```
straight-line method has StackMapTable: false
branching method has StackMapTable: true
frames only where merges exist: true
```

Split verification in one picture: `javac` pre-computes types at merge
points so the verifier checks instead of inferring. No branches → no
merges → no table.

## Common Pitfalls Encountered Here

- **Parsing the pool with +1 steps** — Long/Double take two slots; every
  hand parser must skip (snippet 3).
- **Assuming `javap` numbering is dense** — it isn't, by spec (same cause).
- **Trusting major version from memory** — compile with explicit `--release`
  and read bytes 6–7 (snippet 2); the table in THEORY was built that way.
- **Editing `max_stack` by hand** — the verifier recomputes reachability;
  mismatches are `VerifyError`, not silent corruption.
- **Expecting StackMapTable everywhere** — straight-line code has no frames
  (snippet 5); its absence is normal, not a `-g:none` artifact.
- **Reading `minor_version` as meaningful** — invariably 0 for `javac`
  output; only exotic producers set it.
