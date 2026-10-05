# Exercises — Java IO / NIO Deep (10 hands-on)

## E1 — Classic vs NIO Copy Benchmark
Template:
```java
import java.nio.file.*;
public class CopyBench {
  public static long copyIO(Path s, Path d) throws Exception {
    try (var in = Files.newInputStream(s); var out = Files.newOutputStream(d)) {
      return in.transferTo(out);
    }
  }
  public static long copyNIO(Path s, Path d) throws Exception {
    try (var ch = FileChannel.open(s); var out = FileChannel.open(d,
      StandardOpenOption.CREATE, StandardOpenOption.WRITE)) {
      return ch.transferTo(0, Long.MAX_VALUE, out);
    }
  }
  public static void main(String[] a) throws Exception { /* time both */ }
}
```
Tasks: copy 500MB file both ways, record ms. Try: `java -Xmx512m CopyBench`.

## E2 — Buffer Flip/Clear Semantics
```java
ByteBuffer b = ByteBuffer.allocate(16);
b.putInt(42); b.flip(); System.out.println(b.getInt()); b.clear();
```
Tasks: explain position/limit/capacity after each op. Write a failing test then fix.

## E3 — Direct vs Heap Buffers
```java
ByteBuffer heap = ByteBuffer.allocate(1<<20);
ByteBuffer direct = ByteBuffer.allocateDirect(1<<20);
```
Tasks: benchmark 10k put/get cycles. Run with `-XX:MaxDirectMemorySize=256m -XX:+PrintGCDetails`.

## E4 — FileChannel Scatter/Gather
Template: write header+body with `GatheringByteChannel.write(ByteBuffer[])`, read back with scatter.
Tasks: verify offsets, handle partial writes in a loop.

## E5 — Memory-Mapped File Search
```java
try (var ch = FileChannel.open(p, StandardOpenOption.READ)) {
  var mb = ch.map(FileChannel.MapMode.READ_ONLY, 0, ch.size());
  // scan for byte pattern
}
```
Tasks: grep 1GB file, compare vs `Files.lines()`. Flags: `-XX:+UseG1GC`.

## E6 — Selector Echo Server
Template: `Selector`, `ServerSocketChannel.configureBlocking(false)`, OP_ACCEPT/OP_READ.
Tasks: handle 500 concurrent `nc` clients, no thread-per-conn. Test with `nmap`/script.

## E7 — AsyncFileChannel + CompletableFuture
```java
AsynchronousFileChannel ch = AsynchronousFileChannel.open(p, StandardOpenOption.READ);
ByteBuffer buf = ByteBuffer.allocate(4096);
ch.read(buf, 0, null, new CompletionHandler<Integer,Object>() {
  public void completed(Integer r, Object a) {}
  public void failed(Throwable t, Object a) {}
});
```
Tasks: chain 3 reads with CompletableFuture, measure tail latency.

## E8 — WatchService Directory Sync
Tasks: watch dir, mirror creates/deletes to backup dir. Handle OVERFLOW events.

## E9 — Zero-Copy transferTo/transferFrom
Tasks: serve static file over SocketChannel using transferTo. Compare CPU with plain loop (`time`, `strace`).

## E10 — Backpressure File Pipeline (Capstone)
Tasks: Files.walk → filter → transform → write with bounded queue (ArrayBlockingQueue 128).
Flags: `-Xmx256m -XX:MaxDirectMemorySize=128m`. Assert no OOM on 5GB tree.
Checklist: [ ] benchmarks recorded [ ] flags tried [ ] edge cases handled
