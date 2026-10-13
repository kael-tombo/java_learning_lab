# Socket Programming — Theoretical Foundation

## Core Concept

TCP sockets (`java.net.ServerSocket`/`Socket`) expose the OS transport
endpoint as blocking streams: `accept()` yields a connected `Socket` whose
`getInputStream()`/`getOutputStream()` carry the byte stream. The kernel
completes the three-way handshake (SYN → SYN-ACK → ACK) before `accept()`
returns — by the time your code sees the socket, the connection exists.

## Threading Models (the lab's real subject)

1. **Thread-per-connection**: `while (true) pool-or-thread(handle(accept())))`.
   One thread per client; simple, correct, and dead past a few thousand
   clients (a thread per connection = a megabyte-scale stack per client).
2. **Bounded pool**: `Executors.newFixedThreadPool(N)` fronting `accept()`.
   Caps memory, queues excess in the socket backlog (`ServerSocket(port,
   backlog)` — default 50); overload sheds via queue growth, not crashes.
3. **NIO multiplexing**: one thread, many channels (lab 02) — the answer
   when connection counts exceed thread budgets.

`Socket.setSoTimeout` bounds blocking reads (0 = infinite — the classic
hung-thread default); `setTcpNoDelay(true)` disables Nagle batching for
latency-sensitive protocols; `setKeepAlive`/`setReuseAddress` control probe
and bind behavior. Half-close (`shutdownInput`/`shutdownOutput`) signals
EOF in one direction while keeping the other open — the graceful
protocol-termination primitive.

## Stream Framing Is Your Problem

TCP is a byte stream, not a message stream: one `write` may arrive as many
reads and vice versa. Every protocol needs framing — length prefixes,
delimiters, or fixed sizes — plus a read loop that accumulates until a full
frame exists. The majority of socket bugs are framing bugs wearing
concurrency costumes.

## Key Invariants

1. `accept()` returns only completed connections (kernel handshake first).
2. Each `Socket` needs exactly one owner thread (or explicit handoff) —
   concurrent read+write is fine, concurrent reads are not.
3. Blocking calls need timeouts (`SoTimeout`) or external close to stay
   interruptible — `Thread.interrupt()` alone doesn't unblock a socket read.
4. Close order: streams, then socket; `try`-with-resources on the `Socket`
   closes both (streams close with it).
