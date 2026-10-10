# Step by Step: ConcurrentHashMap

Trace `put("b", 2)` with two threads racing on an empty map (capacity 16).

## Step 1 — initTable (lazy)
- Table is null until first write. One thread wins the sizeCtl CAS and
  allocates 16 bins; the other spins/waits on sizeCtl. sizeCtl becomes 12
  (16 * 0.75).

## Step 2 — Position
- `h = spread("b".hashCode())`, `i = (16-1) & h`. Both threads read
  `f = tabAt(tab, i)` via a volatile load.

## Step 3 — Fast path or lock
- If `f == null`: `casTabAt(tab, i, null, newNode)` — winner inserts with no
  lock; loser re-reads and now sees a head node.
- If head exists and `hash != MOVED`: `synchronized (f)` on the bucket head
  only; recheck head identity inside, then append/replace.

## Step 4 — MOVED encounter (during resize)
- If `f.hash == MOVED`, skip locking: follow ForwardingNode to the new table
  (reads) or call `helpTransfer` and move bins (writers).

## Step 5 — Count
- `addCount(1)`: CAS baseCount; on contention hash thread probe to a
  CounterCell and CAS that. Check `sumCount() >= sizeCtl` for resize.

## Step 6 — Verify
- `get("b")` does a lock-free volatile walk; `size()` returns the cell sum.
- Null probe: `put(null, 1)` must throw NPE — assert it in your test.
