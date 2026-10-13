# Visual Guide: Class Loading

## The tree (JDK 9+, measured)

```text
 bootstrap (null)   String.class.getClassLoader() == null
     ▲
     | parent (null)
 platform ("platform")   java.sql, java.xml, ...
     ▲
     | parent == platform
   app ("app")      your classes, -cp / -p
```

No extension rung. Pre-9 drawings with one describe Java 8.

## Delegation walk for loadClass("Widget")

```text
app.loadClass("Widget")
  -> platform.loadClass("Widget")
       -> bootstrap search: MISS
     <- MISS
  -> app.findClass: read bytes, defineClass -> Class(Widget, app)
```

For `java.lang.String` the walk stops at bootstrap — HIT, app bytes
never consulted.

## Phases on a timeline

```text
t0 load:      bytes -> defineClass -> Class object
t0 link:      verify (frames) -> prepare (zero statics) -> resolve (lazy)
t1 first use: <clinit> ONCE under init lock (superclass first)
t2+ uses:     no loading, no linking, no init — direct execution
constants:    ConstantValue path skips t1 entirely (inlined at compile)
```

## Identity split (SplitIdentity)

```text
Widget.class bytes (one file)
   |-- DirLoader L1.defineClass --> Class W1 (loader L1, statics S1)
   +-- DirLoader L2.defineClass --> Class W2 (loader L2, statics S2)
W1 != W2;  new W1() uncastable to W2  (ClassCastException)
```

## Context loader down-channel

```text
platform code (DocumentBuilderFactory)
   delegation UP only:  platform -> bootstrap  (app invisible)
   context DOWN:        ctx (== app) -> sees Widget, app.xml
```

## Failure-to-phase map

```text
ClassNotFoundException      load      (bytes absent)
VerifyError/ClassFormatError link/verify (bad bytes)
NoSuchMethodError            link/resolve (version skew, lazy)
ExceptionInInitializerError  init      (<clinit> threw)
NoClassDefFoundError         init-failed-earlier (erroneous mark)
```
