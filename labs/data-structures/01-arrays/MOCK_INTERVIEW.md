# Mock Interview: Arrays

## Q1 — Two Sum (LC 1)

**Problem.** Given an array and a target, return indices of two entries that add to the target. Assume exactly one solution.

**Key insight.** Store each value's index as you scan; for `x` look up `target - x`. One pass.

**Complexity.** Time O(n), space O(n).

```java
import java.util.HashMap;
import java.util.Map;

public class ArraysQ1 {
    public static int[] twoSum(int[] a, int target) {
        Map<Integer, Integer> seen = new HashMap<>();
        for (int i = 0; i < a.length; i++) {
            Integer j = seen.get(target - a[i]);
            if (j != null) return new int[]{j, i};
            seen.put(a[i], i);
        }
        return new int[]{-1, -1};
    }

    public static void main(String[] args) {
        int[] r = twoSum(new int[]{2, 7, 11, 15}, 9);
        System.out.println(r[0] + " " + r[1]);
    }
}
```

Output:

```
0 1
```

## Q2 — Maximum Subarray (Kadane, LC 53)

**Problem.** Find the contiguous subarray with the largest sum.

**Key insight.** At each element decide: extend the running sum or restart here. Track the best seen.

**Complexity.** Time O(n), space O(1).

```java
public class ArraysQ2 {
    public static int maxSub(int[] a) {
        int cur = a[0], best = a[0];
        for (int i = 1; i < a.length; i++) {
            cur = Math.max(a[i], cur + a[i]);
            best = Math.max(best, cur);
        }
        return best;
    }

    public static void main(String[] args) {
        System.out.println(maxSub(new int[]{-2, 1, -3, 4, -1, 2, 1, -5, 4}));
    }
}
```

Output:

```
6
```

## Q3 — Binary Search (LC 704)

**Problem.** Find `target` in a sorted array, or return -1.

**Key insight.** Halve the interval each step with `mid = lo + (hi - lo) / 2` to avoid overflow.

**Complexity.** Time O(log n), space O(1).

```java
public class ArraysQ3 {
    public static int search(int[] a, int t) {
        int lo = 0, hi = a.length - 1;
        while (lo <= hi) {
            int mid = lo + (hi - lo) / 2;
            if (a[mid] == t) return mid;
            if (a[mid] < t) lo = mid + 1;
            else hi = mid - 1;
        }
        return -1;
    }

    public static void main(String[] args) {
        System.out.println(search(new int[]{-1, 0, 3, 5, 9, 12}, 9));
        System.out.println(search(new int[]{-1, 0, 3, 5, 9, 12}, 2));
    }
}
```

Output:

```
4
-1
```
