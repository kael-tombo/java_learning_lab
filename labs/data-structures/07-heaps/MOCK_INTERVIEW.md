# Mock Interview: Heaps

## Q1 — Kth Largest Element (LC 215)

**Problem.** Find the kth largest element in an unsorted array.

**Key insight.** Keep a min-heap of size k: it always holds the k largest seen, with the kth largest at the top.

**Complexity.** Time O(n log k), space O(k).

```java
import java.util.PriorityQueue;

public class HeapsQ1 {
    public static int kthLargest(int[] a, int k) {
        PriorityQueue<Integer> pq = new PriorityQueue<>();
        for (int x : a) {
            pq.add(x);
            if (pq.size() > k) pq.poll();
        }
        return pq.peek();
    }

    public static void main(String[] args) {
        System.out.println(kthLargest(new int[]{3, 2, 1, 5, 6, 4}, 2));
    }
}
```

Output:

```
5
```

## Q2 — Linear-Time Heapify

**Problem.** Explain why building a heap from an array is O(n), not O(n log n).

**Key insight.** Sift down from the last parent to the root. Most nodes sit near the leaves with tiny sift distances; summing height-weighted work over levels converges to O(n).

**Complexity.** Time O(n), space O(1) in place.

```java
import java.util.Arrays;

public class HeapsQ2 {
    static void siftDown(int[] a, int i, int n) {
        while (true) {
            int l = 2 * i + 1, r = 2 * i + 2, m = i;
            if (l < n && a[l] > a[m]) m = l;
            if (r < n && a[r] > a[m]) m = r;
            if (m == i) return;
            int t = a[i]; a[i] = a[m]; a[m] = t;
            i = m;
        }
    }

    public static void main(String[] args) {
        int[] a = {3, 1, 4, 1, 5, 9, 2, 6};
        for (int i = a.length / 2 - 1; i >= 0; i--) siftDown(a, i, a.length);
        System.out.println(Arrays.toString(a));
    }
}
```

Output:

```
[9, 6, 4, 1, 5, 3, 2, 1]
```

## Q3 — Running Median with Two Heaps (LC 295)

**Problem.** Support adding numbers and querying the median.

**Key insight.** Split the stream: a max-heap for the lower half, a min-heap for the upper half, kept balanced within one element. The median sits at the tops.

**Complexity.** Time O(log n) add, O(1) median, space O(n).

```java
import java.util.Collections;
import java.util.PriorityQueue;

public class HeapsQ3 {
    public static void main(String[] args) {
        PriorityQueue<Integer> lo = new PriorityQueue<>(Collections.reverseOrder());
        PriorityQueue<Integer> hi = new PriorityQueue<>();
        int[] stream = {1, 2, 3};
        for (int x : stream) {
            lo.add(x);
            hi.add(lo.poll());
            if (hi.size() > lo.size()) lo.add(hi.poll());
        }
        double median = lo.size() > hi.size() ? lo.peek() : (lo.peek() + hi.peek()) / 2.0;
        System.out.println(median);
    }
}
```

Output:

```
2.0
```
