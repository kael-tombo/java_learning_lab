# Internals: CopyOnWriteArrayList Source Map

File: `src/java.base/share/classes/java/util/concurrent/CopyOnWriteArrayList.java`
(OpenJDK; Doug Lea, JSR 166).

## Fields

- `private transient volatile Object[] array` — sole shared state.
- `final transient Object lock = new Object()` — writer mutex (NOT the
  list monitor; external `synchronized(list)` doesn't exclude writers).
- `getArray()` / `setArray(Object[])` — volatile access pair.

## Key methods

- `add(E e)`: lock → `copyOf(len+1)` → set slot → `setArray`. Returns true.
- `set(int, E)`: lock → copy → `es[i] = e` → `setArray` ALWAYS (equal-value
  heartbeat; source comment: "Ensure volatile write semantics even when
  oldvalue == element").
- `remove(Object)`: snapshot scan `indexOfRange`; miss → return false
  (no lock taken); hit → `remove(o, snapshot, index)` which locks,
  revalidates `snapshot != getArray()` via prefix re-scan, then copies.
- `addIfAbsent(E e)`: mirror image — lock-free `indexOf` hit → return
  false without locking; miss → lock + recheck + copy-add.
- `iterator()`: `new COWIterator<>(getArray(), 0)` — snapshot + cursor.
  `COWIterator.remove/set/add` → `UnsupportedOperationException`.
- `subList` / `forEach` / spliterators operate over snapshots similarly;
  `spliterator` is late-binding/immutable rather than weakly consistent.
- `equals` from `AbstractList` (element-wise) — equals an ArrayList with
  same elements.

## Mutation protocol invariant

No published array is ever written in place. All writes happen to private
copies pre-publication. This single convention is what makes lock-free
reads sound.
