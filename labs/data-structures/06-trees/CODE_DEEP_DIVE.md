# CODE_DEEP_DIVE — Trees (Traversal & Structure) (`06-trees`)
> Reference Java implementation + resize / hashing / balancing pitfalls.

## 1. Reference implementation (`TreeOps.java`, trimmed)
```java
import java.util.*;
public class TreeOps<T extends Comparable<T>> {
    private static final int DEFAULT_CAP = 16;
    private static final float LOAD_FACTOR = 0.75f;
    private Object[] table;      // array / buckets / heap array (per structure)
    private Node<T> root;        // tree/trie root (null when empty)
    private int size = 0, modCount = 0;

    static class Node<T> {
        T key; Node<T> left, right; int height = 1; // trees; omit for hash/heap
        Node(T k) { key = k; }
    }

    public TreeOps() { table = new Object[DEFAULT_CAP]; }

    // --- hashing (hash-table labs; keep for others as utility) ---
    private int hash(Object k) {
        int h = k.hashCode();
        h ^= (h >>> 20) ^ (h >>> 12);
        return h ^ (h >>> 7) ^ (h >>> 4); // spread (cf. HashMap.hash)
    }

    // --- heap sift (heap labs) / BST insert (tree labs) sketch ---
    public void add(T x) {
        Objects.requireNonNull(x);
        ensureCapacity();
        // structure-specific insert: append+siftUp | bucket-put | BST-insert+rebalance | trie-walk
        size++; modCount++;
        assert invariant();
    }

    private void ensureCapacity() {
        if (size >= table.length * LOAD_FACTOR) resize();
    }

    private void resize() {
        Object[] old = table;
        table = new Object[old.length * 2]; // geometric: NEVER +constant
        size = 0;
        for (Object o : old) if (o != null) reinsert(o); // rehash / re-place
    }

    @SuppressWarnings("unchecked")
    private void reinsert(Object o) { /* place without recursive resize */ size++; }

    private boolean invariant() {
        if (size < 0 || size > table.length * 4) return false;
        // + per-structure: heap order / BST order / chain reachability / trie terminals
        return true;
    }
}
```
Variants: linked version uses `head/tail` + `static class Node{T v; Node<T> next, prev;}`;
heap keeps `array` + `siftUp/siftDown`; trie uses `Node{Map<Character,Node> next; boolean word;}`;
bloom uses `BitSet bits; int m,k;` with double-hashing.

## 2. Pitfall catalog (check each before submitting)
1. **Resize:** linear growth (+N) ⇒ O(n²); fix = ×2 (or ×1.5). Forgetting to rehash with new mask strands keys.
2. **Hashing:** using `hashCode()%m` with negative hash; fix = `spread(h) & (m-1)` (power-of-2 m) or `floorMod`.
3. **Mutable keys:** key mutated after `put` ⇒ lost entry; fix = immutable keys / defensive copy / document.
4. **equals/hashCode mismatch:** equal objects, different hashes ⇒ duplicates; fix = override both, same fields.
5. **BST delete:** 2-child case must splice successor (min of right), update parent+height; test all 3 cases.
6. **Balancing:** forgetting `height` update after rotation; double rotation order (LR/RL); fix = assert balance factor in tests.
7. **Heap index:** 0-based `parent=(i-1)/2, left=2i+1, right=2i+2`; 1-based confusion ⇒ wrong child sift.
8. **Trie terminal:** prefix node vs word node — missing `isWord` flag returns false positives on prefixes.
9. **Iterator:** memorize `expectedModCount`; every structural write bumps `modCount`.
10. **Overflow/recursion:** `mid=(lo+hi)/2` overflows; use `lo+(hi-lo)/2`. Deep recursion ⇒ `StackOverflowError`; provide iterative DFS/traverse.
11. **Null policy:** decide once (reject with `requireNonNull` vs allow + document); `TreeMap` forbids null with natural ordering.
12. **Concurrency:** check-then-act races; use `ConcurrentHashMap` / locks / copy-on-write — never "synchronized sometimes".

## 3. Java stdlib notes
- `ArrayList` (growth 1.5×), `ArrayDeque` (power-of-2 ring, no nulls), `HashMap` (treeify bins at 8, resize 2×),
  `TreeMap` (Red-Black), `PriorityQueue` (binary heap, no decrease-key), Guava `BloomFilter` (double-hash, optimal k).
- Read the Javadoc complexity notes for the counterpart of trees before MINI_PROJECT.

## 4. Testing recipe
```java
// oracle test: random ops vs stdlib
Random r = new Random(42);
for (int i = 0; i < 5000; i++) {
    int op = r.nextInt(3), v = r.nextInt(50);
    // apply to both TreeOps and oracle; assert size/contains/iteration agree
}
// invariant test: after every 100 ops assert checkInvariant()
```
Plus: empty/singleton, duplicates, null, resize-boundary (size = cap−1, cap, cap+1), adversarial order.

## 5. Performance notes
- Warm up JIT (≥3 throwaway runs), average ≥5 timed runs, report median + p95 if possible.
- Measure resize pauses separately (log n at which copies spike).
- For linked/tree: allocation rate + GC pressure often dominate wall-clock — note it.

## 6. Review checklist
- [ ] Geometric resize + rehash covered by test at threshold.
- [ ] Hash/spread/comparator correct incl. negatives, nulls, duplicates.
- [ ] Balance/sift/rotation asserted, not just "looks right".
- [ ] Fail-fast iterator + modCount.
- [ ] Javadoc Big-O per public method matches measured behavior.
