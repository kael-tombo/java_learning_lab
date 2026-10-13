# Mock Interview: Sorting Basics: Insertion Sort, Merge, Quicksort Partition
> Three worked questions on elementary sorting. Each answer is complete runnable Java; outputs below were observed.

## Q1: Sort a fixed array with insertion sort and show the result.
Key insight: Insertion sort keeps the prefix a[0..i-1] sorted and inserts a[i] by shifting larger elements right; shifting (not swapping) is what makes it stable and cheap on nearly sorted input.
Complexity: Time O(n^2) worst case, O(n) on sorted input; space O(1) extra.
```java
public class L01Q1Insertion {
    public static void main(String[] args) {
        int[] a = {5, 2, 4, 6, 1, 3};
        for (int i = 1; i < a.length; i++) {
            int key = a[i], j = i - 1;
            while (j >= 0 && a[j] > key) { a[j + 1] = a[j]; j--; }
            a[j + 1] = key;
        }
        StringBuilder s = new StringBuilder();
        for (int v : a) s.append(v).append(' ');
        System.out.println("sorted: " + s.toString().trim());
    }
}
```
Observed output: `sorted: 1 2 3 4 5 6`
Follow-up: Why does the inner loop stop early on sorted input, and how many comparisons does n=6 sorted input need?

## Q2: Merge two sorted arrays and count the comparisons.
Key insight: Merge walks both arrays once, always taking the smaller front element; the comparison count on sizes m, n is at most m + n - 1 because each comparison consumes one element and the last element needs none.
Complexity: Time O(m + n); space O(m + n) for the output.
```java
public class L01Q2Merge {
    public static void main(String[] args) {
        int[] l = {1, 3, 5}, r = {2, 4, 6};
        int[] m = new int[6];
        int i = 0, j = 0, k = 0, cmp = 0;
        while (i < 3 && j < 3) { cmp++; if (l[i] <= r[j]) m[k++] = l[i++]; else m[k++] = r[j++]; }
        while (i < 3) m[k++] = l[i++];
        while (j < 3) m[k++] = r[j++];
        System.out.println("merged=" + m[0] + m[1] + m[2] + m[3] + m[4] + m[5] + " cmp=" + cmp);
    }
}
```
Observed output: `merged=123456 cmp=5`
Follow-up: Where does the m + n - 1 comparison bound come from, and which input interleaving attains it?

## Q3: Perform one Lomuto partition step and report the pivot position.
Key insight: Lomuto maintains that a[lo..i-1] <= pivot and a[i..j-1] > pivot; after the scan, swapping a[i] with the pivot puts the pivot in its final sorted position with smaller elements left of it.
Complexity: Time O(n) for the segment; space O(1).
```java
public class L01Q3Partition {
    static int part(int[] a, int lo, int hi) {
        int p = a[hi], i = lo, t;
        for (int j = lo; j < hi; j++)
            if (a[j] <= p) { t = a[i]; a[i] = a[j]; a[j] = t; i++; }
        t = a[i]; a[i] = a[hi]; a[hi] = t;
        return i;
    }
    public static void main(String[] args) {
        int[] a = {3, 6, 1, 5, 2, 4};
        int q = part(a, 0, 5);
        StringBuilder s = new StringBuilder();
        for (int v : a) s.append(v).append(' ');
        System.out.println("pivot=4 at " + q + ": " + s.toString().trim());
    }
}
```
Observed output: `pivot=4 at 3: 3 1 2 4 6 5`
Follow-up: What goes wrong for quicksort when the pivot is always the minimum, and what recurrence describes it?

## Checklist
- State the key insight before coding; name the loop invariant.
- Derive time and space bounds from the code structure, not from memory.
