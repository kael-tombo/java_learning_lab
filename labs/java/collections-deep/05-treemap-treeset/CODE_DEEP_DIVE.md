# TreeMap / TreeSet — Code Deep Dive

All snippets run on any JDK 9+ (verified on JDK 23), no dependencies.

## 1. compareTo == 0 Is Identity — equals() Disagrees

The single most important TreeMap/TreeSet gotcha, demonstrated:

```java
import java.util.TreeSet;

public class CompareVsEquals {
    static final class CaseInsensitive implements Comparable<CaseInsensitive> {
        final String s;
        CaseInsensitive(String s) { this.s = s; }
        @Override public int compareTo(CaseInsensitive o) {
            return s.toLowerCase().compareTo(o.s.toLowerCase());
        }
        @Override public boolean equals(Object o) {
            return o instanceof CaseInsensitive c && s.equals(c.s);  // CASE-SENSITIVE
        }
        @Override public String toString() { return s; }
    }

    public static void main(String[] args) {
        TreeSet<CaseInsensitive> set = new TreeSet<>();
        set.add(new CaseInsensitive("Apple"));
        boolean added = set.add(new CaseInsensitive("APPLE"));
        System.out.println("second add returned: " + added);          // false!
        System.out.println("size: " + set.size());                     // 1
        System.out.println("contains exact 'APPLE': "
                + set.contains(new CaseInsensitive("APPLE")));         // true (compareTo!)
        System.out.println("equals() of elements: "
                + set.first().equals(new CaseInsensitive("APPLE")));   // false
    }
}
```

Expected output:
```
second add returned: false
size: 1
contains exact 'APPLE': true
equals() of elements: false
```

The set says the element is present; `equals` says the stored element isn't
equal to the probe. Both are "right" under their own contract. Never let a
sorted set's equivalence and `equals` diverge in the same codebase.

## 2. Range Views Are Live and Enforce Their Bounds

```java
import java.util.NavigableMap;
import java.util.TreeMap;

public class RangeViews {
    public static void main(String[] args) {
        TreeMap<Integer, String> m = new TreeMap<>();
        for (int i = 0; i < 10; i++) m.put(i, "v" + i);

        NavigableMap<Integer, String> band = m.subMap(2, true, 7, false);
        System.out.println("band = " + band.keySet());

        try {
            band.put(99, "via-view");
            System.out.println("put(99) accepted; m.containsKey(99) = "
                    + m.containsKey(99));
        } catch (IllegalArgumentException e) {
            System.out.println("put(99) rejected: IllegalArgumentException");
        }

        band.put(6, "updated");                    // inside bounds -> writes through
        System.out.println("write-through: m.get(6) = " + m.get(6));

        NavigableMap<Integer, String> narrowed = m.subMap(5, true, 7, false);
        System.out.println("composed view = " + narrowed.keySet());
        System.out.println("ceiling(4) in band = " + band.ceilingKey(4));
        System.out.println("lower(2) in band = " + band.lowerKey(2));
    }
}
```

Run: `java RangeViews.java`

Expected output:
```
band = [2, 3, 4, 5, 6]
put(99) rejected: IllegalArgumentException
write-through: m.get(6) = updated
composed view = [5, 6]
ceiling(4) in band = 4
lower(2) in band = null
```

Two behaviors on display: **writes inside the band propagate to the backing
map** (`m.get(6)` changes), while **writes outside it are refused outright**
with `IllegalArgumentException` — a view is a window with a frame, not a
filter. `lower(2)` returns null because the band starts *at* 2 inclusively
and there is nothing below it inside the view.

## 3. Nearest-Neighbor Lookups HashMap Can't Do

```java
import java.util.TreeMap;

public class Navigable {
    public static void main(String[] args) {
        TreeMap<Integer, String> scores = new TreeMap<>();
        scores.put(55, "F"); scores.put(60, "D"); scores.put(75, "C");
        scores.put(82, "B"); scores.put(91, "A");

        System.out.println("first = " + scores.firstKey() + " " + scores.firstEntry().getValue());
        System.out.println("last  = " + scores.lastKey() + " " + scores.lastEntry().getValue());
        System.out.println("ceiling(76) = " + scores.ceilingKey(76));   // >= 76
        System.out.println("floor(76)   = " + scores.floorKey(76));     // <= 76
        System.out.println("higher(82)  = " + scores.higherKey(82));    // > 82
        System.out.println("lower(82)   = " + scores.lowerKey(82));     // < 82
        System.out.println("descending keys = " + scores.descendingKeySet());
    }
}
```

Expected output:
```
first = 55 F
last  = 91 A
ceiling(76) = 82
floor(76)   = 75
higher(82)  = 91
lower(82)   = 75
descending keys = [91, 82, 75, 60, 55]
```

Six operations, each O(log n), all impossible on a HashMap without materializing
and sorting keys.

## 4. TreeSet vs HashSet: Set Algebra Costs

```java
import java.util.HashSet;
import java.util.TreeSet;

public class SetAlgebra {
    public static void main(String[] args) {
        TreeSet<Integer> a = new TreeSet<>();
        TreeSet<Integer> b = new TreeSet<>();
        for (int i = 0; i < 10; i++) a.add(i);
        for (int i = 5; i < 15; i++) b.add(i);

        TreeSet<Integer> union = new TreeSet<>(a);
        union.addAll(b);
        TreeSet<Integer> inter = new TreeSet<>(a);
        inter.retainAll(b);
        System.out.println("union = " + union);
        System.out.println("intersection = " + inter);

        HashSet<Integer> ha = new HashSet<>(a), hb = new HashSet<>(b);
        ha.addAll(hb);
        System.out.println("HashSet union sorted? " + new java.util.TreeSet<>(ha));
        System.out.println("TreeSet keeps order through copy: " + new TreeSet<>(new TreeSet<>(b)));
    }
}
```

Expected output:
```
union = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
intersection = [5, 6, 7, 8, 9]
HashSet union sorted? [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
TreeSet keeps order through copy: [5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
```

Note the last line: copying one TreeSet into another *preserves* the sorted
order without re-sorting (iterator already ascends); copying from a HashSet
into a TreeSet costs O(n log n) to establish order that a TreeSet would have
maintained incrementally anyway.

## 5. Null Keys: The Empty-Map Pre-Check

```java
import java.util.Comparator;
import java.util.TreeMap;

public class NullKeys {
    public static void main(String[] args) {
        try {
            new TreeMap<String, Integer>().put(null, 1);   // natural ordering
        } catch (NullPointerException e) {
            System.out.println("natural ordering rejects null");
        }
        try {
            new TreeMap<String, Integer>(Comparator.nullsFirst(String::compareTo))
                    .put(null, 1);
            System.out.println("custom nullsFirst comparator accepts null");
        } catch (NullPointerException e) {
            System.out.println("still rejected");
        }
    }
}
```

Expected output:
```
natural ordering rejects null
custom nullsFirst comparator accepts null
```

The rejection happens **before** insertion even on an empty map — the source
calls `compare(key, key)` first (`addEntryToEmptyMap`) precisely so the type
and null contract is enforced at the boundary, not deep in the tree walk.

## Common Pitfalls Encountered Here

- **`TreeSet.equals` vs membership**: `set.contains(x)` uses ordering,
  `set.equals(other)` uses `AbstractSet.equals` (size + `containsAll`) — they
  route through the same comparator equivalence, but a *List* compared against
  a TreeSet uses `equals` element-wise. Mixing the two contracts causes
  one-directional equality (`treeSet.equals(list)` may be false while
  `list.equals(treeSet)` is also false — at least they're consistent here).
- **Natural ordering CCE at first use**: a `TreeMap` built with an un-Comparable
  key type constructs fine and fails on the first `put` — generic type
  parameters don't enforce `Comparable`.
- **`headMap(k)` excludes k**; `headMap(k, true)` includes it. Forgetting the
  boolean inclusive flag silently drops boundary elements.
- **Iteration is O(n) with O(log n) worst per-step successor finds** — but
  don't assume `next()` is O(1): the successor of a deep right-subtree node
  walks up multiple parents.
- **TreeMap is not synchronized** — same fail-fast iterator contract as
  everything else; for concurrent sorted maps consider `ConcurrentSkipListMap`
  (O(log n) too, lock-free reads).
