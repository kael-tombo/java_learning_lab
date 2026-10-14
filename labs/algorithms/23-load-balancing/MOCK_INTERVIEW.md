# Mock Interview: Load Balancing

## Q1: Route keys with consistent hashing and measure remapping

Key insight: hash nodes (with virtual copies) and keys onto one ring; each key belongs to the first node clockwise, so a new node steals only its arcs. Complexity: O(log V) lookup per key, O(V) ring memory.

```java
public class ConsistentHashDemo {
    static int hash(String s) {
        int h = 0x811c9dc5;
        for (int i = 0; i < s.length(); i++) { h ^= s.charAt(i); h *= 0x01000193; }
        return h;
    }
    static java.util.TreeMap<Integer, String> ring(String[] nodes, int vn) {
        java.util.TreeMap<Integer, String> r = new java.util.TreeMap<>();
        for (String n : nodes) for (int v = 0; v < vn; v++) r.put(hash(n + "#" + v), n);
        return r;
    }
    static String owner(java.util.TreeMap<Integer, String> r, String key) {
        Integer s = r.ceilingKey(hash(key));
        return r.get(s == null ? r.firstKey() : s);
    }
    public static void main(String[] a) {
        String[] keys = {"user:12", "user:847", "order:55", "cart:9", "user:300", "order:71", "cart:44", "user:918"};
        java.util.TreeMap<Integer, String> b = ring(new String[]{"n1", "n2", "n3"}, 8), f = ring(new String[]{"n1", "n2", "n3", "n4"}, 8);
        String moves = ""; int m = 0;
        for (String k : keys) { String o = owner(b, k), n = owner(f, k); if (!o.equals(n)) { m++; moves += k + ":" + o + "->" + n + " "; } }
        System.out.println("moved=" + m + "/8 [" + moves.trim() + "]");
    }
}
```

Output:

```text
moved=1/8 [user:300:n3->n4]
```

## Q2: Route keys with rendezvous (highest-weight) hashing

Key insight: score every node against the key and take the maximum; no ring to maintain, and membership changes move only keys ranked first. Complexity: O(N) scoring per key, O(1) state; fits small pools.

```java
public class RendezvousDemo {
    static int hash(String s) {
        int h = 0x811c9dc5;
        for (int i = 0; i < s.length(); i++) { h ^= s.charAt(i); h *= 0x01000193; }
        return h;
    }
    static String owner(String[] nodes, String key) {
        String best = nodes[0]; int bestW = hash(key + "|" + best);
        for (String n : nodes) { int w = hash(key + "|" + n); if (w > bestW) { best = n; bestW = w; } }
        return best;
    }
    public static void main(String[] a) {
        String[] nodes = {"n1", "n2", "n3"}, keys = {"user:12", "order:55", "cart:9"}; String out = "";
        for (String k : keys) out += k + "->" + owner(nodes, k) + " ";
        System.out.println(out.trim());
    }
}
```

Output:

```text
user:12->n2 order:55->n1 cart:9->n3
```

## Q3: Simulate least-connections dispatch over arrivals

Key insight: send each arrival to the server with fewest open connections and release after its holding time; adapts to uneven costs. Complexity: O(N) scan per arrival; beats round-robin on skew.

```java
public class LeastConnDemo {
    public static void main(String[] a) {
        int[] load = {0, 0, 0}; // open connections on s1, s2, s3
        int[] dur = {3, 1, 2, 1, 4, 2}; // holding times in ticks
        int[] who = new int[6], rel = new int[6]; int open = 0; // active holdings
        String picks = "";
        for (int t = 0; t < dur.length; t++) {
            for (int i = open - 1; i >= 0; i--) if (rel[i] <= t) { load[who[i]]--; who[i] = who[--open]; rel[i] = rel[open]; }
            int pick = load[1] < load[0] ? (load[2] < load[1] ? 2 : 1) : (load[2] < load[0] ? 2 : 0);
            load[pick]++; who[open] = pick; rel[open] = t + dur[t]; open++; picks += "s" + (pick + 1) + " ";
        }
        System.out.println(picks.trim());
    }
}
```

Output:

```text
s1 s2 s2 s1 s1 s2
```
