# HashMap Internals — Code Deep Dive

All snippets compile and run on any JDK 9+ (tested on JDK 23). No external
dependencies — reflection opens `java.base/java.util` with `--add-opens`.

## 1. Observing the Bucket Array

```java
import java.lang.reflect.Field;
import java.util.HashMap;
import java.util.Map;

public class BucketView {
    @SuppressWarnings("unchecked")
    public static void main(String[] args) throws Exception {
        Map<String, Integer> map = new HashMap<>();
        map.put("apple", 1);
        map.put("banana", 2);
        map.put("elderberry", 3);

        Field f = HashMap.class.getDeclaredField("table");
        f.setAccessible(true);
        Object[] table = (Object[]) f.get(map);

        int used = 0;
        for (Object bucket : table) if (bucket != null) used++;
        System.out.println("table length = " + table.length);   // 16
        System.out.println("buckets used = " + used);           // 3
    }
}
```

Run: `java --add-opens java.base/java.util=ALL-UNNAMED BucketView.java`

Expected output:
```
table length = 16
buckets used = 3
```

Key point: the table is allocated lazily. A default `new HashMap<>()` has **no**
backing array until the first `put` — which is why capacity 16 appears only here.

## 2. Reproducing the Spread Function

```java
public class Spread {
    static int spread(int h) { return h ^ (h >>> 16); }

    public static void main(String[] args) {
        // A key whose hash differs ONLY in the high bits:
        int a = 0x0001_0000;   // 65536
        int b = 0x0002_0000;   // 131072
        // Without spreading, both mask to bucket 0 at capacity 16:
        System.out.println("raw  a&15=" + (a & 15) + "  b&15=" + (b & 15));
        // With spreading the high bits fold down:
        System.out.println("sprd a&15=" + (spread(a) & 15)
                         + "  b&15=" + (spread(b) & 15));
    }
}
```

Expected output:
```
raw  a&15=0  b&15=0
sprd a&15=1  b&15=2
```

This is exactly the collision the `^ (h >>> 16)` term prevents.

## 3. Forcing a Tree Bin and Watching It Convert

```java
import java.lang.reflect.Field;
import java.util.HashMap;

public class TreeBinDemo {
    static Object bucketOf(HashMap<Integer, ?> m, int i) throws Exception {
        Field f = HashMap.class.getDeclaredField("table");
        f.setAccessible(true);
        return ((Object[]) f.get(m))[i];
    }

    public static void main(String[] args) throws Exception {
        // capacity 64 >= MIN_TREEIFY_CAPACITY; keys are multiples of 64 so
        // spread(h) == h (h < 2^16) and every key lands in bucket 0.
        HashMap<Integer, Integer> m = new HashMap<>(64);
        for (int i = 1; i <= 9; i++) m.put(i * 64, i);
        System.out.println("after 9 colliding puts: "
                + bucketOf(m, 0).getClass().getSimpleName());   // TreeNode

        // delete down to 3 nodes: the tree is now shallow (depth heuristic)
        for (int i = 9; i > 3; i--) m.remove(i * 64);
        System.out.println("after shrinking to 3:    "
                + bucketOf(m, 0).getClass().getSimpleName());   // Node
    }
}
```

Run: `java --add-opens java.base/java.util=ALL-UNNAMED TreeBinDemo.java`

Expected output:
```
after 9 colliding puts: TreeNode
after shrinking to 3:    Node
```

Note the asymmetry verified in the JDK source: **insertion** treeifies at 8 entries,
but **removal** untreeifies on a *depth* test (`root.right == null || root.left ==
null || root.left.left == null`), not a count — that is why 4 nodes can still be a
TreeNode while 3 are already a plain list.

## 4. Resize Bit Test

```java
public class ResizeBit {
    public static void main(String[] args) {
        int oldCap = 16;
        for (int h = 0; h < 32; h++) {
            int oldIdx = h & (oldCap - 1);
            int newIdx = h & (2 * oldCap - 1);
            String move = (newIdx == oldIdx) ? "stay" : "move +" + oldCap;
            System.out.printf("hash=%2d old=%2d new=%2d -> %s%n",
                    h, oldIdx, newIdx, move);
        }
    }
}
```

Expected output (elided):

Every hash maps to either `oldIdx` or `oldIdx + 16`, the whole reason resize is
a single bit test per node instead of a rehash:

```
hash= 0 old= 0 new= 0 -> stay
hash= 1 old= 1 new= 1 -> stay
...
hash=16 old= 0 new=16 -> move +16
hash=17 old= 1 new=17 -> move +16
```

## 5. What null Keys Really Cost

```java
import java.lang.reflect.Field;
import java.util.HashMap;

public class NullKey {
    public static void main(String[] args) throws Exception {
        HashMap<Object, String> m = new HashMap<>();
        m.put(null, "nullable");
        Field f = HashMap.class.getDeclaredField("table");
        f.setAccessible(true);
        Object[] t = (Object[]) f.get(m);
        System.out.println("null key occupies bucket 0: " + (t[0] != null));
        System.out.println("get(null) = " + m.get(null));
    }
}
```

Expected output:
```
null key occupies bucket 0: true
get(null) = nullable
```

`HashMap` special-cases null to hash `0`; `ConcurrentHashMap` rejects null
entirely, because in a concurrent map `get(k) == null` cannot distinguish
"absent" from "mapped to null".

## Common Pitfalls Encountered Here

- **`--add-opens` is mandatory**: without it, `setAccessible` throws
  `InaccessibleObjectException` on JDK 16+ (verified on JDK 23).
- **Reflecting `table` before any `put` returns null**: allocation is lazy.
- **Non-power-of-two capacity does not survive**: `new HashMap<>(50)` still
  allocates 64 buckets (`tableSizeFor` rounds up), so `& (n-1)` stays valid.
- **Treeification at small capacities never happens**: with the default 16-bucket
  table, 9 colliding keys trigger a **resize** instead (table < 64), so buckets
  only ever treeify in tables of ≥ 64 nodes.
