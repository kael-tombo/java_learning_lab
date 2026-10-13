# Step by Step: Class File Format

## Step 1 — Compile a pinned probe

```bash
mkdir -p /tmp/cff && cd /tmp/cff
cat > V.java <<'EOF'
public class V{}
EOF
javac --release 17 V.java
```

The `--release 17` flag pins major 61. No build tool, no IDE — one
file, one flag, reproducible bytes.

## Step 2 — Dump the first 10 bytes

```bash
xxd -l 10 V.class
# expect: cafe babe 0000 003d ...  (003d = 61)
```

Read bytes 0–3 (magic), 4–5 (minor 0), 6–7 (major), 8–9 (pool count).

## Step 3 — Walk the pool and find a gap

```bash
cat > Probe2.java <<'EOF'
public class Probe2 {
    static final long BIG = 0x1122334455667788L;
    static final int SMALL = 42;
    static final double PI2 = 3.14159265358979;
    static final String S = "hi";
}
EOF
javac --release 17 Probe2.java
javap -v -p Probe2.class | grep -E '^ +#[0-9]+ = (Long|Double|Integer|String)'
```

Locate the `Long` and `Double` lines; confirm the next printed index
skips one (`#12 → #14` pattern). Note which tags (5/6) caused it.

## Step 4 — Decompose a Code header

```bash
cat > Probe3.java <<'EOF'
public class Probe3 {
    int counter;
    int absOrNeg(int x, boolean neg) {
        int y;
        if (neg) { y = -x; } else { y = x < 0 ? -x : x; }
        counter += y;
        return y;
    }
}
EOF
javac --release 17 Probe3.java
javap -v -c -p Probe3.class | grep -A2 'int absOrNeg'
```

Expect `stack=3, locals=4, args_size=3`. Map slots: 0 this, 1 x,
2 neg, 3 y.

## Step 5 — Correlate StackMapTable with merges

```bash
cat > Probe4.java <<'EOF'
public class Probe4 {
    int straight(int x) { return x * 2 + 1; }
    int branchy(int x) { return x < 0 ? -x : x; }
}
EOF
javac --release 17 Probe4.java
javap -v -p Probe4.class | grep -B30 StackMapTable | grep -E 'int (straight|branchy)|StackMapTable'
```

Confirm the attribute sits under `branchy` only. Header, pool, Code,
and frames now all verified from primary evidence — state the four
lab invariants aloud: magic fixed, index 0 phantom, wide entries
double, frames only at merges.
