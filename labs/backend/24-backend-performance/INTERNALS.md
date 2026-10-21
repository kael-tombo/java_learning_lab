# Internals: Performance

## JVM Code Cache
JIT-compiled methods stored in code cache. If full, JIT stops. Monitor with -XX:+PrintCodeCache.

## Compressed OOPs
64-bit JVM with heaps < 32GB uses 32-bit object references, reducing memory by ~30%. Above 32GB, references become 64-bit.

## Cache Lines
CPU cache line is 64 bytes. False sharing occurs when threads modify related variables on same cache line.
