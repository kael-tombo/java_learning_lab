# ArrayList Deep Dive — Theoretical Foundation

## Core Concept

`java.util.ArrayList<E>` is a resizable array: an `Object[] elementData` plus a
`size` counter. Elements are stored **contiguously**, so `get(i)` is a single
indexed load — no pointer chasing, prefetcher-friendly scans, cache-line packed
iteration.

## Growth: 1.5×, Lazily, Exactly Once at Default

JDK 23 `grow(int minCapacity)`:

```java
int newCapacity = ArraysSupport.newLength(oldCapacity,
        minCapacity - oldCapacity,   // minimum growth
        oldCapacity >> 1);           // preferred growth  -> +50%
return elementData = Arrays.copyOf(elementData, newCapacity);
```

- **First allocation is lazy**: `new ArrayList<>()` allocates no array. The first
  `add` allocates `DEFAULT_CAPACITY = 10`.
- Growth factor is **1.5×** (`oldCap + oldCap/2`), not HashMap's 2×.
  `ArraysSupport.newLength` also clamps against `MAX_ARRAY_SIZE`
  (`Integer.MAX_VALUE - 8`) and handles overflow.
- `ensureCapacity(n)` lets you pay the copy once up front; `trimToSize()`
  releases slack after bulk loading.

### Why 1.5× and Not 2×

Amortized analysis: each element is copied O(log n) times over its lifetime
(growth steps are n, 1.5n, 1.5²n, …). A factor of 1.5 halves the *wasted slack*
of 2× (up to 50% unused vs up to 100%) at the price of more frequent copies
(log₁.₅ n ≈ 1.71·log₂ n steps). Total copy volume stays O(n) either way —
the factor is a constant-factor trade-off between memory waste and copy count,
not an asymptotic one.

### The Copy Cost Is What `ensureCapacity` Exists For

Appending n elements without pre-sizing performs Σ growth copies ≈ **3n element
moves** at factor 1.5 (geometric series: n·(1/1 + 1/1.5 + 1/1.5² + …) = 3n).
Pre-sizing to n makes it exactly n. Both are O(n), but the constant differs 3×.

## Operation Costs

| Operation | Cost | Notes |
|-----------|------|-------|
| get(i) / set(i, e) | O(1) | direct index |
| add(e) at end | O(1) amortized | O(n) when growing |
| add(i, e) | O(n−i) shift | worst case O(n) at head |
| remove(i) | O(n−i) shift | |
| contains / indexOf | O(n) | linear scan, `equals` per element |
| remove(Object) | O(n) locate + O(n−i) shift | two passes |

`removeLast`/`addLast` are the cheap end: zero shifting. `addFirst`/`removeFirst`
are the expensive end. (Java 21's `SequencedCollection` default `reversed()` and
`addFirst` on ArrayList make this explicit in the API.)

## The modCount / Fail-Fast Contract

Every structural mutation increments `modCount` (a `protected` field inherited
from `AbstractList` — which is why subclassing to override `modCount` behavior is
possible and dangerous). Iterators capture `expectedModCount` and throw
`ConcurrentModificationException` on drift. The check runs once per `next()`, so:

- Modification through `ListIterator.remove/set` updates `expectedModCount` — legal.
- Modification via `list.remove(...)` during iteration — illegal, caught at next step.
- Concurrent modification by another thread — *may not* be caught; the check is
  a heuristic, not a guarantee. Never use fail-fast as a synchronization device.

## Memory Layout: Why ArrayList Usually Wins

An `ArrayList<Integer>` slot is one compressed reference (4 bytes) in contiguous
memory; a `LinkedList<Integer>` slot is a 24-byte node *plus* the boxed Integer,
scattered across the heap. Consequences:

- **Scan cost**: ArrayList walks contiguous words (one cache line holds ~16
  slots); LinkedList dereferences twice per element (next pointer, then item),
  each dereference a potential cache miss.
- **GC cost**: N nodes are N objects to trace vs one array object.
- **Shifting** is memcpy-class (System.arraycopy is optimized to block moves),
  while LinkedList's "O(1) insertion" still pays for the O(n/2) walk to *reach*
  the position.

## The `elementData == DEFAULTCAPACITY_EMPTY_ELEMENTDATA` Sentinel

Two distinct empty-array singletons exist (`DEFAULTCAPACITY_EMPTY_ELEMENTDATA`
vs `EMPTY_ELEMENTDATA`) so that `new ArrayList<>()` grows to 10 on first add,
while `new ArrayList<>(0)` stays at 0 and grows to exactly what's needed. This
subtle distinction is why `ensureCapacity` has that odd guard clause — the JDK
must not pre-grow a caller-constructed zero-capacity list.

## Concurrency

ArrayList is **unsynchronized**: concurrent structural writes race on
`elementData`/`size` and can produce lost elements, `ArrayIndexOutOfBounds`, or
torn state (size doesn't match contents). The documented wrapper is
`Collections.synchronizedList` — which still doesn't protect iteration (its
iterator needs manual `synchronized(list)` blocks). For true concurrent access,
`CopyOnWriteArrayList` trades write cost (full array copy per mutation) for
lock-free reads and snapshot iteration.

## Key Invariants

1. `0 ≤ size ≤ elementData.length` after every public operation.
2. Elements occupy `elementData[0 .. size-1]`; slots `[size .. length)` are null
   — stale references beyond `size` are **cleared on remove** to avoid leaking
   memory the list logically released.
3. `modCount` increments exactly on structural changes, never on `set(i, e)`.
4. Growth never shrinks — only `trimToSize()` reduces capacity.
