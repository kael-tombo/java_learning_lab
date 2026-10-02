# CODE_DEEP_DIVE — Async I/O `MainImplementation`

Package `com.java.io.nio.lab04`.

## 1. `asyncReadFuture` / `asyncWriteFuture` (lines 22–45)

- Channel opened per call in try-with-resources (`READ`, or
  `CREATE+WRITE+TRUNCATE_EXISTING` for writes) — no shared state.
- `ByteBuffer.allocate((int) channel.size())`: whole-file buffer (same
  O(S) caveat as lab02's `readFile`).
- `result.get()` throws checked `InterruptedException`/`ExecutionException`
  — declared on the signature, unlike the callback variant. Callers must
  decide: propagate, wrap, or convert to `CompletableFuture`.

## 2. `asyncReadCallback` (lines 50–74)

- Channel is **not** in try-with-resources (it must outlive the call!) —
  instead both handler methods close it explicitly. This split ownership
  (open here, close later, on another thread) is the central subtlety.
- `channel.read(buf, 0, buf, handler)`: the third arg (attachment) is
  handed back to the handler — here the buffer itself, avoiding closure
  capture issues.
- `completed`: `flip()` → decode → close → `promise.complete(content)`.
  Order matters: complete *after* close so `get()` never observes an
  open handle.
- `failed`: close + `promise.completeExceptionally(exc)` — errors surface
  through the future, never swallowed.

## 3. `createCustomGroup` (lines 79–86)

- `Executors.newFixedThreadPool(poolSize)` with daemon threads
  (`async-io-*` names). `AsynchronousChannelGroup.withThreadPool(pool)`
  binds channels opened with that group to exactly these threads.
- `main` additionally shows the inline variant: opening a channel with
  `Set.of(CREATE, WRITE)` + an explicit pool, writing `"Group test"`,
  shutting the pool down in `finally` (leaked pools = hung JVM).

## 4. `main` flow (lines 88–124)

Future round-trip (`asyncWriteFuture` → `asyncReadFuture`, assert equal),
callback round-trip (write via `Files.writeString`, read via
`asyncReadCallback(...).get()`, assert equal), custom-group write. All temp
files `deleteOnExit`.
