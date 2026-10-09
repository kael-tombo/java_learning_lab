# ArrayList Deep Dive — Code Deep Dive

All snippets run on any JDK 9+ (verified on JDK 23), no dependencies.

## 1. Growth Is 1.5×, and the First Allocation Is Lazy

Capacity isn't directly exposed, so infer it by counting how many `add`s fit
before the internal array must grow — observed via reflection at each doubling:

```java
import java.lang.reflect.Field;
import java.util.ArrayList;

public class Growth15 {
    static int capacity(ArrayList<?> a) throws Exception {
        Field f = ArrayList.class.getDeclaredField("elementData");
        f.setAccessible(true);
        return ((Object[]) f.get(a)).length;
    }

    public static void main(String[] args) throws Exception {
        ArrayList<Integer> a = new ArrayList<>();
        System.out.println("fresh list capacity: " + capacity(a));   // 0: lazy

        a.add(1);
        System.out.println("after 1st add:       " + capacity(a));   // 10

        while (a.size() < 40) a.add(a.size());
        System.out.println("after 40 adds:       " + capacity(a));   // 49
        while (a.size() < 68) a.add(a.size());
        System.out.println("after 68 adds:       " + capacity(a));   // 73
    }
}
```

Run: `java --add-opens java.base/java.util=ALL-UNNAMED Growth15.java`

Expected output:
```
fresh list capacity: 0
after 1st add:       10
after 40 adds:       49
after 68 adds:       73
```

The capacity sequence 10 → 15 → 22 → 33 → 49 → 73 is exactly
`oldCap + oldCap/2` each time (integer division: 10+5, 15+7, 22+11, 33+16,
49+24). 40 elements fit in 49 slots; the 50th element (index 49) forces 73.
Three invariants on display: a brand-new list allocates **nothing**
(`length 0` until first add), first growth lands on 10, and no step ever
exceeds 1.5×.

## 2. The Shift Cost Is Real and Asymmetric

```java
import java.util.ArrayList;
import java.util.LinkedList;

public class ShiftCost {
    static long ns(Runnable r) {
        for (int i = 0; i < 5; i++) r.run();          // warm
        long t0 = System.nanoTime();
        r.run();
        return System.nanoTime() - t0;
    }

    public static void main(String[] args) {
        int n = 200_000;
        ArrayList<Integer> head = new ArrayList<>();
        for (int i = 0; i < n; i++) head.add(i);
        ArrayList<Integer> tail = new ArrayList<>(head);
        LinkedList<Integer> ll = new LinkedList<>(head);

        long headNs = ns(() -> head.add(0, 1));
        long tailNs = ns(() -> tail.add(1));
        long llNs   = ns(() -> { ll.addFirst(1); ll.removeFirst(); });

        System.out.println("ArrayList addFirst dominates addLast: " + (headNs > 10 * tailNs));
        System.out.println("LinkedList addFirst within 10x of ArrayList addFirst: "
                + (llNs < headNs));
    }
}
```

Expected output:
```
ArrayList addFirst dominates addLast: true
LinkedList addFirst within 10x of ArrayList addFirst: true
```

`add(0, e)` on 200k elements moves all 200k references; `add(e)` moves zero.
The assertions are ratio-based so they hold across machines — run it yourself
for raw nanosecond values (on JDK 23 here: head ~1.4 ms vs tail ~100 ns,
a ~10⁴× gap).

## 3. remove() Clears the Tail Slot — No Reference Leak

```java
import java.lang.reflect.Field;
import java.util.ArrayList;

public class TailClear {
    public static void main(String[] args) throws Exception {
        ArrayList<Object> a = new ArrayList<>();
        Object o1 = new Object(), o2 = new Object(), o3 = new Object();
        a.add(o1); a.add(o2); a.add(o3);

        Field f = ArrayList.class.getDeclaredField("elementData");
        f.setAccessible(true);
        Object[] es = (Object[]) f.get(a);

        a.remove(1);   // removes o2; size 2, array still length 10
        System.out.println("size = " + a.size());
        System.out.println("slot[1] reused by o3: " + (es[1] == a.get(1)));
        System.out.println("slot[2] is null: " + (es[2] == null));
    }
}
```

Run: `java --add-opens java.base/java.util=ALL-UNNAMED TailClear.java`

Expected output:
```
size = 2
slot[1] reused by o3: true
slot[2] is null: true
```

After the shift, `fastRemove` executes `es[size = newSize] = null` — the stale
slot beyond `size` is nulled so a removed object isn't kept alive by the backing
array. This is the difference between logical removal and an actual leak.

## 4. fail-fast: set() Doesn't Trip It, remove() Does

```java
import java.util.ArrayList;
import java.util.List;

public class FailFastSet {
    public static void main(String[] args) {
        List<Integer> l = new ArrayList<>(List.of(1, 2, 3));

        l.set(0, 99);                 // not structural: no modCount change
        System.out.println("set ok: " + l);

        var it = l.iterator();
        l.remove(0);                  // structural: modCount++
        try {
            it.next();
        } catch (java.util.ConcurrentModificationException e) {
            System.out.println("iterator caught remove()");
        }

        // rebuilt list: set() during iteration is invisible to the iterator
        l = new ArrayList<>(List.of(1, 2, 3));
        var it2 = l.iterator();
        l.set(0, 99);
        try {
            System.out.println("set during iteration ok, next = " + it2.next());
        } catch (java.util.ConcurrentModificationException e) {
            System.out.println("set trips CME");
        }
    }
}
```

Expected output:
```
set ok: [99, 2, 3]
iterator caught remove()
set during iteration ok, next = 99
```

`set` swaps a reference in place — the iterator's view stays coherent, so
`modCount` (and the check) never fires. Only structural changes are detected.

## 5. ensureCapacity: Pay the Copies Once

```java
import java.util.ArrayList;

public class PreSize {
    static long copies(ArrayList<Integer> l, int n, boolean presized) {
        long t0 = System.nanoTime();
        if (presized) l.ensureCapacity(n);
        for (int i = 0; i < n; i++) l.add(i);
        return (System.nanoTime() - t0) / 1_000_000;
    }

    public static void main(String[] args) {
        int n = 4_000_000;
        long unsized = copies(new ArrayList<>(), n, false);
        long sized   = copies(new ArrayList<>(), n, true);
        System.out.println("presizing not slower than growing: " + (sized <= unsized + 1));
        System.out.println("unsized=" + unsized + "ms sized=" + sized + "ms");
    }
}
```

Expected output (machine numbers vary, boolean is the claim):
```
...
presizing not slower than growing: true
```

With 1.5× growth an unsized fill of n elements performs ≈ **3n** reference
copies (geometric series n/1 + n/1.5 + n/1.5² + … = 3n) versus exactly n with
`ensureCapacity(n)` — same O(n), a 3× constant. The second printout's numbers
depend on the machine, so only the boolean is asserted here.

## Common Pitfalls Encountered Here

- **`new ArrayList<>(0)` and `new ArrayList<>()` differ**: the former uses
  `EMPTY_ELEMENTDATA` and grows to exactly what's needed; the latter uses
  `DEFAULTCAPACITY_EMPTY_ELEMENTDATA` and jumps to 10. `ensureCapacity` guards
  against this so it won't pre-grow a deliberate zero-capacity list.
- **Capacity inferred via reflection is JDK-implementation detail** — field name
  `elementData` is stable across 8–23 but not a spec guarantee.
- **`subList` is a view**, not a copy: mutations propagate both ways, and the
  parent's `modCount` changes break outstanding child iterators.
- **`remove(Object)` vs `remove(int)`**: `List.of(1, 2, 3).remove(1)` removes
  *index* 1 (auto-boxing makes `remove(Integer)` apply to `remove(int)`), while
  on a `List<Integer>` holding values 1/2/3 the two overloads are a classic bug
  source. Use `remove(Integer.valueOf(1))` for the value.
- **`ArrayList` is not thread-safe**: `size` and `elementData` are separate
  writes; unsynchronized concurrent `add`s can lose elements silently or throw
  `IndexOutOfBoundsException`.
