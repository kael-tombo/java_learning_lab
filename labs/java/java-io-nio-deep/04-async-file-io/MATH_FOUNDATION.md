# MATH_FOUNDATION — Async I/O

## 1. Why positioned I/O is O(1)-composable

Stream cursor reads serialize: op2 starts where op1 ended — throughput ≤
1 op / latency. Positioned async ops (`read(buf, pos)`) are independent:
N concurrent ops complete in ~max(latency), not Σ(latency), bounded by
device queue depth. The lab's `thenCombine(a,b)` fetch pair is the
two-op instance: wall time ≈ one fetch, not two.

## 2. Future.get vs callback: thread-accounting

- Future style: calling thread blocks in `get()` — 1 thread occupied per
  outstanding op. N concurrent reads = N waiting threads (same scaling
  wall as blocking I/O, just deferred differently).
- Callback style: 0 caller threads held; pool thread briefly runs the
  handler. N outstanding ops = O(1) caller threads + pool-sized workers.

## 3. Complexities

| Op | Time | Threads held |
|----|------|--------------|
| `asyncWriteFuture` + `get` | O(S) transfer + wait | 1 (blocked) |
| `asyncReadFuture` + `get` | O(S) + wait | 1 (blocked) |
| `asyncReadCallback` | O(S) transfer, 0 caller wait | 0 caller; 1 pool thread transiently |
| Custom group (pool P) | same transfer | ≤ P concurrent handlers |
