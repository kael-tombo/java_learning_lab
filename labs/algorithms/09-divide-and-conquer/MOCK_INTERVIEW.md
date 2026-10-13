# Mock Interview: Divide and Conquer: Mergesort, Maximum Subarray, Master Theorem
> Three worked questions on splitting problems and combining answers. Each answer is complete runnable Java; outputs below were observed.

## Q1: Sort a reversed array with mergesort and count comparisons.
Key insight: Mergesort splits in half, sorts each half, and merges in linear time: T(n) = 2T(n/2) + O(n), which the Master theorem (Case 2) resolves to Theta(n log n). Counting comparisons makes the combine cost concrete.
Complexity: Time Theta(n log n); space O(n).
```java
import java.util.Arrays;
public class L09Q1MergeCount {
    static int cmp = 0;
    static int[] sort(int[] a) {
        if (a.length <= 1) return a;
        int m = a.length / 2;
        int[] l = sort(Arrays.copyOfRange(a, 0, m));
        int[] r = sort(Arrays.copyOfRange(a, m, a.length));
        int[] o = new int[a.length];
        int i = 0, j = 0, k = 0;
        while (i < l.length && j < r.length) { cmp++; o[k++] = l[i] <= r[j] ? l[i++] : r[j++]; }
        while (i < l.length) o[k++] = l[i++];
        while (j < r.length) o[k++] = r[j++];
        return o;
    }
    public static void main(String[] args) {
        int[] a = {8, 7, 6, 5, 4, 3, 2, 1};
        System.out.println("sorted=" + Arrays.toString(sort(a)) + " cmp=" + cmp);
    }
}
```
Observed output: `sorted=[1, 2, 3, 4, 5, 6, 7, 8] cmp=12`
Follow-up: Apply Master Case 2 to T(n) = 2T(n/2) + Theta(n) and state log_b(a) explicitly.

## Q2: Find the maximum subarray with a divide-and-conquer split.
Key insight: The best subarray either lies wholly left, wholly right, or crosses the middle; the crossing case is linear (extend from the middle both ways). Trying only those three cases covers every possibility, which is the correctness argument.
Complexity: Time O(n log n) via T(n) = 2T(n/2) + O(n); space O(log n) stack.
```java
public class L09Q2MaxSub {
    static int cross(int[] a, int lo, int m, int hi) {
        int l = -999999, r = -999999, s = 0;
        for (int i = m; i >= lo; i--) { s += a[i]; l = Math.max(l, s); }
        s = 0;
        for (int i = m + 1; i <= hi; i++) { s += a[i]; r = Math.max(r, s); }
        return l + r;
    }
    static int solve(int[] a, int lo, int hi) {
        if (lo == hi) return a[lo];
        int m = (lo + hi) / 2;
        return Math.max(Math.max(solve(a, lo, m), solve(a, m + 1, hi)), cross(a, lo, m, hi));
    }
    public static void main(String[] args) {
        System.out.println("maxsub=" + solve(new int[]{-2, 1, -3, 4, -1, 2, 1, -5, 4}, 0, 8));
    }
}
```
Observed output: `maxsub=6`
Follow-up: Kadane's algorithm does this in O(n): what optimal-substructure observation lets it skip the recursion?

## Q3: Count binary search steps on n = 2^20 to exhibit O(log n).
Key insight: Binary search satisfies T(n) = T(n/2) + O(1): Master Case 2 with log_b(a) = 0 gives Theta(log n). Measuring steps on 2^20 shows the ~20 bound directly instead of asserting it.
Complexity: Time Theta(log n); space O(1).
```java
public class L09Q3Steps {
    public static void main(String[] args) {
        int n = 1 << 20, lo = 0, hi = n - 1, steps = 0, target = n - 1;
        while (lo <= hi) {
            steps++;
            int m = lo + (hi - lo) / 2;
            if (m == target) break;
            if (m < target) lo = m + 1; else hi = m - 1;
        }
        System.out.println("n=" + n + " steps=" + steps);
    }
}
```
Observed output: `n=1048576 steps=21`
Follow-up: Why does T(n) = T(n/2) + O(1) fall under Master Case 2, and what are a, b, and f(n)?

## Checklist
- State the key insight before coding; name the loop invariant.
- Derive time and space bounds from the code structure, not from memory.
