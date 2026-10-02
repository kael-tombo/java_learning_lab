# THEORY — Async File I/O (lab04)

## 1. Two async styles, one channel

`AsynchronousFileChannel` offers the same operation in two shapes, and
`MainImplementation` (lab04) shows both:

- **Future style** (`asyncReadFuture`/`asyncWriteFuture`): call returns a
  `Future<Integer>`; `result.get()` blocks until done. Simple, but the
  calling thread still waits — async submission, synchronous wait.
- **Callback style** (`asyncReadCallback`): call returns immediately with a
  `CompletableFuture<String>`; a `CompletionHandler` completes it later on
  a pool thread. True non-blocking for the caller.

Rule: Future = "I need the value on this thread eventually";
CompletionHandler = "notify me, I'll keep doing other work".

## 2. Positioned I/O, no shared cursor

Every operation takes an explicit `position` (`read(buf, 0)`,
`write(buf, 0)`). Unlike streams/channels with a moving cursor, concurrent
async ops on the same channel never interfere — each declares its offset.
This is what makes async file I/O composable.

## 3. Who runs the callbacks?

An `AsynchronousChannelGroup` (backed by a thread pool —
`createCustomGroup` builds one with daemon threads named `async-io-*`).
Default group exists, but a custom group isolates I/O threads, bounds
concurrency, and gives meaningful thread names in dumps. Daemon threads
matter: non-daemon pool threads would pin the JVM open after `main`.

## 4. Close discipline in callbacks

`asyncReadCallback` closes the channel in **both** `completed` and
`failed`. Forgetting the `failed` branch leaks the handle on every error
path — the async version of the try-with-resources habit from lab01.
