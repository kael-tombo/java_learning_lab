# Mock Interview: Searching: Binary Search, Lower Bound, Rotated Arrays
> Three worked questions on searching sorted data. Each answer is complete runnable Java; outputs below were observed.

## Q1: Write iterative binary search and test a hit and a miss.
Key insight: Each step discards half the interval; the midpoint must be computed as lo + (hi - lo) / 2 so lo + hi cannot overflow. Returning -1 on a miss keeps the contract total.
Complexity: Time O(log n); space O(1).
```java
public class L03Q1BSearch {
    static int search(int[] a, int t) {
        int lo = 0, hi = a.length - 1;
        while (lo <= hi) {
            int m = lo + (hi - lo) / 2;
            if (a[m] == t) return m;
            if (a[m] < t) lo = m + 1; else hi = m - 1;
        }
        return -1;
    }
    public static void main(String[] args) {
        int[] a = {1, 3, 5, 7, 9, 11, 13};
        System.out.println("idx(7)=" + search(a, 7) + " idx(8)=" + search(a, 8));
    }
}
```
Observed output: `idx(7)=3 idx(8)=-1`
Follow-up: How many iterations at most for n = 10^6, and which recurrence gives that bound?

## Q2: Find the lower bound: first index with value >= target.
Key insight: Lower bound keeps the half-open invariant a[lo..hi) with all of a[0..lo) < target; when the loop ends lo is the first position that can hold target, which also counts how many elements are smaller.
Complexity: Time O(log n); space O(1).
```java
public class L03Q2LowerBound {
    static int lb(int[] a, int t) {
        int lo = 0, hi = a.length;
        while (lo < hi) {
            int m = lo + (hi - lo) / 2;
            if (a[m] < t) lo = m + 1; else hi = m;
        }
        return lo;
    }
    public static void main(String[] args) {
        int[] a = {1, 2, 4, 4, 4, 7};
        System.out.println("lb(4)=" + lb(a, 4) + " lb(5)=" + lb(a, 5) + " lb(0)=" + lb(a, 0));
    }
}
```
Observed output: `lb(4)=2 lb(5)=5 lb(0)=0`
Follow-up: How do you get the upper bound (first > target) and the occurrence count from two such calls?

## Q3: Search a target in a rotated sorted array.
Key insight: Even rotated, one half of [lo..hi] around the midpoint is always sorted; test whether the target lies in that sorted half and discard the other half. The halving argument is unchanged.
Complexity: Time O(log n); space O(1).
```java
public class L03Q3Rotated {
    static int search(int[] a, int t) {
        int lo = 0, hi = a.length - 1;
        while (lo <= hi) {
            int m = lo + (hi - lo) / 2;
            if (a[m] == t) return m;
            if (a[lo] <= a[m]) { if (a[lo] <= t && t < a[m]) hi = m - 1; else lo = m + 1; }
            else { if (a[m] < t && t <= a[hi]) lo = m + 1; else hi = m - 1; }
        }
        return -1;
    }
    public static void main(String[] args) {
        int[] a = {4, 5, 6, 7, 0, 1, 2};
        System.out.println("rot(0)=" + search(a, 0) + " rot(3)=" + search(a, 3));
    }
}
```
Observed output: `rot(0)=4 rot(3)=-1`
Follow-up: What breaks when duplicates are allowed, and what is the worst case then?

## Checklist
- State the key insight before coding; name the loop invariant.
- Derive time and space bounds from the code structure, not from memory.
