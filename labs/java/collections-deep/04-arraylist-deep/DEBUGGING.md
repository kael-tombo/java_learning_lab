# Debugging: ArrayList Deep Dive

## 1. Inspect the live store
- `java.util.ArrayList` internals are visible with `--add-opens java.base/java.util=ALL-UNNAMED`
  plus reflection on the backing fields (see CODE_DEEP_DIVE.md patterns).
- Check: array length vs size (array-backed), first/last/size (linked),
  root/black-height (tree), table/sizeCtl/cells (concurrent).

## 2. Reproduce index/position bugs minimally
- Key fact: growth 1.5x: ArraysSupport.newLength(oldCap, minGrowth, oldCap>>1); copy via Arrays.copyOf.
- Write a 10-line main that inserts 3 entries and prints position-derived
  values; assert size after every step.

## 3. Catch concurrent modification early
- Symptom: `ConcurrentModificationException` from `SubList view + fail-fast Itr/ListItr`.
- Cause: unsynchronized; use Collections.synchronizedList (manual sync for iteration) or CopyOnWriteArrayList.
- Fix: single-thread the mutation, use the iterator's own remove/set, or
  switch to the concurrent variant documented in THEORY.md.

## 4. Null-behavior probe
- Fact: fastRemove nulls the freed slot (elementData[--size]=null) to avoid leaks.
- Test `get(null)` / `put(null, v)` / `add(null)` explicitly; CHM-style maps
  throw NPE by design — that is a signal, not a bug.

## 5. Performance anomaly checklist
- See PERFORMANCE.md; confirm set(i,e) replaces without modCount++; structural ops (add/remove/grow) increment it and two empty singletons: DEFAULTCAPACITY_EMPTY_ELEMENTDATA (grows to 10) vs EMPTY_ELEMENTDATA (grows exact) before blaming the JIT.
- Use `-Xlog:gc` to separate copy/GC pauses from algorithmic cost.

## 6. Logging recipe
- Log size + capacity (or tree height / cell count) at insert milestones
  (10, 10K, 1M) to distinguish growth cost from steady-state cost.
