# Debugging: LinkedList Deep Dive

## 1. Inspect the live store
- `java.util.LinkedList` internals are visible with `--add-opens java.base/java.util=ALL-UNNAMED`
  plus reflection on the backing fields (see CODE_DEEP_DIVE.md patterns).
- Check: array length vs size (array-backed), first/last/size (linked),
  root/black-height (tree), table/sizeCtl/cells (concurrent).

## 2. Reproduce index/position bugs minimally
- Key fact: node(index) walks from nearer end: index < (size>>1) ? forward from first : backward from last.
- Write a 10-line main that inserts 3 entries and prints position-derived
  values; assert size after every step.

## 3. Catch concurrent modification early
- Symptom: `ConcurrentModificationException` from `ListItr / DescendingIterator`.
- Cause: unsynchronized; structural change must flow through link/unlink (size+modCount).
- Fix: single-thread the mutation, use the iterator's own remove/set, or
  switch to the concurrent variant documented in THEORY.md.

## 4. Null-behavior probe
- Fact: fail-fast iterators via modCount/expectedModCount; ListIterator.set/remove legal.
- Test `get(null)` / `put(null, v)` / `add(null)` explicitly; CHM-style maps
  throw NPE by design — that is a signal, not a bug.

## 5. Performance anomaly checklist
- See PERFORMANCE.md; confirm implements Deque: permits null elements (unlike ArrayDeque); push/pop = addFirst/removeFirst and no sentinel node: size==0 means first==last==null, every mutation branches on null before blaming the JIT.
- Use `-Xlog:gc` to separate copy/GC pauses from algorithmic cost.

## 6. Logging recipe
- Log size + capacity (or tree height / cell count) at insert milestones
  (10, 10K, 1M) to distinguish growth cost from steady-state cost.
