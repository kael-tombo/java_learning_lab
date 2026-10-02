# QUIZ — Async I/O

## 1. Future style vs callback style: who waits?
<details><summary>Answer</summary>Future: the caller blocks in `get()`. Callback: nobody waits — the handler runs later on a pool thread and completes the promise.</details>

## 2. Why does `asyncReadCallback` NOT use try-with-resources for the channel?
<details><summary>Answer</summary>The channel must outlive the call (I/O completes later). Ownership splits: open in the method, close in both handler branches.</details>

## 3. What happens if `failed()` forgets `channel.close()`?
<details><summary>Answer</summary>Every error path leaks a handle — slow descriptor exhaustion under failure storms, exactly when the system is already stressed.</details>

## 4. What is the attachment arg (`buf` in `read(buf, 0, buf, handler)`)?
<details><summary>Answer</summary>Context handed back to the handler (`completed(result, attachment)`) — here the buffer, avoiding fragile closure capture.</details>

## 5. In `completed`, why close *before* `promise.complete`?
<details><summary>Answer</summary>So any thread woken by `get()` observes a closed channel — no window where the file looks still-open.</details>

## 6. Why positioned I/O (`read(buf, pos)`) instead of a cursor?
<details><summary>Answer</summary>Ops are independent — concurrent reads never interfere, and ordering is explicit. Cursors would serialize everything.</details>

## 7. Custom channel group: why daemon threads with names?
<details><summary>Answer</summary>Daemon: JVM can exit without explicit shutdown. Names (`async-io-*`): thread dumps stay readable under load.</details>

## 8. `main` shuts the custom pool in `finally`. If forgotten?
<details><summary>Answer</summary>Non-daemon pool threads pin the JVM open after `main` — the classic "program won't exit" hang.</details>

## 9. `allocate((int) channel.size())` — the same caveat as lab02?
<details><summary>Answer</summary>Yes: O(file size) heap. Fine for temp files; stream/window for gigabytes.</details>

## 10. When is Future style actually preferable?
<details><summary>Answer</summary>Few ops, caller genuinely needs the value next (test setup, startup config) — simpler code beats unneeded asynchrony.</details>
