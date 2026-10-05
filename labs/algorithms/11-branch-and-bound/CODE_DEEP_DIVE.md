# CODE_DEEP_DIVE — Branch and Bound (0/1 Knapsack B&B)
> Java implementation with complexity annotations + pitfalls.

## 1. Complete Implementation
```java
import java.util.*;
public final class BnB { // worst O(2ⁿ); bound prunes typical
    static class Node implements Comparable<Node> { int i, w, v; double ub; // layers
        public int compareTo(Node o) { return Double.compare(o.ub, ub); } } // best-first max-heap
    static double fracBound(int[] w, int[] v, int W, int i, int cw, int cv) { // O(n) relaxation
        double b = cv; int c = cw;         // O(1)
        for (int k = i; k < w.length && c < W; k++) { // fractional fill by ratio order
            if (c + w[k] <= W) { c += w[k]; b += v[k]; } // take whole O(1)
            else { b += (double)(W - c) / w[k] * v[k]; break; } // fraction O(1)
        }
        return b;                          // admissible upper (≥ true optimum)
    }
    public static int solve(int[] w, int[] v, int W) { // items pre-sorted by v/w desc
        PriorityQueue<Node> pq = new PriorityQueue<>(); // O(log Q) per node
        Node r = new Node(); r.ub = fracBound(w, v, W, 0, 0, 0); pq.add(r); // root
        int best = 0;                      // incumbent (seed with greedy for prune)
        while (!pq.isEmpty()) {            // nodes explored (worst 2ⁿ)
            Node u = pq.poll();            // O(log Q) best-first
            if (u.ub <= best) continue;    // FATHOM: bound-dominated (sound)
            if (u.i == w.length) continue; // leaf
            int ni = u.i + 1;              // branch on item i
            if (u.w + w[u.i] <= W) {       // take branch (feasible)
                int nv = u.v + v[u.i]; best = Math.max(best, nv); // update incumbent
                Node t = new Node(); t.i = ni; t.w = u.w + w[u.i]; t.v = nv;
                t.ub = fracBound(w, v, W, ni, t.w, t.v); if (t.ub > best) pq.add(t); // O(n+log)
            }
            Node s = new Node(); s.i = ni; s.w = u.w; s.v = u.v; // skip branch
            s.ub = fracBound(w, v, W, ni, s.w, s.v); if (s.ub > best) pq.add(s);
        }
        return best;                       // optimal (fathom rules preserve it)
    }
}
```

## 2. Complexity Annotations
- Nodes worst 2ⁿ; bound O(n) each → worst O(n·2ⁿ); typical far less.
- PQ ops O(log Q); DFS-LIFO variant O(1) + less memory (alternative).
- Presort by ratio O(n log n) once (required for bound validity).

## 3. Pitfalls (5 + fixes)
1. Unsorted bound → inadmissible (over/under). Fix: sort by v/w desc first.
2. `ub <= best` vs `<` — use `<=` to fathom ties (keeps optimal, fewer nodes).
3. No greedy seed → weak early prune. Fix: seed best with greedy/heuristic.
4. Double precision edge (`ub` tie) → epsilon or cross-multiplied fractions.
5. `int` overflow on v sums → long for large values.

## 4. Micro-Opts
- Incremental bound delta O(1) from parent; strong branching for tight instances.

## 5. Test Snippets
```java
// (2,3)(3,4)(4,5) W5 => 7; fractional trap instance: bound > optimum, B&B still exact
```

## 6. Checklist
- [ ] Ratio presort. [ ] Fathom rules. [ ] Greedy seed. [ ] Optimality comment.
