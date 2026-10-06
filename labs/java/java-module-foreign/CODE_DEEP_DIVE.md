# Code Deep Dive — Foreign Function & Memory

## 1. Source Tour
- `java.lang.foreign.Arena`, `MemorySegment`, `Linker` (java.base).
- Native: `libpanama` downcall stubs generated per descriptor.
- OpenJDK: `src/java.base/share/classes/java/lang/foreign/`.

## 2. Bytecode: Downcall
```java
mh.invokeExact(segment);
```
`javap -c` shows `invokevirtual MethodHandle.invokeExact` → intrinsic, no varargs box.
Flags: `-XX:+PrintIntrinsics` shows `MethodHandle` inline.

## 3. Arena Close Path
`Arena.ofConfined().close()` → frees all segments bulk, invalidates liveness bit.
Use-after-close → `IllegalStateException`, not segfault (safety win).

## 4. Layout VarHandle
```java
VarHandle x = point.varHandle(PathElement.groupElement("x"));
```
JIT folds offset math to constant + base. Inspect with `-XX:+PrintAssembly` (hsdis).

## 5. Upcall Stub Lifetime
`linker.upcallStub(handle, desc, arena)` allocates executable stub in arena.
If arena closes early → native call jumps to freed code → crash. Keep arena open!

## 6. mapFile Internals
`MemorySegment.mapFile` → `mmap` + segment with unmap-Cleaner on arena close.
Contrast MappedByteBuffer (Cleaner.invokeCleaner hack).

## 7. Restricted Methods Gate
`MemorySegment::reinterpret`, `Linker::downcallHandle` require `--enable-native-access`.
Without flag → `IllegalCallerException`. Audit with `jdeps --check`.

## 8. Profiling Native
```bash
jcmd <pid> VM.native_memory detail
pmap -x <pid> | grep anon
perf record -g java ... ; perf report
```

## 9. Common Crash Triage
hs_err: `SIGSEGV in libjvm (upcall)` → freed stub. `UnsatisfiedLinkError` → wrong lib path.
Fix: `-Djava.library.path`, `SymbolLookup.libraryLookup`.

## 10. HotSpot Refs
- JEP 454 (Foreign Function & Memory API, final), JEP 412 (incubator history).
- `Linker.java` javadoc has canonical strlen/qsort samples.
