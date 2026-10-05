# CODE_DEEP_DIVE — Backtracking (N-Queens + Subsets)
> Java implementation with complexity annotations + pitfalls.

## 1. Complete Implementation
```java
import java.util.*;
public final class Backtrack { // queens O(n!) pruned; subsets O(2ⁿ)
    public static List<List<String>> queens(int n) { // bitsets O(1) place/remove
        List<List<String>> ans = new ArrayList<>(); // output-dominated
        boolean[] col = new boolean[n], d1 = new boolean[2*n], d2 = new boolean[2*n]; // O(n)
        int[] q = new int[n];                // q[row]=col O(n)
        dfs(0, n, q, col, d1, d2, ans);       // T(n)=n·T(n-1) worst → O(n!)
        return ans;                          // 8-queens: 92
    }
    private static void dfs(int r, int n, int[] q, boolean[] col, boolean[] d1, boolean[] d2, List<List<String>> ans) {
        if (r == n) { ans.add(board(q, n)); return; } // O(n²) copy per solution
        for (int c = 0; c < n; c++) {        // branching ≤ n, pruned by sets
            int a = r + c, b = r - c + n;    // O(1) diag ids
            if (col[c] || d1[a] || d2[b]) continue; // O(1) prune
            q[r] = c; col[c] = d1[a] = d2[b] = true; // O(1) place
            dfs(r + 1, n, q, col, d1, d2, ans); // recurse
            col[c] = d1[a] = d2[b] = false;  // O(1) UNDO (vs copy)
        }
    }
    private static List<String> board(int[] q, int n) { // O(n²) render
        List<String> b = new ArrayList<>(n); // O(n)
        for (int r = 0; r < n; r++) { char[] row = new char[n]; Arrays.fill(row, '.'); row[q[r]] = 'Q'; b.add(new String(row)); }
        return b;                            // O(n²)
    }
    public static void subsets(int[] a, int i, List<Integer> cur, List<List<Integer>> out) { // O(2ⁿ) leaves
        if (i == a.length) { out.add(new ArrayList<>(cur)); return; } // O(n) copy
        cur.add(a[i]); subsets(a, i + 1, cur, out); // take branch
        cur.remove(cur.size() - 1); subsets(a, i + 1, cur, out); // skip (undo)
    }
}
```

## 2. Complexity Annotations
- Queens: nodes ≤ Σ n!/k!; bitsets make node cost O(1); output O(solutions × n²).
- Subsets: 2ⁿ leaves, depth n; copy per leaf dominates.
- Undo O(1) vs copy-state O(n) per edge — aggregate favors undo.

## 3. Pitfalls (5 + fixes)
1. Copy board per node (not solution) → O(n³) blowup. Fix: undo + copy at leaf.
2. Diag index negative (`r−c`) → offset by +n (done).
3. No symmetry breaking → 8× work; note optional `/8` (counting only).
4. Subsets aliasing (`out.add(cur)`) → all rows mutate; copy required.
5. No prune ordering → try constrained rows first (MRV) for hard instances.

## 4. Micro-Opts
- Bitmask ints for n≤32 (single-word cols/diags); iterative stack for depth.

## 5. Test Snippets
```java
assert Backtrack.queens(1).size() == 1; assert Backtrack.queens(4).size() == 2; // known counts
```

## 6. Checklist
- [ ] Undo vs copy justified. [ ] Diag offset. [ ] Solution-copy only at leaf.
