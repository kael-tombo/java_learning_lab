# Mock Interview: Complexity Analysis: O, Omega, Theta with Measured Step Counts
> Three worked questions on asymptotic bounds grounded in counts. Each answer is complete runnable Java; outputs below were observed.

## Q1: Measure binary search steps on n = 1024 to exhibit Theta(log n).
Key insight: T(n) = T(n/2) + O(1) unrolls to one constant-cost level per halving: at most ceil(log2 n) + 1 iterations. Measuring on 1024 shows ~11 steps, matching the theory instead of quoting it.
Complexity: Time Theta(log n); space O(1).
```java
public class L12Q1Steps {
    public static void main(String[] args) {
        int n = 1024, lo = 0, hi = n - 1, steps = 0, target = n - 1;
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
Observed output: `n=1024 steps=11`
Follow-up: State the formal definition of O(g(n)) with witnesses c and n0 for T(n) = 3n + 7.

## Q2: Contrast insertion-sort shifts with mergesort comparisons on reversed n = 64.
Key insight: Insertion sort on reversed input shifts ~n^2/2 times (quadratic), while mergesort always pays Theta(n log n) comparisons. The measured gap at n = 64 already shows the asymptotics separating.
Complexity: Insertion Theta(n^2) worst case; mergesort Theta(n log n) always.
```java
import java.util.Arrays;
public class L12Q2Gap {
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
        int n = 64;
        long shifts = 0;
        for (int i = 1; i < n; i++) shifts += i;
        int[] a = new int[n];
        for (int i = 0; i < n; i++) a[i] = n - i;
        sort(a);
        System.out.println("insertion-shifts=" + shifts + " mergesort-cmp=" + cmp);
    }
}
```
Observed output: `insertion-shifts=2016 mergesort-cmp=192`
Follow-up: Why is the comparison sorting lower bound Omega(n log n), and which sorts escape it and how?

## Q3: Show best vs worst case of linear search by counting comparisons.
Key insight: Best case O(1) (target first), worst case Theta(n) (target last or absent): one algorithm, two bounds. Big-O describes an upper bound on a stated case, which is why the case must always be named.
Complexity: Best O(1), worst Theta(n); space O(1).
```java
public class L12Q3Linear {
    static int find(int[] a, int t) {
        int c = 0;
        for (int v : a) { c++; if (v == t) break; }
        return c;
    }
    public static void main(String[] args) {
        int[] a = new int[100];
        for (int i = 0; i < 100; i++) a[i] = i;
        System.out.println("best=" + find(a, 0) + " worst=" + find(a, 99) + " miss=" + find(a, -1));
    }
}
```
Observed output: `best=1 worst=100 miss=100`
Follow-up: Define Omega and Theta formally, and give a function that is O(n^2) but not Theta(n^2).

## Checklist
- State the key insight before coding; name the loop invariant.
- Derive time and space bounds from the code structure, not from memory.
