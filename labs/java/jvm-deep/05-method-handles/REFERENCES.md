# References: Method Handles

## Specifications

- JSR 292 — *Supporting Dynamically Typed Languages on the Java
  Platform* (Java 7): `invokedynamic`, method handles, `MethodHandle`/
  `MethodType` semantics, bootstrap linkage. The origin document.
- JVMS SE 23, §4.4 — pool tags `MethodHandle=15`, `MethodType=16`,
  `Dynamic=17`, `InvokeDynamic=18`; §4.7.23 — `BootstrapMethods`.
- JVMS SE 23, §5.4.3/§6.5 — `invokedynamic` resolution and execution;
  §5.4 — lazy resolution (failures at first use).
- JLS 17, §15.12 — method invocation expressions (the source-level
  dispatch `invokespecial`/`invokevirtual` compile from).

## JEPs (enhancements, not origins)

- JEP 274 — *Enhanced Method Handles* (Java 9): new combinators,
  loop/finally support, `arrayConstructor`. Enhancement of JSR 292.
- JEP 280 — *Indify String Concatenation* (Java 9): production
  `invokedynamic` use via `StringConcatFactory`.
- JEP 361-adjacent (switch expressions, 14) and record/pattern work
  build linkage atop the same substrate — current atop-work, not
  replacements.

## JDK API and source

- `java.lang.invoke` package Javadoc: `MethodHandles` (lookup +
  `Lookup`), `MethodHandle` (`invokeExact`/`invoke`/`asType`,
  `bindTo`), `MethodType`, `CallSite`/`ConstantCallSite`/
  `MutableCallSite`/`VolatileCallSite`.
- `java.lang.invoke.LambdaMetafactory` — the lambda/string bootstrap
  used by every `invokedynamic` in this module's dumps.
- OpenJDK source: `src/java.base/share/classes/java/lang/invoke/`
  (handles, combinators, call sites),
  `src/hotspot/share/interpreter/linkResolver.cpp` (linkage +
  `WrongMethodTypeException` origins).

## Reading order

JSR 292 specification (linkage model) first, then the
`java.lang.invoke` package Javadoc (lookup/combinator/callsite
reference), then the five CODE_DEEP_DIVE probes as the runnable
index. JEP 274 last — as the enhancement delta, in its proper place.
