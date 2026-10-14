# Mock Interview: Bloom Filter Variants
> Three questions on probabilistic membership. State the false-positive behavior before coding.
## Q1: plain Bloom filter
Problem: insert apple/banana/cherry into a 64-bit, 3-hash filter and query members plus mango/kiwi.
Key insight: double hashing (h1 + i*h2) gives k indices from two base hashes; bits are only ever set, so members always report true and negatives may collide.
Complexity: O(k) per operation, m bits total.
```java
public class L36Q1 {
    static boolean[] b = new boolean[64];
    static int h(String s, int i){ return Math.floorMod(s.hashCode()+i*(s.hashCode()*31+7), 64); }
    static void add(String s){ for (int i = 0; i < 3; i++) b[h(s,i)] = true; }
    static boolean maybe(String s){ for (int i = 0; i < 3; i++) if (!b[h(s,i)]) return false; return true; }
    public static void main(String[] a){
        add("apple"); add("banana"); add("cherry");
        System.out.println("member=" + (maybe("apple") && maybe("banana") && maybe("cherry")));
        System.out.println("mango=" + maybe("mango") + " kiwi=" + maybe("kiwi"));
    }
}
```
Observed output:
```
member=true
mango=false kiwi=false
```
Follow-up: why can a plain Bloom filter never return a false negative?
## Q2: sizing from the FPR formula
Problem: evaluate (1 - e^(-kn/m))^k at m = 1000, n = 100, k = 7 and the optimal k = (m/n) ln 2.
Key insight: k_opt balances sparsity against hash count; k = 7 sits at the optimum 6.93 and gives FPR ~0.0082.
Complexity: O(1) arithmetic; quoted to size real filters.
```java
public class L36Q2 {
    public static void main(String[] a){
        double m = 1000, n = 100, k = 7;
        System.out.println("fpr=" + String.format("%.6f", Math.pow(1-Math.exp(-k*n/m), k)));
        System.out.println("k_opt=" + String.format("%.2f", (m/n)*Math.log(2)));
    }
}
```
Observed output:
```
fpr=0.008194
k_opt=6.93
```
Follow-up: how does the FPR move if n doubles with m fixed?
## Q3: counting variant with delete
Problem: insert a and b into a counting filter, delete a, and query both.
Key insight: per-position counters make delete safe for exactly the inserted multiset, at 4+ bits per position instead of 1; plain bit arrays cannot do this without risking false negatives.
Complexity: O(k) per operation, wider counters.
```java
public class L36Q3 {
    static int[] c = new int[64];
    static int h(String s, int i){ return Math.floorMod(s.hashCode()+i*(s.hashCode()*31+7), 64); }
    static void add(String s){ for (int i=0;i<3;i++) c[h(s,i)]++; }
    static void del(String s){ for (int i=0;i<3;i++) c[h(s,i)]--; }
    static boolean maybe(String s){ for (int i=0;i<3;i++) if (c[h(s,i)]<=0) return false; return true; }
    public static void main(String[] a){ add("a"); add("b"); del("a"); System.out.println("a=" + maybe("a") + " b=" + maybe("b")); }
}
```
Observed output:
```
a=false b=true
```
Follow-up: contrast with cuckoo filters (buckets plus kick-outs) and quotient filters (quotient/remainder slots).
## Pass checklist
- [ ] Rerun Q1 mentally for a non-member and find its three bit positions.
- [ ] Recompute k_opt = 10 x 0.693 by hand.
- [ ] Explain why deleting from a plain Bloom filter is unsound.
