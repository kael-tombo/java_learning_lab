# FLASHCARDS — Selectors

| # | Front | Back |
|---|-------|------|
| 1 | Reactor pattern in one line? | One thread demultiplexes many channels via select, dispatches ready keys. |
| 2 | `select(timeout)` returns? | Ready-key count; 0 = timeout, keep looping. |
| 3 | Must-do per selected key? | `iterator.remove()` — set never auto-clears; else infinite spin. |
| 4 | `isValid()` guard why? | Key may be cancelled (channel closed) between select and dispatch. |
| 5 | Accept path? | `accept()` → non-blocking → register `OP_READ` same selector. |
| 6 | `read() == -1`? | Peer closed — `close()` channel (key auto-cancels). |
| 7 | Non-blocking `write` short? | Normal — loop remainder / re-register `OP_WRITE`. |
| 8 | Port 0 in tests? | OS-assigned free port — no BindException flakes. |
| 9 | `finishConnect` spin — production? | No — use `OP_CONNECT` key instead of yield-spin. |
| 10 | Reactor golden rule? | Never block the selector thread; offload to pool. |
| 11 | Thread-per-conn vs reactor memory? | N·stack (~1MB each) vs O(N) small keys. |
| 12 | Daemon + flag + timeout? | Exit-friendly, prompt stop, bounded close latency. |
| 13 | `OP_ACCEPT` vs `OP_READ`? | Server channel: new connections; socket channel: inbound data. |
| 14 | Forgotten `remove()` symptom? | 100% CPU livelock on one key. |
| 15 | 2 s client deadline purpose? | Bounds waits against lost/slow responses. |
