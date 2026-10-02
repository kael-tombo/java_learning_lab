# MATH_FOUNDATION — Visitor & Watcher

## 1. Walk complexities (n files, depth d)

| Op | Time | Extra space |
|----|------|-------------|
| `walkFileTree` full walk | O(n) visits | O(d) stack (iterative, not recursive) |
| `findByExtension` | O(n) name checks | O(matches) results |
| `totalSize` | O(n) attrs (no extra stat calls) | O(1) accumulator |
| `deleteTree` | O(n) deletes | O(d) |
| `Files.walk` listing | O(n) + O(n log n) `sorted()` | O(n) collected list |

`attrs.size()` reuses the attributes already fetched for the visit —
calling `Files.size(file)` instead would double stat syscalls to 2n.

## 2. WatchService event economics

Polling `Files.exists` every `p` ms over `n` files: O(n/p) stats per
second forever. WatchService: ~0 cost idle, O(events) on change. The
trade: bounded coalescing queue — bursts beyond capacity collapse into
`OVERFLOW`, i.e. lossy compression of event streams. Design rule: treat
any `OVERFLOW` as "rescan the tree" (reconcile state, don't trust the
event log).
