# EXERCISES — Heaps (Advanced Use) (`08-heaps`)
> Implement from scratch · trace by hand · cover edge cases. Java templates included.

## Setup
```bash
cd labs/data-structures/08-heaps
javac src/main/java/**/*.java  # or open in your IDE
jshell  # for quick traces
```

## E1 — From-scratch skeleton (core)
Fill `HeapApps.java`. Do NOT use `java.util` for the core logic (tests may use it as oracle).
```java
public class HeapApps<T> {
    private int size = 0;
    private int modCount = 0;
    // TODO: add backing store (array / nodes / buckets / root)
    public int size() { return size; }
    public boolean isEmpty() { return size == 0; }
    // TODO: implement heapify-O(n), push, pop, meld
    // TODO: implement remaining: d-ary-heap, two-heap-median, A-star-frontier, streaming-topK
    private void checkInvariant() {
        assert size >= 0;
        // TODO: assert structure invariant for heaps
    }
}
```
Tasks: constructor(s), clear, core mutators, `toString`/visualize, fail-fast iterator.
Edge cases: empty op (throw `NoSuchElementException`), single element, null policy (reject or document), duplicates.

## E2 — Trace by hand (paper first)
1. Start empty; apply sequence: insert 5,2,8,2, then delete one 2, then lookup 8.
   Draw backing state after EACH step for heaps.
2. Show hash / rotation / sift / trie-branch step explicitly (as applicable).
3. Predict `size`, `capacity/height/bloom-bits` after each step; then verify in `jshell`.

## E3 — Edge-case battery
Write JUnit 5 tests (`HeapAppsTest.java`):
```java
@Test void emptyThrows() { assertThrows(NoSuchElementException.class, () -> s.remove()); }
@Test void singleElementRoundTrip() { /* add one, get/remove, assert empty invariant */ }
@Test void duplicatesAndNulls() { /* define policy, assert documented behavior */ }
@Test void resizeOrRebalanceTrigger() { /* force threshold; assert invariant + all elements reachable */ }
@Test void iteratorFailFast() { /* mutate during iteration; expect ConcurrentModificationException */ }
@Test void oracleVsStdlib() { /* random ops vs ArrayList/HashMap/TreeMap/PriorityQueue as oracle */ }
```
Aim: ≥10 tests, each names the invariant it guards.

## E4 — Complexity probe
Benchmark: n = 1k, 10k, 100k. Time insert + lookup + delete (use `System.nanoTime`, warm up JIT, average 5 runs).
Plot or tabulate. Question: where does the curve bend (resize? GC? hashing? imbalance?)? 1 paragraph.

## E5 — Adversarial input
Craft worst-case input for heaps: sorted input to naive BST, colliding keys to hash table,
reverse-sorted to heap-sort path, shared-prefix flood to trie, high-α to bloom sizing.
Show degradation, then apply fix (shuffle / randomized hash / balance / larger m,k / compression).

## E6 — API design
Wrap `HeapApps` with a minimal clean API: factory methods, `Optional` returns for lookup,
`Comparator` injection where ordering matters. Document Big-O per method in Javadoc.
Review: does any method leak representation (expose internal array/node)? Fix it.

## E7 — Debugging drill
Inject one bug (off-by-one in resize copy; forget `size++`; broken `hashCode`; missing rotation;
sift wrong child; trie missing terminal flag). Write the failing test FIRST, then fix.
Record symptom → root cause → invariant violated.

## E8 — Interview rep (timed, 25 min)
Implement the headline op of heaps on a whiteboard from memory
(e.g., BST delete / heap sift-down / trie insert / hash resize / linked reverse).
Narrate invariant aloud. Then type it and make tests green.

## E9 — Representation swap
Reimplement ONE operation on the alternative backing (e.g., array→linked, chaining→open
addressing, recursive→iterative). Benchmark both at n=50k. When does the alternative win?
Write 3 bullets: locality effect, allocation effect, code-complexity effect.

## E10 — Teach-back (15 min, no notes)
Explain to a peer (or rubber duck, recorded): layout diagram → invariant sentence →
one op's code path → its Big-O derivation → one production use among streaming analytics, pathfinding, job scheduling, median maintenance.
Grade yourself: diagram correct? derivation or just recital? If recital, redo MATH §7.

## Done checklist
- [ ] Skeleton complete, invariant asserts pass.
- [ ] Trace matches execution.
- [ ] Edge battery green incl. fail-fast + resize/rebalance.
- [ ] Benchmark table + 1-paragraph interpretation.
- [ ] Adversarial case + fix demonstrated.
