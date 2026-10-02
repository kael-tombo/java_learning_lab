# THEORY — NIO Selectors & Reactor (lab03)

## 1. The problem: 10,000 connections, 10,000 threads?

One-thread-per-connection dies at scale (stack memory ~1 MB/thread,
context-switch storms). Selectors invert control: **one thread monitors
many channels**, asking the OS "which of these are ready?" via
`selector.select(timeout)`, then dispatching only ready keys. This is the
**Reactor pattern**: demultiplex → dispatch → handle, all on few threads.

## 2. The key set

`EchoReactor` (lab03) registers `ServerSocketChannel` for `OP_ACCEPT`.
The loop: `select(100)` → `selectedKeys()` → `it.remove()` (mandatory —
keys are *not* auto-cleared) → `isAcceptable()` → accept + register new
`SocketChannel` for `OP_READ`; `isReadable()` → read, echo back with
`sc.write(buf)`. `it.remove()` forgotten = the same key handled forever =
100% CPU spin. `!key.isValid()` check skips cancelled keys.

## 3. Non-blocking discipline

Channels are `configureBlocking(false)`: `connect` may not complete
immediately (client spins on `finishConnect`), `read` may return 0 or
partial data, `write` may accept partial bytes (lab loops
`while (writeBuf.hasRemaining())`). Every I/O call becomes "try, handle
short/zero, retry or park". The 2 s deadline loop in `NonBlockingClient`
bounds the wait — production code uses `OP_CONNECT` registration instead
of a yield-spin.

## 4. Why localhost:0 and daemon threads

Binding port `0` lets the OS pick a free port (`getPort()` reads it back)
— no test flakiness from occupied ports (contrast the `25-spring-boot`
port-8080 lesson). The reactor thread is daemon + `running` flag + 100 ms
select timeout, so `close()` stops it promptly and the JVM can exit.
