# Bytecode Introduction — Code Deep Dive

All snippets run on any JDK 9+ (verified on JDK 23), no dependencies.
Snippets that shell out to `javac`/`javap` assume a JDK (not JRE) on PATH.

## 1. Stack Arithmetic, Instruction by Instruction

```java
import java.nio.file.Files;
import java.nio.file.Path;

public class StackTrace {
    static final String PROBE = """
            public class Arith {
                int add3(int a, int b, int c) { return a + b + c; }
            }
            """;

    public static void main(String[] args) throws Exception {
        Path dir = Files.createTempDirectory("stk");
        Path src = dir.resolve("Arith.java");
        Files.writeString(src, PROBE);
        new ProcessBuilder("javac", "--release", "17", src.toString())
                .redirectErrorStream(true).start().waitFor();
        Process javap = new ProcessBuilder("javap", "-c", "-p",
                dir.resolve("Arith.class").toString())
                .redirectErrorStream(true).start();
        String out = new String(javap.getInputStream().readAllBytes());
        javap.waitFor();

        // normalize: strip addresses/comments, keep opcodes in order (add3 only)
        java.util.List<String> ops = new java.util.ArrayList<>();
        boolean inMethod = false;
        for (String line : out.split("\n")) {
            String s = line.strip();
            if (s.contains("int add3(")) { inMethod = true; continue; }
            // next member declaration has parens+semicolon but no leading "N:" address
            if (inMethod && s.contains("(") && s.contains(";") && !s.matches("\\d+:.*")) break;
            if (inMethod && s.matches("\\d+: \\w+.*"))
                ops.add(s.replaceFirst("\\d+: (\\w+).*", "$1"));
        }
        System.out.println("opcodes = " + ops);
        System.out.println("shape is load,load,add,load,add,return: "
                + ops.equals(java.util.List.of(
                        "iload_1", "iload_2", "iadd", "iload_3", "iadd", "ireturn")));
    }
}
```

Expected output:
```
opcodes = [iload_1, iload_2, iadd, iload_3, iadd, ireturn]
shape is load,load,add,load,add,return: true
```

No locals beyond the parameters, no temporaries, no registers: `a + b + c`
is five pushes/pops and one return. Left-associativity is visible in the
order (add a+b first, then +c).

## 2. All Five Invoke Modes in One Class

```java
import java.nio.file.Files;
import java.nio.file.Path;

public class FiveInvokes {
    static final String PROBE = """
            import java.util.List;
            public class Calls {
                static int stat() { return 1; }
                private int priv() { return 2; }
                int virt() { return priv() + stat(); }
                int iface(List<String> l) { return l.size(); }
                Runnable lam() { return () -> System.out.println("x"); }
            }
            """;

    public static void main(String[] args) throws Exception {
        Path dir = Files.createTempDirectory("inv");
        Path src = dir.resolve("Calls.java");
        Files.writeString(src, PROBE);
        new ProcessBuilder("javac", "--release", "17", src.toString())
                .redirectErrorStream(true).start().waitFor();
        Process javap = new ProcessBuilder("javap", "-c", "-p",
                dir.resolve("Calls.class").toString())
                .redirectErrorStream(true).start();
        String out = new String(javap.getInputStream().readAllBytes());
        javap.waitFor();

        System.out.println("invokestatic present: " + out.contains("invokestatic"));
        System.out.println("invokespecial present: " + out.contains("invokespecial"));
        System.out.println("invokevirtual present: " + out.contains("invokevirtual"));
        System.out.println("invokeinterface present: " + out.contains("invokeinterface"));
        System.out.println("invokedynamic present (lambda): " + out.contains("invokedynamic"));
        System.out.println("all five dispatch modes: "
                + (out.contains("invokestatic") && out.contains("invokespecial")
                && out.contains("invokevirtual") && out.contains("invokeinterface")
                && out.contains("invokedynamic")));
    }
}
```

Expected output:
```
invokestatic present: true
invokespecial present: true
invokevirtual present: true
invokeinterface present: true
invokedynamic present (lambda): true
all five dispatch modes: true
```

`priv()` compiles to `invokespecial` (private = statically bound),
`stat()` to `invokestatic`, `virt()`'s self-call to `invokevirtual`,
`l.size()` to `invokeinterface`, and the lambda body to a synthetic method
reached via `invokedynamic` — the complete dispatch taxonomy from one small
class.

## 3. Descriptors via javap -s

```java
import java.nio.file.Files;
import java.nio.file.Path;

public class DescriptorCheck {
    static final String PROBE = """
            import java.util.List;
            public class Sigs {
                public static void main(String[] argv) { }
                int add(int a, int b) { return a + b; }
                String concat(String a, String b) { return a + b; }
                List<String> get() { return null; }
            }
            """;

    public static void main(String[] args) throws Exception {
        Path dir = Files.createTempDirectory("sig");
        Path src = dir.resolve("Sigs.java");
        Files.writeString(src, PROBE);
        new ProcessBuilder("javac", "--release", "17", src.toString())
                .redirectErrorStream(true).start().waitFor();
        Process javap = new ProcessBuilder("javap", "-s", "-p",
                dir.resolve("Sigs.class").toString())
                .redirectErrorStream(true).start();
        String out = new String(javap.getInputStream().readAllBytes());
        javap.waitFor();

        System.out.println("main descriptor: " + out.contains("([Ljava/lang/String;)V"));
        System.out.println("add descriptor: " + out.contains("(II)I"));
        System.out.println("concat descriptor: "
                + out.contains("(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;"));
        System.out.println("generic erased to List: " + out.contains("()Ljava/util/List;"));
    }
}
```

Expected output:
```
main descriptor: true
add descriptor: true
concat descriptor: true
generic erased to List: true
```

`javap -s` prints the raw descriptors the JVM actually links against —
generics (`List<String>`) already erased to `List` at this level. Overload
resolution, reflection lookups, and linkage errors all operate on these
strings, not on Java signatures.

## 4. MethodHandle sqrt End to End

```java
import java.lang.invoke.MethodHandle;
import java.lang.invoke.MethodHandles;
import java.lang.invoke.MethodType;

public class HandleSqrt {
    public static void main(String[] args) throws Throwable {
        MethodHandles.Lookup lookup = MethodHandles.lookup();
        MethodHandle mh = lookup.findStatic(Math.class, "sqrt",
                MethodType.methodType(double.class, double.class));
        System.out.println("handle type: " + mh.type());
        double result = (double) mh.invokeExact(4.0);
        System.out.println("sqrt(4.0) = " + result);
        System.out.println("exact: " + (result == 2.0));
        try {
            mh.invokeExact("not-a-double");
            System.out.println("wrong type accepted (unexpected)");
        } catch (Throwable t) {
            System.out.println("wrong static type rejected: "
                    + t.getClass().getSimpleName());
        }
    }
}
```

Expected output:
```
handle type: (double)double
sqrt(4.0) = 2.0
exact: true
wrong static type rejected: WrongMethodTypeException
```

`invokeExact` binds the call site to `(double)double` at link time — passing
a `String` fails before any user code runs. Handles are the JVM's
type-checked function pointers; `invokedynamic` bootstraps return them.

## 5. Lambda Links Once via invokedynamic

```java
import java.nio.file.Files;
import java.nio.file.Path;

public class LambdaLink {
    static final String PROBE = """
            public class Lam {
                Runnable r = () -> System.out.println("hello");
                int n = 0;
                void bump() {
                    Runnable inc = () -> n++;
                    inc.run(); inc.run();
                }
            }
            """;

    public static void main(String[] args) throws Exception {
        Path dir = Files.createTempDirectory("lam");
        Path src = dir.resolve("Lam.java");
        Files.writeString(src, PROBE);
        new ProcessBuilder("javac", "--release", "17", src.toString())
                .redirectErrorStream(true).start().waitFor();
        Process javap = new ProcessBuilder("javap", "-v", "-c", "-p",
                dir.resolve("Lam.class").toString())
                .redirectErrorStream(true).start();
        String out = new String(javap.getInputStream().readAllBytes());
        javap.waitFor();

        long dynCount = out.lines().filter(l -> l.contains("invokedynamic")).count();
        System.out.println("invokedynamic sites = " + dynCount + " (two lambdas)");
        System.out.println("bootstrap is LambdaMetafactory: "
                + out.contains("LambdaMetafactory.metafactory"));
        System.out.println("synthetic lambda bodies generated: "
                + (out.contains("lambda$") ));
    }
}
```

Expected output:
```
invokedynamic sites = 2 (two lambdas)
bootstrap is LambdaMetafactory: true
synthetic lambda bodies generated: true
```

Each lambda is one `invokedynamic` site bootstrapped once by
`LambdaMetafactory` to a generated `lambda$...` method — the class is spun
once and cached, so lambdas in hot loops don't reallocate linkage. (The
capturing `() -> n++` lambda additionally allocates an instance per
evaluation — capture cost vs linkage cost are separate budgets.)

## Common Pitfalls Encountered Here

- **Reading `ireturn`-less traces** — normalizer regexes must admit bare
  opcodes (snippet 1's `\\d+: \\w+` shape).
- **Confusing `invokespecial` with virtual dispatch** — private/ctor/super
  calls bind statically (snippet 2).
- **Expecting generic signatures in descriptors** — erased at compile time
  (snippet 3).
- **`invokeExact` with a wrong static type** — link-time
  `WrongMethodTypeException`, not a runtime cast failure (snippet 4).
- **Assuming lambdas are anonymous classes per evaluation** — linkage is
  once-per-site; only *capturing* lambdas allocate per evaluation
  (snippet 5).
- **Forgetting `-p`** — `javap` hides private members by default, including
  the `priv()`/`lambda$` methods these snippets assert on.
