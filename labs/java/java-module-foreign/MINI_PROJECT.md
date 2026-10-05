# Mini Project — Native Grep via Arena

## Goal
Grep byte pattern in 1GB file using mapped MemorySegment, faster than BufferedReader.

## Steps
1. Map file: `MemorySegment.mapFile(path, 0, size, READ_ONLY, arena)`.
2. Sliding scan with `mismatch` or manual loop over JAVA_BYTE.
3. Report offsets + count; time vs `Files.lines().filter()`.
4. Handle edge: pattern split across chunk boundary (overlap = m-1).

## Skeleton
```java
try (Arena a = Arena.ofConfined()) {
  var seg = MemorySegment.mapFile(p, 0, Files.size(p), FileChannel.MapMode.READ_ONLY, a);
  long n = seg.byteSize(); // scan
}
```

## Acceptance
- Correct on binary + text; NUL bytes don't truncate.
- ≥2× faster than buffered scan on 1GB; NMT shows no leak.
- Flags: `--enable-native-access=ALL-UNNAMED -XX:NativeMemoryTracking=detail`.

## Stretch
- Downcall `memmem` for native search.
- Parallel split across shared arena + virtual threads.
- Case-insensitive + regex prefilter.

## Demo (2 min)
Run both variants, show ms + match counts equal.
