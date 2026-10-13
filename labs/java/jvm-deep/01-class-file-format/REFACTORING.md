# Refactoring: Class File Format

Refactoring here means restructuring how your code *emits* class-file
structures — fewer merges, cleaner constants, smaller pools.

## 1. Collapse branches to drop frames

Before (two merges, two frame sites):

```java
int sign(int x) {
    int r;
    if (x < 0) r = -1; else if (x > 0) r = 1; else r = 0;
    return r;
}
```

After (one expression, fewer joins):

```java
int sign(int x) {
    return Integer.compare(x, 0);
}
```

Effect: fewer `StackMapTable` frames, smaller `Code`, single merge.
Confirm with `javap -v`: frame count tracks merge count.

## 2. Hoist constants into ConstantValue fields

Before (literal repeated at 6 sites):

```java
if (code == 8080) ...   // + 5 more sipush 8080 sites
```

After (one pool entry, inlined everywhere):

```java
static final int PORT = 8080;
if (code == PORT) ...
```

Effect: one `Integer`/`ConstantValue` entry referenced 6 times.
Remember the rebuild rule: changing `PORT` requires recompiling clients.

## 3. Replace synthetic-accessor patterns with nests

Before (Java 8 style, accessor bridges):

```java
public class Outer {
    private static int secret;
    static class Inner {
        int peek() { return Outer.secret; }  // bridge method pre-11
    }
}
```

After: the same source on `--release 17` emits `NestHost`/
`NestMembers` instead of bridges. Verify: `javap -v` shows `NestHost`,
no `access$000` synthetic method.

## 4. Split branchy methods for verification locality

Before (one 400-line method, 30 merges — a `VerifyError` somewhere
inside is painful to localize):

```java
int process(int x) { /* 30 branches */ }
```

After (extract each decision region):

```java
int process(int x) { return step1(x) + step2(x); }
```

Effect: per-method `max_stack`/`max_locals` shrink, frames partition
per method, and `javap -c` output becomes diffable.
