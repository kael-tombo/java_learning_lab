# Real-World Project — Native Codec Service

## Problem
Thumbnail/resize images via native lib (e.g., libvips/stb) from Java with zero-copy buffers.

## Architecture
```
HTTP POST /resize → confined arena per request → map input
  → downcall native resize → segment result → stream response
  → metrics (latency, arena bytes, native RSS)
```
Pool native handles (Linker handles are reusable); never share confined arenas.

## Milestones
1. **M1 Binding**: jextract or manual descriptor for `resize(in,len,out,w,h)`.
2. **M2 Service**: HttpServer + per-request arena, size caps (10MB), timeout 5s.
3. **M3 Zero-copy**: input via mapFile, output segment → response without heap copy.
4. **M4 Hardening**: wrong-descriptor fuzz, arena-leak test (100k reqs, RSS flat).
5. **M5 Ops**: Docker with native lib, K8s limits, p99 dashboard.

## Key Code
```java
MethodHandle resize = linker.downcallHandle(sym("img_resize"),
  FunctionDescriptor.of(ValueLayout.JAVA_INT,
    ValueLayout.ADDRESS, ValueLayout.JAVA_LONG, ValueLayout.ADDRESS,
    ValueLayout.JAVA_INT, ValueLayout.JAVA_INT));
try (Arena a = Arena.ofConfined()) {
  MemorySegment in = a.allocateFrom(bytes); MemorySegment out = a.allocate(maxOut);
  int rc = (int) resize.invokeExact(in, (long) bytes.length, out, w, h);
}
```
Run: `java --enable-native-access=ALL-UNNAMED -XX:NativeMemoryTracking=detail App`.

## Testing
- Fuzz sizes/formats; assert no crash, error codes mapped to 400/500.
- Soak: RSS + NMT stable; hs_err absent.
- Bench vs pure-Java ImageIO: document speedup + quality delta.

## Ops
- Base image with lib installed; `ldconfig` verified at startup.
- K8s: 1Gi/1CPU, HPA on p99; alert RSS growth > 20%/h.

## Interview Angles
- Arena choice per request? Upcall lifetime? Descriptor mismatch debug?

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Oracle FFM API: https://docs.oracle.com/en/java/javase/22/docs/api/java.base/java/lang/foreign/package-summary.html
- OpenJDK Panama: https://openjdk.org/projects/panama/
- JEP 454 (FFM): https://openjdk.org/jeps/454
