# Math Foundation: ArrayList

## Growth formula (JDK 23)
- `newCapacity = ArraysSupport.newLength(oldCap, minGrowth, oldCap >> 1)`:
  preferred growth is +50% (1.5x), clamped against MAX_ARRAY_SIZE
  (Integer.MAX_VALUE - 8) with overflow handling.

## Amortized 3n copy volume
- Appending n elements from 10 at 1.5x copies 10 + 15 + 22 + ... ~ 3n total
  element moves (geometric series n/(1 - 1/1.5) = 3n). Presized: exactly n.
  Both O(n); the constant differs 3x — that is what ensureCapacity buys.

## Why 1.5x and not 2x
- 2x wastes up to ~50% slack after a grow (array half empty); 1.5x wastes at
  most ~33%. Price: log_1.5(n) ~= 1.71 * log_2(n) grow steps — more copies,
  less waste. Same asymptotics, different constant trade-off.

## Operation costs from the layout
- get/set: one indexed load, O(1). add(i,e)/remove(i): (n-i) contiguous words
  shifted — O(n) worst case at head, O(1) at tail (removeLast/addLast).
- contains/indexOf: O(n) equals scans; remove(Object): O(n) locate + O(n-i)
  shift (two passes).

## Worked numbers
- 1M appends unsized: ~28 grows (log_1.5(1M/10)), ~3M word moves total.
- 1M appends presized (ensureCapacity(1M)): 1M moves, zero grows.
- Slot size 4 bytes (compressed ref): 1M list = 4 MB array vs 24 MB+ for nodes.

## Huge-array edge
- Near MAX_ARRAY_SIZE (Integer.MAX_VALUE - 8) newLength stops applying +50%
  and grows by the minimum instead; past that it throws OutOfMemoryError
  ("Requested array size exceeds VM limit") rather than wrapping negative.
- trimToSize on a 1M-capacity 10-live list frees ~4 MB in one copy — the only
  supported shrink path, since growth never shrinks on its own.
