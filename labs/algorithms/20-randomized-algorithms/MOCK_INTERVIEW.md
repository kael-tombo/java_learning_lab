# Mock Interview: Randomized Algorithms: Random Pivots, Monte Carlo, Fermat Limits
> Three worked questions on randomness with fixed seeds (fully reproducible). Each answer is complete runnable Java; outputs below were observed.

## Q1: Sort with randomized quicksort under a fixed seed.
Key insight: Random pivots make every input behave like the average case: no fixed input triggers the quadratic worst case with more than exponentially small probability. The fixed seed keeps the run reproducible for testing without changing the analysis.
Complexity: Expected time O(n log n), worst case O(n^2); Las Vegas style - always correct, random runtime.
```java
import java.util.Arrays;
import java.util.Random;
public class L20Q1RandQuick {
    static Random r = new Random(99);
    static void sort(int[] a, int lo, int hi) {
        if (lo >= hi) return;
        int p = a[lo + r.nextInt(hi - lo + 1)], i = lo, j = hi;
        while (i <= j) {
            while (a[i] < p) i++;
            while (a[j] > p) j--;
            if (i <= j) { int t = a[i]; a[i++] = a[j]; a[j--] = t; }
        }
        sort(a, lo, j);
        sort(a, i, hi);
    }
    public static void main(String[] args) {
        int[] a = {5, 1, 9, 3, 7, 2, 8, 4, 6};
        sort(a, 0, a.length - 1);
        System.out.println("randquick=" + Arrays.toString(a));
    }
}
```
Observed output: `randquick=[1, 2, 3, 4, 5, 6, 7, 8, 9]`
Follow-up: Contrast Las Vegas (this) with Monte Carlo: which side holds the error, and how do you amplify success?

## Q2: Estimate pi by Monte Carlo dart-throwing with a fixed seed.
Key insight: The fraction of darts landing in the quarter-circle estimates pi/4 by the law of large numbers; error shrinks like 1/sqrt(n). The fixed seed makes the estimate exactly reproducible - randomness in the method, determinism in the test.
Complexity: Time O(n) for n darts; error O(1/sqrt(n)) with high probability.
```java
import java.util.Random;
public class L20Q2Pi {
    public static void main(String[] args) {
        Random r = new Random(42);
        int n = 200000, hits = 0;
        for (int i = 0; i < n; i++) {
            double x = r.nextDouble(), y = r.nextDouble();
            if (x * x + y * y <= 1) hits++;
        }
        System.out.println("pi~= " + (4.0 * hits / n));
    }
}
```
Observed output: `pi~= 3.14046`
Follow-up: How many darts for 3 correct digits with high confidence, and which inequality justifies the count?

## Q3: Show the Fermat test catching 15 but fooled by Carmichael number 561.
Key insight: Base-2 Fermat usually exposes composites (2^14 != 1 mod 15), but Carmichael numbers like 561 = 3*11*17 pass every coprime base - the test is one-sided with real blind spots. That limitation is exactly why Miller-Rabin adds the square-root check.
Complexity: Time O(log n) modular multiplications per base; space O(1).
```java
public class L20Q3Fermat {
    static long mp(long x, long e, long m) {
        long r = 1;
        while (e > 0) { if ((e & 1) == 1) r = r * x % m; x = x * x % m; e >>= 1; }
        return r;
    }
    public static void main(String[] args) {
        System.out.println("2^14 mod 15=" + mp(2, 14, 15) + " 2^560 mod 561=" + mp(2, 560, 561));
    }
}
```
Observed output: `2^14 mod 15=4 2^560 mod 561=1`
Follow-up: Why does Miller-Rabin catch 561 where Fermat fails: what does x^2 = 1 mod p imply for prime p?

## Checklist
- State the key insight before coding; name the loop invariant.
- Derive time and space bounds from the code structure, not from memory.
