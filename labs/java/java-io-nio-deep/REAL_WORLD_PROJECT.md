# Real-World Project — Log Ingestor Service

## Problem
Ingest app logs over TCP (10k msg/s), parse, batch to disk + forward. Must survive bursts.

## Architecture
```
clients → Selector server (port 9090) → ArrayBlockingQueue(1024)
  → parser pool (virtual threads) → batch writer (FileChannel, 128KB)
  → rotation + metrics endpoint
```
Backpressure: queue full → apply `OP_READ` pause / send `429 BUSY`.

## Milestones
1. **M1 Server**: non-blocking accept/read, length-prefixed frames, echo test.
2. **M2 Pipeline**: queue + parsers (timestamp/level/msg), poison-pill shutdown.
3. **M3 Storage**: gathering writes, hourly rotation, fsync every 1s.
4. **M4 Resilience**: reconnect, partial-frame reassembly, malformed-line DLQ.
5. **M5 Observability**: throughput, p99, queue depth, FD count; JFR on demand.

## Key Code
```java
ServerSocketChannel ssc = ServerSocketChannel.open();
ssc.bind(new InetSocketAddress(9090)); ssc.configureBlocking(false);
Selector sel = Selector.open(); ssc.register(sel, SelectionKey.OP_ACCEPT);
// loop: select → accept/read → q.offer (else backpressure)
```
Run: `java -Xmx1g -XX:MaxDirectMemorySize=512m -Djdk.nio.maxCachedBufferSize=131072 Ingestor`.

## Testing
- k6/`nc` flood: 10k msg/s × 60s, assert 0 loss, p99 < 50ms.
- Chaos: kill mid-write → recover, no corrupt batch (checksum per batch).
- Load: `lsof`, `ss -s`, GC logs reviewed.

## Ops
- Dockerfile: eclipse-temurin:21, non-root, `ulimit nofile 65536`.
- K8s: memory 1.5Gi, liveness TCP probe, PVC for log dir.
- Alert: queue_depth > 800, fd > 10k, p99 > 100ms.

## Interview Angles
- Why selector + queue vs thread-per-conn? Trade-offs with Loom?
- How zero-copy used? Where backpressure applied?

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Oracle NIO docs: https://docs.oracle.com/javase/8/docs/api/java/nio/package-summary.html
- OpenJDK NIO guide: https://openjdk.org/groups/nio/
- Baeldung NIO overview: https://www.baeldung.com/java-nio-2-file-api
