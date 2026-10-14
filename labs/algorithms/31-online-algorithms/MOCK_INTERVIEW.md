# Mock Interview: Online Algorithms
> Three questions on competitive analysis. State the ratio against the offline optimum before coding.
## Q1: LRU paging simulation
Problem: simulate an LRU cache of capacity 2 on put(1), put(2), get(1), put(3), get(2), get(3).
Key insight: access-order map evicts the least-recently-used key; LRU is k-competitive on paging while offline OPT (Belady MIN) evicts the key used farthest in the future.
Complexity: O(1) amortized per operation, O(k) memory.
```java
import java.util.*;
public class L31Q1 {
    public static void main(String[] a){
        final int cap = 2;
        Map<Integer,Integer> c = new LinkedHashMap<>(cap, 0.75f, true){
            protected boolean removeEldestEntry(Map.Entry e){ return size() > cap; }
        };
        c.put(1,10); c.put(2,20); int g1 = c.getOrDefault(1,-1);
        c.put(3,30); int g2 = c.getOrDefault(2,-1); int g3 = c.getOrDefault(3,-1);
        System.out.println("get1=" + g1 + " get2=" + g2 + " get3=" + g3);
        System.out.println("keys=" + c.keySet());
    }
}
```
Observed output:
```
get1=10 get2=-1 get3=30
keys=[1, 3]
```
Follow-up: how does the marking algorithm reach k-competitiveness, and what does randomization buy?
## Q2: ski-rental break-even
Problem: buying skis costs 100, renting costs 10/day, trip is 14 days; also price a 4-day trip.
Key insight: rent until cumulative rent equals the buy price (day 10), then buy; cost is at most twice OPT on any trip length, so the strategy is 2-competitive.
Complexity: O(1) time and memory.
```java
public class L31Q2 {
    public static void main(String[] a){
        int buy = 100, rent = 10, days = 14, t = buy / rent;
        int strategy = (days <= t) ? days * rent : t * rent + buy;
        int opt = Math.min(days * rent, buy);
        System.out.println("strategy=" + strategy + " opt=" + opt + " ratio=" + (strategy/(double)opt));
        System.out.println("short_trip cost=" + Math.min(4*rent, buy));
    }
}
```
Observed output:
```
strategy=200 opt=100 ratio=2.0
short_trip cost=40
```
Follow-up: what randomized rule improves the ratio toward e/(e-1)?
## Q3: secretary observe-and-pick
Problem: pick the maximum of 10 values seen in order; observe the first n/e, then hire the first value beating the observed best.
Key insight: the 1/e observation window balances learning the threshold against running out of candidates; success probability tends to 1/e.
Complexity: O(n) time, O(1) memory.
```java
public class L31Q3 {
    public static void main(String[] a){
        int[] v = {5,1,9,3,8,2,7,4,10,6};
        int skip = (int)(v.length / Math.E), best = -1;
        for (int i = 0; i < skip; i++) best = Math.max(best, v[i]);
        int hire = v.length - 1;
        for (int i = skip; i < v.length; i++) if (v[i] > best){ hire = i; break; }
        System.out.println("skip=" + skip + " hire_index=" + hire + " hire_value=" + v[hire]);
    }
}
```
Observed output:
```
skip=3 hire_index=8 hire_value=10
```
Follow-up: where does the same threshold idea appear in dispatch and hiring pipelines?
## Pass checklist
- [ ] Reproduce all three outputs exactly before claiming the ratio proofs.
- [ ] Explain why LRU can be a factor k worse than OPT on adversarial traces.
- [ ] Derive the break-even day from buy/rent instead of memorizing it.
