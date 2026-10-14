# Mock Interview: Data Stream Algorithms
> Three questions on one-pass summaries. State the guarantee (exact, unbiased, or bounded-error) first.
## Q1: reservoir sampling
Problem: keep a uniform sample of size 3 from the stream 1..10 with a fixed seed.
Key insight: item i replaces a random slot with probability k/i, which keeps every item in the reservoir with probability k/n after n arrivals.
Complexity: O(n) time, O(k) memory.
```java
import java.util.*;
public class L34Q1 {
    public static void main(String[] a){
        int k = 3; int[] res = new int[k]; Random r = new Random(42);
        for (int i = 1; i <= 10; i++){ if (i <= k) res[i-1] = i; else { int j = r.nextInt(i); if (j < k) res[j] = i; } }
        System.out.println("reservoir=" + Arrays.toString(res));
    }
}
```
Observed output:
```
reservoir=[6, 2, 8]
```
Follow-up: prove the k/n invariant by induction over arrivals.
## Q2: Misra-Gries heavy hitters
Problem: track 2 counters over an 11-item stream and report surviving candidates.
Key insight: decrementing every counter on overflow preserves items far above threshold; stored counts are lower bounds, short by at most the number of decrement rounds.
Complexity: O(n) time, O(m) memory for m counters.
```java
import java.util.*;
public class L34Q2 {
    public static void main(String[] a){
        int[] s = {1,2,1,3,1,2,1,4,1,2,1};
        Map<Integer,Integer> c = new LinkedHashMap<>();
        for (int x : s){
            if (c.containsKey(x)) c.put(x, c.get(x)+1);
            else if (c.size() < 2) c.put(x, 1);
            else { List<Integer> dead = new ArrayList<>(); for (Map.Entry<Integer,Integer> e : c.entrySet()){ e.setValue(e.getValue()-1); if (e.getValue()==0) dead.add(e.getKey()); } for (int d : dead) c.remove(d); }
        }
        System.out.println("candidates=" + c + " true_count_1=6 n=" + s.length);
    }
}
```
Observed output:
```
candidates={1=4, 2=1} true_count_1=6 n=11
```
Follow-up: how does Count-Min Sketch trade this undercount for overcount?
## Q3: Count-Min estimates
Problem: query a 2-row width-5 sketch with hand-rolled hashes on a fixed 8-item stream.
Key insight: taking the row minimum keeps est >= true always; collisions only inflate, never deflate, as q=2 (est 3, true 2) shows.
Complexity: O(d) per update and query, O(w*d) memory.
```java
public class L34Q3 {
    public static void main(String[] a){
        int[] s = {5,5,5,2,5,2,7,5};
        int[][] t = new int[2][5];
        for (int x : s){ t[0][x % 5]++; t[1][(3*x+1) % 5]++; }
        for (int q : new int[]{5,2,7}) System.out.println("q=" + q + " est=" + Math.min(t[0][q%5], t[1][(3*q+1)%5]));
    }
}
```
Observed output:
```
q=5 est=5
q=2 est=3
q=7 est=3
```
Follow-up: size w and d from epsilon/delta, and contrast with the Morris counter.
## Pass checklist
- [ ] Check the reservoir contains only seen items and has size k.
- [ ] Confirm every sketch estimate is >= the true count.
- [ ] Explain why decrement rounds bound the Misra-Gries shortfall.
