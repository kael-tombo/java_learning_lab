# MATH_FOUNDATION — I/O Streams

## 1. Syscall amortization

Let file size = `S` bytes, buffer = `B` bytes, cost per syscall = `C`.

- Unbuffered single-byte reads: syscalls ≈ `S`, total cost ≈ `S·C`.
- Buffered reads: syscalls ≈ `⌈S/B⌉`, total cost ≈ `⌈S/B⌉·C`.

For `S = 1 MB`, `B = 8192`: `1,048,576` vs `128` syscalls — a ~8000×
reduction in kernel crossings (wall-clock speedup is smaller, typically
10–100×, because memory copies remain — but syscalls dominate for small
reads).

## 2. Complexities of this lab's methods

| Method | Time | Space | Notes |
|--------|------|-------|-------|
| `bufferedCopy` | O(S) | O(B) = O(1) | Single pass, fixed buffer |
| `writePrimitives` / `readPrimitives` | O(n) in payload | O(n) output array | Positional format, no index |
| `findPattern` (text `n`, pattern `m`) | O(n·m) worst case | O(m) pushback buf | Naive re-scan; KMP would give O(n+m) |
| `concatenate` (total `S`) | O(S) | O(B) buffer | `B = 256` here |

## 3. Why `findPattern` is O(n·m)

On each position matching `pattern[0]`, it reads up to `m-1` lookahead
bytes and compares — then pushes back and advances **one byte**. A text of
all `pattern[0]` bytes triggers a full `m`-byte compare at every position:
`n` positions × `m` work. The Knuth-Morris-Pratt improvement (precompute a
failure function, never re-scan) is the standard follow-up exercise.
