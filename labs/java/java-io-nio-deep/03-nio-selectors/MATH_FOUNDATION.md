# MATH_FOUNDATION — Selectors

## 1. Thread-per-connection vs reactor cost

N connections, stack `S` (~1 MB), per-connection idle overhead:

- Thread-per-connection: memory ≈ `N·S`; wakeups O(N) on broadcast.
  N=10k → ~10 GB stacks alone. Dead.
- Reactor (1 thread + selector): memory O(N) keys (~100s of bytes each);
  per-event work O(ready), not O(N). `select(timeout)` is the OS doing the
  waiting (epoll/kqueue), not 10k parked threads.

## 2. Complexities in this lab

| Operation | Cost |
|-----------|------|
| `select(100)` | O(ready) dispatch + one syscall; O(1) when idle |
| Accept + register | O(1) amortized |
| Echo read/write (k bytes) | O(k) copies |
| Forgotten `selectedKeys.remove()` | O(∞) — infinite re-dispatch (livelock, 100% CPU) |

## 3. Little's-law framing

Throughput `λ`, mean handling time `W`, concurrent in-system `L = λ·W`.
Reactor keeps `W` tiny per event (no blocking), so one thread sustains
high `λ`. Any blocking handler (e.g. `Thread.sleep` in `handleRead`)
inflates `W` and collapses `λ` — hence the rule: **never block the
reactor thread; offload to a worker pool**.
