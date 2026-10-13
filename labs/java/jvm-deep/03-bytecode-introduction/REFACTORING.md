# Refactoring: Bytecode Introduction

## 1. Collapse double dispatch into one invokeinterface

Before (two lookups, concrete coupling):

```java
int n = list.size() + list.size();   // two invokeinterface sites
```

After (one site, one lookup shape):

```java
int n = list.size();
int total = n + n;
```

Effect: half the interface lookups; the JIT profiles one site
instead of splitting history across two. Trivial, and exactly the
kind of win `javap -c` makes visible.

## 2. Hoist capturing lambdas out of hot loops

Before (allocation per iteration):

```java
for (int i = 0; i < n; i++) run(() -> store(i));  // captures i: allocs
```

After (capture once):

```java
IntConsumer c = store::add;         // one invokedynamic linkage, one instance
for (int i = 0; i < n; i++) c.accept(i);
```

Effect: linkage was already once-per-site; this removes the
per-evaluation capture allocation snippet 5 distinguishes from
linkage. Non-capturing lambdas need no such hoist (singleton).

## 3. Replace megamorphic interface calls with a switch on type

Before (itable probe per call, megamorphic after 3+ receivers):

```java
int sum(List<Shape> ss) { int t = 0; for (Shape s : ss) t += s.area(); return t; }
```

After (profile-friendly, devirtualizable arms):

```java
int sum(List<Shape> ss) { int t = 0; for (Shape s : ss) t += areaOf(s); return t; }
static int areaOf(Shape s) {
    if (s instanceof Circle c) return c.circleArea();
    if (s instanceof Rect r) return r.rectArea();
    return s.area();
}
```

Effect: arms dispatch on final-class targets the JIT inlines;
pattern variables keep it readable (Java 17+).

## 4. Trade narrowing conversions for wider locals

Before (silent truncation risk + conversion ops):

```java
byte b = (byte) (a + c);   // iadd, i2b, istore
```

After (widen the computation, narrow once at the boundary):

```java
int sum = a + c;           // stays int through hot path
sink((byte) sum);          // single narrowing at the edge
```

Effect: fewer `i2b/i2c` ops in hot code, truncation audited at one
site instead of scattered casts.
