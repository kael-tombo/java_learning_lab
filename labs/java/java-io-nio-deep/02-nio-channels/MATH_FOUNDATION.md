# MATH_FOUNDATION — NIO Channels

## 1. The buffer state machine

A `ByteBuffer` of capacity `C` has `position`/`limit`:

- After `allocate(C)`: `position=0, limit=C` (write mode, `remaining=C`).
- After filling `k` bytes: `position=k`.
- `flip()`: `limit=position, position=0` (read mode, `remaining=k`).
- After consuming all: `position=limit`; `clear()` resets to write mode.

Forgetting `flip()` means `remaining=0`-vs-`C` confusion: reads return
nothing, writes overwrite — silently.

## 2. Complexities

| Method | Time | Extra space |
|--------|------|-------------|
| `readFile`/`writeFile` | O(S) | O(S) whole-file buffer |
| `scatterRead`/`gatherWrite` | O(S), 1 syscall | O(Σ bufferSizes) |
| mmap int access | O(1) per access (page fault amortized) | O(window) mapped pages |
| `transferTo` | O(S), kernel-side | O(1) user space |

## 3. Zero-copy savings

Classic copy: disk → kernel buf → user buf → kernel socket buf → NIC
(2 copies + 2 context switches per chunk). `transferTo`/`sendfile`:
disk → kernel buf → NIC (0 user-space copies). Steady-state throughput
approaches device bandwidth; CPU cost per byte drops ~2–3×.
