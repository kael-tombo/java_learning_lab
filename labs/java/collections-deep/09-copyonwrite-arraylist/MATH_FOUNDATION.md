# Math Foundation: volatile Happens-Before

## The publication rule (JLS §17.4)

A write to a volatile variable *synchronizes-with* every later read of
that variable; everything before the write *happens-before* everything
after the read. Applied here:

```
writer: copy[i] = e (ordinary stores) ... setArray(v) [volatile write]
reader: getArray() [volatile read] ... x = arr[i] (ordinary load)
```

The reader is guaranteed to see the fully built array — never a
half-copied one — because all construction stores precede the volatile
write in happens-before order. No `synchronized` on the read path needed.

## Why the reference swap is atomic

Reads/writes of references are atomic (JLS §17.7): `getArray()` returns
either the old or the new array, never a mixture. Combined with array
immutability-by-convention, readers need no further synchronization.

## Cost model

- Read: 1 volatile load (~acquire barrier, ~ns on x86/ARM) + bounds check
  + array load → O(1), constant factor barely above plain ArrayList get.
- Write of n elements: n reference copies + 1 allocation of (n±1) slots +
  1 volatile store → O(n) time, O(n) temporary garbage per write.
- Break-even vs `synchronizedList`: COW wins while
  (reads × lock-cost) > (writes × n × copy-cost). At n=1000 with 8-byte
  refs, each write copies ~8KB — 1000 writes/sec = 8MB/sec garbage.

## Lost-race recheck logic

Stale snapshot index i is valid iff `snapshot == current` (no interleaving
write) OR the overlapping prefix re-scan confirms the element still at an
equivalent position. The re-scan bounds the trust: only positions
established *after* re-fetching current are acted on.
