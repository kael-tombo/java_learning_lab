# Mock Interview: Scheduling Algorithms

## Q1: Select the maximum set of non-overlapping intervals

Key insight: sort by finish time and take each job starting after the last accepted end; earliest finish leaves the most room, optimal by exchange.
Complexity: O(n log n) time for the sort, O(n) space; sorting by start time instead fails on one-long-versus-many-short inputs.

```java
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.List;
public class IntervalSchedulingDemo {
    public static void main(String[] a) {
        int[][] jobs = {{1, 4}, {3, 5}, {0, 6}, {5, 7}, {8, 9}, {5, 9}};
        Arrays.sort(jobs, Comparator.comparingInt(j -> j[1])); // earliest finish first
        List<String> picks = new ArrayList<>();
        int lastEnd = -1;
        for (int[] j : jobs) if (j[0] >= lastEnd) { picks.add("[" + j[0] + "," + j[1] + "]"); lastEnd = j[1]; }
        System.out.println(picks + " count=" + picks.size());
    }
}
```

Output:

```text
[[1,4], [5,7], [8,9]] count=3
```

## Q2: Test EDF feasibility for periodic tasks

Key insight: with period equal to deadline, earliest-deadline-first on one processor meets all deadlines exactly when total utilization is at most 1.
Complexity: O(n) time, O(1) space; fixed-priority rate-monotonic has a stricter bound and can fail sets EDF passes.

```java
public class EdfDemo {
    public static void main(String[] a) {
        int[] c = {1, 2, 2}, p = {4, 6, 8}; // execution times, periods (= deadlines)
        double u = 0;
        for (int i = 0; i < c.length; i++) u += (double) c[i] / p[i];
        System.out.println("util=" + u + " feasible=" + (u <= 1.0));
    }
}
```

Output:

```text
util=0.8333333333333333 feasible=true
```

## Q3: Greedily balance jobs across identical machines

Key insight: place each job on the least-loaded machine; never worse than 2 - 1/m times optimal makespan on m machines.
Complexity: O(n m) scan form, O(n log m) with a heap; total work and longest job both lower-bound the optimum.

```java
import java.util.Arrays;
public class ListSchedulingDemo {
    public static void main(String[] a) {
        int[] jobs = {5, 4, 4, 3, 3, 2}, load = {0, 0}; // 2 identical machines
        for (int j : jobs) {
            int pick = load[1] < load[0] ? 1 : 0; // least-loaded machine
            load[pick] += j;
        }
        System.out.println("loads=" + Arrays.toString(load) + " makespan=" + Math.max(load[0], load[1]));
    }
}
```

Output:

```text
loads=[11, 10] makespan=11
```
