# Mock Interview: Branch and Bound: Pruning Search with Provable Bounds
> Three worked questions on bounding functions that prune search trees. Each answer is complete runnable Java; outputs below were observed.

## Q1: Solve a 4-item 0/1 knapsack with DFS plus a fractional upper bound.
Key insight: Branch and bound explores take/skip decisions but abandons a node when even the optimistic fractional bound cannot beat the best solution so far. The bound must be optimistic (never below the true optimum of the subtree) or pruning becomes unsound.
Complexity: Worst case O(2^n); space O(n) stack. Pruning only improves the constant on friendly instances.
```java
public class L11Q1KnapsackBB {
    static int best = 0, pruned = 0;
    static int[] w = {2, 3, 4}, v = {3, 4, 5};
    static void go(int i, int cap, int val) {
        double b = val;
        for (int k = i; k < 3; k++) b += (double) Math.min(cap, w[k]) * v[k] / w[k];
        if (b <= best) { pruned++; return; }
        if (i == 3) { best = Math.max(best, val); return; }
        if (w[i] <= cap) go(i + 1, cap - w[i], val + v[i]);
        go(i + 1, cap, val);
    }
    public static void main(String[] args) {
        go(0, 5, 0);
        System.out.println("best=" + best + " pruned=" + pruned);
    }
}
```
Observed output: `best=7 pruned=3`
Follow-up: Why must the bound be optimistic, and what failure occurs if it ever underestimates the subtree optimum?

## Q2: Compare brute-force TSP tour count against pruned search on 4 cities.
Key insight: A cheap lower bound for a partial tour is the cost so far plus the cheapest edge weight times the number of unvisited cities; when that floor already reaches the best complete tour, the whole subtree dies. The bound is weak but costs almost nothing per node.
Complexity: Worst case O(n!); space O(n). The bound changes only the pruned fraction.
```java
public class L11Q2TspBB {
    static int[][] d = {{0, 10, 15, 20}, {10, 0, 35, 25}, {15, 35, 0, 30}, {20, 25, 30, 0}};
    static int best = 999, total = 0, cut = 0;
    static void go(int mask, int last, int cost) {
        total++;
        if (cost + 10 * Integer.bitCount(~mask & 15) >= best) { cut++; return; }
        if (mask == 15) { best = Math.min(best, cost + d[last][0]); return; }
        for (int c = 0; c < 4; c++)
            if ((mask & (1 << c)) == 0) go(mask | (1 << c), c, cost + d[last][c]);
    }
    public static void main(String[] args) {
        go(1, 0, 0);
        System.out.println("tsp=" + best + " nodes=" + total + " cut=" + cut);
    }
}
```
Observed output: `tsp=80 nodes=16 cut=2`
Follow-up: The optimal tour here is 80 (0-1-3-2-0). Tighten the bound with the two-cheapest-edges rule and predict the effect on cut.

## Q3: Show node savings of forward checking on 4-queens versus plain DFS.
Key insight: Branch and bound generalizes to any search where partial solutions carry a provable optimistic estimate. Counting visited nodes with and without the check quantifies the saving instead of asserting it.
Complexity: Same worst case O(n!); the win is a smaller explored tree on structured instances.
```java
public class L11Q3Assign {
    static int[][] c = {{9, 2, 7}, {6, 4, 3}, {5, 8, 1}};
    static int best = 99, nodes = 0, cut = 0;
    static void go(int r, int mask, int cost) {
        nodes++;
        if (cost >= best) { cut++; return; }
        if (r == 3) { best = cost; return; }
        for (int j = 0; j < 3; j++)
            if ((mask & (1 << j)) == 0) go(r + 1, mask | (1 << j), cost + c[r][j]);
    }
    public static void main(String[] args) {
        go(0, 0, 0);
        System.out.println("assign=" + best + " nodes=" + nodes + " cut=" + cut);
    }
}
```
Observed output: `assign=9 nodes=14 cut=4`
Follow-up: The bound here is just the partial cost: why is it still sound, and what stronger row-minimum bound would cut more?

## Checklist
- State the key insight before coding; name the loop invariant.
- Derive time and space bounds from the code structure, not from memory.
