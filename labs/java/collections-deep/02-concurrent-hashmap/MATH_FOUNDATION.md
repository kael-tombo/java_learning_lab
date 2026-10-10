# Math Foundation: ConcurrentHashMap

## Why counting needs cells
- A single AtomicLong counter serializes all writers: n threads CAS-ing one
  word succeed one at a time, so increment throughput collapses to ~1/CAS-latency.
- CounterCell[] splits contention: thread t hashes its probe to cell t mod m,
  so m cells give ~m-way parallel increments; sumCount() = baseCount + sum(cells).

## Size control arithmetic
- Constructor: `tableSize = 1.0 + initialCapacity / loadFactor`, rounded up to
  a power of two; that value seeds sizeCtl (the next-resize threshold).
- Resize trips when `sumCount() >= sizeCtl` (default load 0.75, e.g. 16 slots
  -> sizeCtl 12). Growth doubles: 16 -> 32 -> 64, one bit re-decides each entry.

## Transfer parallelism
- k threads calling helpTransfer split the table into stride chunks; a table of
  N bins with k helpers moves ~N/k bins each, so pause work scales down with
  helpers instead of blocking readers (old table stays readable via forwarding).

## Cost table
| Op | Cost |
|----|------|
| get | O(1) expected, lock-free volatile read |
| put, empty bin | O(1) expected, one CAS |
| put, occupied bin | O(1) expected + one bucket monitor |
| size() | O(#cells) snapshot, approximate under contention |
| iteration | O(N), weakly consistent |

## Worked numbers
- 64 threads incrementing one key: 1 cell -> ~1M ops/s CAS-bound; 64 cells ->
  near-linear speedup, size() reads 65 words (base + 64 cells).
- 1M entries at load 0.75: table 2^21, mean chain ~0.5, treeify only on attack.
