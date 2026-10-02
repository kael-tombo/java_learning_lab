# FLASHCARDS — Async I/O

| # | Front | Back |
|---|-------|------|
| 1 | Future vs callback style? | Future: caller blocks in get(). Callback: handler completes promise later, nobody waits. |
| 2 | Why no try-with-resources in callback open? | Channel must outlive the call — close moves to both handler branches. |
| 3 | Leaked branch? | `failed()` without close — handle exhaustion under error storms. |
| 4 | Attachment parameter? | Context echoed back to handler (here: the buffer). |
| 5 | Close-before-complete why? | Woken `get()` threads never see an open handle. |
| 6 | Positioned I/O benefit? | Explicit offsets — concurrent ops independent, no cursor serialization. |
| 7 | Custom group why? | Isolate threads, bound concurrency, named daemon threads. |
| 8 | Daemon pool threads? | JVM can exit; non-daemon pins it open. |
| 9 | Pool shutdown in `finally`? | Guaranteed even on exception — else hung JVM. |
| 10 | `orTimeout` on the promise? | Timeout delivery via future; channel must still close on that path. |
| 11 | `allocate(size)` caveat? | O(S) heap — same whole-file warning as lab02. |
| 12 | Errors surface how? | `completeExceptionally` — never swallowed. |
| 13 | Two reads concurrently, same channel? | Safe — positions are per-op, no shared cursor. |
| 14 | `get()` checked exceptions? | `InterruptedException` + `ExecutionException` — declared, must be handled. |
| 15 | When prefer Future style? | Caller needs value immediately after; simplicity wins. |
