# Exercises — Foreign Function & Memory (9 hands-on)

## E1 — Arena Allocate + RW
```java
try (Arena a = Arena.ofConfined()) {
  MemorySegment s = a.allocate(16);
  s.set(ValueLayout.JAVA_INT, 0, 42);
  assert s.get(ValueLayout.JAVA_INT, 0) == 42;
}
```
Tasks: try use-after-close → observe exception. Flags: `--enable-native-access=ALL-UNNAMED`.

## E2 — Confined vs Shared vs Global
Tasks: share confined across threads (fail), fix with shared arena. Document ownership.

## E3 — C String Round-Trip
```java
try (Arena a = Arena.ofConfined()) {
  MemorySegment c = a.allocateFrom("hello");
  String back = c.getString(0);
}
```
Tasks: measure overhead vs byte[] for 1M strings.

## E4 — Linker: strlen/getpid
```java
Linker lk = Linker.nativeLinker();
SymbolLookup std = lk.defaultLookup();
MethodHandle strlen = lk.downcallHandle(std.find("strlen").orElseThrow(),
  FunctionDescriptor.of(ValueLayout.JAVA_LONG, ValueLayout.ADDRESS));
```
Tasks: call strlen on E3 string. Handle missing symbol gracefully.

## E5 — Struct Layout (Point)
```java
StructLayout point = MemoryLayout.structLayout(
  ValueLayout.JAVA_INT.withName("x"), ValueLayout.JAVA_INT.withName("y"));
try (Arena a = Arena.ofConfined()) {
  MemorySegment p = a.allocate(point);
}
```
Tasks: set/get x,y via VarHandle; check sizeof == 8.

## E6 — Array of Structs + Slice
Tasks: allocate 1k points, slice i-th, sum x. Compare vs Java objects memory.

## E7 — Upcall (qsort Comparator)
Tasks: pass Java comparator as upcall stub to C qsort. Keep stub alive in arena!

## E8 — Memory-Mapped Segment
```java
try (Arena a = Arena.ofConfined()) {
  MemorySegment m = MemorySegment.mapFile(Path.of("big.bin"), 0, 4096,
    FileChannel.MapMode.READ_ONLY, a);
}
```
Tasks: scan bytes, compare vs MappedByteBuffer.

## E9 — Zero-Copy Pipeline (Capstone)
Tasks: map file → parse ints off-heap → downcall native checksum.
Flags: `-XX:+UseG1GC --enable-native-access=ALL-UNNAMED`. Assert no arena leak (NMT).
