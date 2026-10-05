# Exercises — Reflection & Annotations (10 hands-on)

## E1 — Class Forensics
```java
Class<?> c = Class.forName("java.util.ArrayList");
for (var m : c.getDeclaredMethods()) System.out.println(m);
```
Tasks: list fields/ctors; `getMethods` vs `getDeclaredMethods`.

## E2 — setAccessible + opens
Tasks: read private field; fix `InaccessibleObjectException` with `--add-opens`.

## E3 — Custom Annotation
```java
@Retention(RUNTIME) @Target(METHOD) @interface Timed {}
// scan methods, time invoke
```
Tasks: retention/target matrix; missing RUNTIME → invisible demo.

## E4 — Proxy Logging
```java
Proxy.newProxyInstance(cl, new Class[]{Svc.class}, (p,m,a) -> m.invoke(target,a));
```
Tasks: add timing + exception path.

## E5 — MethodHandles vs Reflection
```java
MethodHandles.lookup().findVirtual(Svc.class, "go", MethodType.methodType(void.class));
```
Tasks: bench 1M invokes; flags `-XX:+PrintInlining`.

## E6 — Annotation Processor (compile-time)
Tasks: `@Builder`-like processor generating `XBuilder`; verify `javac -processor`.

## E7 — JSON Mini-Mapper
Tasks: serialize record via getters; handle null/nested; no libs.

## E8 — DI Mini-Container
Tasks: `@Inject` ctor + `@Singleton` scope; cycle detection error.

## E9 — Security Sandbox
Tasks: deny `setAccessible` on `java.*` via allowlist; log violations.

## E10 — Capstone: Validator
Tasks: `@NotNull @Min(3)` on fields → `validate(Object)` errors list.
Flags: `-Xmx256m`. Checklist: opens documented, hot path uses handles.
