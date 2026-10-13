# Refactoring: Final Field Semantics

## 1. Store first, publish last

Before:

```java
Leaky() {
    published = this;
    this.x = v;
}
```

After:

```java
Leaky(int v) {
    this.x = v;
    // publish only after ALL stores, or preferably outside entirely
}
static Leaky create(int v) {
    Leaky l = new Leaky(v);
    published = l;
    return l;
}
```

The freeze must precede every publication. Factory methods make the
ordering structural instead of conventional.

## 2. Final-ify snapshot state

Before:

```java
class Holder { int a; String s; int[] arr; ... }
```

After:

```java
class Holder {
    final int a;
    final String s;
    final int[] arr;
    Holder(int a, String s) {
        this.a = a;
        this.s = s;
        this.arr = new int[]{a, a + 1};
    }
}
```

Non-final snapshot fields convert a theorem into weather. Mark every
construction-fixed field `final` so the freeze covers it.

## 4. Defensive-copy mutable inputs

Before:

```java
Holder(int[] ext) { this.arr = ext; }   // alias: caller can mutate
```

After:

```java
Holder(int[] ext) { this.arr = ext.clone(); }
```

Or accept a `List` and store `List.copyOf(ext)`. The transitive rule
protects only storage built inside construction.
