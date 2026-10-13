# Mock Interview: Backtracking: Subsets, N-Queens, Permutations
> Three worked questions on systematic search with undo. Each answer is complete runnable Java; outputs below were observed.

## Q1: Enumerate all subsets of {1, 2, 3}.
Key insight: Backtracking builds a decision tree (take/skip each element) and undoes the take after recursing, so one path buffer serves the whole search. 2^n leaves means 8 subsets here - enumeration cost is inherent, not overhead.
Complexity: Time O(n * 2^n); space O(n) stack plus output.
```java
import java.util.ArrayList;
import java.util.List;
public class L10Q1Subsets {
    static List<String> out = new ArrayList<>();
    static void go(int[] a, int i, List<Integer> cur) {
        if (i == a.length) { out.add(cur.toString()); return; }
        cur.add(a[i]); go(a, i + 1, cur);
        cur.remove(cur.size() - 1); go(a, i + 1, cur);
    }
    public static void main(String[] args) {
        go(new int[]{1, 2, 3}, 0, new ArrayList<>());
        System.out.println("subsets=" + out.size() + " " + out);
    }
}
```
Observed output: `subsets=8 [[1, 2, 3], [1, 2], [1, 3], [1], [2, 3], [2], [3], []]`
Follow-up: How does the code change to enumerate only subsets of size k, and how many leaves remain?

## Q2: Count N-queens solutions for n = 4.
Key insight: Queens are placed row by row with column/diagonal conflict tests; a dead row triggers backtrack (remove and try the next column). Pruning cuts the 4^4 naive space to 16 leaves checked, yielding 2 solutions.
Complexity: Time O(n!) worst case with pruning; space O(n).
```java
public class L10Q2Queens {
    static int n = 4, sols = 0;
    static int[] q = new int[4];
    static boolean ok(int r, int c) {
        for (int i = 0; i < r; i++)
            if (q[i] == c || Math.abs(q[i] - c) == r - i) return false;
        return true;
    }
    static void go(int r) {
        if (r == n) { sols++; return; }
        for (int c = 0; c < n; c++) if (ok(r, c)) { q[r] = c; go(r + 1); }
    }
    public static void main(String[] args) {
        go(0);
        System.out.println("queens(4)=" + sols);
    }
}
```
Observed output: `queens(4)=2`
Follow-up: Why does the diagonal test use Math.abs(q[i]-c) == r-i, and what symmetry halves the search?

## Q3: List all permutations of ABC.
Key insight: Fixing position i and permuting the rest, with a swap-back after each recursion, visits all n! orders exactly once. The swap-back (undo) is what distinguishes backtracking from plain recursion.
Complexity: Time O(n * n!); space O(n) stack plus output.
```java
import java.util.ArrayList;
import java.util.List;
public class L10Q3Perms {
    static List<String> out = new ArrayList<>();
    static void go(char[] a, int i) {
        if (i == a.length) { out.add(new String(a)); return; }
        for (int j = i; j < a.length; j++) {
            char t = a[i]; a[i] = a[j]; a[j] = t;
            go(a, i + 1);
            t = a[i]; a[i] = a[j]; a[j] = t;
        }
    }
    public static void main(String[] args) {
        go(new char[]{'A', 'B', 'C'}, 0);
        System.out.println("perms=" + out.size() + " " + out);
    }
}
```
Observed output: `perms=6 [ABC, ACB, BAC, BCA, CBA, CAB]`
Follow-up: How do you avoid duplicate permutations when the input has repeated letters?

## Checklist
- State the key insight before coding; name the loop invariant.
- Derive time and space bounds from the code structure, not from memory.
