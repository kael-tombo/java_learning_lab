# QUIZ — Selectors

## 1. What does `selector.select(100)` return, and what does 0 mean?
<details><summary>Answer</summary>Count of ready keys; 0 = timeout with nothing ready (loop continues, checks `running`).</details>

## 2. Why must the loop call `selectedKeys().remove()` per key?
<details><summary>Answer</summary>The selected set is never auto-cleared — an un-removed key dispatches again next iteration: infinite busy spin at 100% CPU.</details>

## 3. Why check `key.isValid()` before dispatch?
<details><summary>Answer</summary>A channel closed between select and dispatch cancels its key; operating on it throws `CancelledKeyException`.</details>

## 4. New connection arrives: what two things happen in `handleAccept`?
<details><summary>Answer</summary>`accept()` the `SocketChannel`, set non-blocking, register it for `OP_READ` on the same selector.</details>

## 5. `read()` returns -1. Meaning and required action?
<details><summary>Answer</summary>Peer orderly shutdown — `close()` the channel (cancels key automatically).</details>

## 6. Why bind port 0 in tests?
<details><summary>Answer</summary>OS picks a free ephemeral port — no `BindException` flakiness from occupied fixed ports.</details>

## 7. The client's `while (!finishConnect()) yield()` — acceptable? At scale?
<details><summary>Answer</summary>Fine in a test; at scale it's a spin-wait — prefer registering `OP_CONNECT` and finishing on the selector thread.</details>

## 8. `handleRead` assumes one `write` echoes everything. When does this break?
<details><summary>Answer</summary>Messages > buffer or slow peer → partial write. Must loop on remainder / re-register `OP_WRITE`.</details>

## 9. Golden rule of the reactor thread?
<details><summary>Answer</summary>Never block it — any blocking handler inflates W and collapses throughput (L = λW). Offload to workers.</details>

## 10. Daemon reactor thread + `running` flag + 100 ms timeout: why all three?
<details><summary>Answer</summary>Daemon lets the JVM exit; the flag requests stop; the timeout bounds how long `close()` waits for the loop to notice.</details>
