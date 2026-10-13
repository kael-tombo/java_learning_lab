# Mock Interview: Cuckoo and Robin Hood Hashing

## Q1 — Cuckoo Insert with Two Hashes

**Problem.** Insert into a table where each key lives in one of two positions.
**Key insight.** Evict the occupant to its alternate slot, cascading. Lookups check two slots: worst-case O(1). Past load ~0.5 or a kick limit, rehash. **Complexity.** O(1) lookup worst case, O(1) insert expected amortized.

```java
public class CuckooQ1 {
    static String[] t0 = new String[8], t1 = new String[8];
    static int h0(String k) { return Math.floorMod(k.hashCode(), 8); }
    static int h1(String k) { return Math.floorMod(k.hashCode() * 0x9e3779b9, 8); }
    static boolean contains(String k) { return k.equals(t0[h0(k)]) || k.equals(t1[h1(k)]); }
    static void insert(String k) {
        String cur = k;
        for (int i = 0; i < 16; i++) {
            int p = h0(cur);
            String t = t0[p]; t0[p] = cur;
            if (t == null) return;
            cur = t;
            int q = h1(cur);
            t = t1[q]; t1[q] = cur;
            if (t == null) return;
            cur = t;
        }
        throw new IllegalStateException("rehash needed");
    }
    public static void main(String[] args) {
        insert("alpha"); insert("beta"); insert("gamma");
        System.out.println(contains("beta") + "," + contains("delta"));
    }
}
```

Output:

```
true,false
```

## Q2 — Robin Hood Displacement Invariant

**Problem.** How does Robin Hood hashing bound probe lengths?
**Key insight.** On collision the key farther from home keeps the slot: probe sequences stay sorted by distance-from-home, minimizing probe variance and p99 at high load. **Complexity.** O(1) expected; degrades gracefully.

```java
public class CuckooQ2 {
    public static void main(String[] args) {
        int m = 4;
        String[] t = new String[m];
        int[] dist = new int[m];
        for (String k : new String[]{"a", "b", "e", "f"}) {
            String cur = k;
            int d = 0, i = Math.floorMod(k.hashCode(), m);
            while (true) {
                if (t[i] == null) { t[i] = cur; dist[i] = d; break; }
                if (dist[i] < d) { String tmp = t[i]; t[i] = cur; cur = tmp; int td = dist[i]; dist[i] = d; d = td; }
                i = (i + 1) % m; d++;
            }
        }
        int max = 0;
        for (int x : dist) max = Math.max(max, x);
        System.out.println("maxProbe=" + max + "," + (t[Math.floorMod("e".hashCode(), m)] != null));
    }
}
```

Output:

```
maxProbe=2,true
```

## Q3 — Load Factor Limits

**Problem.** Why do open-addressing tables resize at 0.7 while 2-hash cuckoo resizes near 0.5?
**Key insight.** Linear-probe length grows as 1/(1 - load), exploding near 1; cuckoo insertion fails with constant probability above ~0.5. Match scheme to workload. **Complexity.** O(1) expected below each threshold.

```java
public class CuckooQ3 {
    public static void main(String[] args) {
        for (double load : new double[]{0.5, 0.7, 0.9}) System.out.printf("load=%.1f probe~%.2f%n", load, 1.0 / (1 - load));
    }
}
```

Output:

```
load=0.5 probe~2.00
load=0.7 probe~3.33
load=0.9 probe~10.00
```
