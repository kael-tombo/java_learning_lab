# Mock Interview: Advanced Sorting: Heapsort Idea, Randomized Quicksort, Counting Sort, Stability
> Three worked questions on sorting beyond the basics. Each answer is complete runnable Java; outputs below were observed.

## Q1: Sort with counting sort when keys are small integers.
Key insight: Counting sort skips comparisons entirely: it counts how often each key occurs, then writes keys back in order. It wins only when the key range k is small relative to n.
Complexity: Time O(n + k); space O(k) for the counts.
```java
public class L02Q1Counting {
    public static void main(String[] args) {
        int[] a = {4, 2, 2, 8, 3, 3, 1};
        int[] c = new int[9];
        for (int v : a) c[v]++;
        StringBuilder s = new StringBuilder();
        for (int v = 0; v < 9; v++)
            for (int k = 0; k < c[v]; k++) s.append(v).append(' ');
        System.out.println("counting: " + s.toString().trim());
    }
}
```
Observed output: `counting: 1 2 2 3 3 4 8`
Follow-up: For which (n, k) does counting sort lose to mergesort, and why does the O(n + k) bound explain it?

## Q2: Sort with randomized quicksort (fixed seed so the run is reproducible).
Key insight: A random pivot makes the bad split unlikely on every level; with a fixed seed the run is deterministic, which is how you test randomized code. Expected depth stays logarithmic.
Complexity: Expected time O(n log n), worst case O(n^2); space O(log n) expected stack.
```java
import java.util.Arrays;
import java.util.Random;
public class L02Q2RandQuick {
    static Random r = new Random(7);
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
        int[] a = {9, 4, 7, 1, 8, 2, 6, 3, 5};
        sort(a, 0, a.length - 1);
        System.out.println("randquick=" + Arrays.toString(a));
    }
}
```
Observed output: `randquick=[1, 2, 3, 4, 5, 6, 7, 8, 9]`
Follow-up: Why does fixing the seed not weaken the expected-time argument for real (adversarial) inputs?

## Q3: Show that object sorting with a key comparator is stable.
Key insight: Stability means equal keys keep their original relative order. Arrays.sort on objects is stable, so sorting records by one key never scrambles a previous ordering by another key.
Complexity: Time O(n log n); space O(n) for object TimSort.
```java
import java.util.Arrays;
public class L02Q3Stable {
    public static void main(String[] args) {
        String[] w = {"bb", "a", "cc", "d"};
        Arrays.sort(w, (x, y) -> x.length() - y.length());
        System.out.println("stable-by-length: " + String.join(",", w));
    }
}
```
Observed output: `stable-by-length: a,d,bb,cc`
Follow-up: Heapsort is not stable: construct a 3-element input where equal keys change order.

## Checklist
- State the key insight before coding; name the loop invariant.
- Derive time and space bounds from the code structure, not from memory.
