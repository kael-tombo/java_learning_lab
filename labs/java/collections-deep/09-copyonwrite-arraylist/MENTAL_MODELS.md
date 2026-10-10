# Mental Models: Copy-on-Write

## 1. Versions, not mutations

The list is a chain of immutable arrays; "mutation" appends a new version
and swings one pointer. Readers surf versions; writers mint them. Once you
see versions, snapshots and staleness stop being surprising.

## 2. One volatile field is the whole protocol

No lock for readers because there is nothing to mutually exclude: the
array reference swap is atomic and old arrays are frozen. Visibility =
one happens-before edge from `setArray` to `getArray`.

## 3. Snapshots are stronger than weak consistency

CLQ iterators are fuzzy (may/may not show concurrent writes). COW
iterators are exact: construction-time state, fully reproducible. The
price — pinning the array — is why the guarantee is affordable only for
read-mostly data.

## 4. Optimism inside a lock

`addIfAbsent`/`remove` scan without locking, then lock only when mutation
is likely, rechecking first. The lock protects the copy-publish; the
pre-scan avoids taking it for no-ops. Read the miss path as the fast path.

## 5. Equal writes still write

`set(i, sameValue)` publishing a copy looks wasteful until you see the
barrier purpose: progress markers for the memory system. Not every store
is about data; some are about ordering.

## 6. The workload test is a ratio

Reads ÷ writes ≥ ~100:1 with small n → COW wins (listener lists, config,
routes). Invert either axis (frequent writes, huge arrays) and each write
pays O(n) allocation — the structure becomes a GC stress generator.

## 7. Iterators are leases

Holding an iterator holds an array. Treat long-lived COW iterators like
open file handles: scope them tightly, or versions pile up behind them.
