# Mock Interview: Caching Algorithms

## Q1: Implement LRU with O(1) get and put

Key insight: hash map for lookup plus recency-ordered list; hits move nodes front, overflow drops the tail. Complexity: O(1) per op, O(capacity) space; LRU is k-competitive for paging.

```java
public class LruDemo {
    static class Lru extends java.util.LinkedHashMap<Integer, String> {
        final int cap; Lru(int c) { super(c, 0.75f, true); cap = c; }
        protected boolean removeEldestEntry(java.util.Map.Entry<Integer, String> e) { return size() > cap; }
    }
    public static void main(String[] a) {
        Lru c = new Lru(3);
        c.put(1, "a"); c.put(2, "b"); c.put(3, "c"); c.get(1); c.put(4, "d");
        System.out.println(c.keySet() + " has2=" + c.containsKey(2));
    }
}
```

Output:

```text
[3, 1, 4] has2=false
```

## Q2: Implement LFU and state the eviction rule

Key insight: keep a frequency per key and evict the minimum on overflow, with a fixed tie-break. Complexity: O(1) hit/update, O(capacity) victim scan; slow to adapt when popularity shifts.

```java
import java.util.HashMap;
import java.util.Map;
public class LfuDemo {
    final int cap; final Map<Integer, String> v = new HashMap<>(); final Map<Integer, Integer> f = new HashMap<>();
    LfuDemo(int c) { cap = c; }
    void store(int k, String s) {
        if (v.containsKey(k)) { f.put(k, f.get(k) + 1); return; }
        if (v.size() == cap) {
            int vic = -1, best = Integer.MAX_VALUE;
            for (Map.Entry<Integer, Integer> e : f.entrySet()) if (e.getValue() < best) { best = e.getValue(); vic = e.getKey(); }
            v.remove(vic); f.remove(vic);
        }
        v.put(k, s); f.put(k, 1);
    }
    public static void main(String[] a) {
        LfuDemo c = new LfuDemo(3);
        c.store(1, "a"); c.store(2, "b"); c.store(3, "c");
        c.store(1, "a"); c.store(1, "a"); c.store(2, "b"); c.store(4, "d");
        System.out.println(c.v.keySet() + " has3=" + c.v.containsKey(3));
    }
}
```

Output:

```text
[1, 2, 4] has3=false
```

## Q3: Simulate Belady OPT on a reference string

Key insight: with full future knowledge, evict the cached page used farthest ahead; optimal offline and the online lower bound. Complexity: O(requests times capacity times lookahead) time, O(capacity) space.

```java
public class BeladyDemo {
    public static void main(String[] a) {
        int[] r = {1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5}; int cap = 3, faults = 0;
        java.util.List<Integer> c = new java.util.ArrayList<>();
        for (int i = 0; i < r.length; i++) {
            if (c.contains(r[i])) continue;
            faults++;
            if (c.size() == cap) {
                int vic = -1, far = -1;
                for (int k : c) {
                    int next = Integer.MAX_VALUE;
                    for (int j = i + 1; j < r.length && next == Integer.MAX_VALUE; j++) if (r[j] == k) next = j;
                    if (next > far) { far = next; vic = k; }
                }
                c.remove((Integer) vic);
            }
            c.add(r[i]);
        }
        System.out.println("opt=" + faults);
    }
}
```

Output:

```text
opt=7
```
