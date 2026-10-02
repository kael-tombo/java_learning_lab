# CODE_DEEP_DIVE — Selectors `MainImplementation`

Package `com.java.io.nio.lab03`.

## 1. `EchoReactor` constructor (lines 29–39)

- `Selector.open()` + non-blocking `ServerSocketChannel` bound to
  `localhost:0` (ephemeral port). Registers `OP_ACCEPT` — the *only*
  interest initially. `getPort()` exposes the OS-chosen port to clients.

## 2. Reactor loop (lines 41–63)

- `select(100)`: blocks ≤100 ms; returns ready-key count, 0 on timeout
  (the `continue` keeps the `running` flag responsive).
- `selectedKeys()` + `it.remove()`: **removal is the application's job**.
  Skip it and the key fires every iteration — busy spin.
- `!key.isValid()` guard: a key cancelled (channel closed) between select
  and dispatch must not be touched.
- `handleAccept`: `ssc.accept()` (non-blocking: may return null in
  general, though here it follows a ready signal), new channel registered
  for `OP_READ` on the *same* selector — one thread, many connections.
- Daemon thread + `close()` sets `running=false` and closes the server
  channel (wakes the selector); the loop's trailing `selector.close()`
  runs on exit.

## 3. `handleRead` (lines 72–82)

- 256-byte buffer per read; `bytesRead == -1` = peer closed → `sc.close()`
  (which also cancels the key). Otherwise `flip()` + `write(buf)` echoes.
  Note: `sc.write` may be partial — the lab assumes small messages fit;
  production code tracks unwritten remainder and re-registers `OP_WRITE`.

## 4. `NonBlockingClient.sendAndReceive` (lines 95–124)

- `connect` + `while (!finishConnect()) Thread.yield()` — a spin-wait;
  acceptable in a test, wasteful at scale (prefer `OP_CONNECT`).
- Write loop handles partial writes; read loop accumulates until
  `message.length()` bytes or the 2 s deadline. `trim()` on decode hides
  trailing zero-bytes from the 256-byte buffer — necessary because the
  buffer is bigger than most messages.
- `main` asserts echo equality, then sanity-checks a bare
  `Selector.open()/isOpen()/keys().isEmpty()/close()` lifecycle.
