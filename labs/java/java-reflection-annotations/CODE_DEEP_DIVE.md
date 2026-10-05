# Code Deep Dive — Reflection & Annotations

## 1. Source Tour
- `java.lang.Class`, `Method::invoke`, `Field::get` (java.base).
- `jdk.internal.reflect.NativeMethodAccessorImpl` vs `MethodAccessorGenerator`.
- `java.lang.invoke.MethodHandles`, `DelegatingMethodHandle`.

## 2. Bytecode: Annotation Retention
```java
@Retention(RUNTIME) @interface T {}
```
`javap -v` shows `RuntimeVisibleAnnotations` vs `RuntimeInvisibleAnnotations`.
CLASS retention → invisible; SOURCE → absent.

## 3. Inflation Path
First 15 `Method.invoke` → native; then generated `GeneratedMethodAccessor`.
Flags: `-Dsun.reflect.inflationThreshold=0 -Dsun.reflect.noInflation=true` to compare.
Bench with JMH; handles win on hot loops.

## 4. Proxy Bytecode
`Proxy.newProxyInstance` generates `$Proxy0` implementing ifaces, delegating to handler.
Dump: `-Djdk.proxy.ProxyGenerator.saveGeneratedFiles=true`, `javap -c $Proxy0`.

## 5. setAccessible Gate
`AccessibleObject::checkCanSetAccessible` → module `opens` check.
Fail → `InaccessibleObjectException`; fix `--add-opens java.base/java.util=ALL-UNNAMED`.

## 6. MethodHandle Intrinsic
`mh.invokeExact` is signature-polymorphic (no `invokevirtual` in bytecode sense).
JIT inlines to direct call; `-XX:+PrintIntrinsics` confirms.

## 7. Processor Debugging
```bash
javac -processor com.gen.BProc -XprintRounds -XprintProcessorInfo src/*.java
```
Filer outputs to `target/generated-sources`; inspect + `javap`.

## 8. Profiling Reflect
JFR `jdk.JavaMonitorEnter` + stack on `Method.invoke`; async-profiler flame shows handler frames.
Rule: cache Method/Handle, avoid varargs alloc (pass `new Object[]{}` reuse).

## 9. HotSpot Refs
`reflection.cpp`, `methodHandles.cpp`; `Class::isAccessibleTo` for modules.
