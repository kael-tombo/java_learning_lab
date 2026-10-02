# EXERCISES — Async I/O

## 1. Blocked-caller measurement (beginner)
Time 50 sequential `asyncReadFuture(...).get()` calls vs 50 callback reads
awaited via `CompletableFuture.allOf`. Both move identical bytes — explain
the wall-time gap using the thread-accounting table.

## 2. Missing `failed` close (beginner)
Delete the `channel.close()` in `failed()`, then force failures (read a
deleted file 100× in a loop). Watch open handles grow (Process Explorer /
`lsof`). Restore and explain why try-with-resources couldn't help here.

## 3. Completion order (intermediate)
Fire 10 `asyncReadCallback` reads on different files, record completion
order across runs. Is it deterministic? What determines it (scheduler,
page cache, sizes)?

## 4. Timeout composition (intermediate)
Add `.orTimeout(500, MILLISECONDS)` to the `asyncReadCallback` future and
read a large file from a slow device. Verify `TimeoutException` delivery
and that the channel still closes (no leak on the timeout path).

## 5. Custom group isolation (advanced)
Run a latency-sensitive callback workload on the default group while a
second workload saturates it with 1 s handlers. Measure p99. Then move
workload 2 to `createCustomGroup(2)` and re-measure — the standard noisy-
neighbor isolation argument for custom groups.
