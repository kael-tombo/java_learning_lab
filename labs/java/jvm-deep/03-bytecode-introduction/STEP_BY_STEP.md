# Step by Step: Bytecode Introduction

## Step 1 — Read stack arithmetic

```bash
mkdir -p /tmp/bc && cd /tmp/bc
cat > Arith.java <<'EOF'
public class Arith {
    int add3(int a, int b, int c) { return a + b + c; }
}
EOF
javac --release 17 Arith.java
javap -c -p Arith.class
```

Expect `iload_1, iload_2, iadd, iload_3, iadd, ireturn`. Track stack
depth per line: 0→1→2→1→2→1→0. Note associativity in the order.

## Step 2 — Collect all five invokes

```bash
cat > Calls.java <<'EOF'
import java.util.List;
public class Calls {
    static int stat() { return 1; }
    private int priv() { return 2; }
    int virt() { return priv() + stat(); }
    int iface(List<String> l) { return l.size(); }
    Runnable lam() { return () -> System.out.println("x"); }
}
EOF
javac --release 17 Calls.java
javap -c -p Calls.class | grep -o 'invoke[a-z]*' | sort | uniq -c
```

Expect all five modes present. Map each hit to its source line:
which callee kind selected which instruction?

## Step 3 — Read descriptors

```bash
cat > Sigs.java <<'EOF'
import java.util.List;
public class Sigs {
    public static void main(String[] argv) { }
    int add(int a, int b) { return a + b; }
    String concat(String a, String b) { return a + b; }
    List<String> get() { return null; }
}
EOF
javac --release 17 Sigs.java
javap -s -p Sigs.class
```

Confirm `([Ljava/lang/String;)V`, `(II)I`, the two-`String`
descriptor, and erased `()Ljava/util/List;`.

## Step 4 — Run a handle end to end

Write `HandleSqrt` (CODE_DEEP_DIVE snippet 4): `findStatic` for
`Math.sqrt`, `invokeExact(4.0)` → 2.0, then the wrong-type call.

## Step 5 — Show lambda linkage

```bash
cat > Lam.java <<'EOF'
public class Lam {
    Runnable r = () -> System.out.println("hello");
    int n = 0;
    void bump() { Runnable inc = () -> n++; inc.run(); inc.run(); }
}
EOF
javac --release 17 Lam.java
javap -v -c -p Lam.class | grep -c invokedynamic
javap -v -p Lam.class | grep -o 'LambdaMetafactory.metafactory' | head -1
javap -p Lam.class | grep 'lambda\$'
```

Expect 2 sites, the metafactory bootstrap, and synthetic bodies.
State the linkage-vs-allocation distinction aloud before finishing.
