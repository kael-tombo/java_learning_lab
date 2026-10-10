# Debugging: TreeMap / TreeSet

## 1. Inspect the live store
- `java.util.TreeMap / java.util.TreeSet` internals are visible with `--add-opens java.base/java.util=ALL-UNNAMED`
  plus reflection on the backing fields (see CODE_DEEP_DIVE.md patterns).
- Check: array length vs size (array-backed), first/last/size (linked),
  root/black-height (tree), table/sizeCtl/cells (concurrent).

## 2. Reproduce index/position bugs minimally
- Key fact: color literal: RED=false, BLACK=true; height bound <= 2*log2(n+1).
- Write a 10-line main that inserts 3 entries and prints position-derived
  values; assert size after every step.

## 3. Catch concurrent modification early
- Symptom: `ConcurrentModificationException` from `NavigableSubMap view classes`.
- Cause: unsynchronized; null keys rejected under natural ordering, allowed only if comparator handles them.
- Fix: single-thread the mutation, use the iterator's own remove/set, or
  switch to the concurrent variant documented in THEORY.md.

## 4. Null-behavior probe
- Fact: live bounded views: subMap/headMap/tailMap (+ Navigable variants); descendingMap reversed view.
- Test `get(null)` / `put(null, v)` / `add(null)` explicitly; CHM-style maps
  throw NPE by design — that is a signal, not a bug.

## 5. Performance anomaly checklist
- See PERFORMANCE.md; confirm iteration ascending via on-the-fly successor links; fail-fast via modCount and compare(key,key) null/type pre-check: addEntryToEmptyMap calls it on empty map first before blaming the JIT.
- Use `-Xlog:gc` to separate copy/GC pauses from algorithmic cost.

## 6. Logging recipe
- Log size + capacity (or tree height / cell count) at insert milestones
  (10, 10K, 1M) to distinguish growth cost from steady-state cost.
