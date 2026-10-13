# Mock Interview: LRU Cache

## Q1 — LRU Cache (LC 146)

**Problem.** Implement get/put with O(1) operations and least-recently-used eviction at capacity.

**Key insight.** A HashMap gives O(1) lookup; a doubly linked list keeps recency order. Touch moves a node to the front; overflow evicts the tail. LinkedHashMap in access order does exactly this.

**Complexity.** O(1) get/put, space O(capacity).

```java
import java.util.LinkedHashMap;
import java.util.Map;

public class LruQ1 {
    static class LRU extends LinkedHashMap<Integer, Integer> {
        final int cap;

        LRU(int cap) { super(cap, 0.75f, true); this.cap = cap; }

        protected boolean removeEldestEntry(Map.Entry<Integer, Integer> e) {
            return size() > cap;
        }
    }

    public static void main(String[] args) {
        LRU c = new LRU(2);
        c.put(1, 10); c.put(2, 20);
        c.get(1);
        c.put(3, 30);
        System.out.println(c.get(2));
        System.out.println(c.get(1) + "," + c.get(3));
    }
}
```

Output:

```
null
10,30
```

## Q2 — Why a Plain LinkedHashMap Is Not Enough in Production

**Problem.** What breaks when this textbook LRU faces concurrent traffic?

**Key insight.** LinkedHashMap is not thread-safe, and access-order updates mutate structure on reads, so even get/get races corrupt it. Production caches add sharding, locks, or use ConcurrentHashMap plus a lock-guarded recency list.

**Complexity.** Same O(1) amortized, plus lock contention cost under concurrency.

```java
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.Map;

public class LruQ2 {
    public static void main(String[] args) {
        Map<Integer, Integer> safe =
                Collections.synchronizedMap(new LinkedHashMap<>(16, 0.75f, true));
        safe.put(1, 1); safe.put(2, 2);
        synchronized (safe) {
            safe.get(1);
            System.out.println(safe.keySet());
        }
    }
}
```

Output:

```
[2, 1]
```

## Q3 — LFU vs LRU Eviction Choice

**Problem.** When does LFU (LC 460) beat LRU?

**Key insight.** LRU evicts by recency, so a one-time scan pollutes the cache; LFU evicts by frequency and keeps hot keys through scans. LFU needs frequency buckets (HashMap of key to count plus count-to-keys sets) for O(1) ops.

**Complexity.** Both O(1) with the right auxiliaries.

```java
import java.util.HashMap;
import java.util.Map;

public class LruQ3 {
    public static void main(String[] args) {
        Map<String, Integer> freq = new HashMap<>();
        String[] accesses = {"a", "b", "a", "c", "a", "b"};
        for (String k : accesses) freq.put(k, freq.getOrDefault(k, 0) + 1);
        String victim = null;
        for (String k : new String[]{"a", "b", "c"}) {
            if (victim == null || freq.get(k) < freq.get(victim)) victim = k;
        }
        System.out.println(freq + " evict=" + victim);
    }
}
```

Output:

```
{a=3, b=2, c=1} evict=c
```
