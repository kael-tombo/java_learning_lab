# Quiz: Class Loading

## Q1: Print the JDK 9+ loader chain from a program. What do you expect?
**A:** System loader named "app", platform loader named "platform",
`String.class.getClassLoader()` null; `app.getParent() == platform`
true, `platform.getParent() == null` true. No extension loader.

## Q2: What happened to the extension classloader, and when?
**A:** Removed with JDK 9 modularization (JEP 220). `java.ext.dirs`
is ignored; its domain is covered by the platform loader.

## Q3: After `loader.loadClass("P")` with no `<clinit>` output, then `Class.forName("P")` with `<clinit>` output — explain both.
**A:** `loadClass` loads and links without initializing (silence is
correct). `forName` initializes by default, running `<clinit>`. Same
`Class` object both times — one load, two phases.

## Q4: Two loaders define identical Widget bytes; `w2.cast(o1)` throws. Why?
**A:** Identity is (name, defining loader). `w1 != w2` as `Class`
objects, so the verifier rejects the cast despite identical names.

## Q5: Reading `Config.PORT` (`static final int = 8080`) prints with no `<clinit>` line, but reading `Config.computed` triggers it. Why?
**A:** `PORT` is a compile-time constant inlined via `ConstantValue`
at client-compile time — not an active use (JLS §12.4). The computed
field requires initialization.

## Q6: Custom loader: which method do you override, and what error follows defining twice?
**A:** Override `findClass` (fetch bytes, `defineClass`); inherit
`loadClass` to keep parent-first delegation. Defining one binary
name twice in a loader is `LinkageError: duplicate class definition`.

## Q7: Name the three linking sub-steps and one failure of each.
**A:** Verification (`VerifyError`), preparation (no user failure —
zeroing only), resolution (`NoSuchMethodError` on version skew,
surfaced lazily at first use).

## Q8: Platform-layer code cannot load an app class by delegation. How does it reach one?
**A:** Through `Thread.currentThread().getContextClassLoader()` —
the down-channel. Delegation looks up only; the context loader
looks down.

## Q9: What does `super(null)` mean in the SplitIdentity DirLoader?
**A:** Bootstrap-only delegation: JDK classes still resolve
(bootstrap provides `java.lang.Object`) while `Widget` stays fully
loader-local — total isolation for the demonstration.

## Q10: When does `<clinit>` run, and under what concurrency guarantee?
**A:** On first active use (new, static invoke, non-constant static
access, default forName, subclass init parent-first). Exactly once
per (name, loader), under a JVM-held initialization lock.
