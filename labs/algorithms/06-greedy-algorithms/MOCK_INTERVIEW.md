# Mock Interview: Greedy Algorithms: Activity Selection, Fractional Knapsack, Canonical Coins
> Three worked questions on greedy choice and its limits. Each answer is complete runnable Java; outputs below were observed.

## Q1: Select the maximum number of non-overlapping activities.
Key insight: Sorting by finish time and always taking the earliest-finishing compatible activity is optimal: an exchange argument shows some optimal solution contains that first pick, and the rest is the same problem on later activities.
Complexity: Time O(n log n) for the sort, O(n) for the scan; space O(1) extra.
```java
import java.util.Arrays;
public class L06Q1Activity {
    public static void main(String[] args) {
        int[][] m = {{1, 4}, {3, 5}, {0, 6}, {5, 7}, {8, 9}, {5, 9}};
        Arrays.sort(m, (x, y) -> x[1] - y[1]);
        int n = 0, end = -1;
        StringBuilder s = new StringBuilder();
        for (int[] a : m)
            if (a[0] >= end) { n++; end = a[1]; s.append("[").append(a[0]).append(",").append(a[1]).append("]"); }
        System.out.println("picked=" + n + " " + s);
    }
}
```
Observed output: `picked=3 [1,4][5,7][8,9]`
Follow-up: Why does sorting by start time fail? Give a 3-activity counterexample.

## Q2: Solve fractional knapsack greedily by value density.
Key insight: With fractions allowed, taking items in decreasing value-per-weight order is optimal: any solution using a lower-density item while a higher-density one has room can be improved by swapping. Indivisibility is exactly what breaks this for 0/1 knapsack.
Complexity: Time O(n log n); space O(1) extra.
```java
import java.util.Arrays;
public class L06Q2Frac {
    public static void main(String[] args) {
        double[][] it = {{10, 60}, {20, 100}, {30, 120}};
        Arrays.sort(it, (x, y) -> Double.compare(y[1] / y[0], x[1] / x[0]));
        double C = 50, val = 0;
        for (double[] o : it) {
            double t = Math.min(C, o[0]);
            val += t * o[1] / o[0];
            C -= t;
        }
        System.out.println("fractional=" + val);
    }
}
```
Observed output: `fractional=240.0`
Follow-up: Build a 3-item 0/1 instance where this same greedy order picks a suboptimal set.

## Q3: Make change greedily with canonical denominations {25, 10, 5, 1}.
Key insight: Greedy (take as many of the largest coin as possible) is optimal for canonical systems like these, where each coin divides the next. It is not universally optimal - {1, 3, 4} for total 6 needs DP - so the denomination structure is doing the work.
Complexity: Time O(coins); space O(1).
```java
public class L06Q3GreedyCoin {
    public static void main(String[] args) {
        int[] c = {25, 10, 5, 1};
        int t = 63, n = 0;
        StringBuilder s = new StringBuilder();
        for (int k : c) {
            int u = t / k;
            n += u;
            t -= u * k;
            if (u > 0) s.append(k).append("x").append(u).append(" ");
        }
        System.out.println("coins=" + n + " [" + s.toString().trim() + "]");
    }
}
```
Observed output: `coins=6 [25x2 10x1 1x3]`
Follow-up: Prove greedy optimal here by showing each coin divides the next, then break it with {1, 3, 4}.

## Checklist
- State the key insight before coding; name the loop invariant.
- Derive time and space bounds from the code structure, not from memory.
