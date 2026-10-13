# Mock Interview: Dynamic Programming: Tabulation, Knapsack, Coin Change
> Three worked questions on DP over prefixes and capacities. Each answer is complete runnable Java; outputs below were observed.

## Q1: Compute Fibonacci numbers bottom-up.
Key insight: fib(n) = fib(n-1) + fib(n-2) has overlapping subproblems: naive recursion recomputes the same values exponentially often. Filling a table once in increasing order makes each state O(1).
Complexity: Time O(n); space O(n), reducible to O(1) with two rolling variables.
```java
public class L05Q1Fib {
    public static void main(String[] args) {
        long[] d = new long[21];
        d[1] = 1;
        for (int i = 2; i <= 20; i++) d[i] = d[i - 1] + d[i - 2];
        System.out.println("fib(20)=" + d[20] + " fib(10)=" + d[10]);
    }
}
```
Observed output: `fib(20)=6765 fib(10)=55`
Follow-up: How many additions does naive fib(20) recursion perform compared with these 19?

## Q2: Solve a small 0/1 knapsack with a 1D table.
Key insight: d[c] = best value with capacity c; each item is considered once, scanning capacities downward so item i cannot be reused. The downward scan is the whole correctness argument for the 1D form.
Complexity: Time O(n*C); space O(C).
```java
public class L05Q2Knapsack {
    public static void main(String[] args) {
        int[] w = {2, 3, 4, 5}, v = {3, 4, 5, 6};
        int C = 5, n = 4;
        int[] d = new int[C + 1];
        for (int i = 0; i < n; i++)
            for (int c = C; c >= w[i]; c--) d[c] = Math.max(d[c], d[c - w[i]] + v[i]);
        System.out.println("knapsack(C=5)=" + d[C]);
    }
}
```
Observed output: `knapsack(C=5)=7`
Follow-up: What goes wrong if capacities are scanned upward, and which item gets reused to prove it?

## Q3: Find the minimum coins for total 6 with denominations {1, 3, 4}.
Key insight: d[t] = 1 + min over coins k of d[t-k]: the optimal solution for t must end with some coin, so trying all of them covers every case. Greedy (take 4, then 1, 1) uses 3 coins, but 3+3 uses 2 - this instance shows greedy failing.
Complexity: Time O(T * coins); space O(T).
```java
import java.util.Arrays;
public class L05Q3Coins {
    public static void main(String[] args) {
        int[] c = {1, 3, 4};
        int T = 6;
        int[] d = new int[T + 1];
        Arrays.fill(d, 999);
        d[0] = 0;
        for (int t = 1; t <= T; t++)
            for (int k : c) if (k <= t) d[t] = Math.min(d[t], d[t - k] + 1);
        System.out.println("mincoins(6)=" + d[T]);
    }
}
```
Observed output: `mincoins(6)=2`
Follow-up: Reconstruct the actual coin set from the table: what parent pointer would you store per state?

## Checklist
- State the key insight before coding; name the loop invariant.
- Derive time and space bounds from the code structure, not from memory.
