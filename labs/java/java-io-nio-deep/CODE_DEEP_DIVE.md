# Code Deep Dive — IO / NIO

## 1. Source Tour (OpenJDK)
- `sun.nio.ch.FileChannelImpl.transferTo` → `sendfile64` on Linux.
- `java.nio.DirectByteBuffer` uses `Unsafe.allocateMemory` + Cleaner.
- `sun.nio.ch.SelectorImpl` wraps `epoll` (Linux) / `kqueue` (macOS).
- Read: `SocketChannelImpl.read` → `IOUtil.read` → `readv`.

## 2. Bytecode: try-with-resources
```java
try (var in = Files.newInputStream(p)) { in.read(); }
```
`javap -c` shows: `invokevirtual close`, exception table + `addSuppressed`.
Cost: one extra null check + suppressed array only on exception.

## 3. Direct Buffer Alloc Path
```java
ByteBuffer d = ByteBuffer.allocateDirect(4096);
```
HotSpot: `Bits.reserveMemory` → cap check vs MaxDirectMemory → `Unsafe.allocateMemory`.
Inspect: `-XX:MaxDirectMemorySize=64m -XX:+PrintNMTStatistics -XX:NativeMemoryTracking=detail`.

## 4. Heap Buffer Copy Extra Step
Heap buffer IO does: copy heap→temp direct→syscall. Direct skips first copy.
JVM flag: `-Djdk.nio.maxCachedBufferSize=262144` controls temp cache.

## 5. Selector Wakeup Mechanism
`Selector.wakeup()` writes byte to pipe → epoll_wait returns. See `PipeImpl`.
Strace: `strace -e epoll_wait,read,write java SelectorDemo`.

## 6. FileChannel.map Internals
`map()` → `mmap64` syscall; unmap via `Cleaner.clean()` (Unsafe.invokeCleaner).
Warning: unclosed mapping pins file on Windows.

## 7. Async Channel Threading
`AsynchronousChannelGroup.withFixedThreadPool(4, ...)` → pool threads do completions.
Default group uses cached daemon threads — avoid in servers.

## 8. JIT Intrinsics
`ByteBuffer.getInt/putInt` intrinsified to unaligned loads (`Unsafe.getInt`).
Check: `-XX:+PrintIntrinsics -XX:+PrintCompilation`.

## 9. Profiling Hooks
```bash
jfr start --object-age 5s  # old buffers
lsof -p <pid> | wc -l      # fd count
cat /proc/<pid>/maps | grep -c mmap
```

## 10. HotSpot Refs (verify)
- FileChannelImpl.c, IOUtil.c, DatagramChannelImpl.c in `src/java.base/unix/native`.
- `jdk.nio.maxCachedBufferSize` in `DirectByteBuffer.java`.
Further: `man sendfile`, `man epoll`, OpenJDK `java.nio` package-info.
