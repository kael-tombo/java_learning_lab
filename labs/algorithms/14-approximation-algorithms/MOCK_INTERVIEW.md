# Mock Interview: Approximation Algorithms: Vertex Cover, Set Cover, Makespan
> Three worked questions on provable near-optimality. Each answer is complete runnable Java; outputs below were observed.

## Q1: Compare greedy vertex cover against the true optimum on a small graph.
Key insight: Taking both endpoints of an uncovered edge is a 2-approximation: the chosen edges are disjoint, any cover needs one endpoint per edge, so greedy uses at most twice the optimum. Brute force on 5 nodes verifies the ratio on this instance.
Complexity: Greedy O(V + E); brute-force check O(2^V * E) for the comparison only.
```java
import java.util.HashSet;
public class L14Q1VCover {
    public static void main(String[] args) {
        int[][] e = {{0, 1}, {1, 2}, {2, 3}, {3, 4}, {4, 0}, {0, 2}};
        HashSet<Integer> cov = new HashSet<>();
        for (int[] x : e)
            if (!cov.contains(x[0]) && !cov.contains(x[1])) { cov.add(x[0]); cov.add(x[1]); }
        int opt = 5;
        for (int m = 0; m < 32; m++) {
            boolean ok = true;
            for (int[] x : e)
                if ((m & (1 << x[0])) == 0 && (m & (1 << x[1])) == 0) ok = false;
            if (ok) opt = Math.min(opt, Integer.bitCount(m));
        }
        System.out.println("greedy=" + cov.size() + " opt=" + opt);
    }
}
```
Observed output: `greedy=4 opt=3`
Follow-up: Prove the factor 2 from the disjoint-edges argument, and find an input family attaining it.

## Q2: Cover a universe greedily by always taking the set with most uncovered elements.
Key insight: Greedy set cover repeatedly takes the set covering the most still-uncovered elements; it uses at most H(d) times the optimum where d is the largest set size. The charging argument assigns each newly covered element cost 1/(newly covered).
Complexity: Time O(sets * universe); the ratio is logarithmic, not constant.
```java
import java.util.HashSet;
public class L14Q2SetCover {
    public static void main(String[] args) {
        int[][] sets = {{0, 1, 2}, {2, 3}, {3, 4, 5}, {0, 5}, {1, 4}};
        HashSet<Integer> left = new HashSet<>();
        for (int i = 0; i < 6; i++) left.add(i); int used = 0;
        while (!left.isEmpty()) {
            int bi = -1, bn = -1;
            for (int i = 0; i < sets.length; i++) {
                int n = 0;
                for (int x : sets[i]) if (left.contains(x)) n++;
                if (n > bn) { bn = n; bi = i; }
            }
            for (int x : sets[bi]) left.remove(x);
            used++;
        }
        System.out.println("sets-used=" + used);
    }
}
```
Observed output: `sets-used=2`
Follow-up: Why can no polynomial algorithm do much better in general, in one sentence about hardness?

## Q3: Schedule jobs on 2 machines with longest-processing-time-first and compare to optimal.
Key insight: LPT (assign each job, longest first, to the least-loaded machine) is a 4/3-approximation for makespan. On small inputs brute force over 2^6 assignments gives the optimum to compare against.
Complexity: Greedy O(n log n); brute-force check O(2^n) for the comparison only.
```java
import java.util.Arrays;
public class L14Q3Lpt {
    public static void main(String[] args) {
        int[] jobs = {5, 5, 4, 4, 3, 3};
        Arrays.sort(jobs);
        int a = 0, b = 0;
        for (int i = jobs.length - 1; i >= 0; i--) {
            if (a <= b) a += jobs[i]; else b += jobs[i];
        }
        int greedy = Math.max(a, b), opt = 99;
        for (int m = 0; m < 64; m++) {
            int x = 0;
            for (int i = 0; i < 6; i++) if ((m & (1 << i)) != 0) x += new int[]{5, 5, 4, 4, 3, 3}[i];
            opt = Math.min(opt, Math.max(x, 24 - x));
        }
        System.out.println("lpt=" + greedy + " opt=" + opt);
    }
}
```
Observed output: `lpt=12 opt=12`
Follow-up: Where does the 4/3 factor come from: which job in the order witnesses the worst case?

## Checklist
- State the key insight before coding; name the loop invariant.
- Derive time and space bounds from the code structure, not from memory.
