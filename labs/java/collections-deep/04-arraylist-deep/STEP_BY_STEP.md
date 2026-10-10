# Step by Step: ArrayList

Trace `new ArrayList<>(); add x10; add 11th; remove(0); set(0, z)`.

## Step 1 — Construct (no allocation)
- `elementData == DEFAULTCAPACITY_EMPTY_ELEMENTDATA`, size 0. Zero bytes backing.

## Step 2 — First add -> grow to 10
- add detects the default sentinel, allocates `new Object[10]`, stores at [0].
  size 0->1. (With `new ArrayList<>(0)` it would allocate exactly 1 instead.)

## Step 3 — Adds 2..10 fill the array
- Plain stores at [1]..[9], size -> 10. No copies, no modCount subtlety beyond
  the per-add increment.

## Step 4 — 11th add -> grow 10 -> 15
- `grow(11)`: `newLength(10, 1, 5)` = 15; `Arrays.copyOf` moves 10 refs.
  Store 11th at [10]. size -> 11.

## Step 5 — remove(0) -> shift + null
- `System.arraycopy(data, 1, data, 0, 10)` shifts 10 words left; `data[--size]
  = null` clears slot [10] so the removed head can be GC'd. modCount++.

## Step 6 — set(0, z)
- Direct store, returns old value. modCount UNCHANGED — iterators won't notice.

## Step 7 — Presize and trim discipline
- `ensureCapacity(100)` on this 10-live list grows once to 100 (one copy);
  `trimToSize()` then cuts back to exactly 10. Assert capacity via reflection
  after each: 15 -> 100 -> 10, size pinned at 10 throughout.

## Self-check
- Invariant after every step: `0 <= size <= elementData.length`, slots
  `[size..length)` all null.
