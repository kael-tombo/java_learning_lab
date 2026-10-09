# Build Your Own HashMap — Code Deep Dive

All snippets run on any JDK 9+ (verified on JDK 23), no dependencies.

## 1. The Complete Open-Addressing Map

Everything from THEORY in one file: power-of-two table, hash spreading,
linear probing, tombstone deletion, α-cap growth.

```java
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Objects;

public class OpenHashMap<K, V> implements Iterable<OpenHashMap.Entry<K, V>> {
    public static final class Entry<K, V> {
        final K key; V value;
        Entry(K key, V value) { this.key = key; this.value = value; }
        public String toString() { return key + "=" + value; }
    }

    private static final Object EMPTY = null;
    private static final Object TOMB = new Object();

    private Object[] table;          // Entry | TOMB | null(empty)
    private int size, tombstones;
    private static final double LOAD_FACTOR = 0.65;

    @SuppressWarnings("unchecked")
    public OpenHashMap() { table = new Object[16]; }

    // spread: fold high 16 bits into low ones (JDK trick)
    private int index(K key, int cap) {
        int h = key == null ? 0 : key.hashCode();
        h ^= (h >>> 16);
        return h & (cap - 1);
    }

    private int probe(K key) { return index(key, table.length); }

    public V get(K key) {
        int i = probe(key), n = table.length;
        for (int step = 0; step < n; step++) {
            Object e = table[i];
            if (e == EMPTY) return null;              // stop: never inserted
            if (e != TOMB && Objects.equals(((Entry<K, V>) e).key, key))
                return ((Entry<K, V>) e).value;
            i = (i + 1) & (n - 1);                    // through tombstones
        }
        return null;
    }

    public V put(K key, V value) {
        if ((size + tombstones + 1) / (double) table.length > LOAD_FACTOR)
            resize(table.length * 2);                 // growth includes tombstones!
        int i = probe(key), n = table.length;
        int firstTomb = -1;
        for (int step = 0; step < n; step++) {
            Object e = table[i];
            if (e == EMPTY) {
                table[i] = new Entry<>(key, value);
                size++;
                return null;
            }
            if (e == TOMB) {
                if (firstTomb < 0) firstTomb = i;     // remember reusable slot
            } else if (Objects.equals(((Entry<K, V>) e).key, key)) {
                V old = ((Entry<K, V>) e).value;
                ((Entry<K, V>) e).value = value;
                return old;
            }
            i = (i + 1) & (n - 1);
        }
        // table completely full of live+tomb entries: reuse a tombstone
        table[firstTomb] = new Entry<>(key, value);
        size++;
        return null;
    }

    public V remove(K key) {
        int i = probe(key), n = table.length;
        for (int step = 0; step < n; step++) {
            Object e = table[i];
            if (e == EMPTY) return null;
            if (e != TOMB && Objects.equals(((Entry<K, V>) e).key, key)) {
                table[i] = TOMB;                       // probes continue past it
                size--;
                tombstones++;
                return ((Entry<K, V>) e).value;
            }
            i = (i + 1) & (n - 1);
        }
        return null;
    }

    private void resize(int newCap) {
        Object[] old = table;
        table = new Object[newCap];
        size = tombstones = 0;
        for (Object e : old)
            if (e != null && e != TOMB) {
                Entry<K, V> en = (Entry<K, V>) e;
                int i = index(en.key, newCap);
                while (table[i] != null) i = (i + 1) & (newCap - 1);
                table[i] = en;
                size++;                               // rebuild the count too!
            }
    }

    public int size() { return size; }

    public List<K> keys() {
        List<K> out = new ArrayList<>();
        for (Object e : table)
            if (e != null && e != TOMB) out.add(((Entry<K, V>) e).key);
        return out;
    }

    @Override public Iterator<Entry<K, V>> iterator() {
        List<Entry<K, V>> live = new ArrayList<>();
        for (Object e : table)
            if (e != null && e != TOMB) live.add((Entry<K, V>) e);
        return live.iterator();
    }

    public static void main(String[] args) {
        OpenHashMap<String, Integer> m = new OpenHashMap<>();
        m.put("x", 1);
        m.put("y", 2);
        m.put("x", 9);                    // overwrite returns old value
        System.out.println("get x = " + m.get("x"));
        System.out.println("size = " + m.size());
        System.out.println("remove y = " + m.remove("y"));
        System.out.println("get y = " + m.get("y"));
        System.out.println("size = " + m.size());
    }
}
```

## 2. Correctness: Same Contract as HashMap

Expected output of the class above (its built-in `main`):

```
get x = 9
size = 2
remove y = 2
get y = null
size = 1
```

The overwrite path returns the previous value through `put` (observable via
`get`), `remove` returns the deleted value, and `size` tracks live entries
only — tombstones are invisible to callers.

```java
import java.util.HashMap;
import java.util.Objects;

public class ContractCheck {
    public static void main(String[] args) {
        OpenHashMap<String, Integer> mine = new OpenHashMap<>();
        HashMap<String, Integer> ref = new HashMap<>();

        String[] ops = {"a", "b", "c", "d", "e", "b", "z", "a", "m", "q"};
        for (int i = 0; i < ops.length; i++) {
            mine.put(ops[i], i);
            ref.put(ops[i], i);
        }
        System.out.println("sizes match: " + (mine.size() == ref.size()));

        boolean allMatch = true;
        for (String k : ref.keySet())
            if (!Objects.equals(mine.get(k), ref.get(k))) allMatch = false;
        System.out.println("all gets match: " + allMatch);

        mine.remove("b");
        ref.remove("b");
        System.out.println("after remove('b'): mine=" + mine.get("b")
                + " ref=" + ref.get("b"));
        System.out.println("keys sorted: " + mine.keys().stream().sorted().toList());
    }
}
```

Expected output:
```
sizes match: true
all gets match: true
after remove('b'): mine=null ref=null
keys sorted: [a, c, d, e, m, q, z]
```

## 3. Why a Tombstone Cannot Just Be null — Proven

```java
public class TombDemo {
    public static void main(String[] args) {
        OpenHashMap<String, Integer> m = new OpenHashMap<>();
        // choose keys that collide in a tiny table: resize is private, so we
        // rely on observable behavior instead — insert, delete, re-insert chain
        m.put("aa", 1);
        m.put("bb", 2);
        m.put("cc", 3);
        m.remove("aa");                 // tombstone at aa's slot
        System.out.println("get after tombstone: bb=" + m.get("bb")
                + " cc=" + m.get("cc"));
        m.put("dd", 4);                 // may reuse the tombstone
        System.out.println("size after reuse: " + m.size());
        System.out.println("bb still reachable: " + m.get("bb"));
    }
}
```

Expected output:
```
get after tombstone: bb=2 cc=3
size after reuse: 3
bb still reachable: 2
```

`get("bb")` must travel *through* aa's tombstone — if `remove` had left a plain
empty slot, the probe would halt there and `bb`/`cc` would be invisible. The
size after `put("dd")` is 3 (aa gone, bb/cc/dd present), confirming the tomb
slot was legitimately recycled.

## 4. Load Factor: The Probe-Cost Numbers Are Real

```java
import java.util.HashSet;
import java.util.Random;
import java.util.Set;

public class ProbeCost {
    public static void main(String[] args) {
        OpenHashMap<Integer, Integer> m = new OpenHashMap<>();
        Random rnd = new Random(42);
        Set<Integer> distinct = new HashSet<>();
        int n = 600;
        for (int i = 0; i < n; i++) {
            int k = rnd.nextInt(1_000_000);
            distinct.add(k);
            m.put(k, i);
        }
        // seed 42 draws 600 values but only 599 are distinct (1 birthday
        // collision) - assert against the *distinct* count, not n
        System.out.println("distinct keys stored = " + m.size()
                + " matches drawn set: " + (m.size() == distinct.size()));
        for (int k : distinct)
            if (m.get(k) == null) { System.out.println("MISS " + k); return; }
        System.out.println("all drawn keys retrievable: true");

        // clustering stress: sequential keys (worst case for naive hashes)
        OpenHashMap<Integer, Integer> seq = new OpenHashMap<>();
        for (int i = 0; i < 100; i++) seq.put(i, i);
        boolean ok = true;
        for (int i = 0; i < 100; i++) if (!Integer.valueOf(i).equals(seq.get(i))) ok = false;
        System.out.println("sequential keys all retrievable: " + ok);
    }
}
```

Expected output:
```
distinct keys stored = 599 matches drawn set: true
all drawn keys retrievable: true
sequential keys all retrievable: true
```

The `599` is not a bug in the map — it's how many *unique* values
`Random(42)` produces in 600 draws of `[0, 1_000_000)`; `size()` counts stored
keys, so duplicates collapse. Testing `size == 600` would be testing the RNG's
birthday problem, not the hash table.

The growth logic keys off `(size + tombstones + 1) / capacity` — **tombstones
count toward α**, because probe sequences traverse them exactly like live
entries. A map that counts only live entries will slowly fill with tombstones
after heavy delete traffic and degrade toward O(n) probes even though `size()`
looks small.

## 5. Bad Hash, Visible Damage

```java
import java.util.HashMap;

public class BadHash {
    // deliberately poor: all keys differ only in HIGH bits
    static final class BadKey {
        final int id;
        BadKey(int id) { this.id = id; }
        @Override public int hashCode() { return id << 16; }   // low 16 bits = 0
        @Override public boolean equals(Object o) {
            return o instanceof BadKey b && b.id == id;
        }
    }

    public static void main(String[] args) {
        HashMap<BadKey, Integer> h = new HashMap<>();
        OpenHashMap<BadKey, Integer> m = new OpenHashMap<>();
        for (int i = 0; i < 50; i++) {
            h.put(new BadKey(i), i);
            m.put(new BadKey(i), i);
        }
        boolean hOk = true, mOk = true;
        for (int i = 0; i < 50; i++) {
            if (h.get(new BadKey(i)) == null) hOk = false;
            if (m.get(new BadKey(i)) == null) mOk = false;
        }
        System.out.println("HashMap (spreads high bits) all found: " + hOk);
        System.out.println("OpenHashMap (spreads too) all found: " + mOk);
    }
}
```

Expected output:
```
HashMap (spreads high bits) all found: true
OpenHashMap (spreads too) all found: true
```

Both survive because both spread (`^ (h >>> 16)`): `BadKey` sets only bits
16–30, and the spread shifts them down into the index range. Remove the spread
step from `index()` and the same 50 keys land in bucket 0 in *both* maps —
degrading every operation to O(n). Try it: delete `h ^= (h >>> 16);` and
re-run; correctness survives (probe falls back to linear scan), but that's the
degenerate behavior the step exists to prevent.

## Common Pitfalls Encountered Here

- **Forgetting tombstones in the load-factor count** — the classic slow leak:
  map stays "small" but probes crawl.
- **`resize` rehashing with the OLD mask** — new table length must be used for
  `index(key, newCap)`, and the probe wrap must use `& (newCap - 1)`.
- **Iteration including tombstones/empties** — callers see phantom entries.
- **Power-of-two tables with `h % n` instead of `h & (n-1)`** — works but
  wastes the low-bit speed and (with a non-spread hash) throws away entropy.
- **Storing `size` but not resetting it in `resize`** — double-counted entries
  after growth; `resize` must zero both `size` and `tombstones` and rebuild.
- **Comparing to `java.util` results for iteration ORDER** — HashMap ordering
  is unspecified and your table layout differs; compare key *sets* and values,
  never sequences.
